"""Opt-in suggestion rules. Results are data and are never spoken automatically."""


def suggest_next_step(idle_seconds, pending_task=None, uncertainty=0.0, threshold=120):
    if pending_task and float(idle_seconds) >= float(threshold):
        return {"kind": "resume_task", "task": str(pending_task), "automatic": False}
    if float(uncertainty) >= 0.7:
        return {"kind": "clarify", "automatic": False}
    return None
