import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add elem_classes to HTML
content = content.replace(
    'composer_hint = gr.HTML(',
    'composer_hint = gr.HTML(elem_classes=["composer-hint-wrapper"],'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
