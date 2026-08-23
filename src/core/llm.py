import time
import requests

from src.config import OLLAMA_CHAT_URL, OLLAMA_TAGS_URL, MODEL_NAME, CONTEXT_LENGTH

LAST = {"latency_ms": 0, "inference_ms": 0, "tokens_per_sec": 0.0}


def online():
    try:
        return requests.get(OLLAMA_TAGS_URL, timeout=1).status_code == 200
    except Exception:
        return False


def chat(messages, temperature=0.3):
    t0 = time.time()
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": CONTEXT_LENGTH},
    }
    try:
        r = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=180)
        dt = max(0.05, time.time() - t0)
        text = r.json().get("message", {}).get("content", "").strip()
        tokens = max(1, len(text) // 4)
        LAST["latency_ms"] = int(dt * 1000)
        LAST["inference_ms"] = int(dt * 1000)
        LAST["tokens_per_sec"] = round(tokens / dt, 1)
        return text
    except Exception as e:
        LAST["latency_ms"] = int((time.time() - t0) * 1000)
        return f"[LLM offline] {e}"
