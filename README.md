# hermes-mimo-tts

Xiaomi MiMo TTS provider plugin for [Hermes Agent](https://github.com/nousresearch/hermes-agent).

## Features / 功能

- Chinese and English MiMo TTS voices / 中英文 MiMo TTS 音色
- Hermes Dashboard preview, playback, download, and persistent default-voice controls
- Pay-as-you-go and Token Plan endpoint support
- Uses the same `XIAOMI_API_KEY` as Hermes' Xiaomi LLM provider

## Install / 安装

```bash
mkdir -p ~/.hermes/plugins
git clone https://github.com/iPotatow/hermes-mimo-tts.git ~/.hermes/plugins/mimo-tts
hermes plugins enable mimo-tts
```

## Configure / 配置

```yaml
tts:
  provider: mimo-tts
  model: mimo-v2.5-tts
  voice: 冰糖
  output_format: wav
  mimo-tts:
    max_text_length: 5000
```

## Environment Variables / 环境变量

| Variable | Description |
|----------|-------------|
| `XIAOMI_API_KEY` | Xiaomi API key (`sk-` or `tp-`) |
| `XIAOMI_BASE_URL` | API URL shared with Xiaomi LLM |
| `XIAOMI_TTS_BASE_URL` | TTS-specific API URL override |
| `XIAOMI_TTS_MODEL` | Default TTS model |
| `XIAOMI_TTS_VOICE` | Persistent default voice |
| `XIAOMI_TTS_STYLE_PROMPT` | Global speaking style |

## Dashboard / 控制台

The **MiMo TTS** tab supports voice selection, preview playback, WAV download, and saving the selected voice as the Hermes default.

```bash
hermes dashboard
```

## Voices / 音色

The selectable voices follow Xiaomi's order. `mimo_default` is intentionally not exposed.

| Voice | Language | Gender |
|-------|----------|--------|
| `冰糖` | Chinese | Female |
| `茉莉` | Chinese | Female |
| `苏打` | Chinese | Male |
| `白桦` | Chinese | Male |
| `Mia` | English | Female |
| `Chloe` | English | Female |
| `Milo` | English | Male |
| `Dean` | English | Male |

When no voice is configured, the plugin uses the concrete regional default: `冰糖` for China endpoints and `Mia` for other endpoints. Existing `mimo_default` settings are resolved the same way for compatibility, but are never shown as a selectable voice.

## Endpoints / 端点

| Mode | Base URL | Key |
|------|----------|-----|
| Pay-as-you-go | `https://api.xiaomimimo.com/v1` | `sk-...` |
| Token Plan China | `https://token-plan-cn.xiaomimimo.com/v1` | `tp-...` |

## License

MIT
