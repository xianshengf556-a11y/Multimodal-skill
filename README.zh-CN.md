# doubao-multimodal-skill

> [English](README.md) | [中文](README.zh-CN.md)

让你的 AI 助手**会看图**（任意 OpenAI 兼容的视觉模型）和**会听写**（豆包语音 ASR），自带**用量面板**：识别了多少张图、每个模型用了多少 token，一目了然。

![python](https://img.shields.io/badge/Python-3.9+-blue) ![license](https://img.shields.io/badge/License-MIT-green)

## 有什么

- **聊天里看图**：截图、照片、论文图直接拖进对话框，助手帮你读（描述、OCR、图表、界面）
- **任意视觉厂商**：豆包、OpenAI、通义 Qwen-VL、智谱 GLM-4V、本地模型都行，换厂商只改一处
- **语音转文字**：wav/mp3/ogg 录音转文本
- **用量面板**：一个窗口显示识别张数、各模型 token 用量

## 聊天用户快速开始（就两步）

**第 1 步：安装。** 下载或克隆本仓库，把文件夹放进 skills 目录：

```bash
git clone https://github.com/xianshengf556-a11y/Multimodal-skill.git
```

- Windows：把文件夹放到 `C:\Users\<你>\.codex\skills\`
- macOS / Linux：放到 `~/.codex/skills/`

**第 2 步：使用。** 把图片拖进聊天框，问"这是什么？"。第一次会自动弹配置窗口：选厂商 → 粘贴 API Key → 点"测试" → "保存"。之后就能正常识别，用量面板也会自动打开。

> 日常使用完全不用碰终端；命令行是给开发者用的（见下）。

## 开发者快速开始

```bash
pip install -r requirements.txt

python scripts/vision_recognize.py 图片.png "这是什么？" --json
python scripts/usage_dashboard.py
```

## API Key 怎么填

**不用手动配置。** 第一次使用时会自动弹出配置窗口：选厂商 → 粘贴 API Key → 点"测试" → "保存"，完事。

Key 在哪拿：豆包 → 火山方舟控制台；OpenAI → platform.openai.com；通义 / 智谱 / 自定义 → 各自控制台。

> 开发者也可以提前用 `.env` 文件或环境变量配置（见 `.env.example`），或用 `--provider` 指定厂商。

## 常见问题

- **豆包报"模型不存在"？** 在方舟控制台创建推理接入点，把接入点 ID（`ep-xxxx`）填到 `ARK_MODEL_ID`。
- **用量数据在哪？** 本地 `usage.json`，面板里直接看。
- **会上传我的数据吗？** 只把你要识别的图片和问题发给所选厂商；用量统计只存在本地。

## 许可证

MIT
