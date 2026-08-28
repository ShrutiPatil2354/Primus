# PRIMUS — Architecture

> Maintained alongside the code; update this file when layers change.

PRIMUS is a local-first AI agent studio: a Gradio web app that combines an
LLM brain (Ollama), persistent memory, task execution, reinforcement
learning, and real-time perception (camera + speech) into one dashboard.

## Tech stack

| Concern | Technology |
|---|---|
| UI / server | Gradio 6.x (`gr.Blocks`, `fill_width`), pure-Python |
| LLM | Ollama (`qwen2.5:7b-instruct` by default, configurable) |
| Speech out | Piper TTS (offline, `data/en_US-lessac-medium.onnx`) → edge-tts (online fallback) |
| Speech in | faster-whisper (`small` on CUDA, `base` on CPU fallback) |
| Vision | OpenCV + ultralytics YOLOv8 + MediaPipe |
| Neural core | C++ compiled via pybind11 (`cpp_core/` → `.pyd`) |
| Persistence | JSON / SQLite locally (`data/`), optional Postgres + pgvector |
| Metrics | psutil + GPU telemetry via `monitor.py`, 1.5s UI refresh tick |

## Repository layout (layers)

```
Primus/
├── app.py                    ← ENTRY POINT: builds the Gradio UI, wires all events, launches
├── src/
│   ├── config.py             ← central config: paths, Ollama URLs, ports, .env loader
│   ├── ui/                   ← PRESENTATION LAYER
│   │   ├── handlers.py       ← all event logic (chat pipeline, agents, docs, learning)
│   │   └── theme.py          ← CSS f-string + design tokens (single source of styling)
│   ├── core/                 ← BRAIN / DOMAIN LAYER
│   │   ├── engine.py         ← agent engine orchestrator
│   │   ├── intent.py         ← intent routing (Ask / Learn / skills)
│   │   ├── llm.py            ← Ollama client + latency tracking
│   │   ├── innate.py         ← untrained fallback replies when LLM is offline
│   │   ├── memory.py         ← facts / episodes / sensory / working memory
│   │   ├── storage.py        ← local persistence (memory bank JSON, SQLite)
│   │   ├── postgres_store.py ← optional Postgres + pgvector store
│   │   ├── executor.py       ← task plans, action log, scores
│   │   └── evaluation.py     ← skill evaluation
│   ├── perception/           ← SENSING
│   │   ├── audio.py          ← STT (faster-whisper) + TTS (Piper → edge-tts)
│   │   └── vision.py         ← camera loop, YOLOv8 labels, snapshots
│   ├── training/             ← LEARNING
│   │   ├── curriculum.py     ← teach / Learn Mode flows
│   │   └── meta_rl.py        ← meta-reinforcement learning experiments
│   └── metrics/monitor.py    ← CPU/RAM/GPU telemetry → HTML sparklines
├── cpp_core/                 ← C++ neural core (pybind11; compiled artifact gitignored)
├── data/                     ← runtime artifacts (gitignored): memory, voice replies, models
├── tests/test_primus.py      ← tests
└── docker-compose.yml        ← optional Postgres/pgvector services
```

**Dependency rule:** layers point one way only —
`app.py → ui/handlers → core + perception + metrics`. Nothing in `core/`,
`perception/`, or `metrics/` imports from `ui/`; heavy libs (whisper, piper,
torch) are imported lazily inside functions so startup stays fast.

## Runtime data flow — answering a message

```
User input (text / microphone / document upload)
        │
        ▼
handlers.process_input()                [src/ui/handlers.py]
  1. audio_path? → audio.transcribe()   (faster-whisper)
  2. camera context? → VISION.summary() (YOLOv8 labels)
  3. doc upload? → ingest into agent knowledge
  4. intent/kind → memory recall (+ per-agent private docs)
        │
        ▼
llm.chat(msgs)  ──offline──▶  innate.reply(text)     [src/core/]
        │
        ▼
  memory.set_working / add_episode      │  audio.speak(reply)
  executor.log / plan_html              │        [src/perception/audio.py]
        │                               │
        ▼                               ▼
17-value output tuple ──▶ Gradio UI components (chatbot, voice players,
action log, dashboards, sidebar)  +  gr.Timer(1.5s) refresh loop
```

Every chat event (send button, Enter, doc upload, mic stop-recording) binds
the same `process_input` with the same 9 inputs and 17 outputs, so all
surfaces stay consistent.

## Voice reply pipeline (audio output)

Implemented in `src/perception/audio.py`, wired in `app.py` + `handlers.py`:

1. `Enable Voice Reply` checkbox in the composer (**default ON**) is passed
   to `process_input(..., use_audio_output)`.
2. `audio.speak(reply)` generates a **unique file per reply**:
   `data/voice_replies/voice_reply_<epoch_ms>.wav` (Piper) or `.mp3`
   (edge-tts fallback). Unique names guarantee Gradio/browser treat every
   reply as new content — the audio player refreshes and autoplays each
   time instead of replaying a cached URL.
3. Robustness rules:
   - Piper output must be **non-empty** (0-byte wav → fall through to
     edge-tts instead of serving silent audio);
   - edge-tts runs in its **own thread + event loop** with a 30s timeout,
     so it is safe inside Gradio handlers;
   - old voice files are pruned automatically, newest 10 kept;
   - TTS is wrapped in try/except with executor logging — a voice failure
     never blocks the text reply.
4. The voice path fills two slots of the 17-value output tuple, feeding
   both the compact composer player (`autoplay=True`) and the
   Perception-tab "Latest voice reply" player.

## Configuration

All via `src/config.py`; env overrides are read from `.env` at repo root.

| Variable | Default | Purpose |
|---|---|---|
| `PRIMUS_MODEL_NAME` | `qwen2.5:7b-instruct` | Ollama chat model |
| `PRIMUS_CONTEXT_LENGTH` | `4096` | LLM context window |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama endpoint |
| `PORT` / `GRADIO_SERVER_PORT` | `7860` | Web UI port (auto-increments if busy) |
| `PRIMUS_STREAM_PORT` | `8000` | Camera MJPEG stream port |

Key runtime paths (all under `data/`, gitignored): `memory_bank.json`,
`primus_memory.db`, `tasks.jsonl`, `voice_replies/`,
`en_US-lessac-medium.onnx` (Piper voice model, downloaded by
`setup.ps1` / `setup.sh`).

## Running

```powershell
./setup.ps1     # first-time: venv + deps + voice model (run.sh on Linux/macOS)
./run.ps1       # start the web app
```

A local Ollama instance is required for the full brain; without it PRIMUS
falls back to the innate untrained core — text replies still work and
learning/teaching still records.

