"""Launcher for the full reference architecture companion UI.

Kept separate from ``app.py`` so the existing zPrimus interface and default
ports remain unchanged.
"""

import os


def main():
    from primus.ui import build, start_voice, stop_viewer, stop_voice

    use_voice = os.getenv("PRIMUS_REFERENCE_VOICE", "0").strip().lower() in {
        "1", "true", "yes"
    }
    port = int(os.getenv("PRIMUS_REFERENCE_PORT", "7862"))
    if use_voice:
        print(start_voice())
    try:
        build().launch(server_name="127.0.0.1", server_port=port)
    finally:
        stop_viewer()
        if use_voice:
            stop_voice()


if __name__ == "__main__":
    main()
