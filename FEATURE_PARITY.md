# Reference architecture feature coverage

The full documented source feature set from `primus-architecture-main(1)` is
now present in this repository. The existing zPrimus UI remains the default;
the companion stack and hardware-adjacent pieces are isolated and opt-in.

| Reference area | Added in Primus | How to access it / current limit |
|---|---|---|
| Voice companion, brain, teaching, object naming, people memory, social awareness | `primus/agent.py`, `brain.py`, `ears.py`, `mouth.py`, `objects.py`, `people.py`, `social_awareness.py` and related modules | The same main URL includes a **Reference Simulator** tab with explicit Start/Stop voice controls and camera/simulation viewing. `reference_app.py` remains a standalone option. `PRIMUS_REFERENCE_VOICE=1` starts voice automatically in that standalone app. |
| Cognition sessions 1–9 | Full source package under `primus/`, plus `docs/HUMAN_BEHAVIOR.md` and the reference tests | Set `PRIMUS_REFERENCE_COGNITION=1` to add the cognition prompt/memory hooks to default-app conversation turns. Heuristics remain advisory and use explicit inputs. |
| G1 MuJoCo, kitchen, generated room, camera/rendering | `sim/g1/`, `sim/kitchen_g1.xml`, `primus/scene_builder.py`, `room.py`, `cams.py`, `render.py`, plus `src/simulation/` | Select **Reference Simulator** in the main dashboard, or use the headless `G1Simulation`. The viewer is stopped when another main tab is selected. No physical actuation is included. |
| MJX/PPO, episode collection, ASTRA, export, world-model CEM | `cloud/` including training, collection, serving, and shell scripts | Standalone only. JAX is absent here, so MJX training cannot run in this environment. The CEM loader accepts the ASTRA trainer checkpoint. |
| Cloud speech, depth, person embeddings, YOLO service | `cloud/svc_percept.py`, model download and serve scripts | Model files and service dependencies are not bundled; it is not connected to the default local perception path. |
| ROS 2 camera, brain, and executor topics | `primus_ros2/` | Requires a ROS 2 environment. The executor reports that no motion backend is configured. |
| C++ camera/reflex/spine sources | `core_cpp/` with an optional CMake project | Camera target is Linux-only. CMake is present here, but a C++ compiler and MuJoCo/OpenCV development packages are not, so native targets were not built. |
| Rust safety watchdog prototype | `safety_rs/` | Linux `/proc` and `kill` prototype; Rust toolchain is absent here. It is not a physical emergency stop. |
| Terminal demos, setup and evaluation | `terminal/`, `setup.md`, `scripts/run_human_demo.sh`, `scripts/cloud_bootstrap.sh`, copied reference tests | Shell demos are for Linux. Reference deterministic tests run under the current Windows Python environment. |

The source-tree audit accounted for every reference file. The reference
`dump_xml.py` helper is present under its original name. The generated
`spine_bin` executable and `sim/kitchen_compiled.xml` are build artifacts; the
compiled XML contains absolute paths from the reference workstation. The C++
sources, portable MJCF inputs, licenses, build recipe, and generation helper
are included instead.

## Verification on this workstation

- `python -m unittest discover -s tests`: 80 tests pass.
- The default zPrimus app imports with the Cognition Lab disabled and enabled.
- The combined dashboard serves the existing Workspace and Reference Simulator
  tabs together at one URL. The reference camera remains idle until its tab is
  selected, and the selection/cleanup handlers are covered by tests.
- The reference Gradio viewer builds under a mocked camera object, without
  opening camera hardware.
- The combined dashboard launched locally and returned HTTP 200 with both tab
  labels in its page. The standalone `reference_app.py` also returned HTTP 200
  on port 7862. Camera capture was unavailable on this host, and the viewer
  reported that condition while remaining available.
- Scene feed buttons and orbit sliders appear above the rendered image.
- The Detect feed reports a missing camera explicitly instead of showing an
  indefinite loading status.
- The reference procedural G1 scene loads in MuJoCo on Windows.
- C++ and Rust native builds, ROS 2 launch, MJX training, and model-backed cloud
  services need their respective external toolchains or assets and were not
  executed here.
