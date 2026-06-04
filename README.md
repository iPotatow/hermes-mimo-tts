# hermes-mimo-tts

Xiaomi MiMo TTS provider plugin for [Hermes Agent](https://github.com/nousresearch/hermes-agent).

## Features / 功能

- Chinese and English MiMo TTS voices / 中英文 MiMo TTS 音色
- Dashboard status, preview, playback, download, and persistent default-voice controls
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

## Dashboard / 控制台

The MiMo TTS tab displays the active plugin version, API key state, billing mode, region, endpoint source, effective default voice, voice source, model, and style state. Preview results show the actual voice, request duration, and audio size.

The UI always filters legacy `mimo_default` values, including values returned by an older running Dashboard backend.

```bash
hermes dashboard
```

After updating the plugin, restart Dashboard so its Python API is reloaded:

```bash
cd ~/.hermes/plugins/mimo-tts
git pull
hermes dashboard --stop
hermes dashboard --port 9119
```

## Voices / 音色

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

When no voice is configured, the plugin uses `冰糖` for China endpoints and `Mia` for other endpoints. Existing `mimo_default` settings are resolved for compatibility but are never displayed as a selectable voice.

## Environment Variables / 环境变量

| Variable | Description |
|----------|-------------|
| `XIAOMI_API_KEY` | Xiaomi API key (`sk-` or `tp-`) |
| `XIAOMI_BASE_URL` | API URL shared with Xiaomi LLM |
| `XIAOMI_TTS_BASE_URL` | TTS-specific API URL override |
| `XIAOMI_TTS_MODEL` | Default TTS model |
| `XIAOMI_TTS_VOICE` | Persistent default voice |
| `XIAOMI_TTS_STYLE_PROMPT` | Global speaking style |

## License

MIT
