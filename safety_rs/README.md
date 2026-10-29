# Optional Rust watchdog prototype

This is the reference Linux process watchdog prototype. It validates that the
PID belongs to a Python `app.py` process before accepting an `ESTOP` datagram
on loopback UDP port 9119, then sends that process `SIGTERM`.

It is not a safety-rated controller, does not stop physical actuators, and is
not portable to Windows because its process validation uses `/proc` and its
stop operation invokes `kill`. Do not treat it as a robot emergency stop.

Build on a compatible Rust toolchain with `cargo build --release` from this
directory. Do not run it against a process until the target PID is confirmed.
