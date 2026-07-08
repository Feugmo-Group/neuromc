"""
neuromc.dft — GCMC data-generation factory for cDFT neural-operator training.

Maps the operator  G: V_ext(r) → {ρ(r), c⁽¹⁾(r), c⁽²⁾(r,r')}
using GCMC with pluggable pair interactions (MLIP or analytic) and
a composable library of external potentials.

References
----------
Sammüller et al., J. Phys.: Condens. Matter 36, 243002 (2024)
Evans et al., Phys. Rev. Lett. 134, 148001 (2025)
"""

from .external_field import (
    ExternalField,
    HardWall,
    LinearRamp,
    GaussianPocket,
    Sinusoid,
    FourierSeries,
    CompositeField,
    from_yaml,
    random_fourier_field,
)
from .density_grid import DensityGrid1D, DensityGrid3D
from .sample_writer import SampleWriter
from .pair_dist import PairDistBulk, PairDistPlanar
from .oz import oz_inversion_3d, oz_inversion_1d, free_energy_excess_ti
from .hard_rod_sim import HardRodSystem, simulate, generate_random_vext
from .percus import percus_weights, c1_percus, dft_minimize
from .rpm_sim import RPMSystem, simulate_rpm, lmft_potential
from .widom import (
    WidomHardRod,
    widom_hard_rod,
    WidomRPM,
    widom_rpm,
)

# Requires ASE + MLIP backend — imported conditionally
try:
    from .particle_gcmc import (
        ParticleGCMC,
        simulate_particle_gcmc,
        generate_cdft_training_data,
    )
    _PARTICLE_GCMC_AVAILABLE = True
except ImportError:
    _PARTICLE_GCMC_AVAILABLE = False

__all__ = [
    "ExternalField",
    "HardWall",
    "LinearRamp",
    "GaussianPocket",
    "Sinusoid",
    "FourierSeries",
    "CompositeField",
    "from_yaml",
    "random_fourier_field",
    "DensityGrid1D",
    "DensityGrid3D",
    "SampleWriter",
    "PairDistBulk",
    "PairDistPlanar",
    "oz_inversion_3d",
    "oz_inversion_1d",
    "free_energy_excess_ti",
    "HardRodSystem",
    "simulate",
    "generate_random_vext",
    "percus_weights",
    "c1_percus",
    "dft_minimize",
    "RPMSystem",
    "simulate_rpm",
    "lmft_potential",
    "WidomHardRod",
    "widom_hard_rod",
    "WidomRPM",
    "widom_rpm",
    "ParticleGCMC",
    "simulate_particle_gcmc",
    "generate_cdft_training_data",
]
