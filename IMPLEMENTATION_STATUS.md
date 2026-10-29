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
  pragmatics, demonstration/play/gesture hints, and approximate recall.

The cognition modules are not imported into the default chat pipeline. The
existing Gradio event contract, intent routing, knowledge gate, and voice path
remain independent of them.
- `PRIMUS_COGNITION_UI=1` exposes a separate Cognition Lab tab for research
  memory. The default is off; enabling it does not alter existing tabs or
  handlers. Both UI configurations imported successfully.
- Optional MuJoCo G1 assets and a lazy headless simulation wrapper are under
  `sim/g1/` and `src/simulation/`. The model loads and steps in this environment;
  MJX training remains unavailable until its separate JAX stack is installed.

## Remaining feature groups

1. Port standalone MJX/PPO, ASTRA, episode collection, and policy export only
   after dependency and checkpoint compatibility is established.
2. Evaluate optional cloud perception/planning services individually. The
   reference world-model planner and trainer checkpoint format need an adapter
   before joint use.
3. Keep ROS 2 and hardware-facing control separate until a validated motion
   backend and safety design exist.

## Verification

The original 22-test suite passed after the compatibility fixes. The focused
cognition tests and full 25-test suite also pass. The app imported successfully
with the cognition tab both disabled and enabled. New dependencies and
migrations remain optional, and the default flow is unchanged when disabled.
