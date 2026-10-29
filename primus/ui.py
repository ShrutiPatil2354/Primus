import gradio as gr
import re
import threading

from primus.cams import Cams, FEEDS


_CAMERA_LOCK = threading.Lock()
_C = None
_VOICE_LOCK = threading.Lock()
_VOICE_RUNNING = False
_ACTION_REQUEST = re.compile(
    r'\b(?:find|locate|pick(?:\s+up)?|grab|place|put|sit|stand)\b',
    re.IGNORECASE,
)


def _get_cams():
    global _C
    if _C is None:
        with _CAMERA_LOCK:
            if _C is None:
                _C = Cams()
    return _C


CSS = """
html, body {
    background: #000 !important;
    height: 100%;
    margin: 0 !important;
    overflow: hidden;
    padding: 0 !important;
    width: 100%;
}
.gradio-container {
    background: #000 !important;
    margin: 0 !important;
    max-width: 100vw !important;
    min-height: 100vh !important;
    padding: 0 !important;
    width: 100vw !important;
}
footer { display: none !important; }
#viewport {
    background: #000 !important;
    border: 0 !important;
    height: 100vh !important;
    inset: 0;
    margin: 0 !important;
    max-width: none !important;
    overflow: hidden !important;
    padding: 0 !important;
    position: fixed !important;
    width: 100vw !important;
    z-index: 0;
}
#viewport > div, #viewport .image-container, #viewport .wrap {
    background: #000 !important;
    height: 100vh !important;
    max-height: none !important;
    padding: 0 !important;
    width: 100vw !important;
}
#viewport img {
    background: #000 !important;
    height: 90vh !important;
    max-height: none !important;
    object-fit: contain !important;
    width: 100vw !important;
}
#swap-row {
    align-items: center;
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 4px;
    justify-content: center;
    width: 100%;
}
#swap-row button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 999px !important;
    color: #d8e4e2 !important;
    flex: 0 0 auto !important;
    font: 600 11px ui-monospace, monospace !important;
    letter-spacing: .04em;
    min-height: 32px !important;
    padding: 4px 10px !important;
    white-space: nowrap;
}
#swap-row button:hover {
    background: #71e0c022 !important;
    border-color: #71e0c088 !important;
    color: #8af0ce !important;
}
#controls {
    align-items: center;
    backdrop-filter: blur(14px);
    background: #080d12e8;
    border: 1px solid #ffffff26;
    border-radius: 14px;
    bottom: 12px;
    left: 50%;
    max-width: 96vw;
    padding: 8px 12px;
    position: fixed !important;
    transform: translateX(-50%);
    width: min(920px, 96vw);
    z-index: 20;
}
#orbit-row {
    align-items: center;
    gap: 14px;
}
#orbit-row > div { flex: 1 1 0; min-width: 120px; }
#telemetry {
    background: #080d12bb !important;
    border: 1px solid #ffffff24 !important;
    border-radius: 8px !important;
    left: 12px;
    max-width: calc(100vw - 24px);
    position: fixed !important;
    top: 12px;
    width: max-content;
    z-index: 20;
}
#telemetry textarea {
    background: transparent !important;
    border: 0 !important;
    color: #8af0ce !important;
    font: 600 10px ui-monospace, monospace !important;
    min-height: 28px !important;
    padding: 6px 10px !important;
}
@media (max-width: 620px) {
    #swap-row button {
        font-size: 9px !important;
        padding: 3px 7px !important;
    }
    #orbit-row { gap: 4px; }
    #orbit-row > div { min-width: 90px; }
    #controls { bottom: 8px; padding: 6px; }
}
"""

EMBEDDED_CSS = """
#reference-viewer {
    background: #000 !important;
    border-radius: 12px;
    min-height: 72vh;
    overflow: hidden;
    padding: 12px !important;
    position: relative;
}
#reference-viewer #viewport {
    background: #000 !important;
    border: 0 !important;
    height: min(52vh, 600px) !important;
    inset: auto !important;
    margin: 0 !important;
    max-height: none !important;
    max-width: 100% !important;
    overflow: hidden !important;
    padding: 0 !important;
    position: relative !important;
    width: 100% !important;
    z-index: 0 !important;
}
#reference-viewer #viewport > div,
#reference-viewer #viewport .image-container,
#reference-viewer #viewport .wrap {
    background: #000 !important;
    height: 100% !important;
    max-height: none !important;
    padding: 0 !important;
    width: 100% !important;
}
#reference-viewer #viewport img {
    background: #000 !important;
    height: 100% !important;
    max-height: none !important;
    object-fit: contain !important;
    width: 100% !important;
}
#reference-viewer #swap-row {
    align-items: center;
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 4px;
    justify-content: center;
    width: 100%;
}
#reference-viewer #swap-row button {
    background: transparent !important;
    border: 1px solid #ffffff26 !important;
    border-radius: 999px !important;
    color: #d8e4e2 !important;
    flex: 0 0 auto !important;
    font: 600 11px ui-monospace, monospace !important;
    letter-spacing: .04em;
    min-height: 32px !important;
    padding: 4px 10px !important;
    white-space: nowrap;
}
#reference-viewer #swap-row button:hover {
    background: #71e0c022 !important;
    border-color: #71e0c088 !important;
    color: #8af0ce !important;
}
#reference-viewer #controls {
    backdrop-filter: blur(14px);
    background: #080d12e8;
    border: 1px solid #ffffff26;
    border-radius: 14px;
    bottom: auto !important;
    left: auto !important;
    margin: 10px auto 0 !important;
    max-width: 100% !important;
    padding: 8px 12px;
    position: relative !important;
    transform: none !important;
    width: min(920px, 100%);
    z-index: 2;
}
#reference-viewer #orbit-row { align-items: center; gap: 14px; }
#reference-viewer #orbit-row > div { flex: 1 1 0; min-width: 120px; }
#reference-viewer #telemetry {
    background: #080d12bb !important;
    border: 1px solid #ffffff24 !important;
    border-radius: 8px !important;
    left: 22px !important;
    max-width: calc(100% - 44px) !important;
    position: absolute !important;
    top: 22px !important;
    width: max-content;
    z-index: 3;
}
#reference-viewer #telemetry textarea {
    background: transparent !important;
    border: 0 !important;
    color: #8af0ce !important;
    font: 600 10px ui-monospace, monospace !important;
    min-height: 28px !important;
    padding: 6px 10px !important;
}
@media (max-width: 620px) {
    #reference-viewer #swap-row button {
        font-size: 9px !important;
        padding: 3px 7px !important;
    }
    #reference-viewer #orbit-row { gap: 4px; }
    #reference-viewer #orbit-row > div { min-width: 90px; }
    #reference-viewer #controls { padding: 6px; }
}
"""


def tick():
    cams = _C
    if cams is None:
        return None, 'Viewer paused — select this tab to start the simulator.'
    return cams.view(), cams.status()


def focus(name):
    _get_cams().focus = name
    return tick()


def set_orbit(azimuth, elevation, distance):
    cams = _C
    if cams is not None:
        cams.orbit = (azimuth, elevation, distance)


def start_viewer():
    try:
        _get_cams()
        image, status = tick()
        return image, status, gr.Timer(active=True)
    except Exception as error:
        return None, f'Could not start reference viewer: {error}', gr.Timer(active=False)


def stop_viewer():
    global _C
    with _CAMERA_LOCK:
        cams, _C = _C, None
        if cams is not None:
            cams.close()
    return gr.Timer(active=False)


def start_voice():
    global _VOICE_RUNNING
    with _VOICE_LOCK:
        if _VOICE_RUNNING:
            return 'Voice companion is already running.'
        try:
            from primus.ears import sd

            if sd is None:
                return 'Voice companion not started: install sounddevice first.'
            sd.query_devices(kind='input')
            from primus.agent import start

            start()
            _VOICE_RUNNING = True
            return 'Voice companion is listening. Use Stop voice to end the microphone loop.'
        except Exception as error:
            return f'Voice companion not started: {error}'


def stop_voice():
    global _VOICE_RUNNING
    with _VOICE_LOCK:
        if not _VOICE_RUNNING:
            return 'Voice companion is stopped.'
        try:
            from primus.agent import stop

            stop()
        finally:
            _VOICE_RUNNING = False
    return 'Voice companion stopped.'


def reference_companion_reply(message, history):
    """Run documented reference-brain chat; action plans are display-only."""
    history = list(history or [])
    message = (message or '').strip()
    if not message:
        return history, ''

    try:
        if _ACTION_REQUEST.search(message):
            from primus.skills_action import parse_action

            plan = parse_action(message)
            if plan:
                lines = [
                    f"{index}. {step['prim']}"
                    + (f" {step['obj']}" if step.get('obj') else '')
                    + (f" -> {step['target']}" if step.get('target') else '')
                    for index, step in enumerate(plan, start=1)
                ]
                reply = (
                    'Advisory plan only; no ROS command or robot action was sent.\n'
                    + '\n'.join(lines)
                )
            else:
                reply = 'I could not form an advisory plan from that request.'
        else:
            from primus.brain import think

            reply = think(message)
    except Exception as error:
        reply = f'Reference brain error: {error}'

    history.extend([
        {'role': 'user', 'content': message},
        {'role': 'assistant', 'content': str(reply)},
    ])
    return history, ''


def render():
    with gr.Column(elem_id='reference-viewer'):
        gr.Markdown('### Scene views and camera controls')
        feed_buttons = []
        with gr.Column(elem_id='controls'):
            with gr.Row(elem_id='swap-row'):
                for name in FEEDS:
                    label = name.replace('_', ' ').upper()
                    feed_buttons.append((gr.Button(label, size='sm'), name))
            with gr.Row(elem_id='orbit-row'):
                azimuth = gr.Slider(
                    0, 360, value=200, label='azimuth', step=1
                )
                elevation = gr.Slider(
                    -80, 20, value=-15, label='elevation', step=1
                )
                distance = gr.Slider(
                    1.0, 8.0, value=3.5, label='distance', step=0.1
                )
                for slider in (azimuth, elevation, distance):
                    slider.change(
                        set_orbit,
                        inputs=[azimuth, elevation, distance],
                        outputs=None,
                    )

        viewport = gr.Image(
            elem_id='viewport',
            interactive=False,
            show_label=False,
        )
        telemetry = gr.Textbox(
            elem_id='telemetry',
            interactive=False,
            lines=1,
            show_label=False,
        )
        for button, name in feed_buttons:
            button.click(
                focus,
                inputs=gr.State(name),
                outputs=[viewport, telemetry],
            )

        gr.Markdown('### Voice companion (microphone is opt-in)')
        with gr.Row():
            voice_start = gr.Button('Start voice companion', variant='primary')
            voice_stop = gr.Button('Stop voice companion', variant='secondary')
        voice_status = gr.Markdown(
            'Voice companion is running.' if _VOICE_RUNNING else
            'Voice companion is stopped. Start it only when you are ready to use the microphone.'
        )
        voice_start.click(start_voice, outputs=[voice_status], show_progress='hidden')
        voice_stop.click(stop_voice, outputs=[voice_status], show_progress='hidden')

        timer = gr.Timer(0.05, active=False)
        timer.tick(tick, inputs=None, outputs=[viewport, telemetry])
    return timer, viewport, telemetry


def build():
    with gr.Blocks(css=CSS) as demo:
        _timer, viewport, telemetry = render()
        demo.load(
            start_viewer,
            inputs=None,
            outputs=[viewport, telemetry, _timer],
        )
    return demo
