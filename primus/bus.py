"""Cross-platform atomic JSON telemetry bus used by the reference stack."""

from contextlib import contextmanager
import json
import os
import tempfile
import threading
import time
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
METRICS_PATH = DATA_DIR / "metrics.json"
LOCK_PATH = DATA_DIR / "metrics.lock"
_THREAD_LOCK = threading.RLock()

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None
try:
    import msvcrt
except ImportError:  # Unix
    msvcrt = None


@contextmanager
def _file_lock(lock_file):
    with _THREAD_LOCK:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        elif msvcrt is not None:
            lock_file.seek(0, os.SEEK_END)
            if lock_file.tell() == 0:
                lock_file.write("0")
                lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            yield


def put(**values):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("a+", encoding="utf-8") as lock_file, _file_lock(lock_file):
        if METRICS_PATH.exists():
            with METRICS_PATH.open(encoding="utf-8") as metrics_file:
                current = json.load(metrics_file)
            if not isinstance(current, dict):
                raise ValueError(f"{METRICS_PATH} must contain a JSON object")
        else:
            current = {}
        current.update(values)
        current["t"] = time.time()
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=DATA_DIR,
                prefix=".metrics-", suffix=".tmp", delete=False,
            ) as metrics_file:
                temporary_path = Path(metrics_file.name)
                json.dump(current, metrics_file)
                metrics_file.flush()
                os.fsync(metrics_file.fileno())
            os.replace(temporary_path, METRICS_PATH)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()


def get():
    if not METRICS_PATH.exists():
        return {}
    with METRICS_PATH.open(encoding="utf-8") as metrics_file:
        metrics = json.load(metrics_file)
    if not isinstance(metrics, dict):
        raise ValueError(f"{METRICS_PATH} must contain a JSON object")
    return metrics
