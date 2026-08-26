import random
import threading
import time
from datetime import datetime

from src.core import memory

ACTION_LOG = []
PLAN = []
CURRENT_TASK = None
LOCK = threading.Lock()


def log(type_, detail, status="Success", score=None):
    with LOCK:
        ACTION_LOG.insert(0, [
            datetime.now().strftime("%H:%M:%S"),
            type_,
            detail,
            status,
            f"{score:.2f}" if isinstance(score, (int, float)) else "--",
        ])
        del ACTION_LOG[40:]


def rows():
    with LOCK:
        return list(ACTION_LOG)


def start_plan(skill_id, steps):
    global PLAN, CURRENT_TASK
    with LOCK:
        PLAN = [{"text": s, "status": "pending"} for s in steps]
        CURRENT_TASK = skill_id
    log("Planning", f"Planned {len(steps)} steps for {skill_id}", "Success", 0.89)
    threading.Thread(target=_run, daemon=True).start()


def _run():
    log("Perception", "Scanning environment and locating objects", "Success",
        round(random.uniform(0.85, 0.97), 2))
    for i in range(len(PLAN)):
        with LOCK:
            PLAN[i]["status"] = "in_progress"
            detail = PLAN[i]["text"]
        log("Action", detail, "In Progress", None)
        time.sleep(1.1)
        score = round(random.uniform(0.85, 0.97), 2)
        with LOCK:
            PLAN[i]["status"] = "success"
        log("Action", detail, "Success", score)
        memory.bump_episode()
    log("Learning", f"Task {CURRENT_TASK} completed", "Success", 0.92)
    memory.STORE.record_feedback(CURRENT_TASK, "execution", 1.0, "All planned steps completed")


def plan_html():
    with LOCK:
        plan = list(PLAN)
        task = CURRENT_TASK
    if not plan:
        return ""
    done = sum(1 for p in plan if p["status"] == "success")
    conf = 0.87
    items = []
    for i, p in enumerate(plan, 1):
        if p["status"] == "success":
            icon = '<span style="color:#22c55e">✔</span>'
            color = "#e5e7eb"
        elif p["status"] == "in_progress":
            icon = '<span style="color:#3b82f6">▶</span>'
            color = "#60a5fa"
        else:
            icon = '<span style="color:#475569">○</span>'
            color = "#64748b"
        items.append(
            f'<div style="margin:6px 0;color:{color};font-size:.85rem">{icon} {i}. {p["text"]}</div>'
        )
    return f'''
    <div style="background:rgba(255,255,255,0.07);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.16);border-radius:12px;padding:14px;margin-top:10px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-weight:700;color:#e5e7eb">⚙ Task Plan — {task or ""}</span>
        <span style="color:#22c55e;font-size:.8rem">Confidence: {conf:.2f}</span>
      </div>
      {''.join(items)}
      <div style="color:#64748b;font-size:.72rem;margin-top:6px">{done}/{len(plan)} steps complete</div>
    </div>'''


def stats():
    with LOCK:
        acts = [r for r in ACTION_LOG if r[1] == "Action" and r[3] == "Success"]
        scores = [float(r[4]) for r in acts if r[4] != "--"]
    success_rate = round(len(acts) / max(1, len([r for r in rows() if r[1] == "Action"])), 2)
    avg = sum(scores) / len(scores) if scores else 0.0
    reward = round(avg * 2 - 1, 2)
    return {"success_rate": success_rate, "reward": reward, "avg_score": round(avg, 2)}
