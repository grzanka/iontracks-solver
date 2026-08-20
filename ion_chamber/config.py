"""Simulation configuration: physical inputs, and everything derived from them.

`SimulationConfig` is where a run is specified. Give it the beam, the
chamber and the grid; it works out the LET, the track radius, the number of
tracks, the stable time step and the run length.

Simplified from the full research code: one averaged carrier species (not
two resolved separately), an absorbing chamber wall, and scoring restricted
to the sampled disc. See docs/PHYSICS.md-style reasoning in the comments
below for what each field means.
"""

from dataclasses import dataclass
from math import pi, sqrt
from typing import Optional

import numpy as np

from ion_chamber.constants import (
    AIR_DENSITY_KG_M3,
    ION_DIFFUSION_CM2_S,
    ION_MOBILITY_CM2_VS,
    W_EV_PER_ION_PAIR,
)
from ion_chamber.stopping_power import E_MeV_u_to_LET_keV_um, calc_track_radius_cm, dose_rate_to_fluence_rate


def _von_neumann_dt(D_cm2_s, grid_spacing_cm, mu_cm2_Vs, Efield_V_cm):
    """Largest time step dt (starting from 1 s and shrinking) that satisfies the
    von Neumann stability criterion for the explicit Lax-Wendroff scheme,
    for full 3D diffusion (sx = sy = sz) and drift along z only.
    """
    dt = 1.0
    while True:
        dt /= 1.01
        s = D_cm2_s * dt / grid_spacing_cm**2
        c = mu_cm2_Vs * Efield_V_cm * dt / grid_spacing_cm
        if 6 * s + c**2 <= 1:
            return dt


@dataclass
class SimulationConfig:
    # --- beam / chamber physics ---
    E_MeV_u: float = 60.0
    particle: str = "proton"
    voltage_V: float = 300.0
    electrode_gap_cm: float = 0.2  # 2 mm, a Markus-type plane-parallel chamber

    # --- pulsed-beam timing ---
    pulse_duration_s: float = 540e-6  # one macropulse
    repetition_rate_hz: float = 50.0
    dose_rate_Gy_s: float = 60.0  # time-averaged dose rate (to air)
    n_pulses: int = 1
    n_clearance_separation_times: float = 2.0

    # --- grid (reduced/representative sub-volume, not a full chamber) ---
    grid_size_um: float = 10.0
    sampled_radius_cm: float = 0.006
    buffer_radius: int = 4
    no_z_electrode: int = 3

    # --- gas / carrier physics ---
    W_eV: float = W_EV_PER_ION_PAIR
    air_density_kg_m3: float = AIR_DENSITY_KG_M3

    seed: Optional[int] = None

    def __post_init__(self):
        self.unit_length_cm = self.grid_size_um * 1e-4
        self.LET_keV_um = E_MeV_u_to_LET_keV_um(self.E_MeV_u, self.particle)
        self.track_radius_cm = calc_track_radius_cm(self.LET_keV_um)
        self.Efield_V_cm = self.voltage_V / self.electrode_gap_cm
        self.area_cm2 = pi * self.sampled_radius_cm**2
        self.mu = ION_MOBILITY_CM2_VS
        self.D = ION_DIFFUSION_CM2_S

        # --- grid layout ---
        self.no_xy = int(round(2 * self.sampled_radius_cm / self.unit_length_cm)) + 2 * self.buffer_radius
        self.no_z = int(round(self.electrode_gap_cm / self.unit_length_cm))
        self.no_z_with_buffer = 2 * self.no_z_electrode + self.no_z
        if self.no_xy < 2 * self.buffer_radius + 2:
            raise ValueError(
                f"no_xy={self.no_xy} is too small for buffer_radius={self.buffer_radius}: "
                "increase sampled_radius_cm or decrease buffer_radius/grid_size_um."
            )

        # mid_xy is the grid's true continuous centre, no_xy / 2.0 -- kept as a
        # float (not floor-divided) so every (i - mid_xy) below is exact.
        self.outer_radius = self.no_xy / 2.0
        self.mid_xy = self.outer_radius
        self.sampling_radius = self.outer_radius - self.buffer_radius
        if self.sampling_radius <= 0:
            raise ValueError(
                f"sampling_radius = {self.sampling_radius:.3g} <= 0 (no_xy={self.no_xy}, "
                f"buffer_radius={self.buffer_radius}): sampled_radius_cm is too small "
                "relative to buffer_radius/grid_size_um."
            )
        self.sampling_radius_sq = self.sampling_radius**2
        # Tracks are counted and recombination is scored only inside this disc
        # (the "track_disc" convention -- charge that diffuses past it is
        # still counted as injected, but its later recombination is not).
        self.scoring_radius_sq = self.sampling_radius_sq

        # --- time step (von Neumann stability) ---
        self.dt = _von_neumann_dt(self.D, self.unit_length_cm, self.mu, self.Efield_V_cm)
        self.courant_number = self.mu * self.Efield_V_cm * self.dt / self.unit_length_cm

        # Half-gap transit time of the (single, averaged) carrier species, so
        # the clearance tail below is long enough to let injected charge
        # finish drifting out after the last pulse.
        self.separation_time_steps = int(self.electrode_gap_cm / (2.0 * self.mu * self.Efield_V_cm * self.dt))
        self.clearance_time_steps = int(round(self.n_clearance_separation_times * self.separation_time_steps))

        self.pulse_time_bins = np.arange(0.0, self.pulse_duration_s + self.dt, self.dt)
        self.pulse_time_steps = len(self.pulse_time_bins) - 1
        self.pulse_period_steps = (
            int(round(1.0 / self.repetition_rate_hz / self.dt)) if self.repetition_rate_hz > 0 else self.pulse_time_steps
        )
        if self.n_pulses > 1 and self.pulse_period_steps < self.pulse_time_steps:
            raise ValueError(
                "Pulse period is shorter than the pulse itself at this dt; "
                "reduce pulse_duration_s or repetition_rate_hz."
            )
        self.total_time_steps = (
            (self.n_pulses - 1) * self.pulse_period_steps + self.pulse_time_steps + self.clearance_time_steps
        )

        # --- Gaussian track structure ---
        LET_eV_cm = self.LET_keV_um * 1e7
        self.N0 = LET_eV_cm / self.W_eV
        self.Gaussian_factor = self.N0 / (pi * self.track_radius_cm**2)

        # --- number of tracks injected per pulse, from the average dose rate ---
        dose_per_pulse_Gy = self.dose_rate_Gy_s / self.repetition_rate_hz
        instantaneous_dose_rate_Gy_s = dose_per_pulse_Gy / self.pulse_duration_s
        fluence_rate_inst_cm2_s = dose_rate_to_fluence_rate(
            instantaneous_dose_rate_Gy_s, self.E_MeV_u, self.particle, air_density_kg_m3=self.air_density_kg_m3
        )
        self.number_of_tracks_per_pulse = max(
            1, int(round(fluence_rate_inst_cm2_s * self.pulse_duration_s * self.area_cm2))
        )

        self.estimated_memory_bytes = 4 * self.no_xy**2 * self.no_z_with_buffer * 8

    def scheme_coefficients(self):
        """Lax-Wendroff stencil weights ``(lateral, z_minus, z_plus, centre)``
        for the six face neighbours and the voxel itself."""
        s = self.D * self.dt / self.unit_length_cm**2
        c = self.mu * self.Efield_V_cm * self.dt / self.unit_length_cm
        return (s, s + c * (c + 1.0) / 2.0, s + c * (c - 1.0) / 2.0, 1.0 - c * c - 6.0 * s)

    def summary(self) -> str:
        return (
            f"Particle              : {self.particle} @ {self.E_MeV_u:.1f} MeV/u "
            f"(LET = {self.LET_keV_um:.3g} keV/um, track radius b = {self.track_radius_cm * 1e4:.3g} um)\n"
            f"Chamber               : gap = {self.electrode_gap_cm} cm, V = {self.voltage_V} V "
            f"(E = {self.Efield_V_cm:.4g} V/cm)\n"
            f"Sampled sub-volume    : radius = {self.sampled_radius_cm * 1e4:.3g} um, area = {self.area_cm2:.3g} cm^2\n"
            f"Grid                  : {self.no_xy} x {self.no_xy} x {self.no_z_with_buffer} voxels "
            f"({self.unit_length_cm * 1e4:.3g} um/voxel), "
            f"{self.estimated_memory_bytes / 2**20:.1f} MiB peak\n"
            f"Time step dt          : {self.dt * 1e9:.1f} ns (Courant {self.courant_number:.3f})\n"
            f"Pulse                 : {self.pulse_duration_s * 1e6:.1f} us ({self.pulse_time_steps} steps), "
            f"{self.number_of_tracks_per_pulse} tracks, {self.repetition_rate_hz} Hz, {self.n_pulses} pulse(s)\n"
            f"Total simulated time  : {self.total_time_steps * self.dt * 1e6:.3g} us "
            f"({self.total_time_steps} steps)"
        )
