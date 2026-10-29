"""In-memory interaction counters and caller-declared beliefs."""


class SocialBond:
    def __init__(self):
        self._people = {}

    def record_interaction(self, person_id, positive=0.0):
        state = self._people.setdefault(str(person_id), {"interactions": 0, "trust_hint": 0.0, "beliefs": []})
        state["interactions"] += 1
        state["trust_hint"] = max(-1.0, min(1.0, state["trust_hint"] * 0.95 + float(positive) * 0.05))
        return dict(state)

    def record_belief(self, person_id, belief):
        state = self._people.setdefault(str(person_id), {"interactions": 0, "trust_hint": 0.0, "beliefs": []})
        state["beliefs"].append(str(belief))
        return list(state["beliefs"])

    def get(self, person_id):
        state = self._people.get(str(person_id))
        return dict(state) if state else None
