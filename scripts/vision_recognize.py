#!/usr/bin/env python3
"""Vision recognition CLI (provider-agnostic).

Supports any OpenAI-compatible multimodal model: Doubao/Ark, OpenAI,
Qwen/DashScope, Zhipu GLM-4V, or a custom endpoint.

Environment variables:
    VISION_PROVIDER   doubao | openai | qwen | zhipu | custom (default: auto)
    ARK_API_KEY       Doubao key (provider=doubao)
    OPENAI_API_KEY    OpenAI key (provider=openai)
    DASHSCOPE_API_KEY Qwen key (provider=qwen)
    ZHIPU_API_KEY     Zhipu key (provider=zhipu)
    VISION_API_KEY / VISION_BASE_URL / VISION_MODEL  (provider=custom)
    ARK_MODEL_ID / OPENAI_MODEL / QWEN_MODEL / ZHIPU_MODEL  (model override)
    USAGE_LOG         optional path to the usage JSON log

Usage:
    python vision_recognize.py <image|url> [question] [--provider X] [--model Y]
    python vision_recognize.py img.jpg "描述图片" --provider openai --json
"""
import argparse
import json
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

import usage_tracker
from providers.vision import recognize


def main():
    parser = argparse.ArgumentParser(description="Vision recognition (any OpenAI-compatible provider)")
    parser.add_argument("image", help="local image path or image URL")
    parser.add_argument("question", nargs="?", default="请描述这张图片的内容。",
                        help="question / prompt for the vision model")
    parser.add_argument("--url", action="store_true", help="treat the first argument as a URL")
    parser.add_argument("--provider", default=None, help="doubao|openai|qwen|zhipu|custom (default: auto)")
    parser.add_argument("--model", default=None, help="model ID or inference endpoint ID override")
    parser.add_argument("--json", action="store_true", help="print answer and usage as JSON")
    args = parser.parse_args()

    image = args.image if args.url else args.image
    try:
        answer, usage, cfg = recognize(image, args.question, provider=args.provider, model=args.model)
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


if __name__ == "__main__":
    main()
