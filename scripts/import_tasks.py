"""Bulk-import PRIMUS task procedures from JSONL or a JSON array.

Example:
  python scripts/import_tasks.py data/tasks.jsonl

Each record requires a name and ordered steps:
  {"name":"make coffee","steps":["take a cup","add coffee","pour hot water"]}
"""
import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.storage import STORE  # noqa: E402


def read_records(path):
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("A .json import file must contain an array of task records.")
        return data
    records = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_no}: {exc.msg}") from exc
    return records


def main():
    parser = argparse.ArgumentParser(description="Bulk-import PRIMUS tasks.")
    parser.add_argument("file", type=Path, help=".jsonl or .json task file")
    args = parser.parse_args()
    if not args.file.is_file():
        parser.error(f"File not found: {args.file}")
    records = read_records(args.file)
    imported = STORE.bulk_upsert_skills(records)
    print(f"Imported or updated {imported} task procedures into {STORE.path}")


if __name__ == "__main__":
    main()
