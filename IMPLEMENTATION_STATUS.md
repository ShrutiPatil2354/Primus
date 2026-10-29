# Reference feature implementation status

Updated 2026-10-29.

## Rollback and compatibility checkpoints

- `6051aa5` is pushed to `origin/feature/build-your-own-agent` and captures the
  previously untracked plan and utility scripts before implementation.
- `f5cbdb4` is a local compatibility checkpoint after restoring the tabletop
  simulator API and fixing two legacy flow issues. It passed the original
  22-test suite. A push of this follow-up checkpoint was rejected by the
  approval layer, so the remote rollback point remains `6051aa5`.
- The cognition feature work is isolated on the current branch and can be
  reverted independently. No current memory database or model files were
  migrated or rewritten by this work.

## Implemented in the current working tree

- A small bounded tabletop simulator API under `src/robot_sim/`, with symbolic
  actions and storage of episodes for offline evaluation. It has no hardware
  connection.
- Backward-compatible episodic event recording and Ask Mode upload visibility
  fixes.
- An optional cognition package with a separate salience-aware SQLite store,
  explicit decay/consolidation/forget operations, and a manually started,
  stoppable replay daemon.
- Explicit-input advisory helpers for social/acoustic cues, bounded affect,
  spatial object notes and velocity suggestions, metacognition, proactive
  prompts, developmental counters, toy physiology, social-bond state,
  pragmatics, demonstration/play/gesture hints, approximate recall, and
  optional PyTorch EWC/skill-adapter utilities.

The cognition modules are not imported into the default chat pipeline. The
existing Gradio event contract, intent routing, knowledge gate, and voice path
remain independent of them.
- `PRIMUS_COGNITION_UI=1` exposes a separate Cognition Lab tab for research
  memory. The default is off; enabling it does not alter existing tabs or
  handlers. Both UI configurations imported successfully.
- Optional MuJoCo G1 assets and a lazy headless simulation wrapper are under
  `sim/g1/`, `sim/kitchen_g1.xml`, and `src/simulation/`. The G1 kitchen scene
  loads and steps in this environment; MJX training remains unavailable until
  its separate JAX stack is installed.
- Standalone MJX/PPO collection and training, ASTRA, policy export, CEM planning,
  and lazy cloud perception service sources are now under `cloud/`. The CEM
  loader was adapted for the trainer's state-dictionary checkpoint format.
  These scripts are not called by the UI; MJX cannot run in this environment
  because JAX is absent, and the cloud service has no models here.
- An optional ROS 2 topic package is under `primus_ros2/`. Its perception node
  consumes the zPrimus MJPEG stream; its executor explicitly reports the
  missing motion backend. ROS 2 is not installed in this environment, so this
  package was not built or run.

## Remaining feature groups

1. Validate MJX/PPO, episode collection, ASTRA, and policy export in an isolated
   JAX-capable environment; the current host cannot run the MJX jobs.
2. Run the optional cloud perception/planning services with explicit models
   and service dependencies, then decide whether to add client adapters.
3. Build and exercise the ROS 2 package in a ROS 2 environment. Keep physical
   control separate until a validated motion backend and safety design exist.

## Verification

The full 28-test suite passes, including the isolated cognition, MuJoCo, and
ASTRA/CEM checkpoint checks. The app imports successfully with the cognition
tab both disabled and enabled. All new service integrations remain outside
the default flow.
