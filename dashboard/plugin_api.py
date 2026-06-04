"""Dashboard API routes for the Xiaomi MiMo TTS plugin."""

from __future__ import annotations

import base64
import binascii
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Response

router = APIRouter()
DEFAULT_BASE_URL = "https://api.xiaomimimo.com/v1"
TOKEN_PLAN_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-tts"
MODELS = ["mimo-v2.5-tts", "mimo-v2-tts"]
VOICES = ["冰糖", "茉莉", "苏打", "白桦", "Mia", "Chloe", "Milo", "Dean"]


def _base_url(api_key: str) -> str:
    configured = os.environ.get("XIAOMI_TTS_BASE_URL") or os.environ.get("XIAOMI_BASE_URL")
    if configured:
        return configured.rstrip("/")
    if api_key.startswith("tp-"):
        return TOKEN_PLAN_BASE_URL
    return DEFAULT_BASE_URL


def _redacted_key(api_key: str) -> str:
    if not api_key:
        return ""
    if len(api_key) <= 8:
        return f"{api_key[:2]}...{api_key[-2:]}"
    return f"{api_key[:4]}...{api_key[-4:]}"


def _default_voice(api_key: str) -> str:
    return "冰糖" if "-cn." in _base_url(api_key) else "Mia"


def _configured_voice(api_key: str) -> str:
    voice = os.environ.get("XIAOMI_TTS_VOICE")
    if not voice or voice == "mimo_default":
        return _default_voice(api_key)
    return voice


@router.get("/status")
async def status() -> Dict[str, Any]:
    api_key = os.environ.get("XIAOMI_API_KEY", "")
    return {
        "configured": bool(api_key), "key_preview": _redacted_key(api_key),
        "base_url": _base_url(api_key), "model": os.environ.get("XIAOMI_TTS_MODEL") or DEFAULT_MODEL,
        "voice": _configured_voice(api_key), "style_prompt": os.environ.get("XIAOMI_TTS_STYLE_PROMPT", ""),
        "models": MODELS, "voices": VOICES,
    }


@router.post("/synthesize")
async def synthesize(body: Dict[str, Any]) -> Response:
    api_key = os.environ.get("XIAOMI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=400, detail="XIAOMI_API_KEY is not set")
    text = str(body.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text must be 5000 characters or fewer")
    model = str(body.get("model") or os.environ.get("XIAOMI_TTS_MODEL") or DEFAULT_MODEL)
    voice = str(body.get("voice") or _configured_voice(api_key))
    style = str(body.get("style") or "").strip()
    speed = body.get("speed", 1)
    if model not in MODELS:
        raise HTTPException(status_code=400, detail="Unsupported model")
    if voice not in VOICES:
        raise HTTPException(status_code=400, detail="Unsupported voice")
    instructions = []
    if style:
        instructions.append(style[:1000])
    try:
        speed_value = float(speed)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Speed must be a number")
    if not 0.5 <= speed_value <= 2:
        raise HTTPException(status_code=400, detail="Speed must be between 0.5 and 2.0")
    if abs(speed_value - 1) >= 0.05:
        instructions.append(f"Speak at about {speed_value:.2f}x normal speed.")
    messages = []
    if instructions:
        messages.append({"role": "user", "content": " ".join(instructions)})
    messages.append({"role": "assistant", "content": text})
    payload = {"model": model, "messages": messages, "audio": {"format": "wav", "voice": voice}}
    request = urllib.request.Request(
        f"{_base_url(api_key)}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"api-key": api_key, "Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as upstream:
            result = json.loads(upstream.read().decode("utf-8"))
        audio_data = result["choices"][0]["message"]["audio"]["data"]
        audio_bytes = base64.b64decode(audio_data, validate=True)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HTTPException(status_code=502, detail=f"MiMo returned HTTP {exc.code}: {detail[:600]}")
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach MiMo: {exc.reason}")
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError, binascii.Error):
        raise HTTPException(status_code=502, detail="MiMo returned an invalid audio response")
    return Response(content=audio_bytes, media_type="audio/wav", headers={"Content-Disposition": 'inline; filename="mimo-preview.wav"'})
