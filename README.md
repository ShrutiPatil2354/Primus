# PRIMUS — Zero-Knowledge Real-Time Cognitive Agent

**PRIMUS** is a brain-inspired, **tabula rasa (zero-prior-knowledge)** AI agent that starts knowing *nothing* and learns everything from its teacher — through **text, speech, and live vision** — in real time.

> "I have no prior knowledge about that. I only know what you teach me."

![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-black) ![CUDA](https://img.shields.io/badge/CUDA-RTX_4060-black) ![Python](https://img.shields.io/badge/Python-3.12-black) ![C++](https://img.shields.io/badge/C++-17-black) ![Gradio](https://img.shields.io/badge/UI-Gradio_6-black)

---

## Features

- **Zero-Prior Enforcement (Knowledge Gate)** — task/fact questions are answered *only* from learned memory; unknown tasks are refused.
- **Unified multimodal interaction** — text, speech (Whisper), and live camera (YOLO + MediaPipe) always active.
- **Human-like memory cortex** — Procedural, Episodic, Semantic, Sensory, and Working memory.
- **Live task execution** — animated Task Plan with step-by-step status + action log with scores.
- **Reinforcement learning** — feedback-driven synaptic confidence updates (C++ core).
- **Neural voice** — offline Piper TTS speaks every reply.
- **Real-time glass dashboard** — CPU/RAM/VRAM/GPU temp/FPS/latency sparklines at 1.5s refresh.
- **Hybrid Python + C++ engine** — pybind11-compiled neural core.

## Architecture

```text
Text / Speech / Live Camera
            │
            ▼
     Intent Router (teach / perform / recall / converse)
            │
   ┌────────┼────────────────────────┐
   ▼        ▼                        ▼
Knowledge  Procedural           LLM (strict
Gate       Memory + Executor    tabula-rasa prompt)
   │        │                        │
   ▼        ▼                        ▼
        Memory Cortex (Procedural / Episodic /
        Semantic / Sensory / Working)
            │
            ▼
   Glass Dashboard + Voice Reply
```

## Memory Types (like the human brain)

| Memory | What it stores |
|---|---|
| Procedural | Skills you teach (`Learn X: a; b; c`) |
| Episodic | Timestamped events (taught, performed, rejected) |
| Semantic | Facts (`my name is…`, `I like…`, `remember that…`) |
| Sensory | Last things seen/heard |
| Working | Current intent, active skill, live perception |

## Requirements

- Ubuntu 24.04, NVIDIA GPU (8GB VRAM recommended)
- Python 3.10+, CMake, Ninja, g++
- Ollama

## Quick Start

```bash
git clone https://github.com/dragonbuyareshi/primus.git
cd primus
./setup.sh        # installs everything, builds C++ core, downloads voice
./run.sh          # starts Ollama + PRIMUS
```

Open **http://127.0.0.1:7860** (and **http://127.0.0.1:8000** for the raw live stream).

### Windows 10 / 11

Use PowerShell from the project folder. Python 3.10–3.12 is required; for the
native C++ engine, also install CMake and Visual Studio Build Tools with
**Desktop development with C++**.

```powershell
cd D:\path\to\Primus
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
.\run.ps1
```

`setup.ps1` installs Python packages, builds the C++ module, downloads the
Piper voice model, installs Ollama via winget when available, and pulls the
configured Qwen model. Use `-SkipCppBuild`, `-SkipVoice`, or `-SkipOllama` to
temporarily omit a component. The app starts with graceful fallbacks when an
optional service is unavailable.

## Bulk task import

For large task libraries, import JSONL records directly into the local memory
database instead of entering one task at a time in the dashboard:

```powershell
python scripts\import_tasks.py data\tasks.jsonl
```

Each JSONL line must contain a task name and ordered steps:

```json
{"name":"make coffee","steps":["take a cup","add coffee","pour hot water"]}
```

Re-importing the same task name updates that task. This local SQLite store is
the development foundation for the planned PostgreSQL and vector-search layer.

## Scalable services

For PostgreSQL with pgvector and MinIO object storage, install Docker Desktop
and start the local services:

```powershell
docker compose up -d
```

Copy `.env.example` to `.env` and install the added dependencies before
switching the application from local SQLite to PostgreSQL. Set `DATABASE_URL`
to enable the PostgreSQL backend; if it is unavailable, PRIMUS logs the reason
and continues with SQLite. PostgreSQL holds tasks, versions, feedback, and
episodes, and its `semantic_documents` table is ready for pgvector embeddings.
When `MINIO_ENDPOINT` is configured, generated voice replies and snapshots are
also uploaded to the configured bucket.

Export simulator episodes for offline evaluation or future policy training:

```powershell
python -c "from src.core.evaluation import export_jsonl; export_jsonl('data/robot_training.jsonl')"
```

## Zero-prior continual meta-RL for task knowledge

Prepare the trainer on Windows with `setup-meta-rl.ps1`. The policy starts
with random weights and uses only stored procedures, recall/execute events, and
teacher feedback. It refuses to train until at least two learned tasks have
enough feedback episodes for a held-out evaluation split:

```powershell
.\setup-meta-rl.ps1
.\.venv\Scripts\python.exe -m src.training.meta_rl
```

Use `--resume` to continue from `data/meta_policy.pt`; without it, training
starts from a fresh policy and preserves the zero-prior guarantee.
Teach and use tasks through the dashboard before training. The policy domain is
`task_knowledge`; robot episodes are deliberately excluded. Extend the task
set only with teacher-approved procedures as the dataset grows.

## Robot learning lab

The dashboard includes a safe 3D tabletop pick-and-place sandbox. It exposes
move, grip, and release actions and records each completed episode with a
reward in the local database. This creates the state-action-reward data needed
before introducing an RL or meta-RL training worker.

## How PRIMUS differs from a typical chatbot

| Capability | PRIMUS today | Typical pretrained chatbot |
|---|---|---|
| Task knowledge at startup | Empty local task memory | Large pretrained world knowledge |
| Learning | Stores teacher-approved procedures and outcomes | Usually does not retain local teaching by default |
| Task execution | Shows explicit plans and recorded outcomes | Usually returns text only |
| Robotics | Safe simulated action/reward episodes | No built-in task environment |
| Meta-RL | Data foundation only; training is a future phase | Not part of ordinary chat use |

PRIMUS is therefore a continual, memory-centred learning prototype. It is not
yet a model trained by meta-RL and it does not control real hardware. Its
"zero-prior" claim applies to its local task memory: it begins with no stored
teacher procedures and refuses unknown tasks until they are taught or imported.

## Model Stack (VRAM ≈ 6GB / 8GB)

| Component | Model |
|---|---|
| Reasoning | Qwen2.5-7B-Instruct (Ollama) |
| Speech-to-Text | faster-whisper small (GPU int8) |
| Text-to-Speech | Piper (offline neural) |
| Vision | YOLOv8n (half) + MediaPipe Hands |
| Core math | C++17 pybind11 engine |

## Zero-Prior Demo Script (for reviews)

1. `rm -f data/memory_bank.json` → true blank slate.
2. Ask *"How to make tea?"* → **refused**.
3. Teach `Learn make filter coffee: add filter; add coffee; pour hot water`.
4. Ask *"How to make filter coffee?"* → answers **only your steps**.
