"""Small headless checks for the optional G1 MuJoCo model."""

import importlib.util
import unittest

from src.simulation.mujoco_g1 import G1Simulation


@unittest.skipUnless(importlib.util.find_spec("mujoco"), "MuJoCo is optional")
class TestG1Simulation(unittest.TestCase):
    def test_model_loads_and_steps_without_actuating_hardware(self):
        sim = G1Simulation()
        before = sim.snapshot()
        after = sim.step(frames=2)
        self.assertEqual(before["actuator_count"], 29)
        self.assertTrue(after["simulation_only"])
        self.assertGreater(after["time"], before["time"])

    def test_control_shape_is_checked(self):
        sim = G1Simulation()
        with self.assertRaises(ValueError):
            sim.step(controls=[0.0])


if __name__ == "__main__":
    unittest.main()
