import re

with open('src/ui/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update signature
content = content.replace(
    'def process_input(text, audio_path, history, messages, agent_id=None, use_camera_context=False, chat_mode="dYZ" Learn Mode", doc_file=None):',
    'def process_input(text, audio_path, history, messages, agent_id=None, use_camera_context=False, chat_mode="dYZ" Learn Mode", doc_file=None, use_audio_output=False):'
)

# Update TTS logic
content = content.replace(
    '    voice = audio.speak(reply)',
    '    voice = audio.speak(reply) if use_audio_output else None'
)

with open('src/ui/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)
