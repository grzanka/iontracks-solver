# iontracks-solver

> **Training material.** This repository exists to teach performance
> engineering with an AI coding agent on a real, physically-validated PDE
> solver. It is a deliberately simplified, deliberately slow starting point
> for a workshop exercise, not a scientific reference implementation and not
> a maintained research codebase. If you found this looking for a validated
> ion-recombination model, this isn't it.

**How much charge does an ionisation chamber lose to recombination when a
proton beam arrives in short, intense pulses?**

An ionisation chamber measures dose by collecting the charge a beam
liberates in its gas, on the assumption that the charge it collects is the
charge that was created. Recombination breaks that assumption: positive and
negative ions that meet before reaching an electrode annihilate and are
never counted. The correction factor is `k_s = 1/f`, and computing it is
what this code does.

The approach: simulate it directly. Protons enter the gas as individual
Gaussian ion tracks (not a smooth density), and the coupled
drift-diffusion-recombination equations

```
dn+/dt = D grad^2 n+  -  mu E . grad n+  -  alpha n+ n-  +  tracks
dn-/dt = D grad^2 n-  +  mu E . grad n-  -  alpha n+ n-  +  tracks
```

are advanced on a small 3D voxel grid with an explicit finite-difference
scheme (Lax-Wendroff), one time step at a time.

## What's here

- `ion_chamber/solver.py` -- the solver. **This is the code you're here to
  work on.** It is correct and it is slow; the module docstring says why.
- `ion_chamber/config.py` -- everything a run needs (beam, chamber, grid),
  and everything derived from it (time step, track count, ...).
- `ion_chamber/theory.py` -- Jaffe theory, a closed-form single-track
  recombination formula. Independent of the grid/solver entirely, so it's a
  correctness anchor: the simulator's `k_s` should approach it as the dose
  per pulse is lowered towards the single-track limit.
- `bench.py` -- run the default scenario once, print wall time and `k_s`.
- `sweep.py` -- time it across a range of thread counts, write a CSV.
- `tests/` -- `test_correctness.py` checks against Jaffe theory;
  `test_smoke.py` is a fast sanity check, including that 1 and 2 threads
  agree on the answer.

## Quick start

```bash
python -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -e ".[dev]"
```

```bash
pytest  # a few seconds
```

```bash
python bench.py
```

```bash
python sweep.py --threads 1 2 4 8 --out sweep.csv
```

## The task

The solver above is a working baseline, not a finished one. Two questions to
answer with real measurements, not guesses:

1. **Where does the time actually go?** Profile a run. Don't assume the
   parallelised loop is where the time is spent -- check.
2. **Does adding threads help?** Run `sweep.py` across a range of thread
   counts and plot wall time and speedup against it. Explain the shape you
   see, grounded in what the profiler showed, not in what you'd expect from
   Amdahl's law in the abstract.

Once you have a diagnosis, the next question is what to actually change --
algorithmically, in how work is parallelised, or both -- and whether each
change helps for the reason you expected. Re-run `pytest` after every change:
correctness matters as much as speed here, and it's cheap to check.

## A note on the physics

The chamber, grid and pulse timing in `config.py`'s defaults are a small,
fast representative sub-volume of a real plane-parallel ionisation chamber
(a Markus-type detector, 2 mm electrode gap) -- not a dosimetrically
converged simulation of a full chamber. That's deliberate: it keeps a
correctness check and a full sweep fast enough to iterate on. The physics
(stopping power, track structure, drift-diffusion-recombination) is real
throughout.
