import re
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    ')                            use_camera_context',
    ')\n                            use_camera_context'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
