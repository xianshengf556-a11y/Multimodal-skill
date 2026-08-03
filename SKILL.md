---
name: doubao-multimodal
description: >-
  基于多模态大模型（豆包/OpenAI 兼容任意视觉模型 + 豆包语音 ASR）的通用多模态技能：
  图片识别/视觉理解（图像描述、OCR、图表与文档分析）、语音转写（ASR）、
  语音+图片+文本多模态串联，以及本地可视化用量统计面板（识别图片数、各模型 token 用量）。
  适用于主模型无法看图、需要 OCR/截图/图表质检、录音转文字、或把多模态能力接入自有流程的场景。
---

# 多模态技能（视觉 + 语音 + 用量面板）

## 核心能力

1. **图片识别 / 视觉理解**：调用任意 OpenAI 兼容的多模态模型（豆包 Ark、OpenAI、通义 Qwen-VL、智谱 GLM-4V、自定义端点），支持本地图片（base64）或图片 URL，可做图像描述、OCR、目标识别、图表与文档分析。
2. **语音识别（ASR）**：调用豆包语音大模型，将 wav/mp3/ogg 录音转写为文字。
3. **多模态串联**：语音指令 → ASR 转文字 → 图片理解 → 综合回答（`multimodal_pipeline.py`）。
4. **用量统计面板**：`usage_dashboard.py`（Tkinter）实时显示累计识别图片数、每个模型消耗的 token 与最近调用记录；数据保存在本地 `usage.json`。

## 快速开始

### 1. 配置环境变量（至少一个视觉 Provider）

- `ARK_API_KEY`：火山方舟 API Key（豆包必填）。若默认模型名不可用，另设 `ARK_MODEL_ID` 为方舟推理接入点 ID。
- 其他视觉 Provider：`OPENAI_API_KEY` / `DASHSCOPE_API_KEY` / `ZHIPU_API_KEY`，或 `VISION_API_KEY + VISION_BASE_URL + VISION_MODEL`（自定义 OpenAI 兼容端点）。
- 语音：`DOUBAO_APP_ID`、`DOUBAO_TOKEN`、`DOUBAO_CLUSTER`。
- `VISION_PROVIDER`：`doubao|openai|qwen|zhipu|custom`，不设则按已有 API Key 自动检测。

### 2. 图片识别

```bash
python scripts/vision_recognize.py 本地图片.jpg "图片里有什么？"
python scripts/vision_recognize.py https://example.com/a.png "描述图片" --url --provider openai
```

每次调用自动把 Provider、模型、图片数、token 用量写入 `usage.json`。

### 3. 语音识别

```bash
python scripts/asr_recognize.py 录音.wav
```

### 4. 多模态串联

```bash
python scripts/multimodal_pipeline.py scene.jpg --audio 问题.wav
python scripts/multimodal_pipeline.py scene.jpg --question "图中有没有行人？"
```

### 5. 用量统计面板

```bash
python scripts/usage_dashboard.py
```

Windows 下也可双击 `scripts/run_dashboard.bat` 启动面板。

## 适用场景

- 主模型不支持图片输入时，用视觉模型"看图"：论文图表审阅、截图 OCR、白板/UI 界面理解、渲染结果视觉质检
- 录音、语音备忘录、会议音频转文字
- 在自有应用中集成多模态能力（`providers/vision.py` 为可运行参考实现）
- 统计多模型调用的 token 开销

## 关键接口（OpenAI 兼容）

视觉请求：
```python
from providers.vision import recognize
answer, usage, cfg = recognize("img.png", "图片里有什么？", provider="doubao")
```

语音请求（豆包 ASR）：`POST https://openspeech.bytedance.com/api/v1/auc/submit` 提交任务，轮询 `/query` 获取转写结果，详见 `scripts/asr_recognize.py`。

## 目录结构

```
doubao-multimodal-skill/
├── SKILL.md
├── providers/vision.py        # 多 Provider 视觉调用
├── scripts/
│   ├── vision_recognize.py    # 视觉识别 CLI
│   ├── asr_recognize.py       # 语音转写 CLI
│   ├── multimodal_pipeline.py # 语音+视觉串联
│   ├── voice_input.py         # 录音采集辅助
│   ├── usage_tracker.py       # usage.json 记录
│   ├── usage_dashboard.py     # Tkinter 用量面板
│   └── run_dashboard.bat      # Windows 一键启动
├── references/api_reference.md
└── agents/openai.yaml
```

## 注意事项

- 模型 ID 两种引用方式：模型名（如 `doubao-1.5-vision-pro-32k`）或方舟推理接入点 ID（`ep-xxxxx`），写入请求的 `model` 字段；账号若无默认模型名权限，请用接入点 ID。
- 语音识别对音频格式、时长、大小有限制，超限时先转码/分段。
- 调用前确认服务已在控制台开通，否则返回鉴权或模型不存在错误。
