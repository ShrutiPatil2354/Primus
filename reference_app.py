"""Launcher for the full reference architecture companion UI.

Kept separate from ``app.py`` so the existing zPrimus interface and default
ports remain unchanged.
"""

import os


def main():
    from primus.ui import C, CSS, build

    use_voice = os.getenv("PRIMUS_REFERENCE_VOICE", "0").strip().lower() in {
        "1", "true", "yes"
    }
    port = int(os.getenv("PRIMUS_REFERENCE_PORT", "7862"))
    if use_voice:
        from primus.agent import start, stop
        start()
    try:
        build().launch(server_name="127.0.0.1", server_port=port, css=CSS)
    finally:
        if use_voice:
            stop()
        C.close()


if __name__ == "__main__":
    main()
