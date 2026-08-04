#!/usr/bin/env python3
"""Vision recognition CLI (provider-agnostic) with first-run setup UX.

Flow: if no API key is configured for the chosen provider, a setup window pops
up (Tkinter) where the user picks a provider, enters the key, tests the
connection, and saves it to .env. After a successful recognition the usage
dashboard opens automatically.

Usage:
    python vision_recognize.py <image|url> [question] [--provider X] [--model Y]
    python vision_recognize.py img.jpg "描述图片" --json --no-dashboard
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:  # Windows GBK consoles: avoid UnicodeEncodeError on Chinese/special chars
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import env_loader  # noqa: F401  (loads .env if present)
import usage_tracker
from providers.vision import PROVIDERS, get_config, recognize, resolve_provider


def _gui_available():
    try:
        import tkinter  # noqa: F401
        return True
    except Exception:
        return False


def _ensure_key(provider, args):
    """Return a provider that has a key; open the setup window if needed."""
    if get_config(provider).get("api_key"):
        return provider
    if args.setup or (not args.no_gui and _gui_available()):
        print("未检测到 API Key，正在打开配置窗口…", file=sys.stderr)
        import setup_gui
        setup_gui.run(provider)
        env_loader.load_env_file()
        provider = resolve_provider(args.provider)
        if get_config(provider).get("api_key"):
            return provider
    key_env = PROVIDERS[provider]["api_key_env"]
    raise RuntimeError(
        f"未配置 {provider} 的 API Key（环境变量 {key_env}）。"
        " 请填写 .env 或系统环境变量，或使用 --setup 打开配置窗口。"
    )


def _open_dashboard():
    script = str(Path(__file__).resolve().parent / "usage_dashboard.py")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen([sys.executable, script], creationflags=flags)


def main():
    parser = argparse.ArgumentParser(description="Vision recognition (any OpenAI-compatible provider)")
    parser.add_argument("image", help="local image path or image URL")
    parser.add_argument("question", nargs="?", default="请描述这张图片的内容。",
                        help="question / prompt for the vision model")
    parser.add_argument("--url", action="store_true", help="treat the first argument as a URL")
    parser.add_argument("--provider", default=None, help="doubao|openai|qwen|zhipu|custom (default: auto)")
    parser.add_argument("--model", default=None, help="model ID or inference endpoint ID override")
    parser.add_argument("--json", action="store_true", help="print answer and usage as JSON")
    parser.add_argument("--setup", action="store_true", help="open the API setup window first")
    parser.add_argument("--no-gui", action="store_true", help="fail fast instead of opening the setup window")
    parser.add_argument("--no-dashboard", action="store_true", help="do not open the usage dashboard after success")
    args = parser.parse_args()

    provider = resolve_provider(args.provider)
    try:
        provider = _ensure_key(provider, args)
        answer, usage, cfg = recognize(args.image, args.question,
                                       provider=provider, model=args.model)
    except Exception as exc:
        sys.exit(f"识别失败: {exc}")

    usage_tracker.log_usage(
        provider=cfg["provider"],
        model=cfg["model"],
        images=1,
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        total_tokens=usage.get("total_tokens", 0),
        question=args.question,
        answer_preview=answer,
    )

    if args.json:
        print(json.dumps({
            "provider": cfg["provider"],
            "model": cfg["model"],
            "answer": answer,
            "usage": usage,
        }, ensure_ascii=False, indent=2))
    else:
        print(answer)

    if not args.no_dashboard and not args.json:
        _open_dashboard()


if __name__ == "__main__":
    main()
