# doubao-multimodal-skill

> [English](README.md) | [中文](README.zh-CN.md)

Give your AI assistant the ability to **see images** (any OpenAI-compatible vision model) and **transcribe speech** (Doubao ASR), with a built-in **usage dashboard** that shows how many images were recognized and how many tokens each model used.

![python](https://img.shields.io/badge/Python-3.9+-blue) ![license](https://img.shields.io/badge/License-MIT-green)

## What you get

- **See images in chat** — drag a screenshot / photo / figure into the chat; the assistant reads it (description, OCR, charts, UIs)
- **Any vision provider** — Doubao, OpenAI, Qwen-VL, GLM-4V, or a local endpoint; switch with one setting
- **Speech-to-text** — turn wav/mp3/ogg recordings into text
- **Usage dashboard** — a window that shows recognized-image count and per-model token usage

## Quick start for chat users (2 steps)

**Step 1 — install.** Clone or download this repo, then put the folder into your skills directory:

```bash
git clone https://github.com/xianshengf556-a11y/Multimodal-skill.git
```

- Windows: move the folder to `C:\Users\<you>\.codex\skills\`
- macOS / Linux: move it to `~/.codex/skills/`

**Step 2 — use it.** Drag an image into the chat and ask "what is this?". The first time, a setup window pops up: pick a provider, paste your API key, click **Test**, then **Save**. That's it — recognition and the usage dashboard start working.

> No terminal needed for everyday use. The command line is only for developers (below).

## Quick start for developers

```bash
pip install -r requirements.txt
cp .env.example .env     # fill in your key, e.g. ARK_API_KEY=...

python scripts/vision_recognize.py img.png "what is this?" --json
python scripts/usage_dashboard.py
```

## API keys (the short version)

| Provider | Variables | Where to get it |
|---|---|---|
| Doubao | `ARK_API_KEY` (+ `ARK_MODEL_ID` = endpoint ID) | Volcano Ark console |
| OpenAI | `OPENAI_API_KEY` | platform.openai.com |
| Qwen / Zhipu / custom | see `.env.example` | their consoles |

Pick a provider with `VISION_PROVIDER` (or `--provider`); if unset it is auto-detected from whichever key exists. Full variable list: [.env.example](.env.example).

## FAQ

- **Doubao says "model not found"?** Create an inference endpoint in the Ark console and put its ID (`ep-xxxx`) into `ARK_MODEL_ID`.
- **Where is my usage data?** Local `usage.json`; view it in the dashboard.
- **Does it upload my data?** Only your image and question are sent to the provider you chose. Usage stats stay on your machine.

## License

MIT
