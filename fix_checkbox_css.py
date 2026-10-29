with open('src/ui/theme.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add explicit fix for checkbox styling
checkbox_fix = '''
/* Ensure checkboxes are fully visible and clickable */
.gradio-container input[type="checkbox"] {
    appearance: auto !important;
    -webkit-appearance: checkbox !important;
    background: transparent !important;
    border: 1px solid #94a3b8 !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    width: 16px !important;
    height: 16px !important;
    cursor: pointer !important;
}
.gradio-container input[type="checkbox"]:checked {
    accent-color: #3b82f6 !important;
}
label:has(input[type="checkbox"]) {
    cursor: pointer !important;
    pointer-events: auto !important;
}
'''
last_quote = content.rfind('"""')
content = content[:last_quote] + checkbox_fix + '\n' + content[last_quote:]

with open('src/ui/theme.py', 'w', encoding='utf-8') as f:
    f.write(content)
