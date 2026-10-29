import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the UI element
toggle_ui = '''
                            use_camera_context = gr.Checkbox(
                                label="Use camera context",
                                value=False,
                                interactive=True,
                                elem_classes=["camera-context-toggle"],
                            )
                            use_audio_output = gr.Checkbox(
                                label="Enable Voice Reply",
                                value=False,
                                interactive=True,
                                elem_classes=["camera-context-toggle"],
                            )
'''
content = re.sub(r'\s*use_camera_context = gr\.Checkbox\([\s\S]*?elem_classes=\["camera-context-toggle"\],\n\s*\)', toggle_ui.strip('\n'), content)

# Add use_audio_output to ALL the handlers.process_input inputs lists
content = content.replace(
    '''            chat_mode,
            doc_upload_box,
        ],''',
    '''            chat_mode,
            doc_upload_box,
            use_audio_output,
        ],'''
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
