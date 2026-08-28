import threading
import time
import sys

import numpy as np
import torch

from src.config import STREAM_PORT


class Vision:
    def __init__(self):
        self.cap = None
        self.running = False
        self.paused = False
        self.mirror = False
        self.frame = None
        self.fps = 0.0
        self.labels = []
        self.conf = 0.0
        self.hands = 0
        self.yolo = None
        self.error = ""
        self.stream_ok = False
        self._hands_model = None
        self._server = None

    def start(self):
        if self.running:
            return True
        try:
            import cv2
            # DirectShow is the most reliable low-latency backend on Windows;
            # V4L2 is Linux-only.  Fall back to OpenCV's default backend when
            # either explicit choice is unavailable.
            backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_V4L2
            self.cap = cv2.VideoCapture(0, backend)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.error = "Camera device not found"
                return False
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.running = True
            self.error = ""
            threading.Thread(target=self._loop, daemon=True).start()
            self._start_stream()
            return True
        except Exception as e:
            self.error = str(e)
            return False

    # TRUE LIVE MJPEG STREAM
    def _start_stream(self):
        if self._server is not None:
            return
        try:
            from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
            vision = self

            class H(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path.startswith("/stream"):
                        self.send_response(200)
                        self.send_header("Content-Type",
                                         "multipart/x-mixed-replace; boundary=frame")
                        self.end_headers()
                        try:
                            while vision.running:
                                frame = vision.frame
                                if frame is not None:
                                    import cv2 as _cv2
                                    bgr = _cv2.cvtColor(frame, _cv2.COLOR_RGB2BGR)
                                    ok, jpg = _cv2.imencode(
                                        ".jpg", bgr,
                                        [int(_cv2.IMWRITE_JPEG_QUALITY), 85])
                                    if ok:
                                        data = jpg.tobytes()
                                        self.wfile.write(
                                            b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                                            + str(len(data)).encode() + b"\r\n\r\n" + data + b"\r\n")
                                time.sleep(0.03)
                        except Exception:
                            pass
                    else:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        self.wfile.write(b"<html><body style='margin:0;background:#000'>"
                                         b"<img src='/stream' style='width:100%'></body></html>")

                def log_message(self, *a):
                    pass

            self._server = ThreadingHTTPServer(("0.0.0.0", STREAM_PORT), H)
            self._server.daemon_threads = True
            threading.Thread(target=self._server.serve_forever, daemon=True).start()
            self.stream_ok = True
        except Exception as e:
            self.stream_ok = False
            self.error = f"Stream server failed: {e}"

    # LOW-LATENCY CAPTURE LOOP
    def _loop(self):
        import cv2
        try:
            from ultralytics import YOLO
            self.yolo = YOLO("yolov8n.pt")
        except Exception:
            self.yolo = None

        last = time.time()
        frames = 0
        idx = 0

        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue
            if self.paused:
                time.sleep(0.02)
                continue

            idx += 1
            frames += 1
            now = time.time()
            if now - last >= 1.0:
                self.fps = round(frames / (now - last), 1)
                frames = 0
                last = now

            if self.yolo is not None and idx % 3 == 0:
                try:
                    use_half = bool(torch.cuda.is_available())
                    results = self.yolo(frame, verbose=False, half=use_half)
                    boxes = results[0].boxes
                    self.labels = sorted({self.yolo.names[int(b.cls[0])] for b in boxes})
                    confs = [float(b.conf[0]) if hasattr(b.conf, "__len__") else float(b.conf) for b in boxes]
                    self.conf = round(float(np.mean(confs)), 2) if confs else 0.0
                    frame = results[0].plot()
                except Exception:
                    pass

            if idx % 10 == 0:
                try:
                    import mediapipe as mp
                    if self._hands_model is None:
                        self._hands_model = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2)
                    rgb_for_hands = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    res = self._hands_model.process(rgb_for_hands)
                    self.hands = len(res.multi_hand_landmarks) if res.multi_hand_landmarks else 0
                except Exception:
                    pass

            if self.mirror:
                frame = cv2.flip(frame, 1)

            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def status(self):
        if not self.running:
            return f"OFF ({self.error or 'not started'})"
        if self.paused:
            return "PAUSED"
        return f"ON {self.fps} FPS"

    def summary(self):
        if self.labels:
            return f"Objects perceived: {', '.join(self.labels)} (YOLO conf {self.conf})"
        return "No objects detected"


VISION = Vision()
