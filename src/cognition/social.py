"""Explicit-input social and acoustic heuristics; outputs are advisory only."""

import math


def rms(samples):
    values = [float(x) for x in samples]
    return math.sqrt(sum(x * x for x in values) / len(values)) if values else 0.0


def zero_crossing_rate(samples):
    values = [float(x) for x in samples]
    if len(values) < 2:
        return 0.0
    crossings = sum((a < 0 <= b) or (b < 0 <= a) for a, b in zip(values, values[1:]))
    return crossings / (len(values) - 1)


def turn_taking_hint(audio_energy, people_count, threshold=0.02):
    if int(people_count) <= 0:
        return {"state": "no_person_detected", "confidence": 0.0}
    active = float(audio_energy) >= float(threshold)
    return {"state": "someone_speaking" if active else "quiet",
            "confidence": min(1.0, abs(float(audio_energy)) / max(float(threshold), 1e-6))}


def attention_hint(gaze_xy, objects):
    """Return nearest supplied object to an estimated gaze point."""
    if gaze_xy is None or not objects:
        return None
    gx, gy = map(float, gaze_xy)
    ranked = sorted(objects, key=lambda obj: math.dist((gx, gy), tuple(map(float, obj["center"]))))
    return {"object": ranked[0].get("name", "unknown"),
            "distance": math.dist((gx, gy), tuple(map(float, ranked[0]["center"]))) }


def acoustic_summary(samples):
    return {"rms": rms(samples), "zero_crossing_rate": zero_crossing_rate(samples),
            "interpretation": "signal_features_only"}
