# hermes-mimo-tts

> Xiaomi MiMo TTS provider plugin for [Hermes Agent](https://github.com/nousresearch/hermes-agent)
>
> 小米 MiMo 语音合成插件，为 [Hermes Agent](https://github.com/nousresearch/hermes-agent) 提供中文和英文语音能力

## Features / 功能

- 🎙️ **9 voices / 9种声音** — English (Mia, Chloe, Milo, Dean) + 中文 (冰糖, 茉莉, 苏打, 白桦)
- 🌐 **Bilingual / 双语** — Native Chinese and English support / 原生中英文支持
- ⚡ **Style control / 风格控制** — Natural-language speaking style prompts / 自然语言风格提示
- 🔧 **Speed control / 语速控制** — Adjustable playback speed / 可调播放速度
- 📦 **Zero deps / 零依赖** — Pure Python stdlib / 纯 Python 标准库
- 🔑 **Shared credentials / 共享凭证** — Uses same `XIAOMI_API_KEY` as Hermes Xiaomi LLM provider / 与小米语言模型共用 `XIAOMI_API_KEY`

## Install / 安装

```bash
# Copy plugin to Hermes / 复制插件到 Hermes
mkdir -p ~/.hermes/plugins
cp -R hermes-mimo-tts ~/.hermes/plugins/mimo-tts

# Set API key (same as Xiaomi LLM) / 设置 API 密钥（与小米语言模型相同）
export XIAOMI_API_KEY="your-xiaomi-api-key"

# Enable plugin / 启用插件
hermes plugins enable mimo-tts
```

## Configure / 配置

Add to `~/.hermes/config.yaml` / 添加到 `~/.hermes/config.yaml`:

```yaml
tts:
  provider: mimo-tts
  mimo-tts:
    model: mimo-v2.5-tts
    voice: mimo_default
    max_text_length: 5000
```

Restart Hermes to apply / 重启 Hermes 生效

## Voices / 声音列表

| Voice | Language / 语言 | Gender / 性别 |
|-------|-----------------|---------------|
| `mimo_default` | Auto / 自动 | — |
| `Mia` | English | Female / 女 |
| `Chloe` | English | Female / 女 |
| `Milo` | English | Male / 男 |
| `Dean` | English | Male / 男 |
| `冰糖` | Chinese / 中文 | Female / 女 |
| `茉莉` | Chinese / 中文 | Female / 女 |
| `苏打` | Chinese / 中文 | Male / 男 |
| `白桦` | Chinese / 中文 | Male / 男 |

Override via config or environment / 通过配置或环境变量覆盖:

```bash
export XIAOMI_TTS_VOICE="Chloe"
```

## Style Prompt / 风格提示

MiMo accepts natural-language style control / MiMo 支持自然语言风格控制:

```bash
export XIAOMI_TTS_STYLE_PROMPT="Warm, clear, conversational tone. Slightly upbeat."
```

## Environment Variables / 环境变量

| Variable / 变量 | Required / 必需 | Description / 说明 |
|-----------------|-----------------|---------------------|
| `XIAOMI_API_KEY` | ✅ | Xiaomi API key (shared with LLM) / 小米 API 密钥（与语言模型共用） |
| `XIAOMI_TTS_MODEL` | — | Override default model / 覆盖默认模型 |
| `XIAOMI_TTS_VOICE` | — | Override default voice / 覆盖默认声音 |
| `XIAOMI_TTS_STYLE_PROMPT` | — | Global speaking style / 全局说话风格 |

> 💡 `XIAOMI_API_KEY` is the same credential used by Hermes' Xiaomi LLM provider. If you already have Xiaomi configured as your model provider, TTS works out of the box.
>
> 💡 `XIAOMI_API_KEY` 与 Hermes 小米语言模型使用相同密钥。如果已配置小米为模型提供商，TTS 开箱即用。

## Models / 模型

- `mimo-v2.5-tts` (default / 默认) — Latest, best quality / 最新，最佳质量
- `mimo-v2-tts` — Previous generation / 上一代

## API

Get your API key / 获取 API 密钥: [platform.xiaomimimo.com](https://platform.xiaomimimo.com/console)

## Technical Notes / 技术说明

- Uses MiMo's chat-completions endpoint for speech synthesis / 使用 MiMo 的 chat-completions 端点进行语音合成
- Non-streaming synthesis (MiMo V2.5 doesn't support low-latency streaming yet) / 非流式合成（MiMo V2.5 暂不支持低延迟流式）
- Outputs WAV format; Hermes handles conversion if needed / 输出 WAV 格式，Hermes 会处理转换
- Text is sent as `assistant` message, style prompt as `user` message (MiMo's role convention) / 文本作为 `assistant` 消息发送，风格提示作为 `user` 消息（MiMo 的角色约定）

## License

MIT
