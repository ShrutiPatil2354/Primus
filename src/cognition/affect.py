"""Small bounded affect/style state, not emotion recognition."""


class AffectState:
    def __init__(self):
        self.valence = 0.0
        self.arousal = 0.0
        self.interaction_count = 0

    def update(self, valence_delta=0.0, arousal_delta=0.0):
        self.valence = max(-1.0, min(1.0, self.valence + float(valence_delta)))
        self.arousal = max(0.0, min(1.0, self.arousal + float(arousal_delta)))
        self.interaction_count += 1
        return self.snapshot()

    def snapshot(self):
        return {"valence": self.valence, "arousal": self.arousal,
                "interactions": self.interaction_count, "source": "explicit_updates"}

    def style_hint(self):
        return "calm" if self.arousal < 0.35 else "energetic"
