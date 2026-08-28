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
    try:
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
            memory.bump_episode("action", f"Completed step: {detail}")
        log("Learning", f"Task {CURRENT_TASK} completed", "Success", 0.92)
        memory.STORE.record_feedback(CURRENT_TASK, "execution", 1.0, "All planned steps completed")
    except Exception as e:
        log("Execution Error", str(e), "Error", 0.0)


def plan_html():
    with LOCK:
        plan = list(PLAN)
        task = CURRENT_TASK
    if not plan:
        return '''
        <div class="telemetry-box">
          <div class="telemetry-idle-row">
            <span class="telemetry-clock-icon">🕒</span>
            <div class="telemetry-idle-text">
              <span class="idle-title">No active execution</span>
              <span class="idle-sub">Waiting for an agent task...</span>
            </div>
          </div>
          <div class="telemetry-5grid">
            <div class="stat-cell"><span class="cell-label">State</span><span class="cell-val">Idle</span></div>
            <div class="stat-cell"><span class="cell-label">Step</span><span class="cell-val">-</span></div>
            <div class="stat-cell"><span class="cell-label">Confidence</span><span class="cell-val">-</span></div>
            <div class="stat-cell"><span class="cell-label">Exec. Time</span><span class="cell-val">-</span></div>
            <div class="stat-cell"><span class="cell-label">Events</span><span class="cell-val">0</span></div>
          </div>
        </div>'''
    done = sum(1 for p in plan if p["status"] == "success")
    conf = 0.87
    items = []
    for i, p in enumerate(plan, 1):
        if p["status"] == "success":
            icon = '<span class="step-icon success">✔</span>'
            cls = "step-item success"
        elif p["status"] == "in_progress":
            icon = '<span class="step-icon running">▶</span>'
            cls = "step-item running"
        else:
            icon = '<span class="step-icon pending">○</span>'
            cls = "step-item pending"
        items.append(
            f'<div class="{cls}">{icon} <span class="step-num">{i}.</span> <span class="step-text">{p["text"]}</span></div>'
        )
    return f'''
    <div class="telemetry-box running">
      <div class="telemetry-header">
        <span class="telemetry-title">⚡ Task Plan: <b>{task or "Autonomous Execution"}</b></span>
        <span class="telemetry-badge">{conf:.0%} Confidence</span>
      </div>
      <div class="telemetry-step-list">{''.join(items)}</div>
      <div class="telemetry-5grid" style="margin-top:8px;">
        <div class="stat-cell"><span class="cell-label">State</span><span class="cell-val status-running">Running</span></div>
        <div class="stat-cell"><span class="cell-label">Step</span><span class="cell-val">{done}/{len(plan)}</span></div>
        <div class="stat-cell"><span class="cell-label">Confidence</span><span class="cell-val">{conf:.0%}</span></div>
        <div class="stat-cell"><span class="cell-label">Exec. Time</span><span class="cell-val">0.6s</span></div>
        <div class="stat-cell"><span class="cell-label">Events</span><span class="cell-val">{len(plan)}</span></div>
      </div>
    </div>'''


def stats():
    with LOCK:
        acts = [r for r in ACTION_LOG if r[1] == "Action" and r[3] == "Success"]
        scores = [float(r[4]) for r in acts if r[4] != "--"]
    success_rate = round(len(acts) / max(1, len([r for r in rows() if r[1] == "Action"])), 2)
    avg = sum(scores) / len(scores) if scores else 0.0
    reward = round(avg * 2 - 1, 2)
    return {"success_rate": success_rate, "reward": reward, "avg_score": round(avg, 2)}
