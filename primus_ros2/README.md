# Optional ROS 2 bridges

This ROS 2 Humble package is separate from the zPrimus application and does
not start with `app.py`. It provides three topic nodes:

- `brain_bridge` forwards `/primus/voice_text` to `/primus/command` and logs
  `/primus/status`.
- `perception_bridge` reads the existing local zPrimus MJPEG stream and
  publishes `/primus/camera/image`. It publishes an empty detections list; it
  does not claim detections that it did not calculate.
- `task_executor` classifies command text and reports that no motion backend is
  configured. It never claims to have moved a robot.

The perception bridge reads `http://127.0.0.1:8000/stream` by default. Set
`PRIMUS_STREAM_URL` or `PRIMUS_STREAM_PORT` if the app uses another address.
Start the zPrimus app and camera first, then build the package in a ROS 2
environment:

```bash
cd primus_ros2
source /opt/ros/humble/setup.bash
colcon build --packages-select primus_actions
source install/setup.bash
```

Run `perception_bridge`, `brain_bridge`, and `task_executor` as separate ROS 2
nodes. This integration was not executable in the current Windows environment
because ROS 2 is not installed. It contains no locomotion, grasping, placing,
or physical actuator backend. Do not treat the topic bridge as a validated
robot controller.
