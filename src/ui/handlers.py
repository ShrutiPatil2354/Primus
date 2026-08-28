import html
import os
import time
from datetime import datetime

import gradio as gr

from src.core import memory, llm, intent, executor, innate
from src.core.storage import STORE
from src.perception import vision, audio
from src.metrics import monitor

VISION = vision.VISION

LEARNING = {"active": False, "task": None, "skill": None, "examples": 0, "target": 20, "progress": 0.0}
LEARN_LOG = []

def agent_choices():
    choices = [("🌐 PRIMUS Default Knowledge (Shared Core)", "")]
    for agent in STORE.list_agents():
        domain_tag = f" — {agent['domain']}" if agent.get("domain") else ""
        choices.append((f"🤖 {agent['name']}{domain_tag}", agent["id"]))
    return choices


def _knowledge_cards(skills):
    cards = []
    icons = ["📄", "🌱", "✉", "⚡", "🔍", "📊"]
    for idx, skill in enumerate(skills):
        icon = icons[idx % len(icons)]
        sid = skill["id"]
        steps = skill.get("steps", [])
        preview = " → ".join(html.escape(step) for step in steps[:3]) or "No steps recorded"
        if len(steps) > 3:
            preview += " → ..."
        conf = skill.get("confidence", 0.5)
        cards.append(f'''<div class="procedure-item">
          <div class="procedure-head">
            <span class="procedure-name">{icon} {html.escape(skill.get("name", sid))}</span>
            <span class="procedure-badge">{len(steps)} steps · {conf:.0%} confidence</span>
          </div>
          <div class="procedure-steps">{preview}</div>
        </div>''')
    return "".join(cards)


def agent_overview_html(selected_agent_id=None):
    agents = STORE.list_agents()
    if not agents:
        return ('<div class="empty-state"><b>No custom agents yet</b><br>'
                'Create one using the form above.</div>')
    cards = []
    for agent in agents:
        stats = STORE.agent_stats(agent["id"])
        active = " · ACTIVE" if agent["id"] == selected_agent_id else ""
        cards.append(f'''<div class="built-agent-row">
          <div class="built-agent-main">
            <span class="built-agent-icon">🤖</span>
            <div>
              <div class="built-agent-name">{html.escape(agent["name"])}</div>
              <div class="built-agent-domain">{html.escape(agent["domain"])}</div>
            </div>
          </div>
          <div class="built-agent-meta">
            <span class="meta-badge">{stats["skills"]} tasks · {stats.get("documents", 0)} docs · {stats["events"]} events{active}</span>
          </div>
        </div>''')
    return '<div class="built-agents-list">' + ''.join(cards) + '</div>'


def agent_knowledge_html(agent_id=None):
    agent_id = (agent_id or "").strip()
    agent = STORE.get_agent(agent_id) if agent_id else None
    if not agent:
        skills = STORE.list_skills()
        task_cards = _knowledge_cards(skills) or '<div class="empty-state">No default procedures in memory. Teach with <code>Learn &lt;task&gt;: &lt;steps&gt;</code>.</div>'
        st = memory.stats()
        return f'''<div class="knowledge-panel">
          <div class="knowledge-header">
            <div class="knowledge-title-box">
              <span class="knowledge-icon">🌐</span>
              <div>
                <div class="knowledge-title">PRIMUS DEFAULT KNOWLEDGE SPACE</div>
                <div class="knowledge-sub">Shared Cognitive Core &amp; Innate Memory · {st['skills']} skills · {st['facts']} semantic facts</div>
              </div>
            </div>
          </div>
          <div class="procedure-list task-library">{task_cards}</div>
          <div class="view-all-link"><span>View all procedures →</span></div>
        </div>'''
    skills = STORE.list_agent_skills(agent_id)
    documents = STORE.list_agent_documents(agent_id)
    task_cards = _knowledge_cards(skills) or '<div class="empty-state">No taught procedures for this custom agent yet.</div>'
    doc_cards = []
    for doc in documents[:12]:
        preview = html.escape(" ".join(doc.get("content", "").split())[:180])
        doc_cards.append(f'''<div class="doc-item">
          <div class="doc-head">
            <span class="doc-name">📄 {html.escape(doc["name"])}</span>
            <span class="doc-badge">{len(doc.get("content", ""))} chars</span>
          </div>
          <div class="doc-preview">{preview}...</div>
        </div>''')
    docs_html = "".join(doc_cards) or '<div class="empty-state">No documents uploaded for this custom agent yet.</div>'
    stats = STORE.agent_stats(agent_id)
    return f'''<div class="knowledge-panel">
      <div class="knowledge-header">
        <div class="knowledge-title-box">
          <span class="knowledge-icon">🤖</span>
          <div>
            <div class="knowledge-title">{html.escape(agent["name"]).upper()}</div>
            <div class="knowledge-sub">{html.escape(agent["domain"])} · {stats["skills"]} tasks · {stats.get("documents", 0)} docs</div>
          </div>
        </div>
      </div>
      <div class="panel-section-title">PROCEDURES ({len(skills)})</div>
      <div class="procedure-list task-library">{task_cards}</div>
      <div class="panel-section-title">DOCUMENTS ({len(documents)})</div>
      <div class="doc-list task-library">{docs_html}</div>
    </div>'''


def custom_agent_choices():
    agents = STORE.list_agents()
    if not agents:
        return [("No custom agents created yet", "")]
    return [(f"🤖 {agent['name']} — {agent['domain']}", agent["id"]) for agent in agents]


def agent_document_choices(agent_id=None):
    if not agent_id:
        return []
    docs = STORE.list_agent_documents(agent_id)
    return [(f"📄 {d['name']} ({len(d.get('content', ''))} chars)", d["id"]) for d in docs]


def agent_manager_html(agent_id=None):
    agent_id = (agent_id or "").strip()
    agent = STORE.get_agent(agent_id) if agent_id else None
    if not agent:
        return (
            '<div class="agent-empty-panel">'
            '<div class="empty-icon-wrap">📁</div>'
            '<div class="empty-title">No Agent Selected</div>'
            '<div class="empty-sub">Select a built agent from the dropdown or list to view its profile and manage its knowledge.</div>'
            '</div>'
        )
    stats = STORE.agent_stats(agent_id)
    skills = STORE.list_agent_skills(agent_id)
    documents = STORE.list_agent_documents(agent_id)
    rules = html.escape(agent.get("instructions") or "Answer only from what I teach you or uploaded documents.")

    doc_items = []
    for doc in documents:
        preview = html.escape(" ".join(doc.get("content", "").split())[:200])
        doc_items.append(f'''<div class="doc-item">
          <div class="doc-head"><span class="doc-name">📄 {html.escape(doc["name"])}</span><span class="doc-badge">{len(doc.get("content", ""))} chars</span></div>
          <div class="doc-preview">{preview}...</div>
        </div>''')
    docs_html = "".join(doc_items) or '<div class="empty-state">No documents in this agent. Ingest documents from Learn Mode in Workspace.</div>'

    skill_items = []
    for s in skills:
        steps_preview = " → ".join(html.escape(st) for st in s.get("steps", [])[:3])
        if len(s.get("steps", [])) > 3:
            steps_preview += " → ..."
        skill_items.append(f'''<div class="procedure-item">
          <div class="procedure-head"><span class="procedure-name">⚡ {html.escape(s.get("name", s["id"]))}</span><span class="procedure-badge">{len(s.get("steps", []))} steps · {s.get("confidence", 0):.0%} conf</span></div>
          <div class="procedure-steps">{steps_preview}</div>
        </div>''')
    skills_html = "".join(skill_items) or '<div class="empty-state">No procedures taught to this agent yet. Teach from Workspace with <code>Learn &lt;task&gt;: &lt;steps&gt;</code>.</div>'

    return f'''<div class="selected-agent-workspace">
      <div class="agent-profile-card">
        <div class="profile-header">
          <span class="profile-icon">🤖</span>
          <div>
            <h3 class="profile-title">{html.escape(agent["name"]).upper()}</h3>
            <p class="profile-domain">{html.escape(agent["domain"])}</p>
          </div>
        </div>
        <p class="profile-rules"><b>Response Rules:</b> {rules}</p>
      </div>

      <div class="section-heading">Agent Information</div>
      <div class="agent-stats-grid">
        <div class="stat-box"><span class="stat-label">Tasks</span><span class="stat-val">{stats["skills"]}</span></div>
        <div class="stat-box"><span class="stat-label">Documents</span><span class="stat-val">{stats.get("documents", 0)}</span></div>
        <div class="stat-box"><span class="stat-label">Events</span><span class="stat-val">{stats["events"]}</span></div>
        <div class="stat-box"><span class="stat-label">Status</span><span class="stat-val status-active">Active</span></div>
      </div>

      <div class="section-heading">Knowledge &amp; Tools</div>
      <div class="sub-heading">Procedures in this Agent ({len(skills)})</div>
      <div class="procedure-list">{skills_html}</div>
      <div class="sub-heading">Knowledge Documents ({len(documents)})</div>
      <div class="doc-list">{docs_html}</div>
    </div>'''


def sidebar_agents_html(selected_agent_id=None):
    selected_agent_id = (selected_agent_id or "").strip()
    agents = STORE.list_agents()
    st = memory.stats()
    default_active = " active" if not selected_agent_id else ""
    icons = ["💼", "⚖", "⚙", "👤", "👥", "📖", "📈", "🤖"]
    colors = ["#ec4899", "#a855f7", "#3b82f6", "#06b6d4", "#8b5cf6", "#f97316", "#10b981", "#64748b"]
    items = [
        f'''<div class="agent-nav-item sidebar-agent-item{default_active}" data-agent-id="default" style="cursor: pointer;">
          <span class="agent-avatar-icon globe">🌐</span>
          <div class="agent-nav-info">
            <div class="agent-nav-name">Default Memory (Shared)</div>
            <div class="agent-nav-meta">{st['skills']} skills · {st['facts']} facts · {st['episodes']} events</div>
          </div>
        </div>'''
    ]
    for idx, agent in enumerate(agents):
        is_active = " active" if agent["id"] == selected_agent_id else ""
        stats = STORE.agent_stats(agent["id"])
        icon = icons[idx % len(icons)]
        color = colors[idx % len(colors)]
        items.append(f'''<div class="agent-nav-item sidebar-agent-item{is_active}" data-agent-id="{agent['id']}" style="cursor: pointer;">
          <span class="agent-avatar-icon" style="background:{color}22;color:{color};border:1px solid {color}44;">{icon}</span>
          <div class="agent-nav-info">
            <div class="agent-nav-name">{html.escape(agent["name"])}</div>
            <div class="agent-nav-meta">{html.escape(agent["domain"])} · {stats["skills"]} tasks · {stats.get("documents", 0)} docs</div>
          </div>
        </div>''')
    return f'<div class="agent-sidebar-list">{"".join(items)}</div>'


def clear_active_agent_knowledge(agent_id):
    agent_id = (agent_id or "").strip()
    agent = STORE.get_agent(agent_id) if agent_id else None
    name = agent["name"] if agent else "PRIMUS Default Memory"
    STORE.clear_agent_knowledge(agent_id)
    return (
        f"<div class='reset-notice success'>Cleared knowledge procedures and documents in <b>{html.escape(name)}</b>.</div>",
        agent_knowledge_html(agent_id),
        agent_overview_html(agent_id),
        task_library_html(agent_id),
        agent_manager_html(agent_id),
        sidebar_agents_html(agent_id),
        gr.update(choices=task_choices(agent_id=agent_id), value=None),
        gr.update(choices=agent_document_choices(agent_id), value=None),
        executor.plan_html(),
        memory_table_html(),
        memory_html(),
    )


def create_agent(name, domain, instructions):
    name = (name or "").strip()
    domain = (domain or "").strip()
    if not name or not domain:
        return ("<div class='reset-notice warning'>Agent name and domain are required.</div>",
                gr.update(choices=agent_choices()),
                gr.update(choices=custom_agent_choices(), value=None),
                agent_overview_html(),
                agent_knowledge_html(),
                task_library_html(),
                gr.update(choices=task_choices(), value=None),
                agent_manager_html(),
                gr.update(choices=[]),
                sidebar_agents_html())
    agent = STORE.create_agent(name, domain, instructions or "")
    aid = agent["id"]
    return (f"<div class='reset-notice success'>Created agent <b>{html.escape(agent['name'])}</b> ({html.escape(agent['domain'])}). Selected for management.</div>",
            gr.update(choices=agent_choices(), value=aid),
            gr.update(choices=custom_agent_choices(), value=aid),
            agent_overview_html(aid),
            agent_knowledge_html(aid),
            task_library_html(aid),
            gr.update(choices=task_choices(agent_id=aid), value=None),
            agent_manager_html(aid),
            gr.update(choices=agent_document_choices(aid), value=None),
            sidebar_agents_html(aid))


def select_agent(agent_id):
    agent_id = (agent_id or "").strip()
    choices = task_choices(agent_id=agent_id)
    value = choices[0][1] if choices else None
    doc_choices = agent_document_choices(agent_id)
    return (agent_overview_html(agent_id),
            agent_knowledge_html(agent_id),
            task_library_html(agent_id),
            gr.update(choices=choices, value=value),
            gr.update(value=agent_id),
            agent_manager_html(agent_id),
            gr.update(choices=doc_choices, value=doc_choices[0][1] if doc_choices else None),
            sidebar_agents_html(agent_id))


def choose_existing_agent(agent_id):
    agent_id = (agent_id or "").strip()
    choices = task_choices(agent_id=agent_id)
    value = choices[0][1] if choices else None
    doc_choices = agent_document_choices(agent_id)
    return (gr.update(value=agent_id),
            agent_overview_html(agent_id),
            agent_knowledge_html(agent_id),
            task_library_html(agent_id),
            gr.update(choices=choices, value=value),
            agent_manager_html(agent_id),
            gr.update(choices=doc_choices, value=doc_choices[0][1] if doc_choices else None),
            sidebar_agents_html(agent_id))


def _read_document_text(file_obj):
    path = getattr(file_obj, "name", None) or file_obj
    if not path:
        return "", "document"
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    if ext in {".txt", ".md", ".csv", ".json", ".py", ".html", ".xml"}:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read(), name
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages), name
        except Exception:
            return "", name
    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs), name
        except Exception:
            return "", name
    return "", name


def upload_agent_document(agent_id, file_obj):
    agent_id = (agent_id or "").strip()
    agent = STORE.get_agent(agent_id) if agent_id else None
    if not agent:
        return ("<div class='reset-notice warning'>Select a custom agent before uploading a document.</div>",
                None, agent_manager_html(agent_id), agent_knowledge_html(agent_id), agent_overview_html(agent_id), gr.update(choices=[]), sidebar_agents_html(agent_id))
    content, name = _read_document_text(file_obj)
    content = (content or "").strip()
    if not content:
        return ("<div class='reset-notice warning'>Could not extract text from file. Supported: .txt, .md, .csv, .json, .pdf, .docx</div>",
                None, agent_manager_html(agent_id), agent_knowledge_html(agent_id), agent_overview_html(agent_id), gr.update(choices=agent_document_choices(agent_id)), sidebar_agents_html(agent_id))
    doc = STORE.add_agent_document(agent_id, name, content[:20000])
    STORE.agent_feedback(agent_id, None, "document", 0.5, f"Uploaded document {doc['name']}")
    doc_choices = agent_document_choices(agent_id)
    return (f"<div class='reset-notice success'>Uploaded '<b>{html.escape(doc['name'])}</b>' ({len(content)} chars) into {html.escape(agent['name'])}.</div>",
            None, agent_manager_html(agent_id), agent_knowledge_html(agent_id), agent_overview_html(agent_id), gr.update(choices=doc_choices, value=doc_choices[0][1] if doc_choices else None), sidebar_agents_html(agent_id))


def delete_agent_doc(agent_id, doc_id):
    agent_id = (agent_id or "").strip()
    if not agent_id or not doc_id:
        return ("<div class='reset-notice warning'>Select a document to delete.</div>",
                agent_manager_html(agent_id), agent_knowledge_html(agent_id), agent_overview_html(agent_id), gr.update(choices=agent_document_choices(agent_id)), sidebar_agents_html(agent_id))
    STORE.delete_agent_document(agent_id, doc_id)
    doc_choices = agent_document_choices(agent_id)
    return (f"<div class='reset-notice success'>Deleted document from agent.</div>",
            agent_manager_html(agent_id), agent_knowledge_html(agent_id), agent_overview_html(agent_id), gr.update(choices=doc_choices, value=doc_choices[0][1] if doc_choices else None), sidebar_agents_html(agent_id))


def delete_agent_custom(agent_id):
    agent_id = (agent_id or "").strip()
    if not agent_id:
        return ("<div class='reset-notice warning'>Select a custom agent to delete.</div>",
                agent_overview_html(), agent_knowledge_html(""), agent_manager_html(""),
                gr.update(choices=agent_choices(), value=""),
                gr.update(choices=custom_agent_choices(), value=""),
                gr.update(choices=task_choices(), value=None),
                gr.update(choices=[]),
                sidebar_agents_html(""))
    agent = STORE.get_agent(agent_id)
    name = agent["name"] if agent else agent_id
    STORE.delete_agent(agent_id)
    return (f"<div class='reset-notice success'>Deleted agent <b>{html.escape(name)}</b> and all its knowledge files.</div>",
            agent_overview_html(),
            agent_knowledge_html(""),
            agent_manager_html(""),
            gr.update(choices=agent_choices(), value=""),
            gr.update(choices=custom_agent_choices(), value=""),
            gr.update(choices=task_choices(), value=None),
            gr.update(choices=[]),
            sidebar_agents_html(""))


def _document_excerpt(document, query, limit=12000):
    content = " ".join((document.get("content") or "").split())
    if len(content) <= limit:
        return content
    import re
    tokens = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 3 and t not in {"what", "when", "where", "which", "how", "why", "this", "that", "there", "then", "about"}]
    lowered = content.lower()
    best_start = 0
    best_score = -1
    step = limit // 2
    for i in range(0, max(1, len(lowered) - limit + step), step):
        chunk = lowered[i:i+limit]
        score = sum(chunk.count(t) for t in tokens)
        if score > best_score:
            best_score = score
            best_start = i
    excerpt = content[best_start:best_start + limit].strip()
    if best_start > 0:
        excerpt = "... " + excerpt
    if best_start + limit < len(content):
        excerpt += " ..."
    return excerpt


def reset_learning_data(confirmed):
    if not confirmed:
        notice = '<div class="reset-notice warning">Tick the confirmation box before resetting learning data.</div>'
    else:
        STORE.clear_learning_data()
        LEARN_LOG.clear()
        LEARNING.update(active=False, task=None, skill=None, examples=0, progress=0.0)
        notice = '<div class="reset-notice success">Learning data reset. PRIMUS now has an empty task memory.</div>'
    return (notice, memory_table_html(), memory_html(), task_library_html(), agent_overview_html(),
            agent_knowledge_html(""), gr.update(choices=agent_choices(), value=""),
            gr.update(choices=custom_agent_choices(), value=""),
            gr.update(choices=task_choices(), value=None),
            learning_progress_html(), learning_html(), executor.plan_html(),
            agent_manager_html(""), gr.update(choices=[], value=None),
            sidebar_agents_html(""))


def show_reset_confirmation():
    return ("<div class='reset-notice warning'>This clears all learned tasks, facts, feedback, and versions.</div>",
            gr.update(visible=True), gr.update(visible=True))


def learning_progress_html():
    st = memory.stats()
    retained = st["skills"]
    feedback = STORE.feedback_rows(1)
    latest = feedback[0][4] if feedback else "No feedback recorded yet."
    return f'''<div class="progress-grid">
      <div class="progress-panel"><div><b>Continual task memory</b><span>{retained} retained tasks · {st['episodes']} learning events</span></div>
        <div class="retention-proof">Every taught procedure is stored durably. Latest learning signal: {html.escape(latest)}</div></div>
            <div class="progress-panel"><div><b>Knowledge retention</b><span>{st['facts']} semantic facts · {st['sensory']} sensory records</span></div>
                <div class="retention-proof">Task procedures, feedback, and version history are retained in the local knowledge store.</div></div>
    </div>'''


def _t():
    return datetime.now().strftime("%H:%M:%S")


def learn_log(event, detail, value):
    LEARN_LOG.insert(0, [_t(), event, detail, value])
    del LEARN_LOG[30:]


def _rows_to_html(rows, headers, empty_text="No records yet.", title=None):
    """Render read-only tabular data without using Gradio's spreadsheet widget."""
    rows = rows or []
    head_html = "".join(
        f"<th>{html.escape(str(header))}</th>" for header in headers
    )
    body_parts = []
    for row in rows[:60]:
        cells = []
        for value in list(row)[:len(headers)]:
            text = "" if value is None else str(value)
            cells.append(f"<td>{html.escape(text)}</td>")
        while len(cells) < len(headers):
            cells.append("<td></td>")
        body_parts.append("<tr>" + "".join(cells) + "</tr>")
    if not body_parts:
        body_parts.append(
            f'<tr><td class="event-table-empty" colspan="{len(headers)}">'
            f'{html.escape(empty_text)}</td></tr>'
        )
    title_html = (
        f'<div class="event-table-title">{html.escape(str(title))}</div>'
        if title else ""
    )
    return f"""
    <div class="event-table-card">
      {title_html}
      <div class="event-table-scroll">
        <table class="event-table">
          <thead><tr>{head_html}</tr></thead>
          <tbody>{''.join(body_parts)}</tbody>
        </table>
      </div>
    </div>"""


def message_table_html(rows=None):
    return _rows_to_html(
        rows or [],
        ["Time", "Speaker", "Message"],
        empty_text="No conversation messages yet.",
        title="Conversation Messages",
    )


def executor_table_html(rows=None):
    return _rows_to_html(
        executor.rows() if rows is None else rows,
        ["Time", "Type", "Detail", "Status", "Score"],
        empty_text="No execution events yet.",
        title="Execution Activity",
    )


def learning_table_html(rows=None):
    return _rows_to_html(
        learning_rows() if rows is None else rows,
        ["Time", "Event", "Detail", "Value"],
        empty_text="No learning events yet.",
        title="Learning Activity",
    )


def memory_table_html(rows=None):
    return _rows_to_html(
        memory_rows() if rows is None else rows,
        ["Time", "Type", "Detail"],
        empty_text="No episodic memory events yet.",
        title="Episodic Memory",
    )


def learning_rows():
    rows = [[row[0], row[1], row[4], row[3]] for row in STORE.feedback_rows(30)]
    rows.extend(LEARN_LOG)
    return rows[:30]


def learning_html():
    st = memory.stats()
    if LEARNING["active"]:
        pct = int(LEARNING["progress"])
        return f'''
        <div class="learning-telemetry-active">
          <div class="learning-telemetry-head">
            <span class="learning-telemetry-title">ℹ Learning Engine: <b>Active</b> — "{html.escape(LEARNING['task'] or '')}"</span>
            <span class="learning-telemetry-count">{LEARNING['examples']}/{LEARNING['target']} Examples</span>
          </div>
          <div class="learning-progress-bar"><div style="width:{pct}%;"></div></div>
        </div>'''
    return f'''
    <div class="learning-telemetry-idle">
      <div class="learning-telemetry-badge"><span class="pulse-dot">●</span> Engine Idle</div>
      <div class="learning-telemetry-stats">{st['skills']} Skills · {st['episodes']} Episodes · {st['facts']} Facts</div>
    </div>'''

def camera_html():
    if VISION.stream_ok or VISION.running:
        return '''
        <div style="position:relative;border-radius:12px;overflow:hidden;border:1px solid #1c3252;background:#000">
          <img id="primus-stream" style="width:100%;display:block" src="">
          <div style="position:absolute;top:8px;left:8px;background:#dc2626;color:#fff;font-size:.65rem;padding:3px 8px;border-radius:4px;font-weight:800;letter-spacing:0.04em">● LIVE STREAM</div>
        </div>
        <script>
        (function(){
          var el = document.getElementById('primus-stream');
          if (el) { el.src = '//' + location.hostname + ':8000/stream'; }
        })();
        </script>'''
    return f'''
    <div style="border-radius:12px;border:1px solid #1c3252;background:#080f1b;padding:24px;color:#94a3b8;font-size:.85rem;text-align:center">
      <div style="font-size:1.6rem;margin-bottom:6px">📷</div>
      <div style="color:#ffffff;font-weight:700;margin-bottom:2px">Camera: {VISION.status()}</div>
      <div>Connect a visual input device to stream real-time perception frames.</div>
    </div>'''


def memory_html():
    """Render the persistent-memory overview using theme-owned CSS classes.

    Styling intentionally lives in theme.py rather than inline here so the
    memory UI stays visually consistent with every other dashboard section.
    """
    b = memory.load()
    st = memory.stats()

    def chip(name, count, tone):
        return f'''
        <div class="memory-stat-card">
          <div class="memory-stat-value {html.escape(tone)}">{count}</div>
          <div class="memory-stat-label">{html.escape(name)}</div>
        </div>'''

    facts = b.get("semantic", {})
    fact_lines = "".join(
        f'''<div class="memory-fact-row">
             <span class="memory-bullet">•</span>
             <b>{html.escape(str(k))}</b>
             <span>{html.escape(str(v.get("value", "")))}</span>
           </div>'''
        for k, v in list(facts.items())[-6:]
    )
    if not fact_lines:
        fact_lines = '<div class="memory-empty-line">No semantic facts yet.</div>'

    working = b.get("working", {})
    work_lines = "".join(
        f'''<div class="memory-slot-row">
             <b>{html.escape(str(k))}</b>
             <span>{html.escape(str(v))}</span>
           </div>'''
        for k, v in working.items() if k != "updated"
    )
    if not work_lines:
        work_lines = '<div class="memory-empty-line">Empty working memory.</div>'

    return f'''
    <section class="memory-overview-content">
      <div class="memory-stat-grid">
        {chip("Procedural", st.get("skills", 0), "procedural")}
        {chip("Episodic", st.get("episodes", 0), "episodic")}
        {chip("Semantic", st.get("facts", 0), "semantic")}
        {chip("Sensory", st.get("sensory", 0), "sensory")}
      </div>

      <div class="memory-detail-grid">
        <article class="memory-detail-card">
          <div class="memory-detail-title">Semantic Facts <span>({len(facts)})</span></div>
          <div class="memory-detail-list">{fact_lines}</div>
        </article>

        <article class="memory-detail-card">
          <div class="memory-detail-title">Working Memory Slots</div>
          <div class="memory-detail-list">{work_lines}</div>
        </article>
      </div>
    </section>'''


def task_library_html(agent_id=None):
    """Render a compact, searchable view of learned tasks."""
    skills = STORE.list_agent_skills(agent_id) if agent_id else STORE.list_skills()
    if not skills:
        scope = "this agent" if agent_id else "default PRIMUS"
        return (f'<div class="empty-state"><b>No learned tasks in {scope} yet</b><br>'
                'Teach with <code>Learn &lt;task&gt;: step 1; step 2</code>.</div>')

    return '<div class="task-library">' + _knowledge_cards(skills) + '</div>'


def task_choices(query="", agent_id=None):
    if agent_id:
        query_tokens = set((query or "").lower().split())
        skills = STORE.list_agent_skills(agent_id)
        if query_tokens:
            skills = [
                skill for skill in skills
                if query_tokens & set(f"{skill['id']} {skill.get('name', '')}".lower().split())
            ]
    else:
        skills = STORE.list_skills(query)
    return [(skill["name"], skill["id"]) for skill in skills]


def task_editor(skill_id, agent_id=None):
    skill = STORE.get_agent_skill(agent_id, skill_id) if agent_id and skill_id else STORE.get_skill(skill_id) if skill_id else None
    if not skill:
        return "", "", "<div class='empty-state'>Select a task to inspect it.</div>"
    if agent_id:
        detail = "<div class='version-history'><b>Agent task</b><div>Stored only in this custom agent.</div></div>"
        return skill["name"], "\n".join(skill["steps"]), detail
    versions = STORE.skill_versions(skill_id)
    history = "".join(
        f"<div><b>v{v['version']}</b> · {html.escape(v['created'][:19].replace('T', ' '))} · "
        f"{len(v['steps'])} steps</div>" for v in versions
    ) or "<div>No version history yet.</div>"
    detail = f"<div class='version-history'><b>Version history</b>{history}</div>"
    return skill["name"], "\n".join(skill["steps"]), detail


def save_task(skill_id, name, steps_text, agent_id=None):
    if not skill_id:
        return "Select a task before saving.", task_choices(agent_id=agent_id), task_library_html(agent_id), agent_knowledge_html(agent_id), "", "", ""
    steps = intent.split_steps(steps_text)
    name = (name or "").strip()
    if not name or not steps:
        return "Name and at least one step are required.", task_choices(agent_id=agent_id), task_library_html(agent_id), agent_knowledge_html(agent_id), name, steps_text, task_editor(skill_id, agent_id)[2]
    if agent_id:
        skill = STORE.update_agent_skill(agent_id, skill_id, name, steps)
        STORE.agent_feedback(agent_id, skill_id, "edit", None, "Agent task procedure updated")
    else:
        skill = memory.update_skill(skill_id, name, steps)
        STORE.record_feedback(skill_id, "edit", None, "Task procedure updated")
    memory.add_episode("edit", f"Updated skill {skill_id}")
    return "Task saved.", task_choices(agent_id=agent_id), task_library_html(agent_id), agent_knowledge_html(agent_id), skill["name"], "\n".join(skill["steps"]), task_editor(skill_id, agent_id)[2]


def add_task(name, steps_text, agent_id=None):
    name = (name or "").strip()
    steps = intent.split_steps(steps_text)
    if not name or not steps:
        return "Task name and at least one step are required.", gr.update(choices=task_choices(agent_id=agent_id)), task_library_html(agent_id), agent_knowledge_html(agent_id), name, steps_text, ""
    if agent_id:
        sid, skill = STORE.add_agent_skill(agent_id, name, steps)
        STORE.agent_feedback(agent_id, sid, "learned", 0.5, f"Created with {len(steps)} steps")
    else:
        sid, skill = memory.add_skill(name, steps)
        STORE.record_feedback(sid, "learned", 0.5, f"Created with {len(steps)} steps")
    memory.add_episode("teach", f"Added task {sid} from task library")
    return "Task added.", gr.update(choices=task_choices(agent_id=agent_id), value=sid), task_library_html(agent_id), agent_knowledge_html(agent_id), skill["name"], "\n".join(skill["steps"]), task_editor(sid, agent_id)[2]


def delete_task(skill_id, confirmed, agent_id=None):
    if not skill_id:
        return "Select a task before deleting.", task_choices(agent_id=agent_id), task_library_html(agent_id), agent_knowledge_html(agent_id), "", "", "", False
    if not confirmed:
        editor = task_editor(skill_id, agent_id)
        return "Tick the confirmation box before deleting.", task_choices(agent_id=agent_id), task_library_html(agent_id), agent_knowledge_html(agent_id), editor[0], editor[1], editor[2], True
    deleted = STORE.delete_agent_skill(agent_id, skill_id) if agent_id else memory.delete_skill(skill_id)
    if deleted:
        memory.add_episode("delete", f"Deleted skill {skill_id}")
    choices = task_choices(agent_id=agent_id)
    selected = choices[0][1] if choices else None
    editor = task_editor(selected, agent_id)
    return "Task deleted.", choices, task_library_html(agent_id), agent_knowledge_html(agent_id), editor[0], editor[1], editor[2], False


def memory_rows():
    return memory.episodic_rows(30)


def toggle_chat_mode(mode):
    if "learn" in (mode or "").lower():
        return (
            gr.update(visible=True, value=None),
            gr.update(placeholder="?? Learn Mode: Type instructions or upload a document..."),
        )
    else:
        return (
            gr.update(visible=True, value=None),
            gr.update(placeholder="Ask anything..."),
        )


def process_input(text, audio_path, history, messages, agent_id=None, use_camera_context=False, chat_mode="Ask Mode", doc_file=None, use_audio_output=True):
    import random
    fallback_phrases = [
        "I don't have prior knowledge about this, I would love to learn about that.",
        "I don't have knowledge about that, please teach me.",
        "This is not currently in my knowledge base, could you teach me?",
        "I don't know the answer to that yet. I'm ready to learn if you can teach me!",
        "I haven't acquired knowledge about this yet. Please feel free to add it to my memory.",
        "I don't have any record of this information. Would you like to teach me?"
    ]
    chosen_fallback = random.choice(fallback_phrases)

    t0 = time.time()
    history = history or []
    messages = messages or []
    text = (text or "").strip()
    agent_id = (agent_id or "").strip()
    agent = STORE.get_agent(agent_id) if agent_id else None
    agent_name = agent["name"] if agent else "Default Memory"

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
    if use_camera_context and VISION.running and not VISION.paused and VISION.labels:
        perception = VISION.summary()
        memory.add_sensory("vision", perception[:120])

    doc_notice = ""
    if doc_file:
        content, name = _read_document_text(doc_file)
        content = (content or "").strip()
        if content:
            if agent_id:
                doc = STORE.add_agent_document(agent_id, name, content[:20000])
                STORE.agent_feedback(agent_id, None, "document", 0.5, f"Uploaded document {doc['name']}")
                doc_notice = f"📥 Knowledge Document '<b>{html.escape(name)}</b>' ({len(content)} chars) ingested strictly into <b>{html.escape(agent_name)}</b>.\nThis knowledge is private to {html.escape(agent_name)} and will NOT be shared with other agents."
            else:
                doc_notice = f"📥 Knowledge Document '<b>{html.escape(name)}</b>' ({len(content)} chars) ingested into Default Shared Memory."
            executor.log("Document", f"Ingested {name} into {agent_name}", "Success", 1.0)
        else:
            doc_notice = f"⚠️ Could not extract text from attached file '{html.escape(str(name))}'."

    if not text and not perception and not doc_notice:
        return (history, history, message_table_html(messages), messages, executor_table_html(), learning_table_html(),
                memory_table_html(), executor.plan_html(), learning_html(), memory_html(),
                task_library_html(agent_id), agent_knowledge_html(agent_id), None, None, "", None, sidebar_agents_html(agent_id))

    user_content = text
    if doc_file:
        user_content = f"📎 [Attached: {getattr(doc_file, 'name', 'Document')}]\n{user_content}".strip()
    if not user_content:
        user_content = "Uploaded document for active agent."
    if perception:
        user_content += f"\n[Camera] {perception}"

    history = history + [{"role": "user", "content": user_content}]
    messages = messages + [[_t(), "You", user_content[:160]]]

    kind = intent.classify(text) if text else "conversation"

    # Override intent based on explicitly selected UI mode
    if "learn" in chat_mode.lower():
        if kind == "task_query" or kind == "conversation":
            kind = "teach"
    elif "ask" in chat_mode.lower():
        if kind == "teach":
            kind = "task_query"
    reply = ""
    sid = None

    if not agent and text:
        memory.extract_facts(text)

    if doc_notice and not text:
        reply = doc_notice
    elif kind == "multiple":
        memory.add_episode("clarification", "Multiple requests submitted together")
        executor.log("System", "Multiple requests need clarification", "Blocked", None)
        reply = ("I found more than one request in that message. Please send one at a time "
                 "so I can answer or perform the correct task.")
        if doc_notice:
            reply = f"{doc_notice}\n\n{reply}"

    # TEACH
    elif kind == "teach":
        name = ""
        steps = []
        if (":" in text or ";" in text or "\n" in text) and not perception:
            name, steps = intent.parse_teach(text)
        else:
            if llm.online():
                teach_prompt = (
                    "You are an AI task extraction engine. The user is teaching a procedure using natural voice and/or visual camera context.\n"
                    "Extract the concise task name and break down the procedure into a sequence of discrete, actionable steps.\n"
                    "If the voice command is vague like 'Teach this', use the Camera Context to infer the task name and steps based on what is visible.\n"
                    "Return ONLY valid JSON in this exact format, with no markdown or extra text:\n"
                    '{"name": "task name", "steps": ["step 1", "step 2"]}'
                )
                teach_input = f"Voice Command: {text}\nCamera Context: {perception}"
                resp = llm.chat([
                    {"role": "system", "content": teach_prompt},
                    {"role": "user", "content": teach_input}
                ], temperature=0.1)
                import json
                try:
                    cleaned = resp.strip().strip("").removeprefix("json").strip()
                    data = json.loads(cleaned)
                    name = data.get("name", "")
                    steps = data.get("steps", [])
                except Exception as e:
                    executor.log("Learning", f"LLM parsing failed: {e}", "Warning", 0)
                    name, steps = intent.parse_teach(text or perception)
            else:
                name, steps = intent.parse_teach(text or perception)

        if not name:

            name = f"task_{int(time.time())}"
        if steps:
            if agent:
                sid, skill = STORE.add_agent_skill(agent_id, name, steps)
                STORE.agent_feedback(agent_id, sid, "teach", 0.5, f"Stored {len(steps)} teaching steps")
            else:
                sid, skill = memory.add_skill(name, steps, perception)
                STORE.record_feedback(sid, "learned", 0.5, f"Stored {len(steps)} teaching steps")
            memory.add_episode("teach", f"Learned skill {sid}")
            learn_log("Skill Encoded", sid, skill["confidence"])
            executor.log("Learning", f"Encoded skill {sid} ({len(steps)} steps)", "Success", 0.9)
            LEARNING.update(active=True, task=name, skill=sid, examples=0, progress=0.0)
            reply = (f"Thanks for the information! Skill \'{name}\' learned and stored strictly in '{agent_name}' procedural memory.\n"
                     + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps)))
            if doc_notice:
                reply = f"{doc_notice}\n\n{reply}"
        else:
            reply = "I need steps. Use: Learn <task>: <step 1>; <step 2>; <step 3>"
            if doc_notice:
                reply = f"{doc_notice}\n\n{reply}"

    # PERFORM
    elif kind == "perform":
        skill = STORE.find_agent_skill(agent_id, text) if agent else None
        sid = skill["id"] if skill else None
        if not agent:
            sid, skill = memory.find_skill(text)
        if skill:
            executor.start_plan(sid, skill.get("steps", []))
            memory.add_episode("perform", f"Executed skill {sid}")
            if agent:
                STORE.agent_feedback(agent_id, sid, "perform", 1.0, "Known procedure selected")
            else:
                STORE.record_feedback(sid, "perform", 1.0, "Known procedure selected for execution")
            reply = f"Executing learned skill '{skill.get('name')}'. Live task plan below."
        else:
            memory.add_episode("rejected", f"Perform blocked: {text[:60]}")
            executor.log("Memory", "Perform rejected: unknown task", "Blocked", 0.0)
            reply = (f"I cannot perform that. '{agent_name}' has no prior knowledge and no learned skill for it.\n"
                     "Teach me first with: Learn <task>: <steps>")
        if doc_notice:
            reply = f"{doc_notice}\n\n{reply}"

    # ZERO-PRIOR KNOWLEDGE GATE
    elif kind == "task_query":
        skill = STORE.find_agent_skill(agent_id, text) if agent else None
        sid = skill["id"] if skill else None
        if not agent:
            sid, skill = memory.find_skill(text)
        if skill:
            steps_txt = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(skill.get("steps", [])))
            memory.add_episode("recall", f"Recalled skill {sid}")
            executor.log("Memory", f"Retrieved {sid} from procedural memory", "Success",
                         skill.get("confidence", 0.5))
            if agent:
                STORE.agent_feedback(agent_id, sid, "recall", 1.0, "Known procedure recalled")
            else:
                STORE.record_feedback(sid, "recall", 1.0, "Known procedure recalled")
            reply = f"I know this only because you taught '{agent_name}'.\n\nProcedure for '{skill.get('name', sid)}':\n{steps_txt}"
        else:
            document = STORE.find_agent_document(agent_id, text) if agent else None
            if document:
                excerpt = _document_excerpt(document, text)
                memory.add_episode("recall", f"Recalled document {document['id']}")
                executor.log("Memory", f"Retrieved document {document['id']}", "Success", 0.7)
                STORE.agent_feedback(agent_id, None, "document_recall", 1.0, f"Answered from {document['name']}")
                if llm.online():
                    doc_prompt = (
                        f"You are a strict tabula-rasa agent named '{agent_name}'. "
                        "You MUST NOT use any pre-training knowledge. "
                        "Answer ONLY using the facts explicitly stated in the Document Excerpt below. "
                        f"If the Excerpt does not contain the exact answer to the user's question, you MUST reply exactly with: '{chosen_fallback}' Do NOT guess, infer, or provide outside information.\n\n"
                        f"Document: {document['name']}\nExcerpt:\n{excerpt}"
                    )
                    reply = "From my knowledge base:\n\n" + llm.chat([
                        {"role": "system", "content": doc_prompt},
                        {"role": "user", "content": text},
                    ], temperature=0.0)
                else:
                    reply = (f"From my knowledge base:\n\n"
                             f"{excerpt}")
            else:
                memory.add_episode("rejected", f"Unknown query blocked: {text[:60]}")
                executor.log("Memory", "Unknown task rejected (zero-prior enforcement)", "Blocked", 0.0)
                if agent:
                    STORE.agent_feedback(agent_id, None, "unknown", 0.0, f"Unknown knowledge request: {text[:80]}")
                else:
                    STORE.record_feedback(None, "unknown", 0.0, f"Unknown knowledge request: {text[:80]}")
                reply = (f"'{agent_name}' has no prior knowledge about that. This agent is a blank slate (tabula rasa).\n"
                         "I only know what you teach me.\nTeach me with: Learn <task>: <step1>; <step2>; <step3> or attach a knowledge file.")
        if doc_notice:
            reply = f"{doc_notice}\n\n{reply}"

    # CONVERSATION
    else:
        memory.add_episode("conversation", text[:80])
        if llm.online():
            taught_summary = STORE.agent_summary(agent_id) if agent else memory.summary()
            sys_prompt = (
                f"You are PRIMUS active agent '{agent_name}', a strict zero-prior-knowledge (tabula rasa) cognitive agent.\n"
                "STRICT RULES:\n"
                "1. NEVER answer medical questions, disease causes, tasks, facts, or how-to questions from pretrained knowledge.\n"
                f"2. If the user asks ANY factual or medical question that is not explicitly in your taught knowledge below, you MUST reply: '{chosen_fallback}' Do NOT guess or provide outside information.\n"
                "3. You may freely converse about yourself, your memory, your perceptions, and your state.\n"
                "The ONLY knowledge you possess (acquired from your teacher for this agent):\n" + taught_summary
            )
            if perception:
                sys_prompt += f"\nCurrent visual perception: {perception}"
            msgs = [{"role": "system", "content": sys_prompt}] + history[-12:]
            reply = llm.chat(msgs)
        else:
            executor.log("System", "LLM offline - using innate untrained core", "Warning", None)
            reply = innate.reply(text)
        if doc_notice:
            reply = f"{doc_notice}\n\n{reply}"

    memory.set_working(last_intent=kind, last_skill=sid or "", last_perception=perception[:120])

    history = history + [{"role": "assistant", "content": reply}]
    messages = messages + [[_t(), "PRIMUS", reply[:160]]]

    llm.LAST["latency_ms"] = int((time.time() - t0) * 1000)

    voice = None
    if use_audio_output:
        try:
            voice = audio.speak(reply)
        except Exception as exc:
            executor.log("Speech", f"Voice reply failed: {exc}", "Error", None)
            voice = None

    return (history, history, message_table_html(messages), messages, executor_table_html(), learning_table_html(),
            memory_table_html(), executor.plan_html(), learning_html(), memory_html(),
            task_library_html(agent_id), agent_knowledge_html(agent_id), voice, voice, "", None, sidebar_agents_html(agent_id))


def clear_session(agent_id=None):
    return ([], [], message_table_html([]), [], executor_table_html([]), learning_table_html([]), memory_table_html([]), "", "", "",
            task_library_html(agent_id), agent_knowledge_html(agent_id),
            None, None, "", None, sidebar_agents_html(agent_id))



def start_camera():
    ok = VISION.start()
    return camera_html()

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


def timer_tick(agent_id=None):
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
    return (monitor.stats_html(m), monitor.panels_html(m),
            executor.plan_html(), learning_html(), executor_table_html(), learning_table_html(),
            memory_table_html(), memory_html(), task_library_html(agent_id),
            agent_knowledge_html(agent_id), learning_progress_html())


def boot():
    executor.log("System", "PRIMUS boot complete.", "Success", 1.0)
    return timer_tick()



