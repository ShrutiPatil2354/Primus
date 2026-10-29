# Optional G1 learning and perception services

This directory contains standalone MJX/PPO training, simulator episode
collection, ASTRA training, policy export, a latent CEM planner, and an optional
FastAPI perception service. None is imported or started by `app.py`.

The current environment has MuJoCo but does not have JAX, so MJX collection and
PPO training have not been executed here. Install the JAX/MJX stack separately
in a compatible environment before using those commands. The ASTRA trainer
uses PyTorch and consumes NPZ episodes; it does not make the simulator run on
hardware.

`wm_planner.py` loads the structured state-dictionary checkpoint emitted by
`train_astra.py` with safe weights-only loading. It predicts candidate latent
trajectories and returns an advisory action offset. It is not connected to the
Gradio executor or to a robot controller. `export_policy.py` creates offline
artifacts only; export does not establish control safety.

The perception service loads models lazily and requires its optional model
files and service dependencies. Start it separately and configure a client
explicitly; it is not wired into the existing local audio or vision path.

Use only simulated data for the research workflows. The G1 model license and
attribution are preserved in `sim/g1/LICENSE` and `sim/g1/README.md`.
