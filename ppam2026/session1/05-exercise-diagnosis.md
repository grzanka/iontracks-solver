# Exercise: diagnose before you optimize

The only goal this morning is a measurement-backed diagnosis. No code
changes yet — that's the afternoon session.

## Materials

- `ion_chamber/` — the solver under test.
- `bench.py` — one run, wall time and `k_s`.
- `sweep.py` — wall time across a range of thread counts, written to CSV.
- `tests/test_correctness.py` — checks against Jaffe theory; run it once
  now so everyone starts from a known-good baseline.

## Task

1. Run `pytest` once. Confirm green before touching anything else.
2. Run `python bench.py`. Note the wall time and `k_s`.
3. Ask the agent to profile a `bench.py` run — don't assume the
   parallelised loop is the hot path, check.
4. Run `python sweep.py --threads 1 2 4 8 --out sweep.csv` (adjust the
   thread list to Athena's actual core count — have the agent check it
   rather than guessing).
5. Have the agent plot wall time and speedup vs. thread count from
   `sweep.csv`.
6. Write three to five sentences: where the time goes, whether adding
   threads helps, and why — grounded in what the profiler and plot showed,
   not in Amdahl's law recited from memory.

## What "done" looks like

A plot, a profiler summary, and a short written diagnosis you could hand
to someone else and have them understand what's slow and why, without
reading the code themselves. That diagnosis is what gets compared against
the reference solution in the 16:30 synthesis.
