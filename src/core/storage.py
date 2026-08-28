"""Durable local memory storage.

SQLite is the zero-configuration development store.  Its tables mirror the
future PostgreSQL schema, so moving to PostgreSQL/pgvector does not require
changing the agent-facing memory API.
"""
import json
import os
import re
import sqlite3
import threading
from datetime import datetime

from src.config import DATA_DIR, MEMORY_BANK


DB_PATH = os.getenv("PRIMUS_DB_PATH", os.path.join(DATA_DIR, "primus_memory.db"))


class MemoryStore:
    def __init__(self, path=DB_PATH):
        self.path = path
        self.lock = threading.RLock()
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self):
        with self.lock, self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS skills (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, steps_json TEXT NOT NULL,
                    confidence REAL NOT NULL, perception TEXT, created TEXT, updated TEXT
                );
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, t TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS semantic_facts (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL, t TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sensory_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, t TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS working_memory (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS robot_episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, t TEXT NOT NULL, task TEXT NOT NULL,
                    actions_json TEXT NOT NULL, reward REAL NOT NULL, success INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS skill_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, skill_id TEXT NOT NULL,
                    version INTEGER NOT NULL, name TEXT NOT NULL, steps_json TEXT NOT NULL,
                    confidence REAL NOT NULL, perception TEXT, created TEXT NOT NULL,
                    UNIQUE(skill_id, version)
                );
                CREATE TABLE IF NOT EXISTS feedback_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, skill_id TEXT, event TEXT NOT NULL,
                    reward REAL, detail TEXT NOT NULL, t TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, domain TEXT NOT NULL,
                    instructions TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS agent_skills (
                    id TEXT NOT NULL, agent_id TEXT NOT NULL, name TEXT NOT NULL,
                    steps_json TEXT NOT NULL, confidence REAL NOT NULL, created TEXT NOT NULL,
                    updated TEXT NOT NULL, PRIMARY KEY (agent_id, id)
                );
                CREATE TABLE IF NOT EXISTS agent_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT NOT NULL,
                    skill_id TEXT, event TEXT NOT NULL, reward REAL, detail TEXT NOT NULL,
                    t TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS agent_documents (
                    id TEXT NOT NULL, agent_id TEXT NOT NULL, name TEXT NOT NULL,
                    content TEXT NOT NULL, created TEXT NOT NULL, PRIMARY KEY (agent_id, id)
                );
                CREATE INDEX IF NOT EXISTS idx_episodes_time ON episodes(t DESC);
                CREATE INDEX IF NOT EXISTS idx_sensory_time ON sensory_events(t DESC);
                CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
            """)
        self._migrate_json_once()

    def _migrate_json_once(self):
        with self.lock, self._connect() as db:
            if db.execute("SELECT 1 FROM skills LIMIT 1").fetchone() or not os.path.exists(MEMORY_BANK):
                return
            try:
                with open(MEMORY_BANK, encoding="utf-8") as f:
                    bank = json.load(f)
            except (OSError, json.JSONDecodeError):
                return
            for sid, skill in bank.get("procedural", {}).items():
                db.execute("INSERT OR IGNORE INTO skills VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (sid, skill.get("name", sid), json.dumps(skill.get("steps", [])),
                            skill.get("confidence", .5), skill.get("perception", ""),
                            skill.get("created", ""), skill.get("updated", "")))
            for episode in reversed(bank.get("episodic", [])):
                db.execute("INSERT INTO episodes(t, kind, detail) VALUES (?, ?, ?)",
                           (episode.get("t", ""), episode.get("kind", ""), episode.get("detail", "")))
            for key, fact in bank.get("semantic", {}).items():
                db.execute("INSERT OR REPLACE INTO semantic_facts VALUES (?, ?, ?)",
                           (key, fact.get("value", ""), fact.get("t", "")))

    def snapshot(self):
        with self.lock, self._connect() as db:
            skills = {r["id"]: {"name": r["name"], "steps": json.loads(r["steps_json"]),
                      "confidence": r["confidence"], "perception": r["perception"] or "",
                      "created": r["created"], "updated": r["updated"]}
                      for r in db.execute("SELECT * FROM skills")}
            episodes = [dict(r) for r in db.execute("SELECT t, kind, detail FROM episodes ORDER BY id DESC LIMIT 200")]
            semantic = {r["key"]: {"value": r["value"], "t": r["t"]}
                        for r in db.execute("SELECT * FROM semantic_facts")}
            sensory = [dict(r) for r in db.execute("SELECT t, kind, detail FROM sensory_events ORDER BY id DESC LIMIT 20")]
            working = {r["key"]: r["value"] for r in db.execute("SELECT * FROM working_memory")}
        return {"procedural": skills, "episodic": episodes, "semantic": semantic, "sensory": sensory, "working": working}

    def add_skill(self, name, steps, perception=""):
        now = datetime.now().isoformat()
        sid = "_".join(name.lower().split()) or f"task_{int(datetime.now().timestamp())}"
        steps_clean = [str(s).strip() for s in steps if str(s).strip()]
        with self.lock, self._connect() as db:
            existing = db.execute("SELECT confidence, created FROM skills WHERE id = ?", (sid,)).fetchone()
            confidence = existing["confidence"] if existing else 0.5
            created = existing["created"] if existing else now
            db.execute("""
                INSERT INTO skills(id, name, steps_json, confidence, perception, created, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name, steps_json=excluded.steps_json,
                    perception=excluded.perception, updated=excluded.updated
            """, (sid, name.strip(), json.dumps(steps_clean), confidence, str(perception or ""), created, now))
            version = db.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM skill_versions WHERE skill_id = ?",
                (sid,),
            ).fetchone()[0]
            db.execute(
                "INSERT INTO skill_versions(skill_id, version, name, steps_json, confidence, perception, created) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (sid, version, name.strip(), json.dumps(steps_clean), confidence, str(perception or ""), now),
            )
        return sid, self.get_skill(sid)

    def add_episode(self, kind, detail):
        now = datetime.now().isoformat()
        with self.lock, self._connect() as db:
            db.execute("INSERT INTO episodes(t, kind, detail) VALUES (?, ?, ?)", (now, str(kind), str(detail)))
            db.execute("DELETE FROM episodes WHERE id NOT IN (SELECT id FROM episodes ORDER BY id DESC LIMIT 2000)")

    def add_sensory_event(self, kind, detail):
        now = datetime.now().isoformat()
        with self.lock, self._connect() as db:
            db.execute("INSERT INTO sensory_events(t, kind, detail) VALUES (?, ?, ?)", (now, str(kind), str(detail)))
            db.execute("DELETE FROM sensory_events WHERE id NOT IN (SELECT id FROM sensory_events ORDER BY id DESC LIMIT 200)")

    def set_semantic_fact(self, key, value):
        now = datetime.now().isoformat()
        with self.lock, self._connect() as db:
            db.execute("INSERT OR REPLACE INTO semantic_facts VALUES (?, ?, ?)", (str(key), str(value), now))

    def set_working_memory(self, kv_dict):
        with self.lock, self._connect() as db:
            for k, v in kv_dict.items():
                db.execute("INSERT OR REPLACE INTO working_memory VALUES (?, ?)", (str(k), str(v)))

    def update_confidence(self, skill_id, reward=1.0):
        now = datetime.now().isoformat()
        with self.lock, self._connect() as db:
            current = db.execute("SELECT confidence FROM skills WHERE id = ?", (skill_id,)).fetchone()
            if not current:
                return 0.5
            from src.core import engine
            old_conf = current["confidence"]
            new_conf = round(engine.update_confidence(old_conf, reward), 3)
            db.execute("UPDATE skills SET confidence = ?, updated = ? WHERE id = ?", (new_conf, now, skill_id))
            return new_conf

    def replace_snapshot(self, bank):
        """Compatibility bridge while callers are migrated to repository methods."""
        with self.lock, self._connect() as db:
            for table in ("skills", "episodes", "semantic_facts", "sensory_events", "working_memory"):
                db.execute(f"DELETE FROM {table}")
            for sid, skill in bank.get("procedural", {}).items():
                db.execute("INSERT INTO skills VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (sid, skill.get("name", sid), json.dumps(skill.get("steps", [])),
                            skill.get("confidence", .5), skill.get("perception", ""),
                            skill.get("created", ""), skill.get("updated", "")))
            for episode in bank.get("episodic", []):
                db.execute("INSERT INTO episodes(t, kind, detail) VALUES (?, ?, ?)",
                           (episode.get("t", ""), episode.get("kind", ""), episode.get("detail", "")))
            for key, fact in bank.get("semantic", {}).items():
                db.execute("INSERT INTO semantic_facts VALUES (?, ?, ?)",
                           (key, fact.get("value", ""), fact.get("t", "")))
            for item in reversed(bank.get("sensory", [])):
                db.execute("INSERT INTO sensory_events(t, kind, detail) VALUES (?, ?, ?)",
                           (item.get("t", ""), item.get("kind", ""), item.get("detail", "")))
            for key, value in bank.get("working", {}).items():
                db.execute("INSERT INTO working_memory VALUES (?, ?)", (key, str(value)))

    def bulk_upsert_skills(self, records):
        """Insert/update task procedures in one transaction for batch imports."""
        now = datetime.now().isoformat()
        rows = []
        for record in records:
            name = str(record.get("name", "")).strip()
            steps = [str(step).strip() for step in record.get("steps", []) if str(step).strip()]
            if not name or not steps:
                continue
            skill_id = "_".join(name.lower().split())
            rows.append((skill_id, name, json.dumps(steps), float(record.get("confidence", 0.5)),
                         str(record.get("perception", "")), now, now))
        if not rows:
            return 0
        with self.lock, self._connect() as db:
            db.executemany("""
                INSERT INTO skills(id, name, steps_json, confidence, perception, created, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name, steps_json=excluded.steps_json,
                    confidence=excluded.confidence, perception=excluded.perception,
                    updated=excluded.updated
            """, rows)
            for skill_id, name, steps_json, confidence, perception, _, _ in rows:
                version = db.execute(
                    "SELECT COALESCE(MAX(version), 0) + 1 FROM skill_versions WHERE skill_id = ?",
                    (skill_id,),
                ).fetchone()[0]
                db.execute(
                    "INSERT INTO skill_versions(skill_id, version, name, steps_json, confidence, perception, created) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (skill_id, version, name, steps_json, confidence, perception, now),
                )
        return len(rows)

    def list_skills(self, query=""):
        query = f"%{(query or '').strip()}%"
        with self.lock, self._connect() as db:
            rows = db.execute(
                "SELECT id, name, steps_json, confidence, perception, created, updated "
                "FROM skills WHERE name LIKE ? OR id LIKE ? ORDER BY updated DESC",
                (query, query),
            ).fetchall()
        return [{**dict(row), "steps": json.loads(row["steps_json"])} for row in rows]

    def update_skill(self, skill_id, name, steps):
        now = datetime.now().isoformat()
        with self.lock, self._connect() as db:
            current = db.execute("SELECT * FROM skills WHERE id = ?", (skill_id,)).fetchone()
            if current is None:
                return None
            db.execute(
                "UPDATE skills SET name = ?, steps_json = ?, updated = ? WHERE id = ?",
                (name, json.dumps(steps), now, skill_id),
            )
            version = db.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM skill_versions WHERE skill_id = ?",
                (skill_id,),
            ).fetchone()[0]
            db.execute(
                "INSERT INTO skill_versions(skill_id, version, name, steps_json, confidence, perception, created) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (skill_id, version, name, json.dumps(steps), current["confidence"], current["perception"] or "", now),
            )
        return self.get_skill(skill_id)

    def record_skill_version(self, skill_id, skill):
        now = skill.get("updated") or datetime.now().isoformat()
        with self.lock, self._connect() as db:
            version = db.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM skill_versions WHERE skill_id = ?",
                (skill_id,),
            ).fetchone()[0]
            db.execute(
                "INSERT INTO skill_versions(skill_id, version, name, steps_json, confidence, perception, created) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (skill_id, version, skill.get("name", skill_id), json.dumps(skill.get("steps", [])),
                 skill.get("confidence", 0.5), skill.get("perception", ""), now),
            )

    def get_skill(self, skill_id):
        with self.lock, self._connect() as db:
            row = db.execute("SELECT * FROM skills WHERE id = ?", (skill_id,)).fetchone()
        if row is None:
            return None
        return {**dict(row), "steps": json.loads(row["steps_json"])}

    def delete_skill(self, skill_id):
        with self.lock, self._connect() as db:
            deleted = db.execute("DELETE FROM skills WHERE id = ?", (skill_id,)).rowcount
            db.execute("DELETE FROM skill_versions WHERE skill_id = ?", (skill_id,))
            db.execute("DELETE FROM feedback_events WHERE skill_id = ?", (skill_id,))
        return bool(deleted)

    def skill_versions(self, skill_id, limit=20):
        with self.lock, self._connect() as db:
            rows = db.execute(
                "SELECT version, name, steps_json, confidence, created FROM skill_versions "
                "WHERE skill_id = ? ORDER BY version DESC LIMIT ?", (skill_id, limit),
            ).fetchall()
        return [{**dict(row), "steps": json.loads(row["steps_json"])} for row in rows]

    def record_feedback(self, skill_id, event, reward, detail):
        with self.lock, self._connect() as db:
            db.execute(
                "INSERT INTO feedback_events(skill_id, event, reward, detail, t) VALUES (?, ?, ?, ?, ?)",
                (skill_id, event, reward, detail, datetime.now().isoformat()),
            )

    def feedback_rows(self, limit=30):
        with self.lock, self._connect() as db:
            rows = db.execute(
                "SELECT t, event, skill_id, reward, detail FROM feedback_events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [[row["t"][11:19], row["event"], row["skill_id"] or "", row["reward"] or "--", row["detail"]] for row in rows]

    def knowledge_training_rows(self, limit=1000):
        with self.lock, self._connect() as db:
            rows = db.execute(
                "SELECT f.t, f.skill_id, f.event, f.reward, f.detail, s.name, s.steps_json "
                "FROM feedback_events f LEFT JOIN skills s ON s.id = f.skill_id "
                "WHERE f.skill_id IS NOT NULL AND s.id IS NOT NULL ORDER BY f.id LIMIT ?",
                (limit,),
            ).fetchall()
        return [{"timestamp": row["t"], "skill_id": row["skill_id"], "event": row["event"],
                 "reward": row["reward"], "detail": row["detail"], "name": row["name"],
                 "steps": json.loads(row["steps_json"])} for row in rows]

    def record_robot_episode(self, task, actions, reward, success):
        with self.lock, self._connect() as db:
            db.execute("INSERT INTO robot_episodes(t, task, actions_json, reward, success) VALUES (?, ?, ?, ?, ?)",
                       (datetime.now().isoformat(), task, json.dumps(actions), float(reward), int(bool(success))))

    def robot_episode_rows(self, limit=12):
        with self.lock, self._connect() as db:
            rows = db.execute("SELECT t, task, reward, success FROM robot_episodes ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [[r["t"][11:19], r["task"], f"{r['reward']:.2f}", "Success" if r["success"] else "Learning"] for r in rows]

    def robot_progress(self, limit=20):
        with self.lock, self._connect() as db:
            rows = db.execute("SELECT reward, success FROM robot_episodes ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        rows = list(reversed(rows))
        return [(float(row["reward"]), bool(row["success"])) for row in rows]

    def robot_training_rows(self, limit=1000):
        with self.lock, self._connect() as db:
            rows = db.execute("SELECT t, task, actions_json, reward, success FROM robot_episodes ORDER BY id LIMIT ?", (limit,)).fetchall()
        return [{"timestamp": row["t"], "task": row["task"], "actions": json.loads(row["actions_json"]), "reward": row["reward"], "success": bool(row["success"])} for row in rows]

    def clear_learning_data(self):
        """Remove learned records while retaining the database schema and app settings."""
        with self.lock, self._connect() as db:
            for table in ("skills", "episodes", "semantic_facts", "sensory_events", "working_memory",
                          "robot_episodes", "skill_versions", "feedback_events"):
                db.execute(f"DELETE FROM {table}")
            db.execute("DELETE FROM agent_feedback")
            db.execute("DELETE FROM agent_documents")
            db.execute("DELETE FROM agent_skills")
            db.execute("DELETE FROM agents")

    def create_agent(self, name, domain, instructions=""):
        now = datetime.now().isoformat()
        agent_id = "_".join(name.lower().split()) or f"agent_{int(datetime.now().timestamp())}"
        with self.lock, self._connect() as db:
            db.execute("""
                INSERT INTO agents(id, name, domain, instructions, created, updated)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name, domain=excluded.domain,
                    instructions=excluded.instructions, updated=excluded.updated
            """, (agent_id, name.strip(), domain.strip(), instructions.strip(), now, now))
        return self.get_agent(agent_id)

    def list_agents(self):
        with self.lock, self._connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM agents ORDER BY updated DESC")]

    def get_agent(self, agent_id):
        with self.lock, self._connect() as db:
            row = db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
        return dict(row) if row else None

    def add_agent_skill(self, agent_id, name, steps):
        now = datetime.now().isoformat()
        skill_id = "_".join(name.lower().split()) or f"task_{int(datetime.now().timestamp())}"
        with self.lock, self._connect() as db:
            db.execute("INSERT INTO agent_skills VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(agent_id, id) DO UPDATE SET name=excluded.name, steps_json=excluded.steps_json, updated=excluded.updated",
                       (skill_id, agent_id, name.strip(), json.dumps(steps), 0.5, now, now))
        return skill_id, self.get_agent_skill(agent_id, skill_id)

    def get_agent_skill(self, agent_id, skill_id):
        with self.lock, self._connect() as db:
            row = db.execute("SELECT * FROM agent_skills WHERE agent_id = ? AND id = ?", (agent_id, skill_id)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["steps"] = json.loads(result.pop("steps_json"))
        return result

    def update_agent_skill(self, agent_id, skill_id, name, steps):
        now = datetime.now().isoformat()
        with self.lock, self._connect() as db:
            updated = db.execute(
                "UPDATE agent_skills SET name = ?, steps_json = ?, updated = ? WHERE agent_id = ? AND id = ?",
                (name.strip(), json.dumps(steps), now, agent_id, skill_id),
            ).rowcount
        return self.get_agent_skill(agent_id, skill_id) if updated else None

    def delete_agent_skill(self, agent_id, skill_id):
        with self.lock, self._connect() as db:
            deleted = db.execute(
                "DELETE FROM agent_skills WHERE agent_id = ? AND id = ?",
                (agent_id, skill_id),
            ).rowcount
            db.execute(
                "DELETE FROM agent_feedback WHERE agent_id = ? AND skill_id = ?",
                (agent_id, skill_id),
            )
        return bool(deleted)

    def find_agent_skill(self, agent_id, query):
        tokens = set(re.findall(r"\w+", (query or "").lower()))
        with self.lock, self._connect() as db:
            rows = db.execute("SELECT * FROM agent_skills WHERE agent_id = ?", (agent_id,)).fetchall()
        best = None
        score = 0
        for row in rows:
            name_tokens = set(re.findall(r"\w+", row["name"].lower()))
            value = len(tokens & name_tokens)
            if value > score:
                best = self.get_agent_skill(agent_id, row["id"])
                score = value
        return best

    def list_agent_skills(self, agent_id):
        with self.lock, self._connect() as db:
            rows = db.execute(
                "SELECT * FROM agent_skills WHERE agent_id = ? ORDER BY updated DESC",
                (agent_id,),
            ).fetchall()
        return [{**dict(row), "steps": json.loads(row["steps_json"])} for row in rows]

    def agent_summary(self, agent_id):
        agent = self.get_agent(agent_id)
        if not agent:
            return "No selected agent is active."
        lines = [
            f"[AGENT] {agent['name']}",
            f"[DOMAIN] {agent['domain']}",
        ]
        if agent.get("instructions"):
            lines.append(f"[RULES] {agent['instructions']}")
        skills = self.list_agent_skills(agent_id)
        if skills:
            for skill in skills:
                lines.append(f"[SKILL {skill['id'].upper()}] {skill.get('name', skill['id'])}: " + " -> ".join(skill.get("steps", [])))
        else:
            lines.append("No taught procedures yet.")
        documents = self.list_agent_documents(agent_id)
        if documents:
            for document in documents:
                preview = " ".join(document.get("content", "").split())[:1000]
                lines.append(f"[DOCUMENT {document['id'].upper()}] {document['name']}: {preview}")
        else:
            lines.append("No uploaded documents yet.")
        return "\n".join(lines)

    def agent_knowledge_training_rows(self, agent_id, limit=1000):
        with self.lock, self._connect() as db:
            rows = db.execute(
                "SELECT f.t, f.agent_id, f.skill_id, f.event, f.reward, f.detail, s.name, s.steps_json "
                "FROM agent_feedback f LEFT JOIN agent_skills s "
                "ON s.agent_id = f.agent_id AND s.id = f.skill_id "
                "WHERE f.agent_id = ? AND f.skill_id IS NOT NULL AND s.id IS NOT NULL "
                "ORDER BY f.id LIMIT ?",
                (agent_id, limit),
            ).fetchall()
        return [{"timestamp": row["t"], "agent_id": row["agent_id"], "skill_id": row["skill_id"],
                 "event": row["event"], "reward": row["reward"], "detail": row["detail"],
                 "name": row["name"], "steps": json.loads(row["steps_json"])} for row in rows]

    def add_agent_document(self, agent_id, name, content):
        now = datetime.now().isoformat()
        doc_id = "_".join(re.findall(r"\w+", name.lower())) or f"document_{int(datetime.now().timestamp())}"
        with self.lock, self._connect() as db:
            db.execute(
                "INSERT INTO agent_documents VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(agent_id, id) DO UPDATE SET name=excluded.name, content=excluded.content, created=excluded.created",
                (doc_id, agent_id, name.strip(), content.strip(), now),
            )
        return self.get_agent_document(agent_id, doc_id)

    def get_agent_document(self, agent_id, doc_id):
        with self.lock, self._connect() as db:
            row = db.execute(
                "SELECT * FROM agent_documents WHERE agent_id = ? AND id = ?",
                (agent_id, doc_id),
            ).fetchone()
        return dict(row) if row else None

    def list_agent_documents(self, agent_id):
        with self.lock, self._connect() as db:
            rows = db.execute(
                "SELECT * FROM agent_documents WHERE agent_id = ? ORDER BY created DESC",
                (agent_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def find_agent_document(self, agent_id, query):
        tokens = set(t for t in (query or "").lower().split() if len(t) > 2)
        if not tokens:
            return None
        best = None
        best_score = 0
        for doc in self.list_agent_documents(agent_id):
            searchable = f"{doc['name']} {doc['content']}".lower()
            score = sum(1 for t in tokens if t in searchable)
            if score > best_score:
                best = doc
                best_score = score
        return best if best_score else None

    def agent_feedback(self, agent_id, skill_id, event, reward, detail):
        with self.lock, self._connect() as db:
            db.execute("INSERT INTO agent_feedback(agent_id, skill_id, event, reward, detail, t) VALUES (?, ?, ?, ?, ?, ?)",
                       (agent_id, skill_id, event, reward, detail, datetime.now().isoformat()))

    def delete_agent_document(self, agent_id, doc_id):
        with self.lock, self._connect() as db:
            deleted = db.execute(
                "DELETE FROM agent_documents WHERE agent_id = ? AND id = ?",
                (agent_id, doc_id),
            ).rowcount
        return bool(deleted)

    def delete_agent(self, agent_id):
        with self.lock, self._connect() as db:
            db.execute("DELETE FROM agent_feedback WHERE agent_id = ?", (agent_id,))
            db.execute("DELETE FROM agent_documents WHERE agent_id = ?", (agent_id,))
            db.execute("DELETE FROM agent_skills WHERE agent_id = ?", (agent_id,))
            deleted = db.execute("DELETE FROM agents WHERE id = ?", (agent_id,)).rowcount
        return bool(deleted)

    def clear_agent_knowledge(self, agent_id):
        with self.lock, self._connect() as db:
            if agent_id:
                db.execute("DELETE FROM agent_skills WHERE agent_id = ?", (agent_id,))
                db.execute("DELETE FROM agent_documents WHERE agent_id = ?", (agent_id,))
                db.execute("DELETE FROM agent_feedback WHERE agent_id = ?", (agent_id,))
            else:
                for table in ("skills", "episodes", "semantic_facts", "sensory_events", "working_memory", "skill_versions", "feedback_events"):
                    db.execute(f"DELETE FROM {table}")

    def agent_stats(self, agent_id):
        with self.lock, self._connect() as db:
            skills = db.execute("SELECT COUNT(*) FROM agent_skills WHERE agent_id = ?", (agent_id,)).fetchone()[0]
            events = db.execute("SELECT COUNT(*) FROM agent_feedback WHERE agent_id = ?", (agent_id,)).fetchone()[0]
            documents = db.execute("SELECT COUNT(*) FROM agent_documents WHERE agent_id = ?", (agent_id,)).fetchone()[0]
        return {"skills": skills, "events": events, "documents": documents}



def _create_store():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        try:
            from src.core.postgres_store import PostgresMemoryStore
            store = PostgresMemoryStore(database_url)
            print("[PRIMUS] Using PostgreSQL memory store")
            return store
        except Exception as exc:
            print(f"[PRIMUS] PostgreSQL unavailable ({exc}); using SQLite fallback")
    return MemoryStore()


STORE = _create_store()
