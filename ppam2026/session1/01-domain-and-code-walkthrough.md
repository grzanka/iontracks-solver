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
integrates the coupled drift-diffusion-recombination PDE with explicit
Lax-Wendroff finite differences.

This model -- and the original IonTracks code it's derived from
([jbrage/IonTracks](https://github.com/jbrage/IonTracks)) -- comes from
Jeppe Brage Christensen's work:

- Christensen, J. B., Tölli, H., & Bassler, N. (2016). A general algorithm
  for calculation of recombination losses in ionization chambers exposed
  to ion beams. *Medical Physics*, 43(10), 5484-5492.
  https://doi.org/10.1118/1.4962483
- Christensen, J. B., Almhagen, E., Stolarczyk, L., Liszka, M., Hernandez
  Hernandez, G., Bassler, N., et al. (2020). Mapping initial and general
  recombination in scanning proton pencil beams. *Physics in Medicine &
  Biology*, 65(11), 115003. https://doi.org/10.1088/1361-6560/ab8579

## Scales that matter

These are the actual numbers behind the default config
(`SimulationConfig()`).

### Space

| | Default (this workshop) | Full detector scale |
|---|---|---|
| Sampled radius | 60 µm | 2.65 mm (44×) |
| Grid, x × y × z | 20 × 20 × 206 voxels | 538 × 538 × 206 voxels |
| Physical size | 200 µm × 200 µm × 2.06 mm | 5.38 mm × 5.38 mm × 2.06 mm |
| Voxel size | 10 µm | 10 µm |
| Peak memory | 2.5 MiB | 1.8 GiB (~730×) |
| Tracks per pulse | 91 k | 178 M (~1950×) |

The z-extent (2.06 mm) already matches a real 2 mm electrode gap plus a
6-voxel electrode buffer — only the lateral extent is shrunk down. Scaling
that up to a real Markus-chamber collecting-electrode radius is the gap
between "runs on a laptop" and "resolves an actual detector," which is why
the performance work this afternoon isn't academic.

### Time

| Quantity | Value |
|---|---|
| Time step dt | 383 ns (von Neumann stability limit, 10 µm voxel) |
| One macropulse | 540 µs (1412 steps) |
| Clearance tail | 80 µs (210 steps) |
| Total simulated time | 621 µs (1622 steps) |
| Pulse period (50 Hz) | 20 ms |
| Typical treatment session | minutes |

dt ≪ pulse ≪ pulse period ≪ treatment session. The solver only has to
resolve the first two; nothing past the clearance tail changes `k_s`.

## Reading order

1. [`ion_chamber/config.py`](../../ion_chamber/config.py) — beam, chamber,
   and grid parameters, and what's derived from them (time step, track
   count).
2. [`ion_chamber/solver.py`](../../ion_chamber/solver.py) — the solver
   itself. Correct but deliberately naive — you'll find out exactly where
   the time goes this afternoon, once you profile it yourself.
3. [`ion_chamber/theory.py`](../../ion_chamber/theory.py) — the Jaffe
   closed form, independent of the grid.
4. [`tests/test_correctness.py`](../../tests/test_correctness.py) — how
   "still correct" gets checked after every change made today.
