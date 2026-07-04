"""
External potential (V_ext) primitive library for cDFT data generation.

Each primitive is a callable (N,3) → (N,) that maps particle positions to
potential energy contributions in eV.  Primitives compose additively via
CompositeField.

YAML config syntax (see configs/v_ext_example.yaml):
  components:
    - type: hard_wall
      axis: 2          # z-axis
      z_lo: 0.0        # Å
      z_hi: 20.0       # Å
      strength: 1000.0 # eV·Å¹²
    - type: fourier
      axis: 2
      n_modes: 4
      amplitudes: [0.1, -0.05, 0.08, -0.03]   # eV
      phases: [0.0, 1.57, 0.3, 2.1]            # rad
      L: 20.0                                   # box length along axis
    - type: gaussian
      center: [10.0, 10.0, 10.0]               # Å
      amplitude: -0.2                           # eV (negative = attractive)
      sigma: 1.5                                # Å
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


class ExternalField(abc.ABC):
    """Abstract base for V_ext primitives."""

    @abc.abstractmethod
    def __call__(self, positions: np.ndarray) -> np.ndarray:
        """
        Parameters
        ----------
        positions : np.ndarray, shape (N, 3)
            Particle positions in Å.

        Returns
        -------
        np.ndarray, shape (N,)
            Per-particle potential energy in eV.
        """

    def total_energy(self, positions: np.ndarray) -> float:
        """Sum of per-particle contributions."""
        return float(self(positions).sum())

    def __add__(self, other: "ExternalField") -> "CompositeField":
        return CompositeField([self, other])


@dataclass
class HardWall(ExternalField):
    """Repulsive walls confining particles along one axis (WCA-like, r⁻¹²)."""
    axis: int = 2
    z_lo: float = 0.0
    z_hi: float = 20.0
    strength: float = 1000.0

    def __call__(self, positions: np.ndarray) -> np.ndarray:
        z = positions[:, self.axis]
        lo = self.strength / np.maximum((z - self.z_lo) ** 12, 1e-30)
        hi = self.strength / np.maximum((self.z_hi - z) ** 12, 1e-30)
        return lo + hi


@dataclass
class LinearRamp(ExternalField):
    """V_ext = slope * r_axis (gravity / sedimentation / electric field)."""
    axis: int = 2
    slope: float = 0.01

    def __call__(self, positions: np.ndarray) -> np.ndarray:
        return self.slope * positions[:, self.axis]


@dataclass
class GaussianPocket(ExternalField):
    """Attractive or repulsive Gaussian localisation potential."""
    center: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    amplitude: float = -0.2
    sigma: float = 1.5

    def __post_init__(self):
        self.center = np.asarray(self.center, dtype=float)

    def __call__(self, positions: np.ndarray) -> np.ndarray:
        dr = positions - self.center[None, :]
        r2 = (dr ** 2).sum(axis=1)
        return self.amplitude * np.exp(-r2 / (2.0 * self.sigma ** 2))


@dataclass
class Sinusoid(ExternalField):
    """Single sinusoidal mode along one axis."""
    axis: int = 2
    amplitude: float = 0.1
    frequency: float = 1.0    # cycles per Å
    phase: float = 0.0

    def __call__(self, positions: np.ndarray) -> np.ndarray:
        x = positions[:, self.axis]
        return self.amplitude * np.sin(2.0 * np.pi * self.frequency * x + self.phase)


@dataclass
class FourierSeries(ExternalField):
    """
    Sum of sinusoidal modes — the primary sampling distribution for
    generating diverse V_ext shapes (Sammüller 2024 protocol).

    V_ext(x) = Σ_k  A_k · sin(2π k x / L + φ_k)
    """
    axis: int = 2
    n_modes: int = 4
    amplitudes: np.ndarray = field(default_factory=lambda: np.zeros(4))
    phases: np.ndarray = field(default_factory=lambda: np.zeros(4))
    L: float = 20.0

    def __post_init__(self):
        self.amplitudes = np.asarray(self.amplitudes, dtype=float)
        self.phases = np.asarray(self.phases, dtype=float)

    def __call__(self, positions: np.ndarray) -> np.ndarray:
        x = positions[:, self.axis]
        result = np.zeros(len(positions))
        for k, (A, phi) in enumerate(zip(self.amplitudes, self.phases), start=1):
            result += A * np.sin(2.0 * np.pi * k * x / self.L + phi)
        return result


class CompositeField(ExternalField):
    """Sum of multiple ExternalField primitives."""

    def __init__(self, components: list[ExternalField]):
        self.components = components

    def __call__(self, positions: np.ndarray) -> np.ndarray:
        result = np.zeros(len(positions))
        for comp in self.components:
            result += comp(positions)
        return result

    def __add__(self, other: ExternalField) -> "CompositeField":
        return CompositeField(self.components + [other])


def random_fourier_field(
    axis: int = 2,
    n_modes: int = 4,
    amplitude_scale: float = 0.1,
    L: float = 20.0,
    rng: Optional[np.random.Generator] = None,
) -> FourierSeries:
    """
    Sample a random FourierSeries V_ext — the Sammüller 2024 protocol.

    Parameters
    ----------
    amplitude_scale : float
        Gaussian σ for amplitude sampling (eV).
    """
    if rng is None:
        rng = np.random.default_rng()
    amplitudes = rng.normal(0.0, amplitude_scale, size=n_modes)
    phases = rng.uniform(0.0, 2.0 * np.pi, size=n_modes)
    return FourierSeries(axis=axis, n_modes=n_modes, amplitudes=amplitudes,
                         phases=phases, L=L)


def from_yaml(path: Union[str, Path]) -> ExternalField:
    """
    Load a CompositeField from a YAML config file.

    See configs/v_ext_example.yaml for the schema.
    """
    if not _YAML_AVAILABLE:
        raise ImportError("pyyaml is required: pip install pyyaml")
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return _parse_config(cfg)


def from_dict(cfg: dict) -> ExternalField:
    """Build an ExternalField from a plain dict (e.g. parsed from YAML)."""
    return _parse_config(cfg)


_PRIMITIVE_MAP: dict[str, type] = {
    "hard_wall": HardWall,
    "linear_ramp": LinearRamp,
    "gaussian": GaussianPocket,
    "sinusoid": Sinusoid,
    "fourier": FourierSeries,
}


def _parse_config(cfg: dict) -> ExternalField:
    components_cfg = cfg.get("components", [cfg])  # allow single-component shorthand
    components: list[ExternalField] = []
    for comp_cfg in components_cfg:
        kind = comp_cfg.pop("type")
        cls = _PRIMITIVE_MAP.get(kind)
        if cls is None:
            raise ValueError(f"Unknown V_ext primitive: {kind!r}. "
                             f"Available: {list(_PRIMITIVE_MAP)}")
        components.append(cls(**comp_cfg))
    return components[0] if len(components) == 1 else CompositeField(components)
