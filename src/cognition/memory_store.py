"""Separate salience-aware research memory store.

This additive store never rewrites or migrates the existing zPrimus memory DB.
"""

import json
import os
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager

from src.config import DATA_DIR


class CognitiveMemoryStore:
    def __init__(self, path=None):
        self.path = path or os.path.join(DATA_DIR, "cognitive_memory.sqlite3")
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        self._lock = threading.RLock()
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS cognitive_records (
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL,
                salience REAL NOT NULL, created REAL NOT NULL, accessed REAL NOT NULL,
                access_count INTEGER NOT NULL DEFAULT 0, consolidated_into TEXT
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_cog_salience ON cognitive_records(salience)")

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def add(self, kind, payload, salience=0.5):
        score = max(0.0, min(1.0, float(salience)))
        now = time.time()
        record_id = uuid.uuid4().hex
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO cognitive_records(id,kind,payload,salience,created,accessed) VALUES (?,?,?,?,?,?)",
                       (record_id, str(kind), json.dumps(payload, ensure_ascii=False), score, now, now))
        return record_id

    def query(self, kind=None, limit=50, min_salience=0.0, touch=True):
        limit = max(1, min(int(limit), 500))
        with self._lock, self._connect() as db:
            rows = db.execute("""SELECT * FROM cognitive_records
                WHERE consolidated_into IS NULL AND salience >= ?
                AND (? IS NULL OR kind = ?) ORDER BY salience DESC, accessed DESC LIMIT ?""",
                              (float(min_salience), kind, kind, limit)).fetchall()
            if touch and rows:
                db.executemany("UPDATE cognitive_records SET accessed=?, access_count=access_count+1 WHERE id=?",
                               [(time.time(), row["id"]) for row in rows])
        return [self._decode(row) for row in rows]

    @staticmethod
    def _decode(row):
        item = dict(row)
        item["payload"] = json.loads(item["payload"])
        return item

    def decay(self, half_life_seconds=30 * 86400, now=None):
        """Apply exponential decay based on time since last access; return count."""
        half_life = max(float(half_life_seconds), 1.0)
        now = float(now if now is not None else time.time())
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT id,salience,accessed FROM cognitive_records WHERE consolidated_into IS NULL").fetchall()
            updates = [(max(0.0, row["salience"] * 0.5 ** (max(0.0, now - row["accessed"]) / half_life)), row["id"])
                       for row in rows]
            db.executemany("UPDATE cognitive_records SET salience=? WHERE id=?", updates)
        return len(updates)

    def consolidate(self, older_than_seconds=7 * 86400, now=None):
        """Link older exact duplicate memories, keeping the strongest record."""
        cutoff = float(now if now is not None else time.time()) - max(0.0, float(older_than_seconds))
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT * FROM cognitive_records WHERE created <= ? AND consolidated_into IS NULL ORDER BY salience DESC, created ASC", (cutoff,)).fetchall()
            keep, merged = {}, 0
            for row in rows:
                key = (row["kind"], row["payload"])
                if key in keep:
                    db.execute("UPDATE cognitive_records SET consolidated_into=? WHERE id=?", (keep[key], row["id"]))
                    merged += 1
                else:
                    keep[key] = row["id"]
        return merged

    def forget(self, record_id):
        with self._lock, self._connect() as db:
            cur = db.execute("DELETE FROM cognitive_records WHERE id=? OR consolidated_into=?", (record_id, record_id))
        return cur.rowcount > 0

    def clear(self):
        with self._lock, self._connect() as db:
            cur = db.execute("DELETE FROM cognitive_records")
        return cur.rowcount


STORE = CognitiveMemoryStore()
