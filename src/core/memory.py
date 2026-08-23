import json
import os
import re
import threading
from datetime import datetime

from src.config import MEMORY_BANK
from src.core import engine

_lock = threading.Lock()


def _empty():
    return {
        "procedural": {},
        "episodic": [],
        "semantic": {},
        "sensory": [],
        "working": {},
    }


def load():
    if not os.path.exists(MEMORY_BANK):
        return _empty()
    try:
        with open(MEMORY_BANK, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = _empty()
        base.update(data)
        return base
    except Exception:
        return _empty()


def _save(bank):
    with open(MEMORY_BANK, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)


def _now():
    return datetime.now().isoformat()


# ================= PROCEDURAL (skills) =================

def add_skill(name, steps, perception=""):
    with _lock:
        b = load()
        sid = "_".join(name.lower().split()) or f"task_{int(datetime.now().timestamp())}"
        b["procedural"][sid] = {
            "name": name,
            "steps": steps,
            "confidence": 0.5,
            "perception": perception,
            "created": _now(),
            "updated": _now(),
        }
        _save(b)
        return sid, b["procedural"][sid]


def find_skill(text):
    b = load()
    skills = b["procedural"]
    if not skills:
        return None, None
    query = set(re.findall(r"\w+", (text or "").lower()))
    best_id, best = None, 0
    for sid, s in skills.items():
        blob = " ".join([sid, s.get("name", ""), " ".join(s.get("steps", []))]).lower()
        score = len(query & set(re.findall(r"\w+", blob)))
        if sid.replace("_", " ") in (text or "").lower():
            score += 3
        if score > best:
            best_id, best = sid, score
    if best_id is None or best < 2:
        return None, None
    return best_id, skills[best_id]


def bump_confidence(sid, reward=1.0):
    with _lock:
        b = load()
        if sid in b["procedural"]:
            old = b["procedural"][sid].get("confidence", 0.5)
            b["procedural"][sid]["confidence"] = round(engine.update_confidence(old, reward), 3)
            b["procedural"][sid]["updated"] = _now()
            _save(b)
            return b["procedural"][sid]["confidence"]
    return 0.5


# ================= EPISODIC (events) =================

def add_episode(kind, detail):
    with _lock:
        b = load()
        b["episodic"].insert(0, {"t": _now(), "kind": kind, "detail": detail})
        b["episodic"] = b["episodic"][:200]
        _save(b)


# ================= SENSORY (last seen/heard) =================

def add_sensory(kind, detail):
    with _lock:
        b = load()
        b["sensory"].insert(0, {"t": _now(), "kind": kind, "detail": detail})
        b["sensory"] = b["sensory"][:20]
        _save(b)


# ================= SEMANTIC (facts) =================

def extract_facts(text):
    facts = []
    m = re.search(r"(?:my name is|i am called|call me)\s+([a-zA-Z]+)", text or "", re.I)
    if m:
        facts.append(("user_name", m.group(1).capitalize()))
    m = re.search(r"\bi (?:like|love|prefer|enjoy)\s+(.{2,60})", text or "", re.I)
    if m:
        facts.append(("user_prefers", m.group(1).strip(" .!")))
    m = re.search(r"\bremember that\s+(.{2,80})", text or "", re.I)
    if m:
        facts.append(("fact", m.group(1).strip(" .!")))
    if facts:
        with _lock:
            b = load()
            for k, v in facts:
                b["semantic"][k] = {"value": v, "t": _now()}
            _save(b)
    return facts


# ================= WORKING (current context) =================

def set_working(**kv):
    with _lock:
        b = load()
        b["working"].update(kv)
        b["working"]["updated"] = _now()
        _save(b)


# ================= STATS / SUMMARY =================

def stats():
    b = load()
    procs = list(b["procedural"].values())
    confs = [p.get("confidence", 0.5) for p in procs]
    return {
        "skills": len(procs),
        "episodes": len(b["episodic"]),
        "facts": len(b["semantic"]),
        "sensory": len(b["sensory"]),
        "avg_confidence": round(sum(confs) / len(confs), 2) if confs else 0.0,
    }


def summary():
    b = load()
    lines = []
    for sid, s in b["procedural"].items():
        lines.append(f"[SKILL {sid.upper()}] " + " -> ".join(s.get("steps", [])))
    for k, v in b["semantic"].items():
        lines.append(f"[FACT] {k}: {v['value']}")
    return "\n".join(lines) if lines else "Nothing. The agent knows nothing yet."


def episodic_rows(limit=30):
    return [[e["t"][11:19], e["kind"], e["detail"]] for e in load()["episodic"][:limit]]