with open('src/ui/theme.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update camera-context-toggle
content = content.replace(
    '.camera-context-toggle {',
    '.camera-context-toggle {\n    min-width: 0 !important;\n    width: auto !important;\n    background: transparent !important;\n    border: none !important;'
)

# Add composer-hint-wrapper
css_addition = '''
.composer-hint-wrapper {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    flex: 1 1 auto !important;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    min-width: 0 !important;
}
.composer-top-row {
    flex-wrap: nowrap !important;
}
'''
last_quote = content.rfind('\"\"\"')
content = content[:last_quote] + css_addition + '\n' + content[last_quote:]

with open('src/ui/theme.py', 'w', encoding='utf-8') as f:
    f.write(content)
