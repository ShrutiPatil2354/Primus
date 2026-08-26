"""Generate diverse simulator tasks for cold-start meta-RL evaluation."""
from src.robot_sim.environment import TabletopRobot


TASKS = [
    ("pick_and_place_left", (0.18, 0.10, 0.03), (-0.22, 0.18, 0.03)),
    ("pick_and_place_right", (-0.20, -0.12, 0.03), (0.24, 0.18, 0.03)),
    ("pick_and_place_front", (0.08, -0.22, 0.03), (-0.18, 0.24, 0.03)),
]


def collect(episodes_per_task=4):
    robot = TabletopRobot()
    for task_name, cube, target in TASKS:
        for _ in range(episodes_per_task):
            robot.run_guided_episode(cube, target, task_name)
    return len(TASKS) * episodes_per_task


if __name__ == "__main__":
    print(f"Collected {collect()} curriculum episodes")