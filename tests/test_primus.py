"""Comprehensive unit test suite for PRIMUS cognitive architecture."""
import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.core import engine, intent, memory, executor, innate
from src.core.storage import MemoryStore, STORE
from src.robot_sim.environment import TabletopRobot
from src.metrics import monitor


class TestIntentClassification(unittest.TestCase):
    def test_teach_intent(self):
        cat = intent.classify("Learn make coffee: boil water; add coffee; pour into mug")
        self.assertEqual(cat, "teach")

    def test_task_query_intent(self):
        cat = intent.classify("How do I make coffee?")
        self.assertEqual(cat, "task_query")

    def test_conversation_intent(self):
        cat = intent.classify("Hello there, who are you?")
        self.assertEqual(cat, "conversation")

    def test_clean_task_name(self):
        name = intent.clean_task_name("How do I make a cup of coffee?")
        self.assertIn("coffee", name.lower())


class TestMemoryStoreAndPersistence(unittest.TestCase):
    def setUp(self):
        test_db = str(PROJECT_ROOT / "data" / "test_memory.db")
        self.store = MemoryStore(path=test_db)

    def tearDown(self):
        test_db = str(PROJECT_ROOT / "data" / "test_memory.db")
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except OSError:
                pass

    def test_add_and_get_skill(self):
        sid, skill = self.store.add_skill("Bake Cake", ["mix flour", "bake at 350F"])
        self.assertEqual(sid, "bake_cake")
        self.assertEqual(skill["name"], "Bake Cake")
        self.assertEqual(len(skill["steps"]), 2)

        fetched = self.store.get_skill("bake_cake")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["steps"], ["mix flour", "bake at 350F"])

    def test_update_confidence(self):
        sid, _ = self.store.add_skill("Test Skill", ["step 1"])
        new_conf = self.store.update_confidence(sid, reward=1.0)
        self.assertGreater(new_conf, 0.5)

    def test_add_episode_and_sensory(self):
        self.store.add_episode("action", "Moved arm to target")
        self.store.add_sensory_event("vision", "Detected red block")
        snap = self.store.snapshot()
        self.assertTrue(any(e["detail"] == "Moved arm to target" for e in snap["episodic"]))
        self.assertTrue(any(s["detail"] == "Detected red block" for s in snap["sensory"]))

    def test_semantic_facts_and_working(self):
        self.store.set_semantic_fact("favorite_color", "blue")
        self.store.set_working_memory({"active_tool": "gripper"})
        snap = self.store.snapshot()
        self.assertEqual(snap["semantic"]["favorite_color"]["value"], "blue")
        self.assertEqual(snap["working"]["active_tool"], "gripper")


class TestMemoryAPI(unittest.TestCase):
    def test_memory_add_and_find_skill(self):
        sid, skill = memory.add_skill("Wipe Table", ["grab cloth", "wipe surface", "dry surface"])
        self.assertEqual(sid, "wipe_table")

        found_id, found_skill = memory.find_skill("How do I wipe table?")
        self.assertEqual(found_id, "wipe_table")
        self.assertIsNotNone(found_skill)

    def test_memory_extract_facts(self):
        facts = memory.extract_facts("My name is Alice and I like robotics")
        self.assertTrue(any(k == "user_name" and v == "Alice" for k, v in facts))
        self.assertTrue(any(k == "user_prefers" and "robotics" in v for k, v in facts))

    def test_bump_episode(self):
        memory.bump_episode("action", "Test episodic step")
        rows = memory.episodic_rows(10)
        self.assertTrue(any(r[1] == "action" and "Test episodic step" in r[2] for r in rows))


class TestExecutor(unittest.TestCase):
    def test_executor_logging_and_stats(self):
        executor.log("Action", "Executed pick step", "Success", 0.95)
        st = executor.stats()
        self.assertGreaterEqual(st["success_rate"], 0.0)
        self.assertIn("success_rate", st)


class TestTabletopRobotSimulator(unittest.TestCase):
    def setUp(self):
        self.robot = TabletopRobot()

    def test_move_within_bounds(self):
        init_x, init_y, init_z = self.robot.ee[0], self.robot.ee[1], self.robot.ee[2]
        self.robot.move(0.05, 0.05, 0.0)
        self.assertAlmostEqual(self.robot.ee[0], init_x + 0.05)
        self.assertAlmostEqual(self.robot.ee[1], init_y + 0.05)

    def test_status_html_renders_svg(self):
        svg_html = self.robot.status_html()
        self.assertIn("<svg", svg_html)
        self.assertIn("tabletop", svg_html)

    def test_autonomous_demo(self):
        demo_html = self.robot.autonomous_demo()
        self.assertIn("<svg", demo_html)
        self.assertGreaterEqual(len(self.robot.actions), 1)


class TestMonitorMetrics(unittest.TestCase):
    def test_sample_metrics(self):
        m = monitor.sample()
        self.assertIn("cpu", m)
        self.assertIn("ram", m)
        self.assertIn("disk", m)
        self.assertIn("gpu", m)
        self.assertGreater(m["disk"].total, 0)


class TestUIHandlersAndAgentSelection(unittest.TestCase):
    def test_agent_choices_includes_default_memory(self):
        from src.ui import handlers
        choices = handlers.agent_choices()
        self.assertGreaterEqual(len(choices), 1)
        self.assertEqual(choices[0][1], "")
        self.assertIn("PRIMUS Default Knowledge", choices[0][0])

    def test_agent_knowledge_html_default(self):
        from src.ui import handlers
        html_out = handlers.agent_knowledge_html("")
        self.assertIn("PRIMUS DEFAULT KNOWLEDGE SPACE", html_out)
        self.assertIn("task-library", html_out)

    def test_agent_knowledge_html_custom(self):
        from src.ui import handlers
        STORE.create_agent("HR Bot", "Employee support", "Answer politely")
        html_out = handlers.agent_knowledge_html("hr_bot")
        self.assertIn("HR BOT", html_out)
        self.assertIn("Employee support", html_out)

    def test_custom_agent_management_and_documents(self):
        from src.ui import handlers
        STORE.create_agent("Legal Advisor", "Compliance policies", "Be precise")
        
        # Test custom agent choices
        custom_choices = handlers.custom_agent_choices()
        self.assertTrue(any(c[1] == "legal_advisor" for c in custom_choices))
        
        # Test agent manager html
        mgr_html = handlers.agent_manager_html("legal_advisor")
        self.assertIn("LEGAL ADVISOR", mgr_html)
        self.assertIn("Compliance policies", mgr_html)
        
        # Test document addition directly to agent
        doc = STORE.add_agent_document("legal_advisor", "nda_policy.txt", "NDAs must be signed before meetings.")
        self.assertEqual(doc["name"], "nda_policy.txt")
        
        # Test doc choices
        doc_choices = handlers.agent_document_choices("legal_advisor")
        self.assertEqual(len(doc_choices), 1)
        self.assertIn("nda_policy.txt", doc_choices[0][0])
        
        # Test delete document
        del_res = handlers.delete_agent_doc("legal_advisor", doc["id"])
        del_msg = del_res[0]
        self.assertIn("Deleted document", del_msg)
        self.assertEqual(len(STORE.list_agent_documents("legal_advisor")), 0)

    def test_sidebar_and_clear_active_agent_knowledge(self):
        from src.ui import handlers
        STORE.create_agent("Finance Agent", "Accounting", "Follow GAAP")
        STORE.add_agent_skill("finance_agent", "Audit Expenses", ["check receipts", "verify approvals"])
        STORE.add_agent_document("finance_agent", "tax_guide.pdf", "Tax rates for 2026")
        
        # Test sidebar renders
        sb = handlers.sidebar_agents_html("finance_agent")
        self.assertIn("FINANCE AGENT", sb.upper())
        self.assertIn("sidebar-agent-item", sb)
        
        # Test clear active agent knowledge
        res = handlers.clear_active_agent_knowledge("finance_agent")
        msg = res[0]
        self.assertIn("Cleared knowledge", msg)
        self.assertEqual(len(STORE.list_agent_skills("finance_agent")), 0)
        self.assertEqual(len(STORE.list_agent_documents("finance_agent")), 0)

    def test_chat_modes_and_in_message_upload_isolation(self):
        from src.ui import handlers
        import tempfile
        
        # Test mode toggle
        learn_toggle = handlers.toggle_chat_mode("🎓 Learn Mode")
        self.assertTrue(learn_toggle[0]["visible"])
        
        ask_toggle = handlers.toggle_chat_mode("💬 Ask Mode")
        self.assertFalse(ask_toggle[0]["visible"])
        
        # Create 2 separate agents
        STORE.delete_agent("agent_alpha")
        STORE.delete_agent("agent_beta")
        STORE.create_agent("Agent Alpha", "Alpha Tech", "Rules for Alpha")
        STORE.create_agent("Agent Beta", "Beta Bio", "Rules for Beta")
        
        # Create a temp file to upload
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tf:
            tf.write("Alpha Protocol: Code 9988 is secret to Alpha only.")
            tf_path = tf.name
        
        # Upload file directly via process_input into Agent Alpha
        class MockFile:
            def __init__(self, path):
                self.name = path
        
        mock_file = MockFile(tf_path)
        out = handlers.process_input(
            text="Please ingest this policy",
            audio_path=None,
            history=[],
            messages=[],
            agent_id="agent_alpha",
            use_camera_context=False,
            chat_mode="🎓 Learn Mode",
            doc_file=mock_file,
        )
        
        # Verify document is stored in Agent Alpha ONLY
        alpha_docs = STORE.list_agent_documents("agent_alpha")
        self.assertEqual(len(alpha_docs), 1)
        self.assertIn("Alpha Protocol", alpha_docs[0]["content"])
        
        # Verify Agent Beta has NO documents (strict isolation)
        beta_docs = STORE.list_agent_documents("agent_beta")
        self.assertEqual(len(beta_docs), 0)


if __name__ == "__main__":
    unittest.main()

