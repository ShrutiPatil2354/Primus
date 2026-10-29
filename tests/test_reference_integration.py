"""Compatibility test for the opt-in reference cognition hook in zPrimus."""

import os
import importlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class TestReferenceCognitionHook(unittest.TestCase):
    def test_default_chat_can_opt_in_without_changing_handler_contract(self):
        from src.ui import handlers

        cognition = mock.Mock()
        cognition.think_hook.return_value = {"system_prompt": "Use a calm style."}
        cognition.respond_hook.return_value = {"reply": "Hello."}
        with mock.patch.dict(os.environ, {"PRIMUS_REFERENCE_COGNITION": "1"}):
            with mock.patch("primus.integration.cognition", return_value=cognition):
                with mock.patch.object(handlers.llm, "online", return_value=True):
                    with mock.patch.object(handlers.llm, "chat", return_value="Hello.") as chat:
                        result = handlers.process_input(
                            text="Hello there",
                            audio_path=None,
                            history=[],
                            messages=[],
                            agent_id="",
                            use_camera_context=False,
                            chat_mode="Ask Mode",
                            doc_file=None,
                            use_audio_output=False,
                        )
        self.assertEqual(len(result), 17)
        cognition.think_hook.assert_called_once()
        cognition.respond_hook.assert_called_once_with("Hello.")
        system_message = chat.call_args.args[0][0]["content"]
        self.assertIn("Use a calm style.", system_message)
        self.assertIn("must not add facts or override the knowledge gate", system_message)

    def test_windows_safe_reference_metrics_bus(self):
        from primus import bus

        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory)
            with mock.patch.object(bus, "DATA_DIR", data_dir), \
                    mock.patch.object(bus, "METRICS_PATH", data_dir / "metrics.json"), \
                    mock.patch.object(bus, "LOCK_PATH", data_dir / "metrics.lock"):
                bus.put(fps=30.0, cam_res="640x480")
                self.assertEqual(bus.get()["fps"], 30.0)


@unittest.skipUnless(importlib.util.find_spec("mujoco"), "MuJoCo is optional")
class TestReferenceScene(unittest.TestCase):
    def test_procedural_reference_scene_builds_on_this_platform(self):
        from primus.scene_builder import load_model

        model = load_model()
        self.assertEqual(model.nu, 29)
        self.assertGreater(model.nbody, 31)


class TestReferenceUIConstruction(unittest.TestCase):
    def test_reference_viewer_builds_without_opening_camera_hardware(self):
        import primus.cams as cams

        class FakeCams:
            def __init__(self):
                self.focus = "kitchen"
                self.orbit = (200.0, -15.0, 3.5)

            @staticmethod
            def names():
                return ["kitchen", "teacher"]

            @staticmethod
            def view():
                return None

            @staticmethod
            def status():
                return "test viewer"

        try:
            with mock.patch.object(cams, "Cams", FakeCams):
                ui = importlib.import_module("primus.ui")
                import gradio as gr

                self.assertIsInstance(ui.build(), gr.Blocks)
                self.assertIsNone(ui._C)
        finally:
            sys.modules.pop("primus.ui", None)
            if hasattr(sys.modules.get("primus"), "ui"):
                delattr(sys.modules["primus"], "ui")

    def test_reference_viewer_lifecycle_is_tab_driven(self):
        import primus.cams as cams

        class FakeCams:
            focus = "kitchen"
            orbit = (200.0, -15.0, 3.5)
            closed = False

            @staticmethod
            def names():
                return ["kitchen"]

            @staticmethod
            def view():
                return None

            @staticmethod
            def status():
                return "fake viewer"

            def close(self):
                self.closed = True

        ui = importlib.import_module("primus.ui")
        ui.stop_viewer()
        try:
            with mock.patch.object(cams, "Cams", FakeCams):
                with mock.patch.object(ui, "Cams", FakeCams):
                    self.assertIsNone(ui._C)
                    image, status, timer = ui.start_viewer()
                    self.assertIsNone(image)
                    self.assertEqual(status, "fake viewer")
                    self.assertTrue(timer.active)
                    current = ui._C
                    stopped_timer = ui.stop_viewer()
                    self.assertTrue(current.closed)
                    self.assertFalse(stopped_timer.active)
                    self.assertIsNone(ui._C)
        finally:
            ui.stop_viewer()


class TestCombinedPrimusUI(unittest.TestCase):
    def test_main_dashboard_has_both_surfaces_and_lazy_tab_lifecycle(self):
        import app

        components = app.demo.config["components"]
        tab_labels = [
            component.get("props", {}).get("label")
            for component in components
            if component["type"] == "tabitem"
        ]
        self.assertEqual(tab_labels[0], "Workspace")
        self.assertIn("Reference Simulator", tab_labels)
        self.assertIsNone(app.reference_ui._C)

        dependencies = app.demo.config["dependencies"]
        start_event = next(
            event for event in dependencies
            if event.get("api_name") == "start_viewer"
        )
        stop_events = [
            event for event in dependencies
            if (event.get("api_name") or "").startswith("stop_viewer")
        ]
        self.assertEqual(start_event["targets"][0][1], "select")
        self.assertGreaterEqual(len(stop_events), 5)
        self.assertTrue(all(event["targets"][0][1] == "select" for event in stop_events))

    def test_microphone_loop_is_explicit_and_reports_missing_device(self):
        import primus.ears as ears
        import primus.ui as ui

        with mock.patch.object(ui, "_VOICE_RUNNING", False):
            with mock.patch.object(ears, "sd", None):
                self.assertIn("install sounddevice", ui.start_voice())
                self.assertFalse(ui._VOICE_RUNNING)

            device = mock.Mock()
            with mock.patch.object(ears, "sd", device):
                with mock.patch("primus.agent.start") as start:
                    status = ui.start_voice()
                    self.assertIn("is listening", status)
                    start.assert_called_once()
                    self.assertIn("already running", ui.start_voice())

            with mock.patch("primus.agent.stop") as stop:
                self.assertIn("stopped", ui.stop_voice())
                stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
