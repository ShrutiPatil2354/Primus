import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

MEMORY_BANK = os.path.join(DATA_DIR, "memory_bank.json")
SNAPSHOT_FILE = os.path.join(DATA_DIR, "snapshot.jpg")
AUDIO_OUT = os.path.join(DATA_DIR, "primus_voice.wav")
AUDIO_OUT_MP3 = os.path.join(DATA_DIR, "primus_voice.mp3")
VOICE_MODEL = os.path.join(DATA_DIR, "en_US-lessac-medium.onnx")

OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
MODEL_NAME = "qwen2.5:7b-instruct"
CONTEXT_LENGTH = 4096

START_TIME = time.time()