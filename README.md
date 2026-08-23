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
git clone https://github.com/YOUR_USERNAME/primus.git
cd primus
./setup.sh        # installs everything, builds C++ core, downloads voice
./run.sh          # starts Ollama + PRIMUS
```

Open **http://127.0.0.1:7860** (and **http://127.0.0.1:8000** for the raw live stream).

## Team Access (remote try-out)

The microphone needs a secure context. Team members should tunnel:

```bash
ssh -L 7860:localhost:7860 -L 8000:localhost:8000 user@server-ip
```

Then open **http://localhost:7860** on their machine — full mic + camera works.

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

## Project Structure

```text
app.py            Gradio glass UI + wiring
src/config.py     paths + model config
src/core/         engine(C++), memory, llm, intent, executor, innate
src/perception/   vision (live MJPEG), audio (STT/TTS)
src/metrics/      real-time system monitor
src/ui/           handlers + glass theme
cpp_core/         C++17 neural core (pybind11)
```

## Roadmap

- **Review 1 (Aug 2026):** unified multimodal agent, memory cortex, dashboard ✔
- **Review 2 (Oct 2026):** Qwen2.5-VL demonstration learning, LoRA/DPO preference tuning, ChromaDB, real action execution, wake-word duplex speech.

## License

MIT — see `LICENSE`.
