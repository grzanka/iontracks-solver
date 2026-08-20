"""Correctness check against the analytic Jaffe theory.

Jaffe theory is the exact single-track (low-dose) limit: no track-to-track
overlap, so its k_s is a lower bound the simulator should approach as the
dose per pulse is lowered. This is the check to re-run after every change to
the solver -- if it drifts, the change broke the physics, not just the
speed.
"""

from ion_chamber.config import SimulationConfig
from ion_chamber.solver import run_simulation
from ion_chamber.theory import jaffe_ks


def test_single_track_limit_matches_jaffe():
    # A tiny dose rate means, on average, far less than one track per pulse
    # inside the scored disc -- close enough to the single-track limit for
    # Jaffe theory to be a fair reference, on a grid small enough to run in
    # well under a second.
    config = SimulationConfig(sampled_radius_cm=30e-4, buffer_radius=4, dose_rate_Gy_s=0.05, seed=1)
    result = run_simulation(config, progress=False, num_threads=1)

    reference = jaffe_ks(config.LET_keV_um, config.voltage_V, config.electrode_gap_cm)

    # Loose tolerance: this is a stochastic simulation (Poisson-ish track
    # arrivals) on a small grid, not a deterministic numerical scheme -- it
    # is meant to land in the right ballpark of the analytic answer, not
    # reproduce it to machine precision.
    assert abs(result.ks - reference) / reference < 0.15
