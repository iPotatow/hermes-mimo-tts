"""Xiaomi MiMo TTS provider for Hermes Agent."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.tts_provider import TTSProvider


API_URL = "https://api.xiaomimimo.com/v1/chat/completions"
DEFAULT_MODEL = "mimo-v2.5-tts"
DEFAULT_VOICE = "mimo_default"
SUPPORTED_AUDIO_FORMATS = {"wav", "pcm16"}


class MiMoTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "mimo-tts"

    @property
    def display_name(self) -> str:
        return "Xiaomi MiMo TTS"

    @property
    def voice_compatible(self) -> bool:
        return True

    def is_available(self) -> bool:
        return bool(os.environ.get("MIMO_API_KEY"))

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": self.display_name,
            "badge": "paid",
            "tag": "Xiaomi MiMo-V2.5 speech synthesis",
            "env_vars": [
                {
                    "key": "MIMO_API_KEY",
                    "prompt": "Xiaomi MiMo API key",
                    "url": "https://platform.xiaomimimo.com/console",
                }
            ],
        }

    def list_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "mimo-v2.5-tts",
                "display": "MiMo-V2.5 TTS",
                "languages": ["zh", "en"],
                "max_text_length": 5000,
            },
            {
                "id": "mimo-v2-tts",
                "display": "MiMo-V2 TTS",
                "languages": ["zh", "en"],
                "max_text_length": 5000,
            },
        ]

    def list_voices(self) -> List[Dict[str, Any]]:
        return [
            {"id": "mimo_default", "display": "MiMo default"},
            {"id": "Mia", "display": "Mia", "language": "en", "gender": "female"},
            {"id": "Chloe", "display": "Chloe", "language": "en", "gender": "female"},
            {"id": "Milo", "display": "Milo", "language": "en", "gender": "male"},
            {"id": "Dean", "display": "Dean", "language": "en", "gender": "male"},
            {"id": "冰糖", "display": "冰糖", "language": "zh", "gender": "female"},
            {"id": "茉莉", "display": "茉莉", "language": "zh", "gender": "female"},
            {"id": "苏打", "display": "苏打", "language": "zh", "gender": "male"},
            {"id": "白桦", "display": "白桦", "language": "zh", "gender": "male"},
        ]

    def synthesize(
        self,
        text: str,
        output_path: str,
        *,
        voice: Optional[str] = None,
        model: Optional[str] = None,
        speed: Optional[float] = None,
        format: str = "mp3",
        **extra: Any,
    ) -> str:
        api_key = os.environ.get("MIMO_API_KEY")
        if not api_key:
            raise RuntimeError("MIMO_API_KEY is not set")

        requested_format = (format or "").lower()
        audio_format = requested_format if requested_format in SUPPORTED_AUDIO_FORMATS else "wav"
        final_output_path = self._output_path_for_format(output_path, audio_format)

        instruction = self._build_instruction(speed=speed)
        messages = []
        if instruction:
            messages.append({"role": "user", "content": instruction})
        messages.append({"role": "assistant", "content": text})

        payload = {
            "model": model or os.environ.get("MIMO_TTS_MODEL") or DEFAULT_MODEL,
            "messages": messages,
            "audio": {
                "format": audio_format,
                "voice": voice or os.environ.get("MIMO_TTS_VOICE") or DEFAULT_VOICE,
            },
        }

        response = self._post_json(api_key=api_key, payload=payload)
        audio_data = self._extract_audio_data(response)
        audio_bytes = base64.b64decode(audio_data)

        Path(final_output_path).write_bytes(audio_bytes)
        return final_output_path

    def _build_instruction(self, *, speed: Optional[float]) -> str:
        pieces = []
        style_prompt = os.environ.get("MIMO_TTS_STYLE_PROMPT", "").strip()
        if style_prompt:
            pieces.append(style_prompt)

        if speed and speed > 0 and abs(speed - 1.0) >= 0.05:
            pieces.append(f"Speak at about {speed:.2f}x normal speed.")

        return " ".join(pieces)

    def _post_json(self, *, api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            API_URL,
            data=data,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"MiMo TTS request failed: HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"MiMo TTS request failed: {exc.reason}") from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("MiMo TTS returned invalid JSON") from exc

    def _extract_audio_data(self, response: Dict[str, Any]) -> str:
        try:
            message = response["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"MiMo TTS response did not contain a message: {response}") from exc

        audio = message.get("audio")
        if not isinstance(audio, dict) or not audio.get("data"):
            raise RuntimeError(f"MiMo TTS response did not contain audio data: {response}")

        return audio["data"]

    def _output_path_for_format(self, output_path: str, audio_format: str) -> str:
        path = Path(output_path)
        suffix = f".{audio_format}"
        if path.suffix.lower() == suffix:
            return str(path)
        return str(path.with_suffix(suffix))


def register(ctx):
    ctx.register_tts_provider(MiMoTTSProvider())
