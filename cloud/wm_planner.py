"""Experimental CEM planner for the structured ASTRA checkpoint format."""

import time

import torch


class WMPlanner:
    """Plan action offsets from an ASTRA checkpoint; this is not a controller."""

    def __init__(self, astra_ckpt, z_dim=None, act_dim=29, H=8, K=64,
                 iterations=3, elites=8):
        self.H = max(1, int(H))
        self.K = max(2, int(K))
        self.iterations = max(1, int(iterations))
        self.elites = max(1, min(int(elites), self.K))
        self.model_path = astra_ckpt
        try:
            checkpoint = torch.load(astra_ckpt, map_location="cpu", weights_only=True)
        except TypeError as exc:
            raise RuntimeError("This planner requires a PyTorch version that supports safe weights_only loading") from exc
        if not isinstance(checkpoint, dict) or checkpoint.get("architecture") != "ASTRA":
            raise ValueError("Expected a structured ASTRA state-dictionary checkpoint")

        from cloud.train_astra import ASTRA

        self.net = ASTRA(
            absolute_dim=int(checkpoint["absolute_dim"]),
            action_dim=int(checkpoint["action_dim"]),
            observation_dim=int(checkpoint["observation_dim"]),
            latent_dim=int(checkpoint["latent_dim"]),
        )
        self.net.load_state_dict(checkpoint["model_state_dict"])
        self.net.eval()
        self.z_dim = int(checkpoint["latent_dim"])
        self.act_dim = int(checkpoint["action_dim"])
        if z_dim is not None and int(z_dim) != self.z_dim:
            raise ValueError(f"checkpoint latent size is {self.z_dim}, requested {z_dim}")
        if int(act_dim) != self.act_dim:
            raise ValueError(f"checkpoint action size is {self.act_dim}, requested {act_dim}")

    @torch.no_grad()
    def plan(self, z0, base_action):
        """Return a bounded first-step action offset and elapsed milliseconds."""
        start = time.perf_counter()
        base = torch.as_tensor(base_action, dtype=torch.float32).reshape(-1)
        if base.numel() != self.act_dim:
            raise ValueError(f"expected base_action of length {self.act_dim}")
        latent = torch.as_tensor(z0, dtype=torch.float32)
        if latent.ndim == 3:
            latent = latent[:, -1]
        if latent.ndim == 2:
            latent = latent[-1]
        if latent.ndim != 1 or latent.numel() != self.z_dim:
            raise ValueError(f"expected final latent vector of length {self.z_dim}")

        mean = torch.zeros(self.H, self.act_dim, dtype=base.dtype)
        best, best_reward = None, -float("inf")
        for _ in range(self.iterations):
            candidates = (mean.unsqueeze(0) + 0.3 * torch.randn(self.K, self.H, self.act_dim)).clamp(-1.0, 1.0)
            rewards = torch.zeros(self.K, dtype=base.dtype)
            z = latent.unsqueeze(0).expand(self.K, -1)
            for step in range(self.H):
                action = (base.unsqueeze(0) + candidates[:, step]).clamp(-1.0, 1.0)
                model_input = torch.cat([z, action], dim=-1)
                transition = self.net.transition_head(model_input)
                predicted, _log_variance = transition.chunk(2, dim=-1)
                rewards += self.net.reward_head(model_input).squeeze(-1)
                z = predicted
            top = rewards.topk(self.elites).indices
            if float(rewards[top[0]]) > best_reward:
                best_reward = float(rewards[top[0]])
                best = candidates[top[0]]
            mean = 0.3 * mean + 0.7 * candidates[top].mean(dim=0)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return best[0].clamp(-1.0, 1.0), elapsed_ms
