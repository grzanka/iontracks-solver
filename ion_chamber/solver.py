"""The starting-point solver for the workshop. It is deliberately slow.

Two things happen per time step:

1. **Track deposition.** Each proton track arriving this step writes a 2D
   Gaussian charge cross-section into the grid, repeated along every layer
   of the gap (a track is a straight line through it). This runs
   single-threaded, once per track.

2. **The PDE sweep.** A Lax-Wendroff step advances both carrier densities
   (drift + diffusion + recombination) by one time step. This loop is
   parallelised with Numba's ``prange`` over the outer (x) axis.

Both kernels compute the same physics as a careful implementation would;
nothing here is numerically wrong.
"""

from math import ceil, exp, floor
from time import perf_counter
from typing import Optional

import numba
import numpy as np
import numpy.typing as npt
from numba import prange

from ion_chamber.config import SimulationConfig
from ion_chamber.constants import RECOMBINATION_ALPHA_CM3_S
from ion_chamber.pulses import build_track_schedule, sample_xy_batch
from ion_chamber.state import Diagnostics, Result

FloatArray3D = npt.NDArray[np.float64]
FloatArray1D = npt.NDArray[np.float64]


@numba.njit(cache=True)
def insert_track(
    positive_array: FloatArray3D,
    negative_array: FloatArray3D,
    x: float,
    y: float,
    no_xy: int,
    no_z: int,
    no_z_electrode: int,
    h2: float,
    b2: float,
    gaussian_factor: float,
    mid_xy: float,
    scoring_radius_sq: float,
) -> float:
    """Deposit one track's Gaussian into both carrier arrays.

    Returns the charge that landed inside the scored region, so the caller
    can accumulate the injected total without a second pass.

    ``(x, y)`` is in fractional voxel units. ``h2`` is the voxel area and
    ``b2`` the squared Gaussian track radius, both in cm^2.
    """
    k_lo = no_z_electrode
    k_hi = no_z_electrode + no_z

    inserted = 0.0
    for i in range(no_xy):
        di_sq = (i - mid_xy) ** 2
        for j in range(no_xy):
            r_sq = (i - x) ** 2 + (j - y) ** 2
            ion_density = gaussian_factor * exp(-r_sq * h2 / b2)
            for k in range(k_lo, k_hi):
                positive_array[i, j, k] += ion_density
                negative_array[i, j, k] += ion_density
            if 1 <= i <= no_xy - 2 and 1 <= j <= no_xy - 2 and di_sq + (j - mid_xy) ** 2 < scoring_radius_sq:
                inserted += ion_density * no_z

    return inserted


@numba.njit(parallel=True, cache=True)
def lax_wendroff_step(
    positive_array: FloatArray3D,
    negative_array: FloatArray3D,
    positive_next: FloatArray3D,
    negative_next: FloatArray3D,
    no_xy: int,
    no_z_with_buffer: int,
    no_z_electrode: int,
    no_z: int,
    mid_xy: float,
    scoring_radius_sq: float,
    lat: float,
    zm: float,
    zp: float,
    cen: float,
    alpha_dt: float,
) -> float:
    """Advance both carrier densities by one time step.

    Stencil weights are the same for both species here (one averaged
    mobility/diffusion pair); the two species drift in opposite directions,
    so the z-neighbour weights are swapped between the positive and negative
    update. Returns the recombination summed over the scored region.
    """
    recombined = 0.0
    for i in prange(1, no_xy - 1):
        di_sq = (i - mid_xy) ** 2
        for j in range(1, no_xy - 1):
            inside = di_sq + (j - mid_xy) ** 2 < scoring_radius_sq

            for k in range(1, no_z_with_buffer - 1):
                p = positive_array[i, j, k]
                n = negative_array[i, j, k]

                p_new = (
                    zm * positive_array[i, j, k - 1]
                    + zp * positive_array[i, j, k + 1]
                    + lat * positive_array[i, j - 1, k]
                    + lat * positive_array[i, j + 1, k]
                    + lat * positive_array[i - 1, j, k]
                    + lat * positive_array[i + 1, j, k]
                    + cen * p
                )
                n_new = (
                    zp * negative_array[i, j, k - 1]
                    + zm * negative_array[i, j, k + 1]
                    + lat * negative_array[i, j - 1, k]
                    + lat * negative_array[i, j + 1, k]
                    + lat * negative_array[i - 1, j, k]
                    + lat * negative_array[i + 1, j, k]
                    + cen * n
                )

                recomb = alpha_dt * p * n
                positive_next[i, j, k] = p_new - recomb
                negative_next[i, j, k] = n_new - recomb

                if inside and no_z_electrode <= k < (no_z + no_z_electrode):
                    recombined += recomb

    return recombined


def warmup(num_threads: int = 1) -> None:
    """Trigger Numba JIT compilation of both hot loops on minimal dummy
    arrays, so a subsequent timed call to run_simulation() measures only
    execution time, not one-time compilation."""
    numba.set_num_threads(num_threads)
    shape = (4, 4, 4)
    p, n, p_next, n_next = (np.zeros(shape) for _ in range(4))
    insert_track(p, n, 2.0, 2.0, 4, 1, 1, 1.0, 1.0, 1.0, 2.0, 1.0)
    lax_wendroff_step(p, n, p_next, n_next, 4, 4, 1, 1, 2.0, 1.0, 0.01, 0.01, 0.01, 0.97, 1e-9)


def run_simulation(
    config: SimulationConfig,
    rng: Optional[np.random.Generator] = None,
    progress: bool = True,
    num_threads: int = 1,
) -> Result:
    """Simulate a pulse train and return the full run record."""
    numba.set_num_threads(num_threads)
    rng = rng if rng is not None else np.random.default_rng(config.seed)
    schedule = build_track_schedule(config, rng)

    shape = (config.no_xy, config.no_xy, config.no_z_with_buffer)
    positive_array: FloatArray3D = np.zeros(shape)
    negative_array: FloatArray3D = np.zeros(shape)
    positive_next: FloatArray3D = np.zeros(shape)
    negative_next: FloatArray3D = np.zeros(shape)

    lat, zm, zp, cen = config.scheme_coefficients()
    alpha_dt = RECOMBINATION_ALPHA_CM3_S * config.dt

    h2 = config.unit_length_cm**2
    b2 = config.track_radius_cm**2

    no_initialised = 0.0
    no_recombined = 0.0
    f_t: FloatArray1D = np.ones(config.total_time_steps)
    diagnostics = Diagnostics(config)
    report_every = max(1, config.total_time_steps // 20)
    t0 = perf_counter()

    for step in range(config.total_time_steps):
        n_tracks = int(schedule[step])
        step_xs, step_ys = sample_xy_batch(rng, config.mid_xy, config.sampling_radius, config.no_xy, n_tracks)

        injected_this_step = 0.0
        for x, y in zip(step_xs, step_ys):
            injected_this_step += insert_track(
                positive_array,
                negative_array,
                x,
                y,
                config.no_xy,
                config.no_z,
                config.no_z_electrode,
                h2,
                b2,
                config.Gaussian_factor,
                config.mid_xy,
                config.scoring_radius_sq,
            )

        no_initialised += injected_this_step
        recombined = lax_wendroff_step(
            positive_array,
            negative_array,
            positive_next,
            negative_next,
            config.no_xy,
            config.no_z_with_buffer,
            config.no_z_electrode,
            config.no_z,
            config.mid_xy,
            config.scoring_radius_sq,
            lat,
            zm,
            zp,
            cen,
            alpha_dt,
        )
        no_recombined += recombined
        diagnostics.record(step, injected_this_step, recombined)

        # Interior only, then swap: the outer ring stays at zero (absorbing
        # wall), so nothing needs to be carried over across the swap.
        positive_array[1:-1, 1:-1, 1:-1] = positive_next[1:-1, 1:-1, 1:-1]
        negative_array[1:-1, 1:-1, 1:-1] = negative_next[1:-1, 1:-1, 1:-1]

        f_t[step] = 1.0 if no_initialised == 0.0 else (no_initialised - no_recombined) / no_initialised

        if progress and step % report_every == 0:
            print(f"  step {step + 1}/{config.total_time_steps}  f = {f_t[step]:.4f}")

    elapsed_s = perf_counter() - t0
    if progress:
        print(f"  ({elapsed_s:.2f} s, {num_threads} thread(s))")

    time_s: FloatArray1D = (np.arange(config.total_time_steps) + 1) * config.dt
    ks = 1.0 / f_t[-1]
    return diagnostics.build_result(config, time_s, f_t, ks, positive_array, negative_array)
