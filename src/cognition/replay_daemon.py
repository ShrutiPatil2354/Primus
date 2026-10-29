"""Manually started, stoppable idle maintenance for cognitive memory."""

import threading
import time


class ReplayDaemon:
    def __init__(self, store, idle_seconds=300, interval_seconds=60):
        self.store = store
        self.idle_seconds = max(1.0, float(idle_seconds))
        self.interval_seconds = max(1.0, float(interval_seconds))
        self._last_activity = time.monotonic()
        self._stop = threading.Event()
        self._thread = None

    def mark_activity(self):
        self._last_activity = time.monotonic()

    def start(self):
        if self._thread and self._thread.is_alive():
            return False
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="primus-memory-replay", daemon=True)
        self._thread.start()
        return True

    def stop(self, timeout=2.0):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=max(0.0, float(timeout)))
        return not self._thread or not self._thread.is_alive()

    def _run(self):
        while not self._stop.wait(self.interval_seconds):
            if time.monotonic() - self._last_activity >= self.idle_seconds:
                self.store.consolidate()
                self.store.decay()
