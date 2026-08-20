#!/usr/bin/env python3
"""Time the default scenario across a range of thread counts and write the
results to a CSV -- the raw material for a "wall time / speedup vs. thread
count" plot.

    python sweep.py --out sweep.csv
    python sweep.py --threads 1 2 4 8 --out sweep.csv
"""

import argparse
import csv
import time

from ion_chamber.config import SimulationConfig
from ion_chamber.solver import run_simulation, warmup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threads", type=int, nargs="+", default=[1, 2, 4, 8])
    parser.add_argument("--radius-um", type=float, default=60.0)
    parser.add_argument("--repeats", type=int, default=1, help="repeat each thread count this many times")
    parser.add_argument("--out", default="sweep.csv")
    args = parser.parse_args()

    rows = []
    for threads in args.threads:
        for repeat in range(args.repeats):
            config = SimulationConfig(sampled_radius_cm=args.radius_um * 1e-4, seed=1)
            warmup(threads)  # excluded from the timed run
            t0 = time.perf_counter()
            result = run_simulation(config, progress=False, num_threads=threads)
            elapsed_s = time.perf_counter() - t0
            print(f"threads={threads:>3}  repeat={repeat}  wall={elapsed_s:.2f}s  ks={result.ks:.4f}")
            rows.append({"threads": threads, "repeat": repeat, "wall_s": elapsed_s, "ks": result.ks})

    with open(args.out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["threads", "repeat", "wall_s", "ks"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
