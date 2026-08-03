# doubao-multimodal-skill

基于豆包（火山方舟 Ark）的 Codex 多模态技能：提供**图片识别/视觉理解**（doubao vision 系列）与**语音识别**（豆包语音 ASR）能力，并可作为豆包多模态 API 的可运行参考实现。

## 功能

- 图片识别 / 视觉理解：图像描述、OCR、目标识别、图表与文档分析，支持本地图片（base64）或图片 URL
- 语音识别 ASR：wav / mp3 / ogg 等常见格式转写为文字
- 多模态串联：语音指令 → ASR → 看图 → 综合回答（`scripts/multimodal_pipeline.py`）
- 与火山方舟 Ark 的 OpenAI 兼容接口对接（`vision_recognize.py` 可直接参考或嵌入业务代码）

## 适用场景

- 主模型不支持图片输入时，用豆包 vision 临时"看图"：论文图表审阅、截图 OCR、白板/UI 界面理解、渲染结果视觉质检
- 录音、语音备忘录、会议音频转文字
- 在自有应用中集成豆包视觉 / 语音能力

## 安装

将本仓库克隆或复制到 Codex 的 skills 目录即可被识别：

```bash
git clone https://github.com/<your-name>/doubao-multimodal-skill.git
```

- Windows：放到 `C:\Users\<you>\.codex\skills\doubao-multimodal`
- macOS / Linux：放到 `~/.codex/skills/doubao-multimodal`

## 配置环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `ARK_API_KEY` | 是（图片识别） | 火山方舟 API Key，控制台开通视觉模型后获取 |
| `ARK_MODEL_ID` | 否 | 模型 ID 或推理接入点 ID，默认 `doubao-1.5-vision-pro-32k` |
| `DOUBAO_APP_ID` | 是（语音识别） | 豆包语音 App ID |
| `DOUBAO_TOKEN` | 是（语音识别） | 豆包语音 Access Token |
| `DOUBAO_CLUSTER` | 是（语音识别） | 豆包语音集群名 |

## 用法

```bash
# 图片识别（本地图片或 URL）
python scripts/vision_recognize.py 本地图片.jpg "图片里有什么？"
python scripts/vision_recognize.py https://example.com/a.png "描述图片内容" --url

# 语音转写
python scripts/asr_recognize.py 录音.wav

# 多模态串联：听一句语音指令 + 看一张图 + 综合回答
python scripts/multimodal_pipeline.py
```

## 依赖

- Python 3.9+
- `requests`

```bash
pip install -r requirements.txt
```

## 目录结构

```
doubao-multimodal-skill/
├── SKILL.md                  # 技能说明（Codex 识别入口）
├── scripts/
│   ├── vision_recognize.py   # 图片识别 / 视觉理解
│   ├── asr_recognize.py      # 语音转写
│   ├── multimodal_pipeline.py# 多模态串联示例
│   └── voice_input.py        # 录音采集辅助
├── references/
│   └── api_reference.md      # API 参考
└── agents/
    └── openai.yaml
```

## License

MIT
