"""Caller-supplied metric object state and bounded advisory navigation."""

import math


class SpatialMemory:
    def __init__(self):
        self._objects = {}

    def observe(self, name, xyz, confidence=1.0):
        point = tuple(float(v) for v in xyz)
        if len(point) != 3:
            raise ValueError("xyz must contain three metric coordinates")
        self._objects[str(name)] = {"xyz": point, "confidence": max(0.0, min(1.0, float(confidence)))}

    def get(self, name):
        item = self._objects.get(str(name))
        return dict(item) if item else None

    def all(self):
        return {name: dict(value) for name, value in self._objects.items()}


def potential_field_hint(position, goal, obstacles=(), max_speed=0.15, influence_radius=0.5):
    """Return a normalized advisory vector; this function never commands motion."""
    p, g = tuple(map(float, position)), tuple(map(float, goal))
    if len(p) != 3 or len(g) != 3:
        raise ValueError("position and goal must contain three coordinates")
    vec = [g[i] - p[i] for i in range(3)]
    for obstacle in obstacles:
        o = tuple(map(float, obstacle))
        away = [p[i] - o[i] for i in range(3)]
        d = math.sqrt(sum(v * v for v in away))
        if 1e-6 < d < influence_radius:
            scale = (1.0 / d - 1.0 / influence_radius) / (d * d)
            vec = [vec[i] + away[i] * scale for i in range(3)]
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    speed = max(0.0, min(float(max_speed), 0.15))
    return {"velocity_hint": tuple(v / norm * speed for v in vec), "advisory_only": True}
