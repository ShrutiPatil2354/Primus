import os
import time
import wave
import threading

from src.config import AUDIO_OUT_DIR, VOICE_MODEL

_whisper = None
_voice = None
_KEEP_FILES = 10  # keep the newest N generated voice files


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


def _prune_old_voice_files():
    """Keep only the newest _KEEP_FILES generated voice files."""
    try:
        files = [
            os.path.join(AUDIO_OUT_DIR, name)
            for name in os.listdir(AUDIO_OUT_DIR)
            if name.startswith("voice_reply_")
        ]
        files.sort(key=os.path.getmtime, reverse=True)
        for stale in files[_KEEP_FILES:]:
            try:
                os.remove(stale)
            except OSError:
                pass
    except Exception:
        pass


def _edge_tts_save(text, out_path):
    """Run edge-tts in its own thread + event loop (safe inside Gradio handlers)."""
    import asyncio

    result = {"path": None, "error": None}

    def _worker():
        try:
            import edge_tts

            async def _run():
                comm = edge_tts.Communicate(text, "en-US-AriaNeural")
                await comm.save(out_path)

            asyncio.run(_run())
            result["path"] = out_path
        except Exception as e:  # pragma: no cover
            result["error"] = e

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout=30)
    if thread.is_alive():
        result["error"] = TimeoutError("edge-tts timed out after 30s")
    return result["path"], result["error"]


def speak(text):
    """Generate a voice reply and return its file path.

    Every reply is written to a UNIQUE file (data/voice_replies/voice_reply_<ms>)
    so Gradio serves a fresh URL and the audio player updates + autoplays on
    every agent answer instead of being cached with the previous reply.
    """
    global _voice
    if not text:
        return None
    from src.core import executor

    stamp = int(time.time() * 1000)
    out_wav = os.path.join(AUDIO_OUT_DIR, f"voice_reply_{stamp}.wav")
    out_mp3 = os.path.join(AUDIO_OUT_DIR, f"voice_reply_{stamp}.mp3")

    # Offline neural voice (Piper)
    if os.path.exists(VOICE_MODEL):
        try:
            if _voice is None:
                from piper import PiperVoice
                _voice = PiperVoice.load(VOICE_MODEL)
            with wave.open(out_wav, "wb") as f:
                _voice.synthesize(text[:400], f)
            if os.path.exists(out_wav) and os.path.getsize(out_wav) > 0:
                executor.log("Speech", "Voice reply generated (Piper)", "Success", 1.0)
                _prune_old_voice_files()
                return out_wav
        except Exception as e:
            executor.log("Speech", f"Piper error: {e}", "Error", None)

    # Online fallback (edge-tts)
    try:
        path, error = _edge_tts_save(text[:400], out_mp3)
        if path and os.path.exists(path) and os.path.getsize(path) > 0:
            executor.log("Speech", "Voice reply generated (edge-tts)", "Success", 1.0)
            _prune_old_voice_files()
            return path
        raise error or RuntimeError("edge-tts produced no audio")
    except Exception as e:
        executor.log("Speech", f"TTS unavailable: {e}", "Error", None)
        return None