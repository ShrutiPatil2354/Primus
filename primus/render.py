import mujoco
import numpy as np
from primus.scene_builder import load_model


class Sim:
    TASKS = {
        'stand': [({}, 45)],
        'raise_arms': [
            ({'left_shoulder_roll_joint': 0.85, 'right_shoulder_roll_joint': -0.85}, 75),
            ({}, 75),
        ],
        'reach': [
            ({'right_shoulder_pitch_joint': -0.75, 'right_elbow_joint': 0.55}, 75),
            ({}, 75),
        ],
        'wave': [
            ({'right_shoulder_roll_joint': -0.9, 'right_elbow_joint': 0.55}, 65),
            ({'right_shoulder_roll_joint': -0.9, 'right_elbow_joint': 0.55,
              'right_wrist_roll_joint': 0.45}, 20),
            ({'right_shoulder_roll_joint': -0.9, 'right_elbow_joint': 0.55,
              'right_wrist_roll_joint': -0.45}, 20),
            ({'right_shoulder_roll_joint': -0.9, 'right_elbow_joint': 0.55,
              'right_wrist_roll_joint': 0.45}, 20),
            ({}, 65),
        ],
    }

    def __init__(self, h=540, w=960):
        self.m = load_model()
        self.d = mujoco.MjData(self.m)
        self.r = mujoco.Renderer(self.m, h, w)
        self.cam = mujoco.MjvCamera()
        self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.cam.lookat = np.array([0.0, 0.6, 0.9])
        self.cam.distance = 3.5
        stand_id = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_KEY, 'stand')
        if stand_id >= 0:
            mujoco.mj_resetDataKeyframe(self.m, self.d, stand_id)
        mujoco.mj_forward(self.m, self.d)
        self._stand_ctrl = self.d.ctrl.copy()
        self._actuator_ids = {
            self.mujoco.mj_id2name(self.m, self.mujoco.mjtObj.mjOBJ_ACTUATOR, i): i
            for i in range(self.m.nu)
        }
        self._task_stages = []
        self._task_index = 0
        self._task_elapsed = 0
        self._task_start = None
        self._task_target = None

    def start_task(self, name):
        """Start a small, scripted arm-pose demo in simulation only."""
        if name not in self.TASKS:
            raise ValueError(f'Unknown G1 simulation demo: {name}')
        self._task_stages = list(self.TASKS[name])
        self._task_index = 0
        self._begin_task_stage()

    def _begin_task_stage(self):
        if self._task_index >= len(self._task_stages):
            self._task_stages = []
            return
        pose, _frames = self._task_stages[self._task_index]
        self._task_start = self.d.ctrl.copy()
        self._task_target = self._stand_ctrl.copy()
        for joint_name, value in pose.items():
            actuator_id = self._actuator_ids.get(joint_name)
            if actuator_id is None:
                raise ValueError(f'MuJoCo model has no actuator for {joint_name}')
            self._task_target[actuator_id] = value
        self._task_elapsed = 0

    def advance_task(self):
        """Advance one smooth pose-control frame; call from the sim thread."""
        if not self._task_stages:
            return
        _pose, frames = self._task_stages[self._task_index]
        self._task_elapsed += 1
        fraction = min(1.0, self._task_elapsed / max(1, frames))
        eased = fraction * fraction * (3.0 - 2.0 * fraction)
        self.d.ctrl[:] = self._task_start + (self._task_target - self._task_start) * eased
        if fraction >= 1.0:
            self._task_index += 1
            self._begin_task_stage()

    def named(self, name):
        self.r.update_scene(self.d, name)
        return self.r.render()[..., ::-1]

    def orbit(self, azimuth, elevation, distance):
        self.cam.azimuth, self.cam.elevation, self.cam.distance = azimuth, elevation, distance
        self.r.update_scene(self.d, self.cam)
        return self.r.render()[..., ::-1]

    def close(self):
        self.r.close()
