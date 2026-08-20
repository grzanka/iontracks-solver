"""Fast smoke tests: the solver runs, produces a physically sane answer, and
1 and 2 threads agree (the PDE sweep is the only parallelised kernel, and
its answer must not depend on thread count)."""

import numpy as np

from ion_chamber.config import SimulationConfig
from ion_chamber.solver import run_simulation


def _tiny_config():
    return SimulationConfig(sampled_radius_cm=20e-4, buffer_radius=3, dose_rate_Gy_s=20.0, seed=7)


def test_collection_efficiency_is_physical():
    result = run_simulation(_tiny_config(), progress=False, num_threads=1)
    assert 0.0 < result.f_t[-1] <= 1.0
    assert result.ks >= 1.0


def test_thread_count_does_not_change_the_answer():
    ks_values = [run_simulation(_tiny_config(), progress=False, num_threads=t).ks for t in (1, 2)]
    assert np.isclose(ks_values[0], ks_values[1], rtol=1e-9)
