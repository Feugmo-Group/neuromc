"""
neural_functional.py
====================
PyTorch neural network that learns the map ρ_window → c₁ for 1-D hard rods.

Architecture
------------
A multi-layer perceptron (MLP) with Softplus activations:

    Input:  density window of width window_width centred at x
            shape (batch, n_window_bins)
    Hidden: n_layers × Linear → Softplus
    Output: Linear → scalar c₁(x)   shape (batch, 1)

The functional is local: c₁(x) depends only on a sliding window of ρ
centred at x.  This is an approximation that works well for short-ranged
functionals such as the Percus exact 1-D functional (range = σ).

Torch is imported *lazily* (inside methods) so that the package remains
importable without PyTorch being installed.

References
----------
Sammüller et al., J. Phys.: Condens. Matter 36, 243002 (2024)
https://github.com/sfalmo/NeuralDFT-Tutorial  (Julia reference)
"""

from __future__ import annotations

import math
import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_mlp(n_input: int, hidden_dims: list[int], n_output: int = 1):
    """Build a Softplus-activated MLP.  Lazy torch import."""
    import torch
    import torch.nn as nn

    layers: list[nn.Module] = []
    in_dim = n_input
    for h in hidden_dims:
        layers.append(nn.Linear(in_dim, h))
        layers.append(nn.Softplus())
        in_dim = h
    layers.append(nn.Linear(in_dim, n_output))
    return nn.Sequential(*layers)


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class NeuralC1Functional:
    """
    Neural network approximation of c₁(x; [ρ]).

    The functional is local: c₁(x) depends only on a window of ρ
    centred at x of width ``window_width`` (in σ units).

    Parameters
    ----------
    window_width : float
        Spatial width of the density input window [σ].
    dx : float
        Grid spacing [σ].
    hidden_dims : list[int]
        Hidden layer sizes.  Default [64, 64, 64].
    """

    def __init__(
        self,
        window_width: float = 1.0,
        dx: float = 0.01,
        hidden_dims: list[int] | None = None,
    ):
        self.window_width = float(window_width)
        self.dx = float(dx)
        self.hidden_dims = hidden_dims if hidden_dims is not None else [64, 64, 64]

        # Number of bins in the window (must be odd so window is symmetric)
        n_half = math.ceil(self.window_width / (2.0 * self.dx))
        self.n_window_bins = 2 * n_half + 1

        self._model = None   # lazy-built torch model
        self._device = None

    # ------------------------------------------------------------------
    # Model construction
    # ------------------------------------------------------------------

    def build_model(self):
        """Build (or rebuild) the PyTorch MLP."""
        import torch
        self._model = _build_mlp(self.n_window_bins, self.hidden_dims, n_output=1)
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = self._model.to(self._device)
        return self._model

    def _ensure_model(self):
        if self._model is None:
            self.build_model()

    # ------------------------------------------------------------------
    # Window extraction
    # ------------------------------------------------------------------

    def make_windows(self, rho: np.ndarray) -> np.ndarray:
        """
        Extract sliding windows from a density profile with periodic padding.

        Parameters
        ----------
        rho : np.ndarray (N,)
            Density profile on a periodic grid.

        Returns
        -------
        windows : np.ndarray (N, n_window_bins)
        """
        N = len(rho)
        half = self.n_window_bins // 2

        # Pad periodically on both sides
        rho_padded = np.concatenate([rho[-half:], rho, rho[:half]])

        windows = np.lib.stride_tricks.sliding_window_view(rho_padded, self.n_window_bins)
        # windows shape: (N + 2*half - n_window_bins + 1, n_window_bins)
        # After periodic padding of exactly `half` on each side this is (N, n_window_bins)
        return np.asarray(windows[:N], dtype=np.float32)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, rho: np.ndarray) -> np.ndarray:
        """
        Compute c₁ profile from a density profile.

        Parameters
        ----------
        rho : np.ndarray (N,)

        Returns
        -------
        c1 : np.ndarray (N,)
        """
        import torch

        self._ensure_model()
        windows = self.make_windows(rho)  # (N, n_window_bins)
        x_t = torch.tensor(windows, dtype=torch.float32, device=self._device)

        self._model.eval()
        with torch.no_grad():
            c1_t = self._model(x_t).squeeze(-1)  # (N,)

        return c1_t.cpu().numpy().astype(np.float64)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(
        self,
        rho_profiles: list[np.ndarray],
        c1_profiles: list[np.ndarray],
        epochs: int = 200,
        lr: float = 1e-3,
        batch_size: int = 512,
        val_fraction: float = 0.1,
        verbose: bool = True,
    ) -> dict:
        """
        Train on lists of (ρ, c₁) profile pairs from simulation.

        Data is expanded to (position, window) pairs and augmented with
        mirror-flipped profiles for better generalisation.

        Parameters
        ----------
        rho_profiles : list of np.ndarray (N,)
        c1_profiles  : list of np.ndarray (N,)
        epochs       : int
        lr           : float — learning rate for Adam
        batch_size   : int
        val_fraction : float — fraction of data held out for validation
        verbose      : bool — print epoch losses

        Returns
        -------
        history : dict with 'train_loss' and 'val_loss' lists (per epoch)
        """
        import torch
        import torch.nn as nn
        from torch.utils.data import TensorDataset, DataLoader, random_split

        self._ensure_model()

        # ---- Build dataset ----
        all_windows: list[np.ndarray] = []
        all_c1: list[np.ndarray] = []

        for rho, c1 in zip(rho_profiles, c1_profiles):
            rho = np.asarray(rho, dtype=np.float64)
            c1 = np.asarray(c1, dtype=np.float64)

            # Original
            all_windows.append(self.make_windows(rho))
            all_c1.append(c1.astype(np.float32))

            # Mirror-flipped augmentation (flip spatial axis)
            rho_flip = rho[::-1].copy()
            c1_flip = c1[::-1].copy()
            all_windows.append(self.make_windows(rho_flip))
            all_c1.append(c1_flip.astype(np.float32))

        X = np.concatenate(all_windows, axis=0)   # (M, n_window_bins)
        y = np.concatenate(all_c1, axis=0)        # (M,)

        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)  # (M, 1)

        dataset = TensorDataset(X_t, y_t)
        n_val = max(1, int(len(dataset) * val_fraction))
        n_train = len(dataset) - n_val
        train_ds, val_ds = random_split(
            dataset, [n_train, n_val],
            generator=torch.Generator().manual_seed(42),
        )

        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=batch_size * 4)

        # ---- Optimiser ----
        optimizer = torch.optim.Adam(self._model.parameters(), lr=lr)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, factor=0.5, patience=10, verbose=False
        )
        loss_fn = nn.MSELoss()

        history: dict[str, list[float]] = {"train_loss": [], "val_loss": []}

        # ---- Training loop ----
        for epoch in range(1, epochs + 1):
            self._model.train()
            train_loss_acc = 0.0
            n_batches = 0

            for xb, yb in train_loader:
                xb = xb.to(self._device)
                yb = yb.to(self._device)
                optimizer.zero_grad()
                pred = self._model(xb)
                loss = loss_fn(pred, yb)
                loss.backward()
                optimizer.step()
                train_loss_acc += loss.item()
                n_batches += 1

            train_loss = train_loss_acc / max(n_batches, 1)

            # Validation
            self._model.eval()
            val_loss_acc = 0.0
            n_val_batches = 0
            with torch.no_grad():
                for xb, yb in val_loader:
                    xb = xb.to(self._device)
                    yb = yb.to(self._device)
                    pred = self._model(xb)
                    val_loss_acc += loss_fn(pred, yb).item()
                    n_val_batches += 1
            val_loss = val_loss_acc / max(n_val_batches, 1)

            scheduler.step(val_loss)
            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)

            if verbose and (epoch % 20 == 0 or epoch == 1):
                print(
                    f"  Epoch {epoch:4d}/{epochs} | "
                    f"train MSE = {train_loss:.4e} | "
                    f"val MSE   = {val_loss:.4e}"
                )

        return history

    # ------------------------------------------------------------------
    # Two-body direct correlation via autograd
    # ------------------------------------------------------------------

    def c2_at(self, rho: np.ndarray, x_idx: int) -> np.ndarray:
        """
        Two-body direct correlation c₂(x_fixed, x') = dc₁(x_fixed) / dρ(x').

        Computed via torch autograd (Jacobian of c₁[x_idx] w.r.t. rho).

        Parameters
        ----------
        rho   : np.ndarray (N,)
        x_idx : int — index of x where c₁ is evaluated

        Returns
        -------
        c2 : np.ndarray (N,) — ∂c₁(x_fixed) / ∂ρ(x') for x' on the grid
        """
        import torch

        self._ensure_model()
        N = len(rho)

        # We need gradients with respect to the full rho vector.
        # Strategy: build the full window matrix differentiably by embedding
        # rho in a padded tensor, then extract the single window at x_idx.

        half = self.n_window_bins // 2
        rho_t = torch.tensor(rho, dtype=torch.float32, device=self._device,
                              requires_grad=True)

        # Periodic padding  [rho[-half:], rho, rho[:half]]
        rho_padded = torch.cat([rho_t[-half:], rho_t, rho_t[:half]])

        # Extract window at x_idx (shift by half because of padding offset)
        window = rho_padded[x_idx: x_idx + self.n_window_bins].unsqueeze(0)  # (1, W)

        self._model.eval()
        c1_val = self._model(window).squeeze()  # scalar

        c1_val.backward()

        # rho_t.grad gives dc1(x_idx) / drho (full, with aliasing from PBC padding)
        grad = rho_t.grad.detach().cpu().numpy().astype(np.float64)
        return grad

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str) -> None:
        """Save model weights and hyperparameters to a .pt file."""
        import torch

        self._ensure_model()
        payload = {
            "window_width": self.window_width,
            "dx": self.dx,
            "hidden_dims": self.hidden_dims,
            "n_window_bins": self.n_window_bins,
            "state_dict": self._model.cpu().state_dict(),
        }
        torch.save(payload, path)
        if self._device is not None:
            self._model = self._model.to(self._device)

    @classmethod
    def load(cls, path: str) -> "NeuralC1Functional":
        """Load a previously saved NeuralC1Functional from a .pt file."""
        import torch

        payload = torch.load(path, map_location="cpu", weights_only=False)
        obj = cls(
            window_width=payload["window_width"],
            dx=payload["dx"],
            hidden_dims=payload["hidden_dims"],
        )
        obj.n_window_bins = payload["n_window_bins"]
        obj.build_model()
        obj._model.load_state_dict(payload["state_dict"])
        obj._model = obj._model.to(obj._device)
        return obj


# ---------------------------------------------------------------------------
# Training data generation
# ---------------------------------------------------------------------------

def generate_training_data(
    n_samples: int,
    L: float = 10.0,
    mu_range: tuple[float, float] = (-1.0, 3.0),
    n_bins: int = 1000,
    n_equil: int = 5_000,
    n_prod: int = 50_000,
    rng=None,
    verbose: bool = True,
) -> list[dict]:
    """
    Generate training data by running GCMC with random Vext for each sample.

    For each sample:
      1. Draw a random μ uniformly from mu_range.
      2. Generate a random Vext using generate_random_vext().
      3. Run GCMC to obtain ρ(x) and μ_loc(x).
      4. Compute c₁(x) = ln ρ(x) - μ_loc(x) (point-wise, skipping zeros).

    Parameters
    ----------
    n_samples : int
        Number of (ρ, c₁) profile pairs to generate.
    L : float
        Box length.
    mu_range : (float, float)
        Range for random chemical potential (β-units).
    n_bins : int
        Grid resolution.
    n_equil : int
        GCMC equilibration sweeps.
    n_prod : int
        GCMC production sweeps.
    rng : np.random.Generator, optional
    verbose : bool

    Returns
    -------
    data : list of dict, each with keys:
        'x'      : np.ndarray (n_bins,) — bin centres
        'rho'    : np.ndarray (n_bins,) — density profile
        'c1'     : np.ndarray (n_bins,) — one-body DCF
        'mu_loc' : np.ndarray (n_bins,) — local chemical potential (β-units)
    """
    from mlip_mc.dft.hard_rod_sim import simulate, generate_random_vext

    if rng is None:
        rng = np.random.default_rng()

    data = []
    skipped = 0

    for i in range(n_samples):
        mu = float(rng.uniform(*mu_range))
        vext_fn = generate_random_vext(L, rng=rng)

        x, rho, mu_loc = simulate(
            L=L,
            mu=mu,
            T=1.0,
            vext_fn=vext_fn,
            n_bins=n_bins,
            n_equil=n_equil,
            n_prod=n_prod,
            rng=rng,
        )

        # Skip frames where too many bins are empty (low statistics)
        zero_frac = np.mean(rho < 1e-8)
        if zero_frac > 0.5:
            skipped += 1
            if verbose:
                print(f"  Sample {i+1}/{n_samples}: skipped (zero_frac={zero_frac:.2f})")
            continue

        # c₁(x) = ln ρ(x) - β·μ_loc(x)  from simulation
        # Only valid where ρ > 0; set c₁ = 0 elsewhere (will be masked in training)
        with np.errstate(divide="ignore", invalid="ignore"):
            log_rho = np.where(rho > 1e-12, np.log(np.maximum(rho, 1e-12)), 0.0)
        c1 = log_rho - mu_loc

        # Mask out unreliable bins
        mask = rho > 1e-8
        c1 = np.where(mask, c1, 0.0)

        data.append({"x": x, "rho": rho, "c1": c1, "mu_loc": mu_loc})

        if verbose:
            n_avg = float(np.sum(rho) * (L / n_bins))
            print(
                f"  Sample {i+1}/{n_samples}: mu={mu:.2f}, "
                f"<N>={n_avg:.1f}, zero_frac={zero_frac:.2f}"
            )

    if verbose:
        print(f"\nGenerated {len(data)} samples ({skipped} skipped).")

    return data
