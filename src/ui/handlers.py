import time
from datetime import datetime

from src.core import memory, llm, intent, executor, innate
from src.perception import vision, audio
from src.metrics import monitor

VISION = vision.VISION

LEARNING = {"active": False, "task": None, "skill": None, "examples": 0, "target": 20, "progress": 0.0}
LEARN_LOG = []


def _t():
    return datetime.now().strftime("%H:%M:%S")


def learn_log(event, detail, value):
    LEARN_LOG.insert(0, [_t(), event, detail, value])
    del LEARN_LOG[30:]


def learning_rows():
    return list(LEARN_LOG)


def learning_html():
    st = memory.stats()
    if LEARNING["active"]:
        pct = int(LEARNING["progress"])
        return f'''
        <div style="background:rgba(255,255,255,0.10);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.25);border-radius:12px;padding:14px;margin-top:10px">
          <div style="display:flex;justify-content:space-between;color:#c7d2fe;font-size:.85rem">
            <span>ℹ Learning Mode: <b>Active</b> — "{LEARNING['task']}"</span>
            <span>Examples: {LEARNING['examples']}/{LEARNING['target']}</span>
          </div>
          <div style="background:rgba(255,255,255,0.12);border-radius:8px;height:8px;margin-top:8px">
            <div style="width:{pct}%;height:8px;background:#ffffff;border-radius:8px"></div>
          </div>
        </div>'''
    return f'''
    <div style="background:rgba(255,255,255,0.07);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.16);border-radius:12px;padding:12px 14px;margin-top:10px;color:#8b96ab;font-size:.8rem">
      Learning Mode: <span style="color:#22c55e">Idle</span> • Skills: {st['skills']} • Episodes: {st['episodes']} • Facts: {st['facts']}
    </div>'''

def camera_html():
    if VISION.stream_ok or VISION.running:
        return '''
        <div style="position:relative;border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,0.16);background:#000">
          <img id="primus-stream" style="width:100%;display:block" src="">
          <div style="position:absolute;top:8px;left:8px;background:#dc2626;color:#fff;font-size:.6rem;padding:2px 8px;border-radius:4px;font-weight:700">● LIVE</div>
        </div>
        <script>
        (function(){
          var el = document.getElementById('primus-stream');
          if (el) { el.src = '//' + location.hostname + ':8000/stream'; }
        })();
        </script>'''
    return f'''
    <div style="border-radius:12px;border:1px solid rgba(255,255,255,0.16);background:rgba(255,255,255,0.07);padding:20px;color:#a3a3a3;font-size:.8rem">
      Camera: {VISION.status()}
    </div>'''

def memory_html():
    b = memory.load()
    st = memory.stats()

    chip = lambda name, count, color: f'''
    <div style="flex:1;min-width:100px;background:rgba(255,255,255,0.07);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.16);border-radius:10px;padding:10px;text-align:center">
      <div style="color:{color};font-size:1.2rem;font-weight:800">{count}</div>
      <div style="color:#8b96ab;font-size:.68rem">{name}</div>
    </div>'''

    facts = b["semantic"]
    fact_lines = "".join(
        f'<div style="margin:3px 0;font-size:.76rem;color:#cbd5e1">• <b>{k}</b>: {v["value"]}</div>'
        for k, v in list(facts.items())[-6:]
    ) or '<div style="color:#64748b;font-size:.76rem">No semantic facts yet.</div>'

    w = b["working"]
    work_lines = "".join(
        f'<div style="margin:3px 0;font-size:.76rem;color:#94a3b8">{k}: <span style="color:#e5e7eb">{v}</span></div>'
        for k, v in w.items() if k != "updated"
    ) or '<div style="color:#64748b;font-size:.76rem">Empty.</div>'

    return f'''
    <div style="margin-top:8px">
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        {chip("Procedural", st['skills'], "#ffffff")}
        {chip("Episodic", st['episodes'], "#ffffff")}
        {chip("Semantic", st['facts'], "#ffffff")}
        {chip("Sensory", st['sensory'], "#ffffff")}
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:10px">
        <div style="flex:1;min-width:200px;background:rgba(255,255,255,0.07);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.16);border-radius:10px;padding:10px">
          <div style="color:#e5e7eb;font-size:.8rem;font-weight:700;margin-bottom:4px">Semantic Facts</div>
          {fact_lines}
        </div>
        <div style="flex:1;min-width:200px;background:rgba(255,255,255,0.07);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.16);border-radius:10px;padding:10px">
          <div style="color:#e5e7eb;font-size:.8rem;font-weight:700;margin-bottom:4px">Working Memory</div>
          {work_lines}
        </div>
      </div>
    </div>'''


def memory_rows():
    return memory.episodic_rows(30)


def process_input(text, audio_path, history, messages):
    t0 = time.time()
    history = history or []
    messages = messages or []
    text = (text or "").strip()

    # SPEECH (always available)
    if audio_path:
        transcript = audio.transcribe(audio_path)
        if transcript:
            text = f"{text} {transcript}".strip()
            memory.add_sensory("audio", transcript[:120])
            executor.log("Speech", f"Transcribed: {transcript[:80]}", "Success", 0.9)
        else:
            executor.log("Speech", "No speech detected in audio", "Warning", None)

    # CAMERA (always live)
    perception = ""
    if VISION.running and VISION.labels:
        perception = VISION.summary()
        memory.add_sensory("vision", perception[:120])

    if not text and not perception:
        return (history, history, messages, messages, executor.rows(), learning_rows(),
                memory_rows(), executor.plan_html(), learning_html(), memory_html(), None, "")

    memory.extract_facts(text)

    user_content = text or "Camera observation"
    if perception:
        user_content += f"\n[Camera] {perception}"

    history = history + [{"role": "user", "content": user_content}]
    messages = messages + [[_t(), "You", user_content[:160]]]

    kind = intent.classify(text)
    reply = ""
    sid = None

    # TEACH
    if kind == "teach":
        name, steps = intent.parse_teach(text or perception)
        if not name:
            name = f"task_{int(time.time())}"
        if steps:
            sid, skill = memory.add_skill(name, steps, perception)
            memory.add_episode("teach", f"Learned skill {sid}")
            learn_log("Skill Encoded", sid, skill["confidence"])
            executor.log("Learning", f"Encoded skill {sid} ({len(steps)} steps)", "Success", 0.9)
            if VISION.running:
                LEARNING.update(active=True, task=name, skill=sid, examples=0, progress=0.0)
            reply = (f"Skill '{name}' learned and stored in procedural memory.\n"
                     + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps)))
        else:
            reply = "I need steps. Example: Learn make tea: take cup; add tea bag; pour water."

    # PERFORM
    elif kind == "perform":
        sid, skill = memory.find_skill(text)
        if skill:
            executor.start_plan(sid, skill.get("steps", []))
            memory.add_episode("perform", f"Executed skill {sid}")
            reply = f"Executing learned skill '{skill.get('name')}'. Live task plan below."
        else:
            memory.add_episode("rejected", f"Perform blocked: {text[:60]}")
            executor.log("Memory", "Perform rejected: unknown task", "Blocked", 0.0)
            reply = ("I cannot perform that. I have no prior knowledge and no learned skill for it.\n"
                     "Teach me first with: Learn <task>: <steps>")

    # ZERO-PRIOR KNOWLEDGE GATE
    elif kind == "task_query":
        sid, skill = memory.find_skill(text)
        if skill:
            steps_txt = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(skill.get("steps", [])))
            memory.add_episode("recall", f"Recalled skill {sid}")
            executor.log("Memory", f"Retrieved {sid} from procedural memory", "Success",
                         skill.get("confidence", 0.5))
            reply = f"I know this only because you taught me.\n\nProcedure for '{skill.get('name', sid)}':\n{steps_txt}"
        else:
            memory.add_episode("rejected", f"Unknown query blocked: {text[:60]}")
            executor.log("Memory", "Unknown task rejected (zero-prior enforcement)", "Blocked", 0.0)
            reply = ("I have no prior knowledge about that. I am a blank slate (tabula rasa).\n"
                     "I only know what you teach me.\nTeach me with: Learn <task>: <step1>; <step2>; <step3>")

    # CONVERSATION
    else:
        memory.add_episode("conversation", text[:80])
        if llm.online():
            sys_prompt = (
                "You are PRIMUS, a zero-prior-knowledge (tabula rasa) cognitive agent.\n"
                "STRICT RULES:\n"
                "1. NEVER answer tasks, facts, recipes, or how-to questions from pretrained knowledge.\n"
                "2. If asked about any task or world fact, say you do not know it yet and ask to be taught.\n"
                "3. You may freely converse about yourself, your memory, your perceptions, and your state.\n"
                "The ONLY knowledge you possess (acquired from your teacher):\n" + memory.summary()
            )
            if perception:
                sys_prompt += f"\nCurrent visual perception: {perception}"
            msgs = [{"role": "system", "content": sys_prompt}] + history[-12:]
            reply = llm.chat(msgs)
        else:
            executor.log("System", "LLM offline - using innate untrained core", "Warning", None)
            reply = innate.reply(text)

    memory.set_working(last_intent=kind, last_skill=sid or "", last_perception=perception[:120])

    history = history + [{"role": "assistant", "content": reply}]
    messages = messages + [[_t(), "PRIMUS", reply[:160]]]

    llm.LAST["latency_ms"] = int((time.time() - t0) * 1000)

    voice = audio.speak(reply)

    return (history, history, messages, messages, executor.rows(), learning_rows(),
            memory_rows(), executor.plan_html(), learning_html(), memory_html(), voice, "")


def clear_session():
    return [], [], [], [], [], [], [], "", "", "", None, ""


def pause_camera():
    VISION.paused = not VISION.paused
    executor.log("System", "Camera paused" if VISION.paused else "Camera resumed", "Success", None)


def flip_camera():
    VISION.mirror = not VISION.mirror
    executor.log("System", "Camera flipped", "Success", None)


def snapshot_camera():
    if VISION.frame is not None:
        try:
            import cv2
            from src.config import SNAPSHOT_FILE
            cv2.imwrite(SNAPSHOT_FILE, cv2.cvtColor(VISION.frame, cv2.COLOR_RGB2BGR))
            executor.log("Perception", "Snapshot saved", "Success", 0.99)
        except Exception:
            pass


def timer_tick():
    if LEARNING["active"]:
        LEARNING["progress"] = min(100.0, LEARNING["progress"] + 4.0)
        examples = int(LEARNING["progress"] / 100 * LEARNING["target"])
        while LEARNING["examples"] < examples:
            LEARNING["examples"] += 1
            memory.add_episode("example", f"Demonstration example {LEARNING['examples']} for {LEARNING['task']}")
        if LEARNING["examples"] >= LEARNING["target"]:
            LEARNING["active"] = False
            memory.bump_confidence(LEARNING["skill"], 1.0)
            executor.log("Learning", f"Demonstration complete: {LEARNING['task']}", "Success", 0.95)
            learn_log("Demonstration Complete", LEARNING["task"], 0.95)

    m = monitor.sample()
    return (monitor.header_html(), monitor.stats_html(m), monitor.panels_html(m),
            executor.plan_html(), learning_html(),
            executor.rows(), learning_rows(), memory_rows(), memory_html())


def boot():
    ok = VISION.start()
    executor.log("System", f"PRIMUS boot complete. Camera {'online' if ok else 'offline'}", "Success", 1.0)
    return timer_tick()