"""Bounded working memory, prediction error, practice, and uncertainty helpers."""

from collections import deque


class WorkingMemory:
    def __init__(self, capacity=7):
        self._items = deque(maxlen=max(1, int(capacity)))

    def add(self, item):
        self._items.append(item)
        return list(self._items)

    def snapshot(self):
        return list(self._items)


def prediction_error(predicted, observed):
    if len(predicted) != len(observed):
        raise ValueError("predicted and observed vectors must have the same length")
    return sum(abs(float(a) - float(b)) for a, b in zip(predicted, observed)) / max(1, len(predicted))


def uncertainty_hint(confidence):
    c = max(0.0, min(1.0, float(confidence)))
    return {"uncertainty": 1.0 - c, "ask_for_clarification": c < 0.45}


class PracticeCounter:
    def __init__(self):
        self._counts = {}

    def record(self, skill, success=True):
        row = self._counts.setdefault(str(skill), {"attempts": 0, "successes": 0})
        row["attempts"] += 1
        row["successes"] += bool(success)
        return dict(row)
