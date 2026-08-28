import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add max_lines=1 to msg Textbox
content = content.replace('elem_classes=["chatgpt-textbox"],\n                            )', 'elem_classes=["chatgpt-textbox"],\n                                max_lines=1,\n                            )')

# Add chatbot.clear wiring
clear_wiring = '''    chatbot.clear(
        handlers.clear_session,
        inputs=[agent_select],
        outputs=OUTPUTS
    )
'''
content = content.replace('    # Task search/editor', clear_wiring + '\n    # Task search/editor')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
