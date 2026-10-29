"""Optional approximate recall for non-critical notes; never use for task facts."""

import random


def reconstruct(note, drift=0.0, seed=None):
    """Return the original note plus a clearly separated optional paraphrase.

    The stored value is always preserved. Drift is clamped and this helper is
    unsuitable for factual answers, task procedures, or safety decisions.
    """
    amount = max(0.0, min(1.0, float(drift)))
    words = str(note).split()
    if len(words) > 1 and amount:
        rng = random.Random(seed)
        for i in range(len(words) - 1):
            if rng.random() < amount * 0.1:
                words[i], words[i + 1] = words[i + 1], words[i]
    return {"stored_note": str(note), "reconstruction": " ".join(words), "drift": amount,
            "for_factual_use": False}
