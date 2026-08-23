#!/usr/bin/env bash
cd "$(dirname "$0")"
source .venv/bin/activate
(ollama serve >/dev/null 2>&1 &) || true
sleep 2
python app.py
