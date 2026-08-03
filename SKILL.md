---
name: doubao-multimodal
description: >-
  基于豆包（火山方舟 Ark）大模型搭建多模态应用，提供图片识别/视觉理解（doubao vision 系列模型）与语音识别（豆包语音 ASR 大模型）能力。
  Use when the user wants to: (1) 识别或理解图片内容（图像描述、OCR、目标识别、图表/文档分析），(2) 将语音或音频转写为文字，
  (3) 将图片识别与语音识别集成到多模态应用，(4) 接入火山引擎方舟 OpenAI 兼容 API 或豆包语音 API，(5) 搭建/调试/调用豆包多模态模型。
---

# 豆包多模态模型

## 核心能力

本 skill 用豆包大模型实现两种多模态能力：

1. **图片识别（视觉理解）**：调用火山方舟的 doubao vision 系列模型，支持图片 URL 或本地图片（base64），可做图像描述、OCR、目标识别、图表分析等。
2. **语音识别（ASR）**：调用豆包语音大模型，将录音文件或流式音频转写为文字。

两者可组合成"图片 + 语音 + 文本"的多模态应用。

## 快速开始

### 1. 准备密钥

在火山引擎控制台开通对应服务并获取密钥，通过环境变量注入：

- `ARK_API_KEY`：火山方舟 API Key（图片识别必填，控制台「API Key 管理」获取）
- `ARK_MODEL_ID`：模型 ID 或推理接入点 ID（可选，默认 `doubao-1.5-vision-pro-32k`）
- `DOUBAO_APP_ID`：豆包语音 App ID（语音识别必填）
- `DOUBAO_TOKEN`：豆包语音 Access Token（语音识别必填）
- `DOUBAO_CLUSTER`：语音服务集群名（语音识别必填，控制台获取）

> 使用前请在火山方舟控制台开通视觉模型，并配置环境变量：`ARK_API_KEY`（必填）；`ARK_MODEL_ID`（可选，默认 `doubao-1.5-vision-pro-32k`，也可填你的方舟推理接入点 ID）。语音识别需另行配置豆包语音三件套（`DOUBAO_APP_ID` / `DOUBAO_TOKEN` / `DOUBAO_CLUSTER`）。

### 2. 图片识别

运行 `scripts/vision_recognize.py`：

```bash
python scripts/vision_recognize.py 本地图片.jpg "这张图里有什么？"
python scripts/vision_recognize.py https://example.com/a.png "描述图片内容" --url
```

默认使用模型 ID `doubao-1.5-vision-pro-32k`，可用 `--model` 或环境变量 `ARK_MODEL_ID` 指定其他已开通的模型/推理接入点。

### 3. 语音识别（录音文件）

运行 `scripts/asr_recognize.py`：

```bash
python scripts/asr_recognize.py 录音.wav
```

支持 wav/mp3/ogg 等常见格式；本地文件会以 base64 提交，也可用 `--url` 传可访问的音频 URL。

## 关键接口速览

### 图片识别（OpenAI 兼容）

```python
import base64
import os
import requests

image_b64 = base64.b64encode(open("图片.jpg", "rb").read()).decode()
resp = requests.post(
    "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['ARK_API_KEY']}"},
    json={
        "model": "doubao-1.5-vision-pro-32k",
        "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": question},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},  # 或图片 URL
        ],
        }],
    },
    timeout=120,
)
print(resp.json()["choices"][0]["message"]["content"])
```

### 语音识别（HTTP 录音文件识别）

提交任务：`POST https://openspeech.bytedance.com/api/v1/auc/submit`，返回 `task_id`；轮询 `POST https://openspeech.bytedance.com/api/v1/auc/query` 获取转写结果。认证方式为 `Authorization: Bearer; <DOUBAO_TOKEN>`（注意分号），请求体含 `app.appid`、`cluster`、`audio` 字段。完整示例见 `scripts/asr_recognize.py`。

## 多模态组合示例

典型流程：语音输入 → ASR 转文字 → 图片理解 → 文本/语音回答。参考 `scripts/multimodal_pipeline.py`，它演示了"听一句语音指令 + 看一张图 + 豆包综合回答"的串联方式。

## 参考文档

- [API 参考](references/api_reference.md)：模型 ID、endpoint、请求格式、错误处理与限制。
- 官方文档以火山引擎控制台和 [volcengine.com/docs](https://www.volcengine.com/docs/82379/1263482) 为准，模型 ID 以你在方舟控制台开通的为准。

## 注意事项

- 模型 ID 有两种引用方式：直接用模型 ID（如 `doubao-1.5-vision-pro-32k`）或使用方舟推理接入点 ID（`ep-xxxxxxxx`），两者都写在请求的 `model` 字段。
- 本地图片优先转 base64 的 `data:` URL；大文件用 URL 或先压缩。
- 语音识别对音频格式、时长、大小有限制（不同版本不同），超限时先转码/分段。
- 调用前确认服务已在控制台开通，否则会返回鉴权或模型不存在错误。
