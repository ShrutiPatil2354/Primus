"""Handlers for the opt-in cognition lab; separate from chat handlers."""

import html
import json

from src.cognition.memory_store import STORE


def list_memories(kind=None):
    records = STORE.query(kind=kind or None, limit=100, touch=False)
    if not records:
        return "<div class='empty-state'>No cognition memories recorded.</div>"
    cards = []
    for record in records:
        payload = html.escape(json.dumps(record["payload"], ensure_ascii=False))
        cards.append(
            "<div class='procedure-item'>"
            f"<b>{html.escape(record['kind'])}</b> · salience {record['salience']:.2f}<br>"
            f"<code>{html.escape(record['id'])}</code><br><span>{payload}</span></div>"
        )
    return "".join(cards)


def add_memory(kind, payload_text, salience):
    kind = str(kind or "note").strip() or "note"
    raw = str(payload_text or "").strip()
    if not raw:
        return "Enter a note first.", list_memories()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"text": raw}
    record_id = STORE.add(kind, payload, salience=float(salience))
    return f"Saved cognition note {record_id}.", list_memories()


def maintain_memories():
    merged = STORE.consolidate()
    decayed = STORE.decay()
    return f"Maintenance complete: consolidated {merged} duplicate notes; decayed {decayed} notes.", list_memories()


def forget_memory(record_id):
    ok = STORE.forget(str(record_id or "").strip())
    return ("Memory forgotten." if ok else "No matching memory ID."), list_memories()
