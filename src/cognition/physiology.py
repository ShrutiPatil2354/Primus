"""Explicit-input toy sleep, mood, and contact state; no runtime gating."""


class SleepCycle:
    def __init__(self):
        self.pressure = 0.0
        self.stage = "awake"

    def tick(self, awake_minutes=1.0, rested=False):
        self.pressure = max(0.0, min(1.0, self.pressure + float(awake_minutes) / 960.0 - (0.5 if rested else 0.0)))
        self.stage = "rem" if self.pressure > 0.95 else "nrem" if self.pressure > 0.8 else "awake"
        return {"pressure": self.pressure, "stage": self.stage}


class MoodState:
    def __init__(self):
        self.mood = 0.0
        self.fatigue = 0.0

    def tick(self, reward=0.0, effort=0.0, rest=0.0):
        self.mood = max(-1.0, min(1.0, self.mood * 0.95 + float(reward) * 0.05))
        self.fatigue = max(0.0, min(1.0, self.fatigue + float(effort) * 0.05 - float(rest) * 0.1))
        return {"mood": self.mood, "fatigue": self.fatigue}


def contact_hint(force, threshold=10.0):
    value = max(0.0, float(force))
    return {"contact": value > 0.0, "avoidance_hint": min(1.0, value / max(float(threshold), 1e-6)),
            "advisory_only": True}
