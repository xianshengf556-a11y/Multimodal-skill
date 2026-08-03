#!/usr/bin/env python3
"""豆包多模态组合示例：语音指令 + 图片 + 文本综合回答。

流程: 语音文件 -> ASR 转文字 -> 与图片一起送入豆包视觉模型 -> 输出回答。

环境变量: ARK_API_KEY, DOUBAO_APP_ID, DOUBAO_TOKEN, DOUBAO_CLUSTER

用法:
    python multimodal_pipeline.py <音频文件> <图片路径> [--model 模型ID]
"""

import argparse
import os
import sys

import requests

from asr_recognize import build_app, query, submit
from vision_recognize import ARK_BASE_URL, DEFAULT_MODEL, file_to_data_url


def transcribe(audio_path: str, format_name: str) -> str:
    import base64
    from pathlib import Path

    app = build_app()
    p = Path(audio_path)
    audio = {"data": base64.b64encode(p.read_bytes()).decode("utf-8")}
    task_id = submit(app, audio, format_name)
    return query(app, task_id)


def answer(text: str, image: str, model: str) -> str:
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        sys.exit("缺少环境变量 ARK_API_KEY。")
    prompt = (
        "下面是一段语音转写的内容和一张图片，请结合两者回答语音中的问题。\n"
        f"语音转写: {text}"
    )
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": file_to_data_url(image)}},
                ],
            }
        ],
    }
    resp = requests.post(
        f"{ARK_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=120,
    )
    if resp.status_code != 200:
        sys.exit(f"调用失败 HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        sys.exit(f"响应格式异常: {data}")


def main() -> None:
    parser = argparse.ArgumentParser(description="豆包多模态组合（语音+图片）")
    parser.add_argument("audio", help="语音文件路径")
    parser.add_argument("image", help="图片路径")
    parser.add_argument("--format", default="wav", help="音频格式，默认 wav")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"视觉模型 ID，默认 {DEFAULT_MODEL}")
    args = parser.parse_args()

    print("Step 1/2: 语音转写...", file=sys.stderr)
    text = transcribe(args.audio, args.format)
    print(f"语音转写结果: {text}", file=sys.stderr)

    print("Step 2/2: 图片+文本理解...", file=sys.stderr)
    print(answer(text, args.image, args.model))


if __name__ == "__main__":
    main()
