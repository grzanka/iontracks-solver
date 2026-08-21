# Domain problem and code walkthrough

Talking points for the first walkthrough, before anyone opens the agent.

## The problem

A plane-parallel ionization chamber under a pulsed proton beam.
Recombination before collection means the chamber under-reports dose; the
correction is `k_s = 1/f`. Jaffe theory gives a closed-form `k_s` for a
single track and is the correctness anchor for the whole day — the
simulator's `k_s` must converge to it as dose per pulse goes to zero.

Why this can't be a smooth-density diffusion problem: recombination is an
interaction between individual positive and negative ion pairs, so the
simulator seeds the grid with discrete Gaussian tracks (one per proton) and
integrates the coupled drift-diffusion-recombination PDE
(`ion_chamber/solver.py`) with explicit Lax-Wendroff finite differences.

## Reading order

1. `ion_chamber/config.py` — beam, chamber, and grid parameters, and what's
   derived from them (time step, track count).
2. `ion_chamber/solver.py` — the solver itself. Point out where it's
   correct but naive; don't say where the time actually goes yet, that's
   this afternoon's measurement, not a spoiler for the walkthrough.
3. `ion_chamber/theory.py` — the Jaffe closed form, independent of the
   grid.
4. `tests/test_correctness.py` — how "still correct" gets checked after
   every change made today.

## Worth saying out loud, not just showing

- Why per-track simulation instead of a smooth source term.
- Why the grid is a small, fast, representative sub-volume rather than a
  full chamber (the top-level README's physics note covers this — worth
  reading aloud once).
- That `bench.py` and `sweep.py` exist so nobody has to hand-write timing
  code before lunch.
