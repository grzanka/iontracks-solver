"""Analytic reference used to sanity-check the PDE simulation.

Jaffe theory: a closed-form expression for the initial recombination of a
*single* ion track (valid in the low-dose / single-track limit -- no
track-to-track overlap). It has nothing to do with the PDE grid, the time
step, or the number of tracks simulated, so it is an independent check: if
the simulator's k_s does not converge towards jaffe_ks() as the simulated
dose is lowered, something in the simulator is wrong, not just imprecise.

Reference: Jaffe, G. (1913), theory of initial recombination.
"""

from math import log, pi

import mpmath

from ion_chamber.constants import ION_DIFFUSION_CM2_S, ION_MOBILITY_CM2_VS, W_EV_PER_ION_PAIR
from ion_chamber.stopping_power import calc_track_radius_cm

mpmath.mp.dps = 50  # precision for the exponential-integral evaluation

_ALPHA_CM3_S = 1.60e-6  # Jaffe/Boag recombination constant (Kanai et al. 1998)


def jaffe_ks(LET_keV_um, voltage_V, electrode_gap_cm, W_eV=None, mu=None, D=None, alpha=None):
    """Jaffe theory recombination correction factor k_s = 1/f for a single track."""
    W_eV = W_EV_PER_ION_PAIR if W_eV is None else W_eV
    mu = ION_MOBILITY_CM2_VS if mu is None else mu
    D = ION_DIFFUSION_CM2_S if D is None else D
    alpha = _ALPHA_CM3_S if alpha is None else alpha

    LET_eV_cm = LET_keV_um * 1e7
    electric_field = voltage_V / electrode_gap_cm
    b_cm = calc_track_radius_cm(LET_keV_um)

    N0 = LET_eV_cm / W_eV
    g = alpha * N0 / (8.0 * pi * D)

    factor = mpmath.exp(-1.0 / g) * mu * b_cm**2 * electric_field / (2.0 * g * electrode_gap_cm * D)
    first_term = mpmath.ei(1.0 / g + log(1.0 + (2.0 * electrode_gap_cm * D / (mu * b_cm**2 * electric_field))))
    second_term = mpmath.ei(1.0 / g)
    f = factor * (first_term - second_term)
    return float(1.0 / f)
