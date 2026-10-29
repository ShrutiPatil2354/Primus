"""ROS 2 bridge for the already-running zPrimus MJPEG stream."""

import os
import time

import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


class PerceptionBridge(Node):
    def __init__(self):
        super().__init__("primus_perception_bridge")
        port = os.environ.get("PRIMUS_STREAM_PORT", "8000")
        self._stream_url = os.environ.get("PRIMUS_STREAM_URL", f"http://127.0.0.1:{port}/stream")
        self._camera = None
        self._last_open_attempt = 0.0
        self._image_pub = self.create_publisher(Image, "/primus/camera/image", 10)
        self._detection_pub = self.create_publisher(String, "/primus/detections", 10)
        self._timer = self.create_timer(0.1, self._publish_frame)
        self.get_logger().info(f"ROS 2 bridge will read the zPrimus stream at {self._stream_url}")

    def _open_stream(self):
        now = time.monotonic()
        if now - self._last_open_attempt < 2.0:
            return False
        self._last_open_attempt = now
        self._camera = cv2.VideoCapture(self._stream_url)
        if not self._camera.isOpened():
            self._camera.release()
            self._camera = None
            self.get_logger().warning("Camera stream unavailable; start the zPrimus camera and retrying")
            return False
        return True

    def _publish_frame(self):
        if self._camera is None and not self._open_stream():
            return
        ok, frame = self._camera.read()
        if not ok or frame is None:
            self._camera.release()
            self._camera = None
            return
        image = Image()
        image.height, image.width = frame.shape[:2]
        image.encoding = "bgr8"
        image.is_bigendian = False
        image.step = image.width * 3
        image.data = frame.tobytes()
        self._image_pub.publish(image)
        # zPrimus detection overlays are visible in the source stream. This
        # bridge does not claim to publish structured detections it did not run.
        empty = String()
        empty.data = "[]"
        self._detection_pub.publish(empty)

    def destroy_node(self):
        if self._camera is not None:
            self._camera.release()
            self._camera = None
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionBridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
