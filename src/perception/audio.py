import os
import wave

from src.config import AUDIO_OUT, AUDIO_OUT_MP3, VOICE_MODEL

_whisper = None
_voice = None


def transcribe(path):
    global _whisper
    if not path:
        return ""
    from src.core import executor
    try:
        if _whisper is None:
            from faster_whisper import WhisperModel
            try:
                _whisper = WhisperModel("small", device="cuda", compute_type="int8")
            except Exception:
                _whisper = WhisperModel("base", device="cpu", compute_type="int8")
        segs, _ = _whisper.transcribe(path, language="en", beam_size=1, vad_filter=True)
        return " ".join(s.text.strip() for s in segs).strip()
    except Exception as e:
        executor.log("Speech", f"STT error: {e}", "Error", None)
        return ""


def speak(text):
    global _voice
    if not text:
        return None
    from src.core import executor

    # Offline neural voice (Piper)
    if os.path.exists(VOICE_MODEL):
        try:
            if _voice is None:
                from piper import PiperVoice
                _voice = PiperVoice.load(VOICE_MODEL)
            with wave.open(AUDIO_OUT, "wb") as f:
                _voice.synthesize(text[:400], f)
            from src.core.artifacts import ARTIFACTS
            ARTIFACTS.put_file(AUDIO_OUT, content_type="audio/wav")
            executor.log("Speech", "Voice reply generated (Piper)", "Success", 1.0)
            return AUDIO_OUT
        except Exception as e:
            executor.log("Speech", f"Piper error: {e}", "Error", None)

    # Online fallback (edge-tts)
    try:
        import asyncio
        import edge_tts

        async def _run():
            comm = edge_tts.Communicate(text[:400], "en-US-AriaNeural")
            await comm.save(AUDIO_OUT_MP3)

        asyncio.run(_run())
        from src.core.artifacts import ARTIFACTS
        ARTIFACTS.put_file(AUDIO_OUT_MP3, content_type="audio/mpeg")
        executor.log("Speech", "Voice reply generated (edge-tts)", "Success", 1.0)
        return AUDIO_OUT_MP3
    except Exception as e:
        executor.log("Speech", f"TTS unavailable: {e}", "Error", None)
        return None