import re
import random

with open('src/ui/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

random_phrases_logic = '''
    import random
    fallback_phrases = [
        "I don't have prior knowledge about this, I would love to learn about that.",
        "I don't have knowledge about that, please teach me.",
        "This is not currently in my knowledge base, could you teach me?",
        "I don't know the answer to that yet. I'm ready to learn if you can teach me!",
        "I haven't acquired knowledge about this yet. Please feel free to add it to my memory.",
        "I don't have any record of this information. Would you like to teach me?"
    ]
    chosen_fallback = random.choice(fallback_phrases)
'''

# Find the start of process_input
content = content.replace('def process_input(', random_phrases_logic.strip() + '\n\ndef process_input(')

# Inject chosen_fallback into process_input scope. 
# Wait, if process_input is called, we want a random one each time!
# So we should put chosen_fallback = random.choice(...) INSIDE process_input!

# Let's remove the global one and put it inside process_input
content = content.replace(random_phrases_logic.strip() + '\n\ndef process_input(', 'def process_input(')

injected_logic = '''
    import random
    fallback_phrases = [
        "I don't have prior knowledge about this, I would love to learn about that.",
        "I don't have knowledge about that, please teach me.",
        "This is not currently in my knowledge base, could you teach me?",
        "I don't know the answer to that yet. I'm ready to learn if you can teach me!",
        "I haven't acquired knowledge about this yet. Please feel free to add it to my memory.",
        "I don't have any record of this information. Would you like to teach me?"
    ]
    chosen_fallback = random.choice(fallback_phrases)
'''

content = content.replace('    if not text:', injected_logic + '\n    if not text:')

# Now replace the static prompts with {chosen_fallback}
content = content.replace(
    "you MUST reply exactly with: 'This agent was not taught that yet.'",
    "you MUST reply exactly with: '{chosen_fallback}'"
)

content = content.replace(
    "you MUST reply: 'I do not know that yet, please teach me.'",
    "you MUST reply: '{chosen_fallback}'"
)

# Wait, this requires f-string formatting!
content = content.replace(
    "you MUST reply exactly with: '{chosen_fallback}'",
    "you MUST reply exactly with: '{chosen_fallback}'"  # wait, doc_prompt is already an f-string!
)
# Let's check doc_prompt definition

with open('src/ui/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)
