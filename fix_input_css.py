with open('src/ui/theme.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace general input targeting
content = content.replace(
    '.gradio-container input,',
    '.gradio-container input:not([type="checkbox"]):not([type="radio"]),'
)

# And also for the dark-dataframe inputs just in case, though dataframe inputs are text usually
content = content.replace(
    '.dark-dataframe input,',
    '.dark-dataframe input:not([type="checkbox"]),'
)
content = content.replace(
    '.memory-table input,',
    '.memory-table input:not([type="checkbox"]),'
)
content = content.replace(
    '.gradio-dataframe input,',
    '.gradio-dataframe input:not([type="checkbox"]),'
)
content = content.replace(
    '[data-testid="dataframe"] input {',
    '[data-testid="dataframe"] input:not([type="checkbox"]) {'
)

with open('src/ui/theme.py', 'w', encoding='utf-8') as f:
    f.write(content)
