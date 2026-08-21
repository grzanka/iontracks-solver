# Domain problem and code walkthrough

*[↑ Session 1](README.md) · Prev: — · [Next: Why an on-prem LLM →](02-why-onprem-llms.md)*

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

## Scales that matter

Numbers below are from `SimulationConfig()`'s defaults — the kind of
concrete quantities worth putting on screen for a computer-science
audience.

- **Mesh.** 20 × 20 × 206 voxels at 10 µm/voxel → 200 µm × 200 µm × 2.06 mm.
  The z-extent already matches the real 2 mm electrode gap plus a 6-voxel
  electrode buffer; the lateral extent is the part that's shrunk down.
- **Why bigger grids matter.** A real Markus-chamber collecting electrode
  has a radius of ~2.65 mm, not the toy config's 60 µm sampled disc (44×
  larger). Keep the same voxel size and z-extent and scale the lateral
  extent up to that: 538 × 538 × 206 voxels (5.38 mm × 5.38 mm × 2.06 mm) —
  ~730× the memory (1.8 GiB vs. 2.5 MiB) and, because the number of tracks
  scales with area, ~1950× the tracks injected per pulse (178M vs. 91k).
  That gap between "runs on a laptop" and "resolves an actual detector" is
  why the performance work this afternoon isn't academic.
- **Time step.** dt = 383 ns, set by the von Neumann stability limit of the
  explicit scheme on a 10 µm voxel (diffusion and drift both constrain it —
  not an arbitrary round number).
- **Run length.** 1622 steps ≈ 621 µs of simulated time: one 540 µs
  macropulse (1412 steps) plus a 210-step clearance tail, long enough for
  drifting charge to finish leaving the gap.
- **Where that sits physically.** dt (383 ns) ≪ pulse (540 µs) ≪ pulse
  period (20 ms at 50 Hz) ≪ a treatment session (minutes). The solver only
  has to resolve the first two; nothing past the clearance tail affects
  `k_s`.
