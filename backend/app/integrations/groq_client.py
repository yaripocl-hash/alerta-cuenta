from groq import Groq

from app.config import get_settings

_MIME_TO_EXT = {
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/mp4": "mp4",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
}


def transcribe_audio(audio_bytes: bytes, mime_type: str) -> str:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY no configurada")
    ext = _MIME_TO_EXT.get(mime_type, "webm")
    client = Groq(api_key=settings.groq_api_key)
    transcription = client.audio.transcriptions.create(
        file=(f"audio.{ext}", audio_bytes),
        model="whisper-large-v3",
        language="es",
        response_format="text",
    )
    return (transcription or "").strip()
