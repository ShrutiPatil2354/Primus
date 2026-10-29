import re
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove audio_in component
content = re.sub(
    r'\s*audio_in = gr\.Audio\([^)]+\)',
    '',
    content
)

# Replace the input wiring. We must replace 'audio_in' in the inputs list with None or remove it.
# Wait, in handlers.py, process_input expects:
# def process_input(text, audio_path, history, messages, agent_id=None, use_camera_context=False, chat_mode="Learn Mode", doc_file=None)
# If we remove audio_in from Gradio inputs, we must pass None for audio_path.
# Actually, the easiest way is to just pass gr.State(None) or just remove udio_in from the list and change process_input signature.
# Or keep audio_in as a hidden state, or just replace udio_in in inputs with gr.State(None).
