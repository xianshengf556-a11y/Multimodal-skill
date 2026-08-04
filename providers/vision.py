"""Provider-agnostic vision recognition.

All providers use the OpenAI-compatible ``chat/completions`` interface, so any
multimodal model that exposes this interface (Doubao/Ark, OpenAI, Qwen/DashScope,
Zhipu GLM-4V, local Ollama, etc.) can be plugged in via environment variables.
"""
import base64
import mimetypes
import os
import winreg
from pathlib import Path

import requests

PROVIDERS = {
    "doubao": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-1.5-vision-pro-32k",
        "api_key_env": "ARK_API_KEY",
        "model_env": "ARK_MODEL_ID",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-vl-plus",
        "api_key_env": "DASHSCOPE_API_KEY",
        "model_env": "QWEN_MODEL",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4v-plus",
        "api_key_env": "ZHIPU_API_KEY",
        "model_env": "ZHIPU_MODEL",
    },
    "custom": {
        "base_url": None,  # VISION_BASE_URL
        "model": None,     # VISION_MODEL
        "api_key_env": "VISION_API_KEY",
        "model_env": "VISION_MODEL",
    },
}


def system_proxies():
    """Read Windows system proxy settings for requests (no-op elsewhere)."""
    proxies = {}
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        ) as key:
            enable = int(winreg.QueryValueEx(key, "ProxyEnable")[0])
            server = winreg.QueryValueEx(key, "ProxyServer")[0]
        if enable and server:
            if not server.startswith("http://") and not server.startswith("https://"):
                server = f"http://{server}"
            proxies = {"http": server, "https": server}
    except OSError:
        pass
    return proxies


def resolve_provider(name=None):
    """Pick a provider: explicit name wins, otherwise auto-detect by API key."""
    if name and name in PROVIDERS:
        return name
    env_provider = os.environ.get("VISION_PROVIDER", "").strip().lower()
    if env_provider in PROVIDERS:
        return env_provider
    for p in ("doubao", "openai", "qwen", "zhipu"):
        if os.environ.get(PROVIDERS[p]["api_key_env"]):
            return p
    return "openai"


def get_config(provider):
    spec = PROVIDERS[provider]
    if provider == "custom":
        return {
            "provider": "custom",
            "base_url": os.environ.get("VISION_BASE_URL", "").rstrip("/"),
            "model": os.environ.get("VISION_MODEL", ""),
            "api_key": os.environ.get("VISION_API_KEY", ""),
        }
    return {
        "provider": provider,
        "base_url": spec["base_url"],
        "model": os.environ.get(spec["model_env"], spec["model"]),
        "api_key": os.environ.get(spec["api_key_env"], ""),
    }


def file_to_data_url(path):
    p = Path(path)
    mime, _ = mimetypes.guess_type(str(p))
    if not mime or not mime.startswith("image/"):
        mime = "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def recognize(image, question, provider=None, model=None, timeout=120):
    """Send one image + question to a vision model.

    Returns ``(answer_text, usage, config)`` where ``usage`` is the token usage
    dict returned by the provider (may be empty).
    """
    cfg = get_config(resolve_provider(provider))
    if model:
        cfg["model"] = model
    if not cfg.get("api_key"):
        raise RuntimeError(
            f"Missing API key for provider '{cfg['provider']}'."
            " Set the matching API key environment variable (see README)."
        )
    image_url = image if image.startswith(("http://", "https://")) else file_to_data_url(image)
    payload = {
        "model": cfg["model"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
    }
    resp = requests.post(
        f"{cfg['base_url']}/chat/completions",
        headers={"Authorization": f"Bearer {cfg['api_key']}"},
        json=payload,
        timeout=timeout,
        proxies=system_proxies(),
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:400]}")
    data = resp.json()
    content = data["choices"][0]["message"]["content"] or ""
    usage = data.get("usage") or {}
    return content, usage, cfg
