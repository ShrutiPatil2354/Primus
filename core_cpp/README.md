# Optional reference C++ core sources

This directory contains the reference camera publisher, reflex simulation, and
policy-spine sources. They are isolated from the existing `cpp_core/` neural
module and are not started by either Python app.

Configure with CMake on Linux after installing the MuJoCo C development package
and OpenCV development files. Targets are enabled only when CMake finds those
packages:

```bash
cmake -S core_cpp -B core_cpp/build
cmake --build core_cpp/build
```

The camera publisher uses POSIX shared memory and V4L2, so that target is
Linux-only. The reflex and spine operate on simulation inputs and are not a
validated hardware controller. The spine expects the offline exported policy
artifacts documented in `cloud/README.md`.
