import re

SELF_KEYS = ["who are you", "your name", "how are you", "what can you do",
             "what do you know", "your memory", "about yourself", "help"]

TEACH_KEYS = ["learn", "teach", "remember", "encode", "store skill"]

PERFORM_KEYS = ["perform", "execute", "run ", "start", "do ", "use skill"]

TASK_QUERY_KEYS = [
    "how to", "how do", "how should", "how can i", "way to", "steps for",
    "procedure for", "recipe", "make ", "cook ", "chop ", "cut ", "boil ",
    "bake ", "prepare ", "brew ", "what is", "who is", "where is", "when is",
    "why is", "explain", "capital", "meaning",
]


def classify(text):
    t = (text or "").lower()
    parts = [part.strip() for part in re.split(r"[\n!?]+", t) if part.strip()]
    if len(parts) > 1:
        request_kinds = {classify(part) for part in parts}
        request_kinds.discard("conversation")
        if len(request_kinds) > 1:
            return "multiple"
    if any(k in t for k in SELF_KEYS):
        return "conversation"
    if any(k in t for k in TEACH_KEYS):
        return "teach"
    if any(k in t for k in PERFORM_KEYS):
        return "perform"
    if any(k in t for k in TASK_QUERY_KEYS):
        return "task_query"
    return "conversation"


def clean_task_name(text):
    text = (text or "").strip().lower()
    for w in ["learn", "teach", "remember", "add", "create", "encode", "task",
              "skill", "primus", "how", "to", "the", "a", "an", "please", "me"]:
        text = re.sub(rf"\b{w}\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_steps(text):
    if not text:
        return []
    parts = re.split(r"[\n;]+|\bthen\b|\. |, then ", text, flags=re.IGNORECASE)
    steps = []
    for p in parts:
        p = re.sub(r"^\d+[.)]\s*", "", p.strip()).strip(" .,")
        if len(p) > 1:
            steps.append(p)
    return steps[:20]


def parse_teach(text):
    text = (text or "").strip()
    if ":" in text:
        name_part, steps_part = text.split(":", 1)
    elif "\n" in text:
        lines = text.splitlines()
        name_part, steps_part = lines[0], "\n".join(lines[1:])
    else:
        name_part = steps_part = text
    return clean_task_name(name_part), split_steps(steps_part)