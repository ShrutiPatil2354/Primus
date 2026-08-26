import gradio as gr

from src.ui import theme
from src.ui import handlers

with gr.Blocks() as demo:

    with gr.Tabs(elem_classes=["app-tabs"]):
        with gr.Tab("Workspace"):
            with gr.Row():
                with gr.Column(scale=6):
                    gr.HTML('<div class="panel-title">Conversation / Teaching</div><div class="panel-sub">Teach a task or ask about procedures already in memory.</div>')
                    chatbot = gr.Chatbot(height=430, label="Conversation", elem_id="primus-chat")
                    with gr.Row(equal_height=True):
                        msg = gr.Textbox(label="Message", scale=5, placeholder="Learn <task>: <step 1>; <step 2>")
                        send_btn = gr.Button("Send", variant="primary", scale=2)
                    clear_btn = gr.Button("Clear Session", variant="secondary")
                with gr.Column(scale=4):
                    gr.HTML('<div class="panel-title">Current response</div><div class="panel-sub">Plans and actions appear here as the agent works.</div>')
                    plan_html = gr.HTML()
                    learning_html = gr.HTML(handlers.learning_html())
                    with gr.Tabs():
                        with gr.Tab("Messages"):
                            msg_df = gr.Dataframe(headers=["Time", "Speaker", "Message"], value=[], interactive=False, wrap=True)
                        with gr.Tab("Actions"):
                            act_df = gr.Dataframe(headers=["Time", "Type", "Detail", "Status", "Score"], value=[], interactive=False, wrap=True)

        with gr.Tab("Perception"):
            gr.HTML('<div class="panel-title">Perception studio</div><div class="panel-sub">Camera and audio live here because they are inputs to the agent, not conversation output.</div>')
            with gr.Row():
                with gr.Column(scale=3):
                    cam_html = gr.HTML(handlers.camera_html())
                    with gr.Row():
                        flip_btn = gr.Button("Flip camera")
                        pause_btn = gr.Button("Pause / resume")
                        snap_btn = gr.Button("Save snapshot")
                with gr.Column(scale=2):
                    audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Voice input")
                    voice_out = gr.Audio(label="Latest voice reply", interactive=False, autoplay=True)

        with gr.Tab("Learning"):
            with gr.Tabs():
                with gr.Tab("Activity"):
                    learn_df = gr.Dataframe(headers=["Time", "Event", "Detail", "Value"], value=[], interactive=False, wrap=True)
                    progress_html = gr.HTML(handlers.learning_progress_html())
                with gr.Tab("Memory"):
                    mem_df = gr.Dataframe(headers=["Time", "Type", "Detail"], value=[], interactive=False, wrap=True)
                    mem_html = gr.HTML(handlers.memory_html())
                    gr.HTML('<div class="danger-zone-title">Clear learning data</div><div class="panel-sub">Remove learned tasks, facts, feedback, and versions.</div>')
                    reset_memory_btn = gr.Button("🗑", variant="stop", elem_id="reset-learning-icon")
                    reset_confirm = gr.Checkbox(label="I understand this clears all learning data", visible=False)
                    reset_confirm_btn = gr.Button("Confirm clear", variant="stop", visible=False)
                    reset_notice = gr.HTML()
                with gr.Tab("Task library"):
                    task_search = gr.Textbox(label="Search tasks", placeholder="Filter by task name")
                    task_select = gr.Dropdown(label="Task", choices=handlers.task_choices(), interactive=True)
                    task_library = gr.HTML(handlers.task_library_html())
                    with gr.Row():
                        task_name = gr.Textbox(label="Task name", scale=2)
                        task_steps = gr.Textbox(label="Steps", lines=5, scale=3)
                    version_html = gr.HTML()
                    with gr.Row():
                        task_add = gr.Button("Add task", variant="primary")
                        task_save = gr.Button("Save new version")
                        task_delete = gr.Button("Delete task", variant="stop")
                    task_delete_confirm = gr.Checkbox(label="Confirm task deletion")
                    task_notice = gr.HTML()
                    task_search.input(handlers.task_choices, inputs=task_search, outputs=task_select)
                    task_select.change(handlers.task_editor, inputs=task_select, outputs=[task_name, task_steps, version_html])
                    task_save.click(handlers.save_task, inputs=[task_select, task_name, task_steps], outputs=[task_notice, task_select, task_library, task_name, task_steps, version_html])
                    task_add.click(handlers.add_task, inputs=[task_name, task_steps], outputs=[task_notice, task_select, task_library, task_name, task_steps, version_html])
                    task_delete.click(handlers.delete_task, inputs=[task_select, task_delete_confirm], outputs=[task_notice, task_select, task_library, task_name, task_steps, version_html, task_delete_confirm])

        with gr.Tab("System"):
            gr.HTML('<div class="panel-title">System health</div><div class="panel-sub">One consolidated view of runtime, model, perception, and memory state.</div>')
            stats_html = gr.HTML()
            panels_html = gr.HTML()

    chat_state = gr.State([])
    msg_state = gr.State([])

    OUTPUTS = [chatbot, chat_state, msg_df, msg_state, act_df, learn_df, mem_df,
               plan_html, learning_html, mem_html, task_library, voice_out, msg]

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

    reset_memory_btn.click(
        handlers.show_reset_confirmation,
        inputs=None,
        outputs=[reset_notice, reset_confirm, reset_confirm_btn],
    )
    reset_confirm_btn.click(
        handlers.reset_learning_data,
        inputs=[reset_confirm],
        outputs=[reset_notice, mem_df, mem_html, task_library, progress_html,
                 learning_html, plan_html],
    )

    TICK_OUTPUTS = [stats_html, panels_html, plan_html,
                    learning_html, act_df, learn_df, mem_df, mem_html, task_library, progress_html]

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
