with open('src/ui/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '"If the Excerpt does not contain the exact answer to the user\'s question, you MUST reply exactly with: \'{chosen_fallback}\'',
    'f"If the Excerpt does not contain the exact answer to the user\'s question, you MUST reply exactly with: \'{chosen_fallback}\''
)

content = content.replace(
    '"2. If the user asks ANY factual or medical question that is not explicitly in your taught knowledge below, you MUST reply: \'{chosen_fallback}\'',
    'f"2. If the user asks ANY factual or medical question that is not explicitly in your taught knowledge below, you MUST reply: \'{chosen_fallback}\''
)

with open('src/ui/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)
