with open('src/ui/theme.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will find the block I just added at the end and fix the braces
bad_block = '''
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
good_block = '''
.composer-hint-wrapper {{
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
}}
.composer-top-row {{
    flex-wrap: nowrap !important;
}}
'''

content = content.replace(bad_block, good_block)

# Also check camera-context-toggle that I updated earlier
content = content.replace(
    '.camera-context-toggle {\n    min-width: 0 !important;\n    width: auto !important;\n    background: transparent !important;\n    border: none !important;',
    '.camera-context-toggle {{\n    min-width: 0 !important;\n    width: auto !important;\n    background: transparent !important;\n    border: none !important;'
)

with open('src/ui/theme.py', 'w', encoding='utf-8') as f:
    f.write(content)
