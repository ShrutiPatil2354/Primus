import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Simple .env file loader
_env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(_env_file):
    try:
        with open(_env_file, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip().strip("'\""))
    except Exception:
        pass

MEMORY_BANK = os.path.join(DATA_DIR, "memory_bank.json")
SNAPSHOT_FILE = os.path.join(DATA_DIR, "snapshot.jpg")
AUDIO_OUT = os.path.join(DATA_DIR, "primus_voice.wav")
AUDIO_OUT_MP3 = os.path.join(DATA_DIR, "primus_voice.mp3")
VOICE_MODEL = os.path.join(DATA_DIR, "en_US-lessac-medium.onnx")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", f"{OLLAMA_BASE_URL}/api/chat")
OLLAMA_TAGS_URL = os.getenv("OLLAMA_TAGS_URL", f"{OLLAMA_BASE_URL}/api/tags")
MODEL_NAME = os.getenv("PRIMUS_MODEL_NAME", "qwen2.5:7b-instruct")
CONTEXT_LENGTH = int(os.getenv("PRIMUS_CONTEXT_LENGTH", "4096"))
SERVER_PORT = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860")))
STREAM_PORT = int(os.getenv("PRIMUS_STREAM_PORT", "8000"))

START_TIME = time.time()