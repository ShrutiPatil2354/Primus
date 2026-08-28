import re
with open('src/ui/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('def _document_excerpt(document, query, limit=3000):', 'def _document_excerpt(document, query, limit=12000):')

with open('src/ui/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)
