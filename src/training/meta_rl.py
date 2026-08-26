"""Zero-prior continual meta-RL for PRIMUS task knowledge.

The policy learns which knowledge response to prefer for a task context from
stored procedures and teacher feedback. It never consumes robot trajectories.
"""
import argparse
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import torch
from torch import nn

from src.core.storage import STORE

ACTIONS = {"teach": 0, "recall": 1, "perform": 2, "revise": 3, "unknown": 4}
EVENT_ACTIONS = {**ACTIONS, "learned": ACTIONS["teach"], "edit": ACTIONS["revise"]}
FEATURES = 32


class KnowledgePolicy(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(FEATURES, 64), nn.Tanh(), nn.Linear(64, len(ACTIONS)))

    def forward(self, context):
        return self.network(context)


def context_vector(row):
    text = f"{row['skill_id']} {row['name']} {' '.join(row['steps'])}"
    vector = [0.0] * FEATURES
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        vector[int.from_bytes(digest[:2], "big") % FEATURES] += 1.0
    scale = max(1.0, sum(vector))
    vector = [value / scale for value in vector]
    vector[0] = min(1.0, len(row["steps"]) / 20.0)
    return vector


def knowledge_tasks(limit=1000):
    tasks = defaultdict(list)
    for row in STORE.knowledge_training_rows(limit):
        if row["event"] not in EVENT_ACTIONS:
            continue
        tasks[row["skill_id"]].append((context_vector(row), EVENT_ACTIONS[row["event"]], float(row["reward"] if row["reward"] is not None else 0.0)))
    return dict(tasks)


def adapt(model, rows, steps=3, lr=0.02):
    learner = copy.deepcopy(model)
    optimizer = torch.optim.SGD(learner.parameters(), lr=lr)
    contexts, labels, rewards = zip(*rows)
    contexts = torch.tensor(contexts, dtype=torch.float32)
    labels = torch.tensor(labels, dtype=torch.long)
    weights = 1.0 + torch.clamp((torch.tensor(rewards) + 1.0) / 2.0, 0.0, 1.0)
    for _ in range(steps):
        loss = (nn.functional.cross_entropy(learner(contexts), labels, reduction="none") * weights).mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return learner


def train(epochs=25, checkpoint="data/knowledge_meta_policy.pt", resume=False):
    tasks = {key: rows for key, rows in knowledge_tasks().items() if len(rows) >= 2}
    if len(tasks) < 2:
        raise ValueError("Knowledge meta-RL needs at least two learned tasks with two feedback episodes each. Teach and use more tasks first.")
    model = KnowledgePolicy()
    start_epoch = 0
    path = Path(checkpoint)
    if resume and path.exists():
        saved = torch.load(path, map_location="cpu", weights_only=True)
        model.load_state_dict(saved["model"])
        start_epoch = int(saved.get("epoch", 0))
    history = []
    for epoch in range(start_epoch, start_epoch + epochs):
        accuracy = []
        base = copy.deepcopy(model.state_dict())
        for rows in tasks.values():
            split = max(1, len(rows) // 2)
            learner = adapt(model, rows[:split])
            contexts, labels, _ = zip(*rows[split:])
            predicted = learner(torch.tensor(contexts, dtype=torch.float32)).argmax(1)
            accuracy.append(float((predicted == torch.tensor(labels)).float().mean()))
            for name, parameter in model.named_parameters():
                parameter.data.add_(0.1 * (learner.state_dict()[name] - base[name]))
        history.append({"epoch": epoch + 1, "task_accuracy": sum(accuracy) / len(accuracy)})
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "epoch": start_epoch + epochs,
                "tasks": sorted(tasks), "zero_prior": not resume,
                "domain": "task_knowledge", "history": history}, path)
    return {"checkpoint": str(path), "tasks": sorted(tasks), "history": history}


def main():
    parser = argparse.ArgumentParser(description="Train PRIMUS zero-prior continual meta-RL over task knowledge")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--checkpoint", default="data/knowledge_meta_policy.pt")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    result = train(args.epochs, args.checkpoint, args.resume)
    print(json.dumps({"checkpoint": result["checkpoint"], "domain": "task_knowledge", "tasks": result["tasks"], "final": result["history"][-1]}, indent=2))


if __name__ == "__main__":
    main()
