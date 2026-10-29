import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove elem_classes from both checkboxes
content = re.sub(r'use_camera_context = gr\.Checkbox\(\s*label="Use camera context",\s*value=False,\s*interactive=True,\s*elem_classes=\["camera-context-toggle"\],\s*\)',
                 'use_camera_context = gr.Checkbox(\n                                label="Use camera context",\n                                value=False,\n                                interactive=True,\n                            )', content)

content = re.sub(r'use_audio_output = gr\.Checkbox\(\s*label="Enable Voice Reply",\s*value=False,\s*interactive=True,\s*elem_classes=\["camera-context-toggle"\],\s*\)',
                 'use_audio_output = gr.Checkbox(\n                                label="Enable Voice Reply",\n                                value=False,\n                                interactive=True,\n                            )', content)

# Remove elem_classes from row? No, keep it, just remove it from checkboxes
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
