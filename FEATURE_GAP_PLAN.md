# zPrimus feature gap and implementation plan

## Scope and comparison basis

This review compares `D:\Primus_Major\Primus` (the current zPrimus app) with
`D:\Primus_Major\primus-architecture-main(1)\primus-architecture-main`.
It is based on the checked-in source and documentation, not on running either
application. A feature described as a prototype in the reference is treated as
a prototype, not as a production capability. No application code or existing
runtime flow was changed for this review.

## Feature coverage

| Reference capability | zPrimus status | Suggested action |
|---|---|---|
| Persistent SQLite memory with salience, decay, consolidation, explicit forgetting, and idle replay | Partial overlap: zPrimus already has procedural, episodic, semantic, sensory, and working memory, plus local/optional PostgreSQL storage; salience ranking, decay/consolidation, explicit forget, and replay maintenance are not evident in its `src/core` modules. | Add as an optional memory service behind the existing memory/storage API. Preserve current record formats and defaults. |
| Social awareness, affect/style, bonding, pragmatic intent and proactive suggestions | Missing as dedicated modules. | Add opt-in advisory helpers; do not make them alter routing or speak proactively by default. |
| Spatial object memory, proprioception, motor-planning suggestions | Missing. Current YOLO/camera perception does not establish metric 3D state or robot proprioception. | Defer until there is a reliable source of calibrated spatial/simulation state; keep outputs advisory. |
| Physiology-style helpers: sleep cycle, mood/fatigue, contact/pain state | Missing. | Low priority research prototypes only; no impact on listening, execution, or control without explicit validated integration. |
| Imitation/demo storage, play suggestions, nonverbal symbols, developmental counters, cognitive-load and reconstructive-recall helpers | Missing as dedicated capabilities. | Select individual helpers based on a concrete product need; keep them isolated and optional. |
| MuJoCo G1 scene, procedural room, camera rendering and simulation app | Missing. zPrimus has a camera/YOLO pipeline and a tabletop robot-learning sandbox, but no G1/MuJoCo scene stack. | Separate optional simulation milestone; do not replace the current dashboard or robot sandbox. |
| MJX/PPO training, episode collection, ASTRA training and policy export | Partial overlap: zPrimus has curriculum/meta-RL and evaluation foundations, but not the reference's G1 MJX/ASTRA workflow. | Defer until simulator assets, dependency isolation, and an evaluation target are agreed. Keep training outside the interactive runtime. |
| Cloud services: vLLM/Moshi/transcription/depth/person embeddings and latent CEM planner | Missing as integrated reference-style services. zPrimus already has Ollama and optional PostgreSQL/pgvector/MinIO foundations. | Consider only service-by-service, behind configuration and local fallbacks. The reference itself documents that its planner/checkpoint path is not integrated. |
| ROS 2 bridges, C++ camera/reflex/spine sources, early Rust safety crate | Missing. zPrimus has a separate pybind11 C++ neural core, which is not a robot-control spine. | Defer; require a separate integration design and safety review. Do not connect to physical hardware as part of feature parity. |

## Recommended implementation order

1. **Compatibility baseline.** Record the existing user journeys: launch, text chat, teach/recall/execute a learned task, audio input/output, camera perception, memory persistence, and optional backend fallback. Capture their current inputs/outputs and storage assumptions before implementation.
2. **Memory capabilities (smallest useful gap).** Add a versioned, opt-in memory extension through the current storage boundary. Migrate or adapt records without destructive rewrites. Add explicit forgetting and maintenance controls; never enable decay by default until retention behavior is reviewed.
3. **Advisory cognition helpers.** Add only selected social/affect/proactive utilities as independent services. Feed them explicit inputs and return suggestions/data; do not change intent decisions, memory answers, UI output tuple, or voice behavior in the first integration pass.
4. **Spatial/simulation foundation.** Decide whether zPrimus should adopt MuJoCo/G1 or extend its existing sandbox. Add it as a separately launched optional module with its own dependencies and state, leaving the existing app start path intact.
5. **Offline learning workflows.** If the simulation milestone is accepted, port episode collection/training/export as standalone commands. Do not load experimental policies into the live executor automatically.
6. **Cloud and robot integration.** Evaluate each service independently. ROS 2/hardware control requires a separately approved design, tested motion backend, emergency-stop path, limits, and supervised validation; the reference repository does not provide a complete validated controller.

## Flow-preservation requirements for every future change

- Keep current behavior as the default; gate new behavior behind a disabled-by-default setting until its compatibility is established.
- Preserve public function signatures and the Gradio event input/output contract. Prefer adapters over changing existing handlers or replacing the current engine.
- Keep current local memory readable; use additive schema migrations with backups and an explicit rollback path. Never clear or rewrite the existing memory bank as part of migration.
- Keep optional dependencies lazy and isolated so missing MuJoCo, ROS 2, cloud credentials, GPU libraries, or new model files cannot prevent the current app from starting.
- Do not let heuristic cognition modules bypass the current knowledge gate, change task selection, or claim that simulated/advisory actions were physically executed.
- Integrate one capability at a time. For each, compare baseline journeys before and after, check persistence compatibility, test the feature both enabled and disabled, and verify the fallback path when its dependency is unavailable.
- Ship each phase behind a reversible configuration switch; retain a clear rollback to the previous release and database backup.

## Suggested acceptance gates

Before enabling a phase by default, require all of the following:

1. The existing launch and user journeys above behave the same with the feature disabled.
2. Existing memory data opens without loss, and rollback restores the prior schema/data.
3. New dependency/service failures degrade to the current behavior with a clear log message.
4. New behavior has focused checks and manual UI verification for the affected paths.
5. Any simulation or advisory output is labeled accurately; no prototype is presented as validated real-world control.

## Next decision

Start with the memory extension only after agreeing on retention/forgetting
semantics. Then select which advisory cognition helpers have a concrete user
need. Treat simulation, cloud training, and ROS 2 as separate projects rather
than a single bulk port. This document is a plan; implementation has not begun.
