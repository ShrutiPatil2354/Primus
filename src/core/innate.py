from src.core import memory


def reply(text):
    t = (text or "").lower()
    st = memory.stats()

    if t.strip() in ["hi", "hey"] or any(k in t for k in ["hello", "hey ", "good morning", "good evening"]):
        return "Hello. I am PRIMUS, a zero-prior cognitive agent. I know only what you teach me."

    if "who are you" in t or "your name" in t:
        return ("I am PRIMUS. I was created as a blank slate. I have innate faculties for "
                "language, perception, and learning, but no acquired knowledge. You are my teacher.")

    if "how are you" in t:
        return "All systems nominal. My memory cortex is active and I am ready to learn."

    if "what can you do" in t or "help" in t:
        return ("I can learn tasks from your instruction, perform learned tasks, see through my camera, "
                "hear your speech, and remember everything you teach me. Teach me with: "
                "Learn <task>: <step1>; <step2>")

    if "what do you know" in t or "your memory" in t or "remember" in t:
        return (f"I currently hold {st['skills']} skills, {st['episodes']} episodes, and {st['facts']} facts. "
                "Everything in my memory was acquired from you, not pretrained.")

    if "thank" in t:
        return "You are welcome, teacher."

    return ("I have no prior knowledge to interpret that. I am tabula rasa. "
            "Teach me with: Learn <task>: <step1>; <step2>; <step3>")