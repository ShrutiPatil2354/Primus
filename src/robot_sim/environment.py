"""A deterministic 3D tabletop learning sandbox.

This is intentionally a safe simulator, not a hardware controller.  Its API
matches the action/reward/episode loop needed before swapping in MuJoCo or a
physical robot.
"""
import math

import mujoco

from src.core.storage import STORE


class TabletopRobot:
    task_name = "pick and place cube"

    @property
    def task_id(self):
        return "_".join(self.task_name.lower().split())

    def __init__(self):
        self.model = mujoco.MjModel.from_xml_string('''<mujoco model="primus_cartesian_robot">
          <option gravity="0 0 -9.81" timestep="0.002"/>
          <worldbody><geom type="plane" size="1 1 .1" rgba=".08 .14 .24 1"/>
            <body name="gantry_x" pos="0 0 .28"><joint name="x" type="slide" axis="1 0 0" range="-.42 .42"/><geom type="sphere" size=".006" mass=".01"/>
              <body name="gantry_y"><joint name="y" type="slide" axis="0 1 0" range="-.42 .42"/><geom type="sphere" size=".006" mass=".01"/>
                <body name="gantry_z"><joint name="z" type="slide" axis="0 0 1" range="-.25 .12"/>
                  <geom type="cylinder" size=".025 .06" rgba=".35 .65 1 1"/><site name="gripper" size=".025" rgba=".2 .7 1 1"/></body>
              </body></body>
            <body name="cube" pos=".18 .10 .03"><freejoint/><geom type="box" size=".025 .025 .025" mass=".05" rgba="1 .55 .05 1"/></body>
            <site name="target" pos="-.22 .18 .03" size=".04" rgba=".1 1 .3 .35" type="sphere"/>
          </worldbody></mujoco>''')
        self.data = mujoco.MjData(self.model)
        self.reset()

    def reset(self):
        self.ee = [0.0, -0.32, 0.26]
        self.cube = [0.18, 0.10, 0.03]
        self.target = [-0.22, 0.18, 0.03]
        self.grasped = False
        self.actions = []
        self.reward = 0.0
        self.done = False
        self._sync_physics()
        return self.status_html()

    def _sync_physics(self):
        """Keep the UI action state and the MuJoCo scene in lockstep."""
        self.data.qpos[:3] = [self.ee[0], self.ee[1], self.ee[2] - .28]
        self.data.qpos[3:6] = self.cube
        self.data.qpos[6:10] = [1, 0, 0, 0]
        mujoco.mj_forward(self.model, self.data)

    def _state(self):
        return {
            "ee": list(self.ee),
            "cube": list(self.cube),
            "target": list(self.target),
            "grasped": self.grasped,
        }

    def _record_action(self, action, before):
        self.actions.append({
            **action,
            "state_before": before,
            "state_after": self._state(),
            "reward": self.reward,
        })

    @staticmethod
    def _distance(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def move(self, dx=0.0, dy=0.0, dz=0.0):
        if self.done:
            # A completed episode should not make the controls appear broken.
            # Manual interaction begins a fresh exploration episode.
            self.reset()
        limits = ((-0.42, 0.42), (-0.42, 0.42), (0.03, 0.40))
        before = self._state()
        delta = (dx, dy, dz)
        self.ee = [max(lo, min(hi, value + change)) for value, change, (lo, hi) in zip(self.ee, delta, limits)]
        if self.grasped:
            self.cube = [self.ee[0], self.ee[1], max(0.03, self.ee[2] - 0.06)]
        self._sync_physics()
        self._shape_reward()
        self._record_action({"action": "move", "delta": delta}, before)
        return self.status_html()

    def grip(self):
        if self.done:
            self.reset()
        before = self._state()
        if not self.done and self._distance(self.ee, self.cube) < 0.11:
            self.grasped = True
            self.reward += 0.2
            result = "grasped"
        else:
            self.reward -= 0.03
            result = "missed"
        self._record_action({"action": "grip", "result": result}, before)
        return self.status_html()

    def release(self):
        if self.done:
            self.reset()
        before = self._state()
        if self.grasped:
            self.grasped = False
            if self._distance(self.cube, self.target) < 0.10:
                self.reward = 1.0
                self.done = True
                successful = True
            else:
                self.reward -= 0.05
                successful = False
            self._record_action({"action": "release"}, before)
            if successful:
                STORE.record_robot_episode(self.task_name, self.actions, self.reward, True)
        return self.status_html()

    def _shape_reward(self):
        goal = self.target if self.grasped else self.cube
        self.reward = max(-1.0, self.reward - 0.005 - self._distance(self.ee, goal) * 0.01)

    def autonomous_demo(self):
        """Run a deterministic guided episode through the public action API."""
        return self.run_guided_episode(self.cube, self.target, self.task_name)

    def run_guided_episode(self, cube, target, task_name):
        """Collect one labelled trajectory without teleporting state."""
        self.task_name = task_name
        self.reset()
        self.cube = list(cube)
        self.target = list(target)
        self._sync_physics()
        self.move(dx=self.cube[0] - self.ee[0], dy=self.cube[1] - self.ee[1], dz=self.cube[2] + 0.06 - self.ee[2])
        self.grip()
        self.move(dx=self.target[0] - self.ee[0], dy=self.target[1] - self.ee[1])
        self.release()
        return self.status_html()

    def status_html(self):
        project = lambda p: (50 + p[0] * 88 + p[1] * 24, 145 - p[1] * 42 - p[2] * 105)
        ex, ey = project(self.ee)
        cx, cy = project(self.cube)
        tx, ty = project(self.target)
        state = "Complete - next action starts a new episode" if self.done else ("Holding cube - move to green target" if self.grasped else "Exploring - move blue arm to orange cube")
        return f'''<div class="robot-lab"><div class="robot-status"><b>3D tabletop sandbox</b><span>{state} · reward {self.reward:.2f}</span></div>
        <svg viewBox="0 0 200 170" role="img" aria-label="Robot tabletop simulation">
          <polygon points="20,120 100,82 184,120 102,160" fill="#152a48" stroke="#3b82f6"/>
          <circle cx="{tx:.0f}" cy="{ty:.0f}" r="12" fill="none" stroke="#22c55e" stroke-width="3"/>
          <rect x="{cx-7:.0f}" y="{cy-7:.0f}" width="14" height="14" rx="2" fill="#f59e0b"/>
          <line x1="100" y1="30" x2="{ex:.0f}" y2="{ey:.0f}" stroke="#93c5fd" stroke-width="7" stroke-linecap="round"/>
          <circle cx="{ex:.0f}" cy="{ey:.0f}" r="8" fill="#60a5fa"/>
        </svg><p>Blue: end effector · Orange: cube · Green: target</p></div>'''


ROBOT = TabletopRobot()
