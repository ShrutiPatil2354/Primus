import re
with open('src/ui/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'def process_input\(text, audio_path, history, messages, agent_id=None, use_camera_context=False, chat_mode="[^"]+", doc_file=None\):',
    'def process_input(text, audio_path, history, messages, agent_id=None, use_camera_context=False, chat_mode="Ask Mode", doc_file=None, use_audio_output=False):',
    content
)

with open('src/ui/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)
