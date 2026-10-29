"""Lazy MuJoCo G1 simulation wrapper. This is simulation only, not hardware control."""

from pathlib import Path
import math


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = PROJECT_ROOT / "sim" / "g1" / "scene.xml"


class G1Simulation:
    def __init__(self, model_path=DEFAULT_MODEL):
        try:
            import mujoco
        except ImportError as exc:
            raise RuntimeError("Install the optional MuJoCo dependency to use G1 simulation") from exc
        self.mujoco = mujoco
        self.model_path = Path(model_path).resolve()
        if not self.model_path.is_file():
            raise FileNotFoundError(f"MuJoCo model not found: {self.model_path}")
        self.model = mujoco.MjModel.from_xml_path(str(self.model_path))
        self.data = mujoco.MjData(self.model)
        self.reset()

    def reset(self, keyframe="stand"):
        mujoco = self.mujoco
        mujoco.mj_resetData(self.model, self.data)
        if keyframe:
            key_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_KEY, str(keyframe))
            if key_id < 0:
                raise ValueError(f"Unknown G1 keyframe: {keyframe}")
            mujoco.mj_resetDataKeyframe(self.model, self.data, key_id)
        mujoco.mj_forward(self.model, self.data)
        return self.snapshot()

    def step(self, controls=None, frames=1):
        count = max(1, min(int(frames), 10_000))
        if controls is not None:
            values = [float(v) for v in controls]
            if len(values) != self.model.nu:
                raise ValueError(f"expected {self.model.nu} actuator targets, got {len(values)}")
            for i, value in enumerate(values):
                if not math.isfinite(value):
                    raise ValueError("actuator targets must be finite")
                if self.model.actuator_ctrllimited[i]:
                    low, high = self.model.actuator_ctrlrange[i]
                    value = max(float(low), min(float(high), value))
                self.data.ctrl[i] = value
        for _ in range(count):
            self.mujoco.mj_step(self.model, self.data)
        return self.snapshot()

    def snapshot(self):
        return {
            "time": float(self.data.time),
            "qpos": self.data.qpos.copy().tolist(),
            "qvel": self.data.qvel.copy().tolist(),
            "actuator_count": int(self.model.nu),
            "simulation_only": True,
        }

    def render(self, width=640, height=480, camera="track"):
        """Render one RGB frame; graphics backend is loaded only on demand."""
        renderer = self.mujoco.Renderer(self.model, height=int(height), width=int(width))
        try:
            renderer.update_scene(self.data, camera=camera)
            return renderer.render().copy()
        finally:
            renderer.close()


def mjx_available():
    """Check optional MJX dependencies without importing them at app startup."""
    try:
        import jax  # noqa: F401
        from mujoco import mjx  # noqa: F401
    except ImportError:
        return False
    return True
