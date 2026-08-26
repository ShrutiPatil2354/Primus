"""Export simulator episodes as stable training records."""
import json
from pathlib import Path

from src.core.storage import STORE


def export_jsonl(path, limit=1000):
    """Write state-action-reward records for offline evaluation and training."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = STORE.robot_training_rows(limit)
    with destination.open("w", encoding="utf-8") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=True) + "\n")
    return len(rows)
