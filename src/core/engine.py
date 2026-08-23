try:
    import primus_core as _cpp
    ENGINE_NAME = "C++ Neural Engine"
except Exception:
    _cpp = None
    ENGINE_NAME = "Python Fallback Engine"


def update_confidence(old, reward, lr=0.15):
    if _cpp is not None:
        return float(_cpp.update_confidence(old, reward, lr))
    new = old + lr * (reward - old)
    return max(0.0, min(1.0, new))


def status():
    return ENGINE_NAME
