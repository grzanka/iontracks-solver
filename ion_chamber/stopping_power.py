"""LET/stopping-power lookup and Gaussian track-radius estimate.

Both functions read small tabulated data files in ion_chamber/data/ so the
physics stays real (PSTAR stopping power, a fitted track-radius model)
without hand-picking numbers.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from ion_chamber.constants import AIR_DENSITY_KG_M3, JOULE_TO_KEV

DATA_DIR = Path(__file__).parent / "data"


def E_MeV_u_to_LET_keV_um(E_MeV_u, particle="proton"):
    """Interpolate the (dry air) stopping power from tabulated PSTAR data."""
    df = pd.read_csv(DATA_DIR / "stopping_power_air.csv", skiprows=3)
    particle_col = f"{particle}_LET_keV_um"
    if particle_col not in df.columns:
        raise ValueError(f"Particle '{particle}' not found in stopping power table")

    interpolate_LET = interp1d(df["E_MeV_u"], df[particle_col])
    return float(interpolate_LET(E_MeV_u))


def calc_track_radius_cm(LET_keV_um):
    """Gaussian track radius b [cm], fitted vs. log10(LET) (Rossomme et al.)."""
    data = np.genfromtxt(DATA_DIR / "LET_b.dat", delimiter=",", dtype=float)
    scale = 1e-3
    LET = data[:, 0] * scale
    b = data[:, 1]
    z = np.polyfit(np.log10(LET), b, 2)
    p = np.poly1d(z)

    b_cm = p(np.log10(LET_keV_um)) * 1e-3
    threshold = 2e-3
    return max(b_cm, threshold)


def dose_rate_to_fluence_rate(dose_rate_Gy_s, E_MeV_u, particle="proton", air_density_kg_m3=None):
    """Convert a dose-rate in dry air [Gy/s] to a fluence-rate [cm^-2 s^-1]."""
    LET_keV_um = E_MeV_u_to_LET_keV_um(E_MeV_u, particle)
    LET_keV_cm = LET_keV_um * 1e4
    density = AIR_DENSITY_KG_M3 if air_density_kg_m3 is None else air_density_kg_m3
    density_kg_cm3 = density * 1e-6
    return dose_rate_Gy_s * JOULE_TO_KEV * density_kg_cm3 / LET_keV_cm
