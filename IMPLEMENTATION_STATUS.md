# Reference feature implementation status

Updated 2026-10-29 on `feature/reference-architecture`.

## Compatibility and rollback

- `6051aa5` is the original pre-feature checkpoint on the remote base branch.
- The current reference-architecture branch retains all earlier commits and
  adds each feature group in separate commits. Changes in this work are being
  verified before updating the remote branch.
- Existing local databases and model files were not migrated or rewritten.
- The original zPrimus chat/UI flow remains the default. Reference cognition
  enters it only when `PRIMUS_REFERENCE_COGNITION=1`; the reference viewer is a
  separate `reference_app.py` process on port 7862 by default.

## Added feature groups

- Full `primus/` reference package: conversation brain, voice loop, object and
  people memory, camera/detection, cognition integration, social/affect,
  spatial/proprioceptive helpers, simulation scene composition, and terminal
  demos. Includes the reference docs and tests.
- Optional salience-aware cognition UI/store under `src/cognition/`, with a
  separate database, manual decay/consolidation/forget controls, and advisory
  helpers.
- G1 and kitchen MuJoCo assets, a lazy headless simulator wrapper, and the
  reference procedural scene builder.
- Standalone cloud/MJX training and collection workflows, ASTRA, policy export,
  CEM planning, perception service, and model/serve scripts.
- Optional ROS 2 bridges adapted to read the zPrimus camera stream.
- Reference C++ camera/reflex/spine sources with a CMake recipe, and the Rust
  watchdog prototype with its platform and safety limits documented.
- A separate reference viewer/voice launcher; voice is opt-in, preventing a
  second microphone loop from starting with the default app.

## Verification and remaining environment requirements

- Reference SQLite connections now close deterministically on Windows; the
  telemetry file lock has a Windows implementation; the procedural MJCF
  builder closes its temporary file before MuJoCo loads it.
- The optional reference voice imports audio dependencies lazily while keeping
  patchable module symbols for its tests.
- All 76 tests pass. The reference viewer builds under a mocked camera object,
  and the default app builds with the Cognition Lab both disabled and enabled.
- MJX training needs JAX. Cloud inference needs model files. ROS 2 needs a ROS
  environment. The C++ sources need an installed compiler plus MuJoCo/OpenCV
  development packages. The Rust watchdog needs a Rust toolchain and is Linux
  specific. These runtime paths cannot be exercised on the current host as
  configured.

No physical motor controller is provided by the reference repository or this
port. Prototype motor/planning outputs remain advisory or simulation-only.
