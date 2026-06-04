"""Dashboard API routes for the Xiaomi MiMo TTS plugin."""
from __future__ import annotations
import base64, binascii, json, os, urllib.error, urllib.request
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Response

router = APIRouter()
PLUGIN_VERSION = "0.4.0"
DEFAULT_BASE_URL = "https://api.xiaomimimo.com/v1"
TOKEN_PLAN_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-tts"
MODELS = ["mimo-v2.5-tts", "mimo-v2-tts"]
VOICES = ["冰糖", "茉莉", "苏打", "白桦", "Mia", "Chloe", "Milo", "Dean"]

def _base_url(api_key: str) -> str:
    configured = os.environ.get("XIAOMI_TTS_BASE_URL") or os.environ.get("XIAOMI_BASE_URL")
    if configured: return configured.rstrip("/")
    return TOKEN_PLAN_BASE_URL if api_key.startswith("tp-") else DEFAULT_BASE_URL

def _redacted_key(api_key: str) -> str:
    if not api_key: return ""
    return f"{api_key[:2]}...{api_key[-2:]}" if len(api_key) <= 8 else f"{api_key[:4]}...{api_key[-4:]}"

def _default_voice(api_key: str) -> str: return "冰糖" if "-cn." in _base_url(api_key) else "Mia"
def _configured_voice(api_key: str) -> str:
    voice = os.environ.get("XIAOMI_TTS_VOICE")
    return _default_voice(api_key) if not voice or voice == "mimo_default" else voice

def _status_details(api_key: str) -> Dict[str, str]:
    base_url = _base_url(api_key)
    saved_voice = os.environ.get("XIAOMI_TTS_VOICE", "")
    region = "中国" if "-cn." in base_url else "新加坡" if "-sgp." in base_url else "阿姆斯特丹" if "-ams." in base_url else "全球"
    voice_source = "已保存设置" if saved_voice in VOICES else "旧配置已转换" if saved_voice == "mimo_default" else "区域默认"
    return {"billing_mode": "Token Plan" if "token-plan" in base_url else "按量计费", "region": region, "endpoint_source": "手动配置" if os.environ.get("XIAOMI_TTS_BASE_URL") or os.environ.get("XIAOMI_BASE_URL") else "自动识别", "voice_source": voice_source, "saved_voice": saved_voice if saved_voice in VOICES else ""}

@router.get("/status")
async def status() -> Dict[str, Any]:
    api_key = os.environ.get("XIAOMI_API_KEY", "")
    return {"plugin_version": PLUGIN_VERSION, "configured": bool(api_key), "key_preview": _redacted_key(api_key), "base_url": _base_url(api_key), "model": os.environ.get("XIAOMI_TTS_MODEL") or DEFAULT_MODEL, "voice": _configured_voice(api_key), "style_prompt": os.environ.get("XIAOMI_TTS_STYLE_PROMPT", ""), "style_configured": bool(os.environ.get("XIAOMI_TTS_STYLE_PROMPT", "").strip()), "output_format": "wav", "models": MODELS, "voices": VOICES, **_status_details(api_key)}

@router.post("/synthesize")
async def synthesize(body: Dict[str, Any]) -> Response:
    api_key = os.environ.get("XIAOMI_API_KEY", "")
    if not api_key: raise HTTPException(status_code=400, detail="XIAOMI_API_KEY is not set")
    text = str(body.get("text", "")).strip()
    if not text: raise HTTPException(status_code=400, detail="Text is required")
    if len(text) > 5000: raise HTTPException(status_code=400, detail="Text must be 5000 characters or fewer")
    model = str(body.get("model") or os.environ.get("XIAOMI_TTS_MODEL") or DEFAULT_MODEL)
    voice = str(body.get("voice") or _configured_voice(api_key))
    style, speed = str(body.get("style") or "").strip(), body.get("speed", 1)
    if model not in MODELS: raise HTTPException(status_code=400, detail="Unsupported model")
    if voice not in VOICES: raise HTTPException(status_code=400, detail="Unsupported voice")
    try: speed_value = float(speed)
    except (TypeError, ValueError): raise HTTPException(status_code=400, detail="Speed must be a number")
    if not 0.5 <= speed_value <= 2: raise HTTPException(status_code=400, detail="Speed must be between 0.5 and 2.0")
    instructions = ([style[:1000]] if style else []) + ([f"Speak at about {speed_value:.2f}x normal speed."] if abs(speed_value - 1) >= 0.05 else [])
    messages = ([{"role": "user", "content": " ".join(instructions)}] if instructions else []) + [{"role": "assistant", "content": text}]
    request = urllib.request.Request(f"{_base_url(api_key)}/chat/completions", data=json.dumps({"model": model, "messages": messages, "audio": {"format": "wav", "voice": voice}}, ensure_ascii=False).encode("utf-8"), headers={"api-key": api_key, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=120) as upstream: result = json.loads(upstream.read().decode("utf-8"))
        audio_bytes = base64.b64decode(result["choices"][0]["message"]["audio"]["data"], validate=True)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace"); raise HTTPException(status_code=502, detail=f"MiMo returned HTTP {exc.code}: {detail[:600]}")
    except urllib.error.URLError as exc: raise HTTPException(status_code=502, detail=f"Could not reach MiMo: {exc.reason}")
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError, binascii.Error): raise HTTPException(status_code=502, detail="MiMo returned an invalid audio response")
    return Response(content=audio_bytes, media_type="audio/wav", headers={"Content-Disposition": 'inline; filename="mimo-preview.wav"'})
