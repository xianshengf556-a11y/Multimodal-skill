# 豆包多模态 API 参考

## 一、图片识别（视觉理解）

### 服务

- 平台：火山引擎方舟（ModelArk / Ark）
- 协议：OpenAI 兼容（`/chat/completions`），可用 openai SDK
- Base URL：`https://ark.cn-beijing.volces.com/api/v3`
- 认证：`Authorization: Bearer <ARK_API_KEY>`

### 模型 ID（以控制台开通为准）

常见视觉理解模型：

| 模型 | 说明 |
| --- | --- |
| `doubao-1.5-vision-pro-32k` | 视觉理解，性价比高、稳定 |
| `doubao-1.5-vision-pro` | 同系列更大上下文 |
| `doubao-seed-1.6-vision` | 新一代多模态理解 |

也可使用方舟「推理接入点」ID（`ep-xxxxxxxx`）作为 `model` 字段。本项目默认使用
`doubao-1.5-vision-pro-32k`（通过 `vision_recognize.py --model` 或环境变量 `ARK_MODEL_ID` 指定其他模型/接入点）。

### 请求格式

```json
{
  "model": "doubao-1.5-vision-pro-32k",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "描述这张图片"},
        {"type": "image_url", "image_url": {"url": "https://... 或 data:image/jpeg;base64,..."}}
      ]
    }
  ]
}
```

### 图片传入方式

- 图片 URL：必须可公网访问。
- Base64：`data:image/{格式};base64,{base64}`，适合小文件。
- 大文件（>50 MB）：优先 URL 或先压缩，请求体一般不能超过 64 MB。

## 二、语音识别（豆包语音大模型）

豆包语音与方舟大模型是两套服务，需在火山引擎「语音技术 / 豆包语音」控制台开通，使用独立的 App ID、Token、集群。

### 录音文件识别（HTTP 标准版）

- 提交：`POST https://openspeech.bytedance.com/api/v1/auc/submit`
- 查询：`POST https://openspeech.bytedance.com/api/v1/auc/query`
- 认证：`Authorization: Bearer; <DOUBAO_TOKEN>`（注意分号）
- 请求体（submit）：

```json
{
  "app": {"appid": "<DOUBAO_APP_ID>", "token": "<DOUBAO_TOKEN>", "cluster": "<DOUBAO_CLUSTER>"},
  "user": {"uid": "example"},
  "audio": {"format": "wav", "url": "https://... 或 data": "base64字符串"},
  "request": {"model_name": "bigmodel"}
}
```

- 响应含 `id`（task_id），用 `/query` 轮询；`code == 0` 表示完成，`result` 为转写文本。

### 流式语音识别（WebSocket）

- 地址：`wss://openspeech.bytedance.com/api/v3/sauc/bigmodel`
- 适合实时对话场景；需先发 metadata（含 appid、token、cluster），再传音频帧，接收临时/最终结果。

### 音频限制（以官方文档为准）

- 常见限制：PCM/WAV/MP3/OGG(OPUS) 等格式；时长和大小有上限，超限先转码或分段。

## 三、常用环境变量

| 变量 | 用途 |
| --- | --- |
| `ARK_API_KEY` | 方舟 API Key（视觉理解） |
| `DOUBAO_APP_ID` | 豆包语音 App ID（ASR） |
| `DOUBAO_TOKEN` | 豆包语音 Access Token（ASR） |
| `DOUBAO_CLUSTER` | 豆包语音集群名（ASR） |

## 四、错误排查

- `401/鉴权失败`：检查 API Key / App ID / Token 是否正确、服务是否已开通。
- `模型不存在`：模型 ID 未开通或拼写错误，去方舟控制台「开通管理」确认。
- `图片格式不支持`：确认 MIME 类型与 base64 前缀一致。
- `音频超限`：转码（如降采样到 16k 单声道 wav）或分段处理。
- 官方文档：<https://www.volcengine.com/docs/82379/1263482>（方舟）、<https://www.volcengine.com/docs/6561/80814>（豆包语音）
