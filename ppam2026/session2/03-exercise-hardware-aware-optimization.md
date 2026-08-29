# Exercise: hardware-aware optimization

*[↑ Session 2](README.md) · [← Prev: Exercise: algorithmic optimization](02-exercise-algorithmic-optimization.md) · [Next: Session 3 →](../session3/01-solution-reveal-and-synthesis.md)*

Continuing in the same opencode session as
[the previous file](02-exercise-algorithmic-optimization.md) — no new
`srun` needed unless your allocation's `--time` ran out, in which case
repeat [Resume your session](02-exercise-algorithmic-optimization.md#resume-your-session)
first.

With the algorithmic fix committed, the question changes: not "make it
faster" but "given this job's actual cores, cache, and NUMA layout —
found this morning with `lscpu`, `nproc`, `taskset`, and `numactl`, see
[session1/06](../session1/06-exercise-diagnosis.md) — how (and whether)
should this parallelize?"

## Task

1. **opencode.** This morning's sweep (before today's algorithmic fix)
   showed threading not helping, or actively hurting, at the default
   grid size. Re-run that same kind of sweep now, on top of the fix, and
   make the agent explain the result from this run's numbers — not from
   general parallel-computing rules of thumb.

   <details>
   <summary>Example prompt</summary>

   ```
   Re-run a thread-count sweep like this morning's (same --threads
   list), now on top of today's algorithmic fix. Does the parallelised
   PDE sweep pay off yet at this grid size, or is per-step overhead --
   plus our cores being scattered across NUMA nodes -- still bigger
   than any parallel win? Explain using this run's numbers.
   ```
   </details>

2. **opencode.** Push for a concrete, hardware-grounded recommendation,
   not a hedge.

   <details>
   <summary>Example prompt</summary>

   ```
   Given the cache sizes and NUMA layout from this morning, and the
   working-set size at the default grid (no_xy x no_xy x
   no_z_with_buffer, four f64 arrays), what thread count -- if any --
   actually makes sense at this problem size right now? Would that
   answer change at a bigger grid?
   ```
   </details>

3. **opencode.** That last question is worth actually testing rather
   than trusting the agent's extrapolation. [Session 1's domain
   notes](../session1/01-domain-and-code-walkthrough.md) named the real
   target this whole exercise has been a stand-in for: a full
   Markus-chamber scale of 2.65 mm sampled radius — 538×538×206 voxels,
   ~178 million tracks per pulse, vs. today's 60 µm / 20×20×206 / ~91 k.
   Jumping straight there risks a run that doesn't finish in the room:
   the PDE sweep's cost grows with grid area, and track count grows with
   sampled area too, so total cost climbs faster than the radius alone
   even after today's fix. Estimate before you launch anything large.

   <details>
   <summary>Example prompt</summary>

   ```
   Increase --radius-um from 60 to something like 150 or 200 and
   re-run the sweep at a couple of thread counts. Does the picture
   change -- does more threads help now that there's more work per
   step?
   ```
   </details>

   <details>
   <summary>Example prompt</summary>

   ```
   Using the timings from a couple of --radius-um sizes, estimate how
   long a run at session 1's "full detector scale" (2.65 mm radius,
   538x538x206 voxels, ~178 million tracks/pulse) would take now, and
   at how many threads. Don't launch that run -- just estimate, and
   show the reasoning, not just a number.
   ```
   </details>

   <details>
   <summary>Example prompt</summary>

   ```
   Given that estimate, what's the largest --radius-um you'd actually
   run to completion in the time we have left? Is full detector scale
   within reach today, or still out of reach even after both
   optimizations?
   ```
   </details>

   If the estimate says a bigger-but-not-full-scale run is feasible,
   this is the moment to actually run it — a concrete "the grid used to
   be a reduced stand-in, now it isn't (as much)" result is a better
   afternoon than a number in a spreadsheet.

4. **opencode.** Before calling it done: re-run the correctness check
   one more time. `test_correctness.py` always checks its own fixed,
   small single-track config against Jaffe theory — it doesn't scale
   with whatever `--radius-um` you were experimenting with above — but
   it's still the thing that catches a change that broke the physics
   rather than just the speed.

   <details>
   <summary>Example prompt</summary>

   ```
   Run pytest one more time and confirm today's changes -- the
   algorithmic fix and anything about thread count -- didn't break the
   Jaffe-theory correctness check.
   ```
   </details>

## Optional: is a GPU worth it here?

Athena's nodes aren't CPU-only — each one also carries 8× NVIDIA
A100-SXM4-40GB (see [setup](../session1/04-setup.md)). Nothing in
`ion_chamber/solver.py` uses one today; both kernels are Numba
`njit`/`prange` on CPU. If there's time left after the task above, the
same hardware-aware question applies one level up: not just "how many
CPU threads," but "is a GPU worth porting to at all, for this problem?"

This needs a fresh allocation, not the one steps 1–4 ran in — GPUs are a
`--gres` request, not something you add to a running job. From the
access node:

```bash
srun -C memfs --time=2:00:00 -A tutorial -p tutorial --nodes=1 --ntasks-per-node=1 --cpus-per-task=16 --gres=gpu:1 --mem=120G --pty bash
```

Same flags as [the CPU-only `srun`](../session1/05-exercise-measurement.md),
plus `--gres=gpu:1` — one GPU, and 16 CPU cores is already this node's
actual per-GPU share (128 cores ÷ 8 GPUs). Ask an organizer if
`--gres=gpu:1` doesn't actually hand you a GPU — the generic-resource
name can vary between Slurm configs. Module load, venv, and `opencode`
are unchanged from [session1/05](../session1/05-exercise-measurement.md).

**opencode**, optional. Check what's actually there before reasoning
about it — don't take the agent's answer without having it look first:

<details>
<summary>Example prompt</summary>

```
Confirm we actually have a GPU on this allocation (nvidia-smi, and
whether numba.cuda.is_available() agrees), then look at insert_track
and lax_wendroff_step and reason about whether porting either to the
GPU would plausibly pay off here -- kernel launch overhead, data
transfer, and the actual working-set size all matter, not just "GPUs
are fast." Don't write any CUDA code yet, just the reasoning.
```
</details>

The likely answer is worth sitting with rather than skipping past: at
today's default grid (2.5 MiB, 91k tracks/pulse, ~1622 steps), the work
per kernel launch is tiny next to a GPU's launch and transfer overhead —
the same "problem too small for the parallelism" trap from this
morning's thread-count question, one level up. Does that change at the
full-detector scale from step 3 above (178 million tracks, ~730× the
memory)? That's the more interesting question than whether it helps
today.

If the reasoning says it's genuinely worth trying, treat an actual port
as a stretch goal, not a requirement — read the diff the same way as
this afternoon's other change, and don't let a GPU experiment put the
correctness check (step 4) at risk.
