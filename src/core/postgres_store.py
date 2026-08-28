"""PostgreSQL memory backend with pgvector-ready semantic retrieval."""
import json
import os
import re
from datetime import datetime


class PostgresMemoryStore:
    def __init__(self, url=None):
        global text
        from sqlalchemy import create_engine, text
        self._text = text
        self.url = url or os.environ["DATABASE_URL"]
        self.path = self.url
        self.engine = create_engine(self.url, pool_pre_ping=True, future=True)
        self._initialize()

    def _sql(self, statement):
        return self._text(statement)

    def _initialize(self):
        ddl = """
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, steps_json JSONB NOT NULL,
            confidence DOUBLE PRECISION NOT NULL, perception TEXT, created TEXT, updated TEXT
        );
        CREATE TABLE IF NOT EXISTS episodes (
            id BIGSERIAL PRIMARY KEY, t TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS semantic_facts (
            key TEXT PRIMARY KEY, value TEXT NOT NULL, t TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sensory_events (
            id BIGSERIAL PRIMARY KEY, t TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS working_memory (
            key TEXT PRIMARY KEY, value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS robot_episodes (
            id BIGSERIAL PRIMARY KEY, t TEXT NOT NULL, task TEXT NOT NULL,
            actions_json JSONB NOT NULL, reward DOUBLE PRECISION NOT NULL, success BOOLEAN NOT NULL
        );
        CREATE TABLE IF NOT EXISTS skill_versions (
            id BIGSERIAL PRIMARY KEY, skill_id TEXT NOT NULL, version INTEGER NOT NULL,
            name TEXT NOT NULL, steps_json JSONB NOT NULL, confidence DOUBLE PRECISION NOT NULL,
            perception TEXT, created TEXT NOT NULL, UNIQUE(skill_id, version)
        );
        CREATE TABLE IF NOT EXISTS feedback_events (
            id BIGSERIAL PRIMARY KEY, skill_id TEXT, event TEXT NOT NULL,
            reward DOUBLE PRECISION, detail TEXT NOT NULL, t TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS semantic_documents (
            id BIGSERIAL PRIMARY KEY, source_type TEXT NOT NULL, source_id TEXT NOT NULL,
            content TEXT NOT NULL, embedding vector(384), created TEXT NOT NULL,
            UNIQUE(source_type, source_id)
        );
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, domain TEXT NOT NULL,
            instructions TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS agent_skills (
            id TEXT NOT NULL, agent_id TEXT NOT NULL, name TEXT NOT NULL,
            steps_json JSONB NOT NULL, confidence DOUBLE PRECISION NOT NULL,
            created TEXT NOT NULL, updated TEXT NOT NULL, PRIMARY KEY (agent_id, id)
        );
        CREATE TABLE IF NOT EXISTS agent_feedback (
            id BIGSERIAL PRIMARY KEY, agent_id TEXT NOT NULL, skill_id TEXT,
            event TEXT NOT NULL, reward DOUBLE PRECISION, detail TEXT NOT NULL, t TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS agent_documents (
            id TEXT NOT NULL, agent_id TEXT NOT NULL, name TEXT NOT NULL,
            content TEXT NOT NULL, created TEXT NOT NULL, PRIMARY KEY (agent_id, id)
        );
        """
        with self.engine.begin() as db:
            for statement in ddl.split(";"):
                if statement.strip():
                    db.execute(self._sql(statement))

    @staticmethod
    def _skill(row):
        if row is None:
            return None
        result = dict(row)
        result["steps"] = result.pop("steps_json")
        if isinstance(result["steps"], str):
            result["steps"] = json.loads(result["steps"])
        return result

    def snapshot(self):
        with self.engine.connect() as db:
            skills = {r["id"]: self._skill(r) for r in db.execute(text("SELECT * FROM skills")).mappings()}
            episodes = [dict(r) for r in db.execute(text("SELECT t, kind, detail FROM episodes ORDER BY id DESC LIMIT 200")).mappings()]
            semantic = {r["key"]: {"value": r["value"], "t": r["t"]} for r in db.execute(text("SELECT * FROM semantic_facts")).mappings()}
            sensory = [dict(r) for r in db.execute(text("SELECT t, kind, detail FROM sensory_events ORDER BY id DESC LIMIT 20")).mappings()]
            working = {r["key"]: r["value"] for r in db.execute(text("SELECT * FROM working_memory")).mappings()}
        return {"procedural": skills, "episodic": episodes, "semantic": semantic, "sensory": sensory, "working": working}

    def replace_snapshot(self, bank):
        with self.engine.begin() as db:
            for table in ("skills", "episodes", "semantic_facts", "sensory_events", "working_memory"):
                db.execute(text(f"DELETE FROM {table}"))
            for sid, skill in bank.get("procedural", {}).items():
                db.execute(text("INSERT INTO skills VALUES (:id, :name, :steps, :confidence, :perception, :created, :updated)"), {"id": sid, "name": skill.get("name", sid), "steps": skill.get("steps", []), "confidence": skill.get("confidence", .5), "perception": skill.get("perception", ""), "created": skill.get("created", ""), "updated": skill.get("updated", "")})
            for episode in bank.get("episodic", []):
                db.execute(text("INSERT INTO episodes(t, kind, detail) VALUES (:t, :kind, :detail)"), episode)
            for key, fact in bank.get("semantic", {}).items():
                db.execute(text("INSERT INTO semantic_facts VALUES (:key, :value, :t)"), {"key": key, "value": fact.get("value", ""), "t": fact.get("t", "")})
            for item in reversed(bank.get("sensory", [])):
                db.execute(text("INSERT INTO sensory_events(t, kind, detail) VALUES (:t, :kind, :detail)"), item)
            for key, value in bank.get("working", {}).items():
                db.execute(text("INSERT INTO working_memory VALUES (:key, :value) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value"), {"key": key, "value": str(value)})

    def list_skills(self, query=""):
        with self.engine.connect() as db:
            rows = db.execute(text("SELECT * FROM skills WHERE name ILIKE :query OR id ILIKE :query ORDER BY updated DESC"), {"query": f"%{query.strip()}%"}).mappings()
            return [self._skill(row) for row in rows]

    def bulk_upsert_skills(self, records):
        imported = 0
        for record in records:
            name = str(record.get("name", "")).strip()
            steps = [str(step).strip() for step in record.get("steps", []) if str(step).strip()]
            if not name or not steps:
                continue
            self.add_skill(name, steps, str(record.get("perception", "")))
            imported += 1
        return imported

    def get_skill(self, skill_id):
        with self.engine.connect() as db:
            return self._skill(db.execute(text("SELECT * FROM skills WHERE id = :id"), {"id": skill_id}).mappings().first())

    def update_skill(self, skill_id, name, steps):
        now = datetime.now().isoformat()
        with self.engine.begin() as db:
            current = db.execute(text("SELECT * FROM skills WHERE id = :id"), {"id": skill_id}).mappings().first()
            if current is None:
                return None
            db.execute(text("UPDATE skills SET name=:name, steps_json=:steps, updated=:updated WHERE id=:id"), {"id": skill_id, "name": name, "steps": steps, "updated": now})
            version = db.execute(text("SELECT COALESCE(MAX(version), 0) + 1 FROM skill_versions WHERE skill_id=:id"), {"id": skill_id}).scalar_one()
            db.execute(text("INSERT INTO skill_versions(skill_id, version, name, steps_json, confidence, perception, created) VALUES (:id,:version,:name,:steps,:confidence,:perception,:created)"), {"id": skill_id, "version": version, "name": name, "steps": steps, "confidence": current["confidence"], "perception": current["perception"] or "", "created": now})
        return self.get_skill(skill_id)

    def add_skill(self, name, steps, perception=""):
        sid = "_".join(name.lower().split()) or f"task_{int(datetime.now().timestamp())}"
        now = datetime.now().isoformat()
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO skills VALUES (:id,:name,:steps,:confidence,:perception,:created,:updated) ON CONFLICT (id) DO UPDATE SET steps_json=EXCLUDED.steps_json, updated=EXCLUDED.updated"), {"id": sid, "name": name, "steps": steps, "confidence": .5, "perception": perception, "created": now, "updated": now})
            db.execute(text("INSERT INTO skill_versions(skill_id, version, name, steps_json, confidence, perception, created) VALUES (:id, COALESCE((SELECT MAX(version)+1 FROM skill_versions WHERE skill_id=:id), 1), :name,:steps,.5,:perception,:created)"), {"id": sid, "name": name, "steps": steps, "perception": perception, "created": now})
        return sid, self.get_skill(sid)

    def delete_skill(self, skill_id):
        with self.engine.begin() as db:
            deleted = db.execute(text("DELETE FROM skills WHERE id=:id"), {"id": skill_id}).rowcount
            db.execute(text("DELETE FROM skill_versions WHERE skill_id=:id"), {"id": skill_id})
            db.execute(text("DELETE FROM feedback_events WHERE skill_id=:id"), {"id": skill_id})
        return bool(deleted)

    def skill_versions(self, skill_id, limit=20):
        with self.engine.connect() as db:
            return [dict(row) for row in db.execute(text("SELECT version,name,steps_json,confidence,created FROM skill_versions WHERE skill_id=:id ORDER BY version DESC LIMIT :limit"), {"id": skill_id, "limit": limit}).mappings()]

    def record_skill_version(self, skill_id, skill):
        self.add_skill(skill.get("name", skill_id), skill.get("steps", []), skill.get("perception", ""))

    def add_episode(self, kind, detail):
        now = datetime.now().isoformat()
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO episodes(t, kind, detail) VALUES (:t, :kind, :detail)"), {"t": now, "kind": str(kind), "detail": str(detail)})

    def add_sensory_event(self, kind, detail):
        now = datetime.now().isoformat()
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO sensory_events(t, kind, detail) VALUES (:t, :kind, :detail)"), {"t": now, "kind": str(kind), "detail": str(detail)})

    def set_semantic_fact(self, key, value):
        now = datetime.now().isoformat()
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO semantic_facts(key, value, t) VALUES (:key, :value, :t) ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value, t=EXCLUDED.t"), {"key": str(key), "value": str(value), "t": now})

    def set_working_memory(self, kv_dict):
        with self.engine.begin() as db:
            for k, v in kv_dict.items():
                db.execute(text("INSERT INTO working_memory(key, value) VALUES (:key, :value) ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value"), {"key": str(k), "value": str(v)})

    def update_confidence(self, skill_id, reward=1.0):
        now = datetime.now().isoformat()
        with self.engine.begin() as db:
            current = db.execute(text("SELECT confidence FROM skills WHERE id=:id"), {"id": skill_id}).mappings().first()
            if not current:
                return 0.5
            from src.core import engine
            old_conf = current["confidence"]
            new_conf = round(engine.update_confidence(old_conf, reward), 3)
            db.execute(text("UPDATE skills SET confidence=:confidence, updated=:updated WHERE id=:id"), {"id": skill_id, "confidence": new_conf, "updated": now})
            return new_conf

    def record_feedback(self, skill_id, event, reward, detail):
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO feedback_events(skill_id,event,reward,detail,t) VALUES (:skill_id,:event,:reward,:detail,:t)"), {"skill_id": skill_id, "event": event, "reward": reward, "detail": detail, "t": datetime.now().isoformat()})

    def feedback_rows(self, limit=30):
        with self.engine.connect() as db:
            return [[r["t"][11:19], r["event"], r["skill_id"] or "", r["reward"] if r["reward"] is not None else "--", r["detail"]] for r in db.execute(text("SELECT t,event,skill_id,reward,detail FROM feedback_events ORDER BY id DESC LIMIT :limit"), {"limit": limit}).mappings()]

    def knowledge_training_rows(self, limit=1000):
        with self.engine.connect() as db:
            rows = db.execute(text("SELECT f.t,f.skill_id,f.event,f.reward,f.detail,s.name,s.steps_json FROM feedback_events f JOIN skills s ON s.id=f.skill_id ORDER BY f.id LIMIT :limit"), {"limit": limit}).mappings()
        return [{"timestamp": row["t"], "skill_id": row["skill_id"], "event": row["event"], "reward": row["reward"], "detail": row["detail"], "name": row["name"], "steps": row["steps_json"]} for row in rows]

    def record_robot_episode(self, task, actions, reward, success):
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO robot_episodes(t,task,actions_json,reward,success) VALUES (:t,:task,:actions,:reward,:success)"), {"t": datetime.now().isoformat(), "task": task, "actions": actions, "reward": reward, "success": bool(success)})

    def robot_episode_rows(self, limit=12):
        with self.engine.connect() as db:
            return [[r["t"][11:19], r["task"], f"{r['reward']:.2f}", "Success" if r["success"] else "Learning"] for r in db.execute(text("SELECT t,task,reward,success FROM robot_episodes ORDER BY id DESC LIMIT :limit"), {"limit": limit}).mappings()]

    def robot_progress(self, limit=20):
        with self.engine.connect() as db:
            rows = list(db.execute(text("SELECT reward,success FROM robot_episodes ORDER BY id DESC LIMIT :limit"), {"limit": limit}).mappings())
        return [(float(row["reward"]), bool(row["success"])) for row in reversed(rows)]

    def robot_training_rows(self, limit=1000):
        with self.engine.connect() as db:
            rows = db.execute(text("SELECT t,task,actions_json,reward,success FROM robot_episodes ORDER BY id LIMIT :limit"), {"limit": limit}).mappings()
        return [{"timestamp": row["t"], "task": row["task"], "actions": row["actions_json"], "reward": row["reward"], "success": bool(row["success"])} for row in rows]

    def clear_learning_data(self):
        with self.engine.begin() as db:
            for table in ("skills", "episodes", "semantic_facts", "sensory_events", "working_memory", "robot_episodes", "skill_versions", "feedback_events", "semantic_documents"):
                db.execute(text(f"DELETE FROM {table}"))
            for table in ("agent_feedback", "agent_documents", "agent_skills", "agents"):
                db.execute(text(f"DELETE FROM {table}"))

    def create_agent(self, name, domain, instructions=""):
        now = datetime.now().isoformat()
        agent_id = "_".join(name.lower().split()) or f"agent_{int(datetime.now().timestamp())}"
        with self.engine.begin() as db:
            db.execute(text("""
                INSERT INTO agents(id, name, domain, instructions, created, updated)
                VALUES (:id, :name, :domain, :instructions, :created, :updated)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name, domain = EXCLUDED.domain,
                    instructions = EXCLUDED.instructions, updated = EXCLUDED.updated
            """), {"id": agent_id, "name": name.strip(), "domain": domain.strip(), "instructions": instructions.strip(), "created": now, "updated": now})
        return self.get_agent(agent_id)

    def list_agents(self):
        with self.engine.connect() as db:
            return [dict(row) for row in db.execute(text("SELECT * FROM agents ORDER BY updated DESC")).mappings()]

    def get_agent(self, agent_id):
        with self.engine.connect() as db:
            row = db.execute(text("SELECT * FROM agents WHERE id=:id"), {"id": agent_id}).mappings().first()
        return dict(row) if row else None

    def add_agent_skill(self, agent_id, name, steps):
        now = datetime.now().isoformat()
        skill_id = "_".join(name.lower().split()) or f"task_{int(datetime.now().timestamp())}"
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO agent_skills VALUES (:id,:agent_id,:name,:steps,.5,:created,:updated) ON CONFLICT (agent_id,id) DO UPDATE SET steps_json=EXCLUDED.steps_json, updated=EXCLUDED.updated"), {"id": skill_id, "agent_id": agent_id, "name": name.strip(), "steps": steps, "created": now, "updated": now})
        return skill_id, self.get_agent_skill(agent_id, skill_id)

    def get_agent_skill(self, agent_id, skill_id):
        with self.engine.connect() as db:
            row = db.execute(text("SELECT * FROM agent_skills WHERE agent_id=:agent_id AND id=:id"), {"agent_id": agent_id, "id": skill_id}).mappings().first()
        if not row:
            return None
        result = dict(row)
        result["steps"] = result.pop("steps_json")
        return result

    def update_agent_skill(self, agent_id, skill_id, name, steps):
        now = datetime.now().isoformat()
        with self.engine.begin() as db:
            updated = db.execute(text(
                "UPDATE agent_skills SET name=:name, steps_json=:steps, updated=:updated "
                "WHERE agent_id=:agent_id AND id=:id"
            ), {"agent_id": agent_id, "id": skill_id, "name": name.strip(), "steps": steps, "updated": now}).rowcount
        return self.get_agent_skill(agent_id, skill_id) if updated else None

    def delete_agent_skill(self, agent_id, skill_id):
        with self.engine.begin() as db:
            deleted = db.execute(text(
                "DELETE FROM agent_skills WHERE agent_id=:agent_id AND id=:id"
            ), {"agent_id": agent_id, "id": skill_id}).rowcount
            db.execute(text(
                "DELETE FROM agent_feedback WHERE agent_id=:agent_id AND skill_id=:id"
            ), {"agent_id": agent_id, "id": skill_id})
        return bool(deleted)

    def find_agent_skill(self, agent_id, query):
        tokens = set(re.findall(r"\w+", (query or "").lower()))
        with self.engine.connect() as db:
            rows = list(db.execute(text("SELECT id,name FROM agent_skills WHERE agent_id=:agent_id"), {"agent_id": agent_id}).mappings())
        matches = [(len(tokens & set(re.findall(r"\w+", row["name"].lower()))), row["id"]) for row in rows]
        matches.sort(reverse=True)
        return self.get_agent_skill(agent_id, matches[0][1]) if matches and matches[0][0] else None

    def list_agent_skills(self, agent_id):
        with self.engine.connect() as db:
            rows = db.execute(text("SELECT * FROM agent_skills WHERE agent_id=:agent_id ORDER BY updated DESC"), {"agent_id": agent_id}).mappings()
            return [self._skill(row) for row in rows]

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
        with self.engine.connect() as db:
            rows = db.execute(text(
                "SELECT f.t,f.agent_id,f.skill_id,f.event,f.reward,f.detail,s.name,s.steps_json "
                "FROM agent_feedback f JOIN agent_skills s "
                "ON s.agent_id=f.agent_id AND s.id=f.skill_id "
                "WHERE f.agent_id=:agent_id ORDER BY f.id LIMIT :limit"
            ), {"agent_id": agent_id, "limit": limit}).mappings()
        return [{"timestamp": row["t"], "agent_id": row["agent_id"], "skill_id": row["skill_id"],
                 "event": row["event"], "reward": row["reward"], "detail": row["detail"],
                 "name": row["name"], "steps": row["steps_json"]} for row in rows]

    def add_agent_document(self, agent_id, name, content):
        now = datetime.now().isoformat()
        doc_id = "_".join(re.findall(r"\w+", name.lower())) or f"document_{int(datetime.now().timestamp())}"
        with self.engine.begin() as db:
            db.execute(text(
                "INSERT INTO agent_documents VALUES (:id,:agent_id,:name,:content,:created) "
                "ON CONFLICT (agent_id,id) DO UPDATE SET name=EXCLUDED.name, content=EXCLUDED.content, created=EXCLUDED.created"
            ), {"id": doc_id, "agent_id": agent_id, "name": name.strip(), "content": content.strip(), "created": now})
        return self.get_agent_document(agent_id, doc_id)

    def get_agent_document(self, agent_id, doc_id):
        with self.engine.connect() as db:
            row = db.execute(text(
                "SELECT * FROM agent_documents WHERE agent_id=:agent_id AND id=:id"
            ), {"agent_id": agent_id, "id": doc_id}).mappings().first()
        return dict(row) if row else None

    def list_agent_documents(self, agent_id):
        with self.engine.connect() as db:
            rows = db.execute(text(
                "SELECT * FROM agent_documents WHERE agent_id=:agent_id ORDER BY created DESC"
            ), {"agent_id": agent_id}).mappings()
        return [dict(row) for row in rows]

    def find_agent_document(self, agent_id, query):
        tokens = set(re.findall(r"\w+", (query or "").lower()))
        if not tokens:
            return None
        best = None
        best_score = 0
        for doc in self.list_agent_documents(agent_id):
            searchable = f"{doc['name']} {doc['content'][:4000]}".lower()
            score = len(tokens & set(re.findall(r"\w+", searchable)))
            if score > best_score:
                best = doc
                best_score = score
        return best if best_score else None

    def agent_feedback(self, agent_id, skill_id, event, reward, detail):
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO agent_feedback(agent_id,skill_id,event,reward,detail,t) VALUES (:agent_id,:skill_id,:event,:reward,:detail,:t)"), {"agent_id": agent_id, "skill_id": skill_id, "event": event, "reward": reward, "detail": detail, "t": datetime.now().isoformat()})

    def delete_agent_document(self, agent_id, doc_id):
        with self.engine.begin() as db:
            deleted = db.execute(text(
                "DELETE FROM agent_documents WHERE agent_id = :agent_id AND id = :id"
            ), {"agent_id": agent_id, "id": doc_id}).rowcount
        return bool(deleted)

    def delete_agent(self, agent_id):
        with self.engine.begin() as db:
            db.execute(text("DELETE FROM agent_feedback WHERE agent_id = :id"), {"id": agent_id})
            db.execute(text("DELETE FROM agent_documents WHERE agent_id = :id"), {"id": agent_id})
            db.execute(text("DELETE FROM agent_skills WHERE agent_id = :id"), {"id": agent_id})
            deleted = db.execute(text("DELETE FROM agents WHERE id = :id"), {"id": agent_id}).rowcount
        return bool(deleted)

    def clear_agent_knowledge(self, agent_id):
        with self.engine.begin() as db:
            if agent_id:
                db.execute(text("DELETE FROM agent_skills WHERE agent_id = :id"), {"id": agent_id})
                db.execute(text("DELETE FROM agent_documents WHERE agent_id = :id"), {"id": agent_id})
                db.execute(text("DELETE FROM agent_feedback WHERE agent_id = :id"), {"id": agent_id})
            else:
                for table in ("skills", "episodes", "semantic_facts", "sensory_events", "working_memory", "skill_versions", "feedback_events"):
                    db.execute(text(f"DELETE FROM {table}"))

    def agent_stats(self, agent_id):
        with self.engine.connect() as db:
            skills = db.execute(text("SELECT COUNT(*) FROM agent_skills WHERE agent_id=:agent_id"), {"agent_id": agent_id}).scalar_one()
            events = db.execute(text("SELECT COUNT(*) FROM agent_feedback WHERE agent_id=:agent_id"), {"agent_id": agent_id}).scalar_one()
            documents = db.execute(text("SELECT COUNT(*) FROM agent_documents WHERE agent_id=:agent_id"), {"agent_id": agent_id}).scalar_one()
        return {"skills": skills, "events": events, "documents": documents}


    def upsert_embedding(self, source_type, source_id, content, embedding):
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO semantic_documents(source_type,source_id,content,embedding,created) VALUES (:source_type,:source_id,:content,CAST(:embedding AS vector),:created) ON CONFLICT (source_type,source_id) DO UPDATE SET content=EXCLUDED.content, embedding=EXCLUDED.embedding"), {"source_type": source_type, "source_id": source_id, "content": content, "embedding": "[" + ",".join(str(value) for value in embedding) + "]", "created": datetime.now().isoformat()})

    def search_embeddings(self, embedding, limit=5):
        with self.engine.connect() as db:
            vector = "[" + ",".join(str(value) for value in embedding) + "]"
            return [dict(row) for row in db.execute(text("SELECT source_type,source_id,content,1-(embedding <=> CAST(:embedding AS vector)) AS score FROM semantic_documents WHERE embedding IS NOT NULL ORDER BY embedding <=> CAST(:embedding AS vector) LIMIT :limit"), {"embedding": vector, "limit": limit}).mappings()]
