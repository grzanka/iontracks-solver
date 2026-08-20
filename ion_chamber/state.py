"""Run state that lives outside the JIT kernels: what a finished run hands
back, and the per-time-step record accumulated while it runs.

The chamber wall is absorbing (the default in the original IonTracks-Cython
model this is ported from): the outer voxel ring simply stays at zero for
the whole run, so there is no boundary-condition bookkeeping here at all.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class Result:
    """Everything a finished run hands back.

    Densities are in cm^-3 and the summed quantities are density sums over
    voxels, not absolute counts -- the voxel volume cancels in the collection
    efficiency, so the solver never multiplies it back in.
    """

    config: object  # the SimulationConfig this run was built from
    time_s: np.ndarray  # end-of-step time, seconds
    f_t: np.ndarray  # collection efficiency so far: (injected - recombined) / injected
    ks: float  # recombination correction factor 1/f after full clearance
    positive_array: np.ndarray  # final density snapshot, shape (no_xy, no_xy, no_z_with_buffer)
    negative_array: np.ndarray


class Diagnostics:
    """Accumulates the per-time-step injected/recombined record while a run
    proceeds. Deliberately not a jitted structure: the kernels return
    scalars and this stores them."""

    def __init__(self, config):
        self.injected = np.zeros(config.total_time_steps)
        self.recombined = np.zeros(config.total_time_steps)

    def record(self, step: int, injected: float, recombined: float) -> None:
        self.injected[step] = injected
        self.recombined[step] = recombined

    def build_result(self, config, time_s, f_t, ks, positive_array, negative_array) -> Result:
        return Result(
            config=config,
            time_s=time_s,
            f_t=f_t,
            ks=ks,
            positive_array=positive_array,
            negative_array=negative_array,
        )
