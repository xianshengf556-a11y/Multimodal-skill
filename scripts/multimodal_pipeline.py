#!/usr/bin/env python3
"""Multimodal pipeline: (optional) ASR of an audio instruction -> vision question
on an image -> combined answer."""
import argparse
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asr_recognize
import usage_tracker
from providers.vision import recognize


def transcribe(audio_path: str) -> str:
    p = Path(audio_path)
    if not p.is_file():
        sys.exit(f"音频文件不存在: {audio_path}")
    app = asr_recognize.build_app()
    audio = {"data": base64.b64encode(p.read_bytes()).decode("utf-8")}
    task_id = asr_recognize.submit(app, audio, "wav")
    print(f"ASR 任务已提交: {task_id}，等待转写……", file=sys.stderr)
    return asr_recognize.query(app, task_id)


def main():
    parser = argparse.ArgumentParser(description="ASR (optional) + vision pipeline")
    parser.add_argument("image", help="local image path or image URL")
    parser.add_argument("--audio", help="local audio file (wav) to transcribe as the question")
    parser.add_argument("--question", default="请描述这张图片的内容。", help="text question (used when --audio is absent)")
    parser.add_argument("--provider", default=None, help="vision provider (default: auto)")
    parser.add_argument("--model", default=None, help="vision model override")
    args = parser.parse_args()

    question = args.question
    if args.audio:
        question = transcribe(args.audio)
        print(f"语音转写结果: {question}")

    answer, usage, cfg = recognize(args.image, question, provider=args.provider, model=args.model)
    usage_tracker.log_usage(
        provider=cfg["provider"],
        model=cfg["model"],
        images=1,
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        total_tokens=usage.get("total_tokens", 0),
        question=question,
        answer_preview=answer,
    )
    print(f"模型回答: {answer}")


if __name__ == "__main__":
    main()
