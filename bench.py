#!/usr/bin/env python3
"""Run the default scenario once and report wall time and the recombination
correction factor.

    python bench.py                  # 1 thread
    python bench.py --threads 4      # 4 threads for the PDE sweep
    python bench.py --radius-um 80   # a bigger sampled column (more tracks, bigger grid)
"""

import argparse
import time

from ion_chamber.config import SimulationConfig
from ion_chamber.solver import run_simulation, warmup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threads", type=int, default=1, help="thread count for the PDE sweep")
    parser.add_argument("--radius-um", type=float, default=60.0, help="sampled column radius, in um")
    parser.add_argument("--seed", type=int, default=1, help="RNG seed")
    parser.add_argument("--quiet", action="store_true", help="suppress per-step progress output")
    args = parser.parse_args()

    config = SimulationConfig(sampled_radius_cm=args.radius_um * 1e-4, seed=args.seed)
    print(config.summary())
    print()

    warmup(args.threads)  # one-off JIT compilation, excluded from the timing below
    t0 = time.perf_counter()
    result = run_simulation(config, progress=not args.quiet, num_threads=args.threads)
    elapsed_s = time.perf_counter() - t0

    print(f"\nWall time ({args.threads} thread(s)): {elapsed_s:.2f} s")
    print(f"Collection efficiency f      = {result.f_t[-1]:.4f}")
    print(f"Recombination factor  k_s = 1/f = {result.ks:.4f}")


if __name__ == "__main__":
    main()
