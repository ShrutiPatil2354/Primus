import re
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'\s*max_lines=\d+,', '', content)
content = content.replace('elem_classes=["chatgpt-textbox"],', 'elem_classes=["chatgpt-textbox"],\n                                max_lines=1,')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
