#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "[PRIMUS] Installing system dependencies..."
sudo apt update
sudo apt install -y build-essential cmake ninja-build pkg-config \
    python3-dev python3-venv python3-pip git curl wget ffmpeg portaudio19-dev

echo "[PRIMUS] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

echo "[PRIMUS] Building C++ neural core..."
cmake -S cpp_core -B cpp_core/build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"
cmake --build cpp_core/build -j
cp cpp_core/build/primus_core*.so .

echo "[PRIMUS] Downloading neural voice..."
mkdir -p data
[ -f data/en_US-lessac-medium.onnx ] || \
  wget -q -P data https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
[ -f data/en_US-lessac-medium.onnx.json ] || \
  wget -q -P data https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

echo "[PRIMUS] Pulling LLM..."
command -v ollama >/dev/null || curl -fsSL https://ollama.com/install.sh | sh
(ollama serve >/dev/null 2>&1 &) || true
sleep 2
ollama pull qwen2.5:7b-instruct || true

echo "[PRIMUS] Setup complete. Run: ./run.sh"
