# hermes-mimo-tts

> Xiaomi MiMo TTS provider plugin for [Hermes Agent](https://github.com/nousresearch/hermes-agent)

Bring Xiaomi's MiMo V2.5 speech synthesis to Hermes. Supports Chinese and English with 9 built-in voices.

## Features

- 🎙️ **9 voices** — English (Mia, Chloe, Milo, Dean) + Chinese (冰糖, 茉莉, 苏打, 白桦)
- 🌐 **Bilingual** — Native Chinese and English support
- ⚡ **Style control** — Natural-language speaking style prompts
- 🔧 **Speed control** — Adjustable playback speed
- 📦 **Zero deps** — Pure Python, uses stdlib only

## Install

```bash
# Copy plugin to Hermes
mkdir -p ~/.hermes/plugins
cp -R hermes-mimo-tts ~/.hermes/plugins/mimo-tts

# Set API key
export MIMO_API_KEY="your-xiaomi-mimo-api-key"

# Enable plugin
hermes plugins enable mimo-tts
```

## Configure

Add to `~/.hermes/config.yaml`:

```yaml
tts:
  provider: mimo-tts
  mimo-tts:
    model: mimo-v2.5-tts
    voice: mimo_default
    max_text_length: 5000
```

Restart Hermes to apply.

## Voices

| Voice | Language | Gender |
|-------|----------|--------|
| `mimo_default` | Auto | — |
| `Mia` | English | Female |
| `Chloe` | English | Female |
| `Milo` | English | Male |
| `Dean` | English | Male |
| `冰糖` | Chinese | Female |
| `茉莉` | Chinese | Female |
| `苏打` | Chinese | Male |
| `白桦` | Chinese | Male |

Override via config or environment:

```bash
export MIMO_TTS_VOICE="Chloe"
```

## Style Prompt

MiMo accepts natural-language style control. Set a global speaking style:

```bash
export MIMO_TTS_STYLE_PROMPT="Warm, clear, conversational tone. Slightly upbeat."
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MIMO_API_KEY` | ✅ | Xiaomi MiMo API key |
| `MIMO_TTS_MODEL` | — | Override default model |
| `MIMO_TTS_VOICE` | — | Override default voice |
| `MIMO_TTS_STYLE_PROMPT` | — | Global speaking style |

## Models

- `mimo-v2.5-tts` (default) — Latest, best quality
- `mimo-v2-tts` — Previous generation

## API

Get your API key at [platform.xiaomimimo.com](https://platform.xiaomimimo.com/console).

## Technical Notes

- Uses MiMo's chat-completions endpoint for speech synthesis
- Non-streaming synthesis (MiMo V2.5 doesn't support low-latency streaming yet)
- Outputs WAV format; Hermes handles conversion if needed
- Text is sent as `assistant` message, style prompt as `user` message (MiMo's role convention)

## License

MIT
