import re
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'(\s+)(flip_btn = gr\.Button\([^)]+\))', r'\1start_cam_btn = gr.Button("Start Camera")\1\2', content, count=1)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
