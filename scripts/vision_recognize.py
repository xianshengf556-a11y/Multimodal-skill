#!/usr/bin/env python3
"""豆包视觉理解（图片识别）示例脚本。

环境变量:
    ARK_API_KEY  火山方舟 API Key（必填，控制台开通视觉模型后获取）
    ARK_MODEL_ID 模型 ID 或推理接入点 ID（可选，默认 doubao-1.5-vision-pro-32k）

用法:
    python vision_recognize.py <图片路径或URL> [问题] [--model 模型ID]
"""

import argparse
import base64
import mimetypes
import os
import sys
import winreg
from pathlib import Path

import requests


DEFAULT_MODEL = "doubao-1.5-vision-pro-32k"
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


def system_proxies() -> dict:
    """读取 Windows 系统代理设置，供 requests 使用。"""
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


def file_to_data_url(path: str) -> str:
    """把本地图片转成 data: URL，供 image_url 使用。"""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"图片不存在: {path}")
    mime, _ = mimetypes.guess_type(str(p))
    if not mime or not mime.startswith("image/"):
        mime = "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def recognize(image: str, question: str, is_url: bool, model: str) -> str:
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        sys.exit("缺少环境变量 ARK_API_KEY，请先设置火山方舟 API Key。")
    image_url = image if is_url else file_to_data_url(image)
    payload = {
        "model": model,
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
        f"{ARK_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=120,
        proxies=system_proxies(),
    )
    if resp.status_code != 200:
        sys.exit(f"调用失败 HTTP {resp.status_code}（请确认已开通模型 {model} 且 ARK_API_KEY 正确）: {resp.text}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        sys.exit(f"响应格式异常: {data}")


def main() -> None:
    parser = argparse.ArgumentParser(description="豆包视觉理解（图片识别）")
    parser.add_argument("image", help="本地图片路径或图片 URL")
    parser.add_argument("question", nargs="?", default="请描述这张图片的内容。", help="提问内容")
    parser.add_argument("--url", action="store_true", help="第一个参数是 URL 而非本地路径")
    parser.add_argument(
        "--model",
        default=os.environ.get("ARK_MODEL_ID", DEFAULT_MODEL),
        help=f"模型 ID 或接入点 ID，默认取环境变量 ARK_MODEL_ID，否则 {DEFAULT_MODEL}",
    )
    args = parser.parse_args()

    try:
        result = recognize(args.image, args.question, args.url, args.model)
    except requests.RequestException as exc:
        sys.exit(f"网络请求失败: {exc}")
    print(result)


if __name__ == "__main__":
    main()
