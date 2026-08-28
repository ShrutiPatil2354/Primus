import re

# 1. Modify handlers.py boot
with open('src/ui/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('ok = VISION.start()\n    executor.log("System", f"PRIMUS boot complete. Camera {\'online\' if ok else \'offline\'}", "Success", 1.0)', 'executor.log("System", "PRIMUS boot complete.", "Success", 1.0)')

# Add start_camera handler
start_camera_code = '''
def start_camera():
    ok = VISION.start()
    return camera_html()
'''
content = content.replace('def pause_camera():', start_camera_code + '\ndef pause_camera():')
with open('src/ui/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Modify app.py UI
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

start_camera_ui_code = '''
def start_camera_ui():
    handlers.start_camera()
    return handlers.camera_html()
'''
app_content = app_content.replace('def pause_camera_ui():', start_camera_ui_code + '\ndef pause_camera_ui():')

app_content = app_content.replace('flip_btn = gr.Button("?? Flip")', 'start_cam_btn = gr.Button("?? Start Camera")\n                        flip_btn = gr.Button("?? Flip")')

app_content = app_content.replace('''    # Perception
    flip_btn.click(''', '''    # Perception
    start_cam_btn.click(
        start_camera_ui,
        outputs=[cam_html],
    )

    use_camera_context.change(
        start_camera_ui,
        outputs=[cam_html]
    )

    flip_btn.click(''')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)
