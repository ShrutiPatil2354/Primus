"""Checkpoint compatibility check for the optional ASTRA/CEM path."""

import importlib.util
import tempfile
from pathlib import Path
import unittest


@unittest.skipUnless(importlib.util.find_spec("torch"), "PyTorch is optional")
class TestWorldModelPlanner(unittest.TestCase):
    def test_loads_astra_state_dict_and_returns_bounded_action(self):
        import torch
        from cloud.train_astra import ASTRA
        from cloud.wm_planner import WMPlanner

        model = ASTRA(absolute_dim=3, action_dim=2, observation_dim=4, latent_dim=5)
        checkpoint = {
            "format_version": 1,
            "architecture": "ASTRA",
            "absolute_dim": 3,
            "action_dim": 2,
            "observation_dim": 4,
            "latent_dim": 5,
            "model_state_dict": model.state_dict(),
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint_path = Path(temp_dir) / "astra.pt"
            torch.save(checkpoint, checkpoint_path)
            planner = WMPlanner(checkpoint_path, act_dim=2, H=3, K=4, iterations=1, elites=2)
            action, elapsed_ms = planner.plan(torch.zeros(5), torch.zeros(2))
        self.assertEqual(tuple(action.shape), (2,))
        self.assertTrue(bool(torch.all(action.abs() <= 1.0)))
        self.assertGreaterEqual(elapsed_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
