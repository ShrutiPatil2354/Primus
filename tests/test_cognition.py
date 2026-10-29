"""Deterministic checks for opt-in cognition helpers."""

import os
import tempfile
import time
import unittest

from src.cognition.memory_store import CognitiveMemoryStore
from src.cognition.replay_daemon import ReplayDaemon
from src.cognition.spatial import SpatialMemory, potential_field_hint
from src.cognition.metacognition import WorkingMemory, prediction_error
from src.cognition.social import acoustic_summary
from src.cognition.proactive import suggest_next_step


class TestCognitiveMemoryStore(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CognitiveMemoryStore(os.path.join(self.temp.name, "memory.sqlite3"))

    def tearDown(self):
        self.temp.cleanup()

    def test_salience_decay_consolidation_and_forgetting(self):
        now = time.time()
        original = self.store.add("note", {"text": "remember"}, salience=0.8)
        duplicate = self.store.add("note", {"text": "remember"}, salience=0.4)
        self.assertEqual(len(self.store.query("note")), 2)
        self.store.decay(half_life_seconds=10, now=now + 10)
        salience = self.store.query("note")[0]["salience"]
        self.assertGreater(salience, 0.39)
        self.assertLess(salience, 0.41)
        self.assertEqual(self.store.consolidate(older_than_seconds=0, now=now + 11), 1)
        self.assertEqual(len(self.store.query("note")), 1)
        self.assertTrue(self.store.forget(original))
        self.assertEqual(self.store.query("note"), [])

    def test_replay_daemon_is_explicit_and_stoppable(self):
        daemon = ReplayDaemon(self.store, idle_seconds=1, interval_seconds=1)
        self.assertTrue(daemon.start())
        self.assertTrue(daemon.stop())


class TestAdvisoryCognition(unittest.TestCase):
    def test_helpers_are_bounded_and_explicit(self):
        memory = SpatialMemory()
        memory.observe("cup", (0.2, 0.1, 0.0))
        self.assertEqual(memory.get("cup")["xyz"], (0.2, 0.1, 0.0))
        hint = potential_field_hint((0, 0, 0), (1, 0, 0), max_speed=2.0)
        self.assertLessEqual(sum(v * v for v in hint["velocity_hint"]) ** 0.5, 0.150001)
        self.assertTrue(hint["advisory_only"])
        working = WorkingMemory(capacity=2)
        for item in (1, 2, 3):
            working.add(item)
        self.assertEqual(working.snapshot(), [2, 3])
        self.assertAlmostEqual(prediction_error((1, 2), (2, 2)), 0.5)
        self.assertEqual(acoustic_summary([])["interpretation"], "signal_features_only")
        self.assertIsNone(suggest_next_step(10, uncertainty=0.1))


if __name__ == "__main__":
    unittest.main()
