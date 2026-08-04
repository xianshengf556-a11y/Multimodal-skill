#!/usr/bin/env python3
"""豆包语音大模型 - 录音文件识别示例脚本（HTTP 标准版）。

依赖:
    pip install requests

环境变量:
    DOUBAO_APP_ID    豆包语音 App ID（必填）
    DOUBAO_TOKEN     豆包语音 Access Token（必填）
    DOUBAO_CLUSTER   语音服务集群名（必填，控制台获取）

用法:
    python asr_recognize.py <音频文件> [--url <音频URL>] [--format wav]

说明:
    认证方式为 Authorization: Bearer; <TOKEN>（注意分号）。提交任务后轮询
    /query 接口直到拿到转写结果。音频格式、时长、大小限制以官方文档为准。
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader  # noqa: F401  (loads .env if present)

import requests


SUBMIT_URL = "https://openspeech.bytedance.com/api/v1/auc/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v1/auc/query"


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer; {token}", "Content-Type": "application/json"}


def build_app() -> dict:
    app_id = os.environ.get("DOUBAO_APP_ID")
    token = os.environ.get("DOUBAO_TOKEN")
    cluster = os.environ.get("DOUBAO_CLUSTER")
    if not (app_id and token and cluster):
        sys.exit("缺少环境变量 DOUBAO_APP_ID / DOUBAO_TOKEN / DOUBAO_CLUSTER。")
    return {"appid": app_id, "token": token, "cluster": cluster}


def submit(app: dict, audio: dict, format_name: str) -> str:
    body = {
        "app": app,
        "user": {"uid": "multimodal-skill"},
        "audio": {**audio, "format": format_name},
        "request": {"model_name": "bigmodel"},
    }
    resp = requests.post(SUBMIT_URL, headers=auth_header(app["token"]), json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        sys.exit(f"提交失败: {data}")
    return data["id"]


def query(app: dict, task_id: str, max_seconds: int = 300) -> str:
    deadline = time.time() + max_seconds
    while time.time() < deadline:
        resp = requests.post(
            QUERY_URL,
            headers=auth_header(app["token"]),
            json={"app": {"appid": app["appid"], "token": app["token"]}, "id": task_id},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        code = data.get("code")
        if code == 0:
            return data.get("result", "")
        if code in (1, 2):  # 进行中
            time.sleep(3)
            continue
        sys.exit(f"查询失败: {data}")
    sys.exit("等待识别结果超时。")


def main() -> None:
    parser = argparse.ArgumentParser(description="豆包语音大模型录音文件识别")
    parser.add_argument("audio", nargs="?", help="本地音频文件路径（与 --url 二选一）")
    parser.add_argument("--url", help="可访问的音频 URL（与本地文件二选一）")
    parser.add_argument("--format", default="wav", help="音频格式，默认 wav")
    args = parser.parse_args()

    if not args.url and not args.audio:
        sys.exit("请提供本地音频文件路径或 --url。")

    app = build_app()
    if args.url:
        audio = {"url": args.url}
    else:
        p = Path(args.audio)
        if not p.is_file():
            sys.exit(f"音频文件不存在: {args.audio}")
        audio = {"data": base64.b64encode(p.read_bytes()).decode("utf-8")}

    task_id = submit(app, audio, args.format)
    print(f"任务已提交: {task_id}，等待识别...", file=sys.stderr)
    result = query(app, task_id)
    print(result)


if __name__ == "__main__":
    main()
