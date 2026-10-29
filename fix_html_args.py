with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '''composer_hint = gr.HTML(elem_classes=["composer-hint-wrapper"],
                                '<span class="composer-hint">'
                                'Ask about something PRIMUS already knows...'
                                '</span>'
                            )''',
    '''composer_hint = gr.HTML(
                                '<span class="composer-hint">'
                                'Ask about something PRIMUS already knows...'
                                '</span>',
                                elem_classes=["composer-hint-wrapper"]
                            )'''
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
