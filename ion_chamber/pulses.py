"""Pulse-train track scheduling: when (which time step) and where (which xy
position) each ion track is injected into the grid.

Track arrival times within a pulse are spread out using a cumulative-sum-of
-uniforms trick, an easy way to get an increasing sequence of arrival times
without rejection sampling in time. xy positions are rejection-sampled
uniformly inside the sampled disc.
"""

import numpy as np


def build_track_schedule(config, rng: np.random.Generator) -> np.ndarray:
    """Return an int array of length config.total_time_steps: the number of
    new tracks to insert at each time step, repeated every pulse_period_steps
    for config.n_pulses pulses.
    """
    schedule = np.zeros(config.total_time_steps, dtype=np.int64)
    counts = _sample_pulse_arrival_histogram(config, rng)
    for pulse_index in range(config.n_pulses):
        start = pulse_index * config.pulse_period_steps
        schedule[start : start + len(counts)] += counts
    return schedule


def _sample_pulse_arrival_histogram(config, rng: np.random.Generator) -> np.ndarray:
    n_tracks = config.number_of_tracks_per_pulse
    summed = np.cumsum(rng.random(n_tracks))
    summed /= summed[-1]
    summed *= config.pulse_duration_s
    counts, _ = np.histogram(summed, config.pulse_time_bins)
    return counts.astype(np.int64)


def sample_xy_batch(rng: np.random.Generator, mid_xy: float, radius: float, no_xy: int, n: int):
    """Rejection-sample ``n`` grid coordinates uniformly inside the disc of
    the given ``radius``, centred at ``(mid_xy, mid_xy)``."""
    if n == 0:
        return np.empty(0), np.empty(0)

    radius_sq = radius * radius
    accept_rate = min(1.0, max(0.05, pi_area_ratio(radius, no_xy)))
    xs_parts, ys_parts = [], []
    remaining = n
    while remaining > 0:
        m = max(64, int(remaining / accept_rate * 1.3))
        x = rng.uniform(0.0, no_xy, m)
        y = rng.uniform(0.0, no_xy, m)
        mask = (x - mid_xy) ** 2 + (y - mid_xy) ** 2 <= radius_sq
        xs_parts.append(x[mask][:remaining])
        ys_parts.append(y[mask][:remaining])
        remaining -= len(xs_parts[-1])
    return np.concatenate(xs_parts), np.concatenate(ys_parts)


def pi_area_ratio(radius: float, no_xy: int) -> float:
    return np.pi * radius * radius / (no_xy * no_xy)
