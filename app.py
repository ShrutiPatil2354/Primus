import gradio as gr

from src.ui import theme
from src.ui import handlers
from src.metrics import monitor

with gr.Blocks() as demo:

    header = gr.HTML(monitor.header_html())

    with gr.Row():

        with gr.Column(scale=5):

            gr.HTML('<div class="panel-title">Conversation / Teaching</div>'
                    '<div class="panel-sub">Text, speech, and live camera are ALWAYS active.</div>')

            with gr.Row():
                chatbot = gr.Chatbot(height=420, label="Conversation", elem_id="primus-chat")
                cam_html = gr.HTML(handlers.camera_html())

            plan_html = gr.HTML()
            learning_html = gr.HTML(handlers.learning_html())

            with gr.Row():
                flip_btn = gr.Button("Flip")
                pause_btn = gr.Button("Pause / Resume")
                snap_btn = gr.Button("Snapshot")

            voice_out = gr.Audio(label="PRIMUS Voice", interactive=False, autoplay=True)
            audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Speak to PRIMUS (mic or upload)")

            with gr.Row():
                msg = gr.Textbox(label="Message",
                                 placeholder="Type or speak... e.g. Learn make tea: take cup; add tea bag; pour water")
                send_btn = gr.Button("Send", variant="primary")

            clear_btn = gr.Button("Clear Session", variant="secondary")

        with gr.Column(scale=5):

            gr.HTML('<div class="panel-title">Results & Agent Output</div>'
                    '<div class="panel-sub">Live responses, actions, learning, and memory updates</div>')

            with gr.Tabs():
                with gr.Tab("Messages"):
                    msg_df = gr.Dataframe(headers=["Time", "Speaker", "Message"], value=[], interactive=False, wrap=True)
                with gr.Tab("Actions"):
                    act_df = gr.Dataframe(headers=["Time", "Type", "Detail", "Status", "Score"], value=[], interactive=False, wrap=True)
                with gr.Tab("Learning"):
                    learn_df = gr.Dataframe(headers=["Time", "Event", "Detail", "Value"], value=[], interactive=False, wrap=True)
                with gr.Tab("Memory"):
                    mem_df = gr.Dataframe(headers=["Time", "Type", "Detail"], value=[], interactive=False, wrap=True)
                    mem_html = gr.HTML(handlers.memory_html())

            gr.HTML('<div class="panel-title" style="margin-top:14px">System Dashboard</div>'
                    '<div class="panel-sub">Real-time metrics and performance monitoring</div>')

            stats_html = gr.HTML()
            panels_html = gr.HTML()
            hw_html = gr.HTML(monitor.hardware_html())

    chat_state = gr.State([])
    msg_state = gr.State([])

    OUTPUTS = [chatbot, chat_state, msg_df, msg_state, act_df, learn_df, mem_df,
               plan_html, learning_html, mem_html, voice_out, msg]

    send_btn.click(handlers.process_input,
                   inputs=[msg, audio_in, chat_state, msg_state],
                   outputs=OUTPUTS)

    msg.submit(handlers.process_input,
               inputs=[msg, audio_in, chat_state, msg_state],
               outputs=OUTPUTS)

    clear_btn.click(handlers.clear_session, inputs=None, outputs=OUTPUTS)

    pause_btn.click(handlers.pause_camera)
    flip_btn.click(handlers.flip_camera)
    snap_btn.click(handlers.snapshot_camera)

    TICK_OUTPUTS = [header, stats_html, panels_html, plan_html,
                    learning_html, act_df, learn_df, mem_df, mem_html]

    if hasattr(gr, "Timer"):
        timer = gr.Timer(1.5)
        timer.tick(handlers.timer_tick, outputs=TICK_OUTPUTS)

    demo.load(handlers.boot, outputs=TICK_OUTPUTS)

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    theme=gr.themes.Base(),
    css=theme.CSS,
    share=False,
)