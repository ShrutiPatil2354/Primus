import json
import os
import re
import threading
from datetime import datetime

from src.core import engine
from src.core.storage import STORE

_lock = threading.Lock()

# These words describe a request, not the skill being requested.  They must
# never be enough to retrieve a procedure on their own (for example, both
# "How to make tea?" and "How to make coffee?" contain "how", "to", and
# "make").
_MATCH_STOPWORDS = {
    "a", "an", "and", "bake", "boil", "brew", "can", "chop", "clean",
    "cook", "cut", "do", "for", "how", "i", "is", "make", "prepare",
    "perform", "run", "start", "use", "wash", "water", "me", "of", "please", "procedure", "recipe", "steps", "the", "to",
    "what", "with", "you",
}


def _empty():
    return {
        "procedural": {},
        "episodic": [],
        "semantic": {},
        "sensory": [],
        "working": {},
    }


def load():
    try:
        return STORE.snapshot()
    except Exception:
        return _empty()


def _save(bank):
    STORE.replace_snapshot(bank)


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
        STORE.record_skill_version(sid, b["procedural"][sid])
        return sid, b["procedural"][sid]


def update_skill(sid, name, steps):
    return STORE.update_skill(sid, name.strip(), steps)


def delete_skill(sid):
    return STORE.delete_skill(sid)


def find_skill(text):
    b = load()
    skills = b["procedural"]
    if not skills:
        return None, None
    raw_text = (text or "").lower()
    query = set(re.findall(r"\w+", raw_text))
    meaningful_query = query - _MATCH_STOPWORDS
    best_id, best = None, 0
    for sid, s in skills.items():
        # Only the skill's name identifies it.  Matching its step words can
        # otherwise return an unrelated skill merely because both tasks use a
        # common action such as "add" or "pour".
        name_tokens = set(re.findall(r"\w+", f"{sid} {s.get('name', '')}".lower()))
        meaningful_name = name_tokens - _MATCH_STOPWORDS
        if not (meaningful_query & meaningful_name):
            continue

        score = len(meaningful_query & meaningful_name)
        if sid.replace("_", " ") in raw_text:
            score += 3
        if score > best:
            best_id, best = sid, score
    if best_id is None:
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
