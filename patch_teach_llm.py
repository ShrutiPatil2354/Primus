import re

with open('src/ui/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

llm_teach_code = '''    elif kind == "teach":
        name = ""
        steps = []
        if (":" in text or ";" in text or "\\n" in text) and not perception:
            name, steps = intent.parse_teach(text)
        else:
            if llm.online():
                teach_prompt = (
                    "You are an AI task extraction engine. The user is teaching a procedure using natural voice and/or visual camera context.\\n"
                    "Extract the concise task name and break down the procedure into a sequence of discrete, actionable steps.\\n"
                    "If the voice command is vague like 'Teach this', use the Camera Context to infer the task name and steps based on what is visible.\\n"
                    "Return ONLY valid JSON in this exact format, with no markdown or extra text:\\n"
                    '{"name": "task name", "steps": ["step 1", "step 2"]}'
                )
                teach_input = f"Voice Command: {text}\\nCamera Context: {perception}"
                resp = llm.chat([
                    {"role": "system", "content": teach_prompt},
                    {"role": "user", "content": teach_input}
                ], temperature=0.1)
                import json
                try:
                    cleaned = resp.strip().strip("").removeprefix("json").strip()
                    data = json.loads(cleaned)
                    name = data.get("name", "")
                    steps = data.get("steps", [])
                except Exception as e:
                    executor.log("Learning", f"LLM parsing failed: {e}", "Warning", 0)
                    name, steps = intent.parse_teach(text or perception)
            else:
                name, steps = intent.parse_teach(text or perception)

        if not name:
'''

content = content.replace('''    elif kind == "teach":
        name, steps = intent.parse_teach(text or perception)
        if not name:''', llm_teach_code)

with open('src/ui/handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)
