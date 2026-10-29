"""A bounded, non-hardware tabletop sandbox.

This simulator is intentionally lightweight: it records symbolic actions and
does not model robot dynamics or connect to actuators.
"""

import html
import math

from src.core.storage import STORE


class TabletopRobot:
    """Simple end-effector point model for deterministic sandbox episodes."""

    BOUNDS = ((-0.35, 0.35), (-0.30, 0.30), (0.0, 0.45))

    def __init__(self):
        self.ee = [0.0, 0.0, 0.12]
        self.actions = []

    def move(self, dx, dy, dz):
        values = [float(dx), float(dy), float(dz)]
        proposed = [self.ee[i] + values[i] for i in range(3)]
        self.ee = [max(lo, min(hi, proposed[i]))
                   for i, (lo, hi) in enumerate(self.BOUNDS)]
        self.actions.append({"action": "move", "delta": values, "position": list(self.ee)})
        return list(self.ee)

    def status_html(self):
        x, y, z = self.ee
        return (
            '<div class="tabletop-sandbox"><svg viewBox="0 0 320 200" '
            'role="img" aria-label="Tabletop robot sandbox">'
            '<rect x="20" y="145" width="280" height="18" rx="4" fill="#475569"/>'
            '<text x="24" y="185" fill="#cbd5e1">tabletop</text>'
            f'<circle cx="{160 + x * 240:.1f}" cy="{130 - z * 180:.1f}" '
            'r="10" fill="#38bdf8"/>'
            f'<text x="20" y="22" fill="#cbd5e1">EE: '
            f'{html.escape(f"{x:.2f}, {y:.2f}, {z:.2f}")}</text>'
            '</svg></div>'
        )

    def autonomous_demo(self):
        self.move(0.05, 0.05, 0.02)
        self.actions.append({"action": "grip", "position": list(self.ee)})
        return self.status_html()

    def run_guided_episode(self, source, target, task_name="pick_and_place"):
        """Record a simple simulated trajectory for offline evaluation."""
        source = tuple(float(v) for v in source)
        target = tuple(float(v) for v in target)
        if len(source) != 3 or len(target) != 3:
            raise ValueError("source and target must each contain three coordinates")

        episode_actions = []
        for action, point in (("approach", source), ("grasp", source),
                              ("transport", target), ("release", target)):
            episode_actions.append({"action": action, "position": list(point)})
        distance = math.dist(source, target)
        reward = max(0.0, 1.0 - min(distance, 1.0) * 0.1)
        STORE.record_robot_episode(task_name, episode_actions, reward, True)
        self.actions.extend(episode_actions)
        return {"task": task_name, "actions": episode_actions,
                "reward": reward, "success": True}
