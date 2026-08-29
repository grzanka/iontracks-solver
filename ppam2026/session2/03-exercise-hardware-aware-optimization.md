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
