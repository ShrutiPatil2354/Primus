"""Non-actuated play, gesture, and demonstration-record prototypes."""


class Demonstrations:
    def __init__(self):
        self._items = {}

    def record(self, name, observations):
        self._items[str(name)] = list(observations)
        return len(self._items[str(name)])

    def get(self, name):
        return list(self._items.get(str(name), []))


def play_suggestion(idle_seconds, safe_objects=()):
    if float(idle_seconds) < 300 or not safe_objects:
        return None
    return {"kind": "explore_object", "object": str(safe_objects[0]), "actuated": False}


def symbolic_gesture(label):
    gestures = {"greeting": "wave", "approval": "nod", "uncertainty": "tilt_head"}
    return {"symbol": str(label), "gesture_hint": gestures.get(str(label), "none"), "actuated": False}
