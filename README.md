# hermes-mimo-tts

> Xiaomi MiMo TTS provider plugin for [Hermes Agent](https://github.com/nousresearch/hermes-agent)
>
> 小米 MiMo 语音合成插件，为 [Hermes Agent](https://github.com/nousresearch/hermes-agent) 提供中文和英文语音能力

## Features / 功能

- 🎙️ **9 voices / 9种声音** — English (Mia, Chloe, Milo, Dean) + 中文 (冰糖, 茉莉, 苏打, 白桦)
- 🌐 **Bilingual / 双语** — Native Chinese and English support / 原生中英文支持
- ⚡ **Style control / 风格控制** — Natural-language speaking style prompts / 自然语言风格提示
- 🔧 **Speed control / 语速控制** — Adjustable playback speed / 可调播放速度
- 📊 **Dashboard / 控制台** — Status, persistent voice controls, synthesis preview and WAV download / 状态检查、默认音色设置、合成试听与下载
- 📦 **Zero extra deps / 零额外依赖** — Provider uses Python stdlib; dashboard uses Hermes' bundled FastAPI / Provider 使用 Python 标准库，Dashboard 使用 Hermes 自带 FastAPI
- 🔑 **Shared credentials / 共享凭证** — Uses same `XIAOMI_API_KEY` as Hermes Xiaomi LLM provider / 与小米语言模型共用 `XIAOMI_API_KEY`
- 🌏 **Dual endpoints / 双端点** — Supports both Pay-as-you-go and Token Plan / 支持按量计费和 Token Plan

## Install / 安装

```bash
mkdir -p ~/.hermes/plugins
cp -R hermes-mimo-tts ~/.hermes/plugins/mimo-tts
export XIAOMI_API_KEY="your-xiaomi-api-key"
hermes plugins enable mimo-tts
```

## Configure / 配置

```yaml
tts:
  provider: mimo-tts
  model: mimo-v2.5-tts
  voice: mimo_default
  output_format: wav
  mimo-tts:
    max_text_length: 5000
```

## API Endpoints / API 端点

| Mode / 模式 | Base URL | API Key Format / 格式 |
|-------------|----------|----------------------|
| **Pay-as-you-go / 按量计费** | `https://api.xiaomimimo.com/v1` | `sk-xxxxx` |
| **Token Plan / 订阅制** | `https://token-plan-cn.xiaomimimo.com/v1` | `tp-xxxxx` |

A `tp-` API key automatically selects the Token Plan endpoint unless a base URL override is set.

## Environment Variables / 环境变量

| Variable / 变量 | Required / 必需 | Description / 说明 |
|-----------------|-----------------|---------------------|
| `XIAOMI_API_KEY` | ✅ | Xiaomi API key (`sk-` or `tp-`) / 小米 API 密钥 |
| `XIAOMI_BASE_URL` | — | API base URL shared with LLM / 与语言模型共用的 API 地址 |
| `XIAOMI_TTS_BASE_URL` | — | TTS-specific override / TTS 专用覆盖 |
| `XIAOMI_TTS_MODEL` | — | Override default model / 覆盖默认模型 |
| `XIAOMI_TTS_VOICE` | — | Persistent default voice / 持久化默认音色 |
| `XIAOMI_TTS_STYLE_PROMPT` | — | Global speaking style / 全局说话风格 |

## Dashboard / 控制台

The **MiMo TTS** dashboard tab provides connection status, voice selection, speed/style controls, preview playback, WAV download, and a **Set as default voice / 设为默认音色** action. Saving a default voice persists `XIAOMI_TTS_VOICE` through Hermes.

```bash
hermes dashboard
```

After changing only the UI bundle, rescan and refresh:

```bash
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

## Voices / 声音列表

The order below follows Xiaomi's TTS documentation / 下列顺序与小米 TTS 文档一致：

| Voice | Language / 语言 | Gender / 性别 |
|-------|-----------------|---------------|
| `mimo_default` | Cluster default: China uses 冰糖; other clusters use Mia / 集群默认：中国区使用冰糖，其他集群使用 Mia | — |
| `冰糖` | Chinese / 中文 | Female / 女 |
| `茉莉` | Chinese / 中文 | Female / 女 |
| `苏打` | Chinese / 中文 | Male / 男 |
| `白桦` | Chinese / 中文 | Male / 男 |
| `Mia` | English | Female / 女 |
| `Chloe` | English | Female / 女 |
| `Milo` | English | Male / 男 |
| `Dean` | English | Male / 男 |

## Style Prompt / 风格提示

```bash
export XIAOMI_TTS_STYLE_PROMPT="Warm, clear, conversational tone. Slightly upbeat."
```

## Models / 模型

- `mimo-v2.5-tts` (default / 默认)
- `mimo-v2-tts`

## Technical Notes / 技术说明

- Uses MiMo's chat-completions endpoint for speech synthesis / 使用 MiMo 的 chat-completions 端点进行语音合成
- Non-streaming synthesis / 非流式合成
- Outputs WAV format / 输出 WAV 格式
- Text is sent as `assistant`; style prompt is sent as `user` / 文本作为 `assistant`，风格提示作为 `user`

## License

MIT
