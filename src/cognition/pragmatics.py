"""Indirect-request candidates that require confirmation before action."""


def candidate_request(text):
    lowered = str(text or "").lower()
    patterns = (("open", ("it's hot in here", "could use some air")),
                ("turn_on_light", ("it's dark", "hard to see")),
                ("bring_water", ("i'm thirsty", "could use a drink")))
    for action, phrases in patterns:
        if any(phrase in lowered for phrase in phrases):
            return {"candidate": action, "requires_confirmation": True, "executed": False}
    return None
