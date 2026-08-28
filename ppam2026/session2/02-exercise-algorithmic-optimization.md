# Exercise: algorithmic optimization

*[↑ Session 2](README.md) · [← Prev: Reframing the question](01-reframing-the-question.md) · [Next: Exercise: hardware-aware optimization →](03-exercise-hardware-aware-optimization.md)*

First real code change of the day. [Ground rules](../session1/03-agent-safety-rules.md)
2 and 3 stop being theoretical here: read every diff, commit before and
after.

## Resume your session

Same node, same repo, same venv as this morning — nothing to reinstall,
but the module load and venv activation don't survive a fresh `srun`
(see [session1/05](../session1/05-exercise-measurement.md) for why):

```bash
srun -C memfs --time=2:00:00 -A tutorial -p tutorial --nodes=1 --ntasks-per-node=1 --cpus-per-task=16 --mem=120G --pty bash
```

```bash
cd $SCRATCH/iontracks-solver
```

```bash
module load GCC Python/3.13.5
```

```bash
source venv/bin/activate
```

```bash
opencode
```

## Task

Assumes your morning's profiling pointed at `insert_track` (the
track-deposition kernel) as the hot function — that's the intended
result. If yours pointed somewhere else, swap that in below instead.

1. **opencode.** Confirm there's nothing uncommitted before the agent
   starts editing.

   <details>
   <summary>Example prompt</summary>

   ```
   Check git status. If there are uncommitted changes, tell me what
   they are before you touch anything.
   ```
   </details>

2. **opencode.** Before handing over the fix, make the agent find the
   problem itself. Don't paste in what's wasteful — describe the
   physics and let it read the code.

   <details>
   <summary>Example prompt</summary>

   ```
   insert_track is the hot function we found this morning. Read it
   carefully and tell me what's algorithmically wasteful about it --
   don't change anything yet, just diagnose. Think about what the
   Gaussian charge distribution actually looks like in space, and where
   in that loop time is being spent on grid points that barely
   contribute to the result.
   ```
   </details>

   `solver.py`'s own module docstring names two specific
   inefficiencies: the loop scans the *entire* xy plane for every
   track instead of a bounded window around it, and the 2D Gaussian is
   never factored into cheaper separable 1D pieces. If the agent's
   diagnosis lands on both on its own, good — that's the point of
   asking first instead of telling. If it only catches one, or neither,
   nudge it rather than just handing over the answer:

   <details>
   <summary>Example prompt (if it needs a nudge)</summary>

   ```
   You're right that the window doesn't need to cover the whole grid --
   but look again at how the exponent is computed: r_sq =
   (i-x)^2 + (j-y)^2, then a single exp(-r_sq*h2/b2). Is there a way to
   avoid calling exp() once per grid point inside that window?
   ```
   </details>

   Once the diagnosis actually covers both points, have it implement
   what it just described:

   <details>
   <summary>Example prompt</summary>

   ```
   Go ahead and implement the fix(es) you just described. Keep the
   physics identical -- this is about doing the same computation
   faster, not approximating it.
   ```
   </details>

3. **opencode.** Read the diff before accepting it (ground rule 2) — ask
   the agent to walk you through it if the Numba-flavored code isn't
   obvious at a glance.

   <details>
   <summary>Example prompt</summary>

   ```
   Explain what you just changed and why, in a few sentences, then run
   pytest and confirm nothing about the physics changed -- only the
   speed.
   ```
   </details>

4. **opencode.** Commit it (ground rule 3).

   <details>
   <summary>Example prompt</summary>

   ```
   Commit this change with a message that describes the algorithmic fix
   -- the bounded window and the separated Gaussian -- not just
   "optimize solver".
   ```
   </details>

5. **opencode.** Measure the actual win, same thread count as this
   morning's baseline so this isolates the algorithmic change from any
   parallelization question (that's next file).

   <details>
   <summary>Example prompt</summary>

   ```
   Run bench.py with --threads 1 and compare wall time against this
   morning's single-thread baseline. How much of a speedup was that
   alone?
   ```
   </details>

6. **opencode.** Profile again — has the ranking changed?

   <details>
   <summary>Example prompt</summary>

   ```
   Profile this new run under cProfile the same way as this morning.
   Is insert_track still the top function by cumulative time, or has
   something else taken over?
   ```
   </details>

If the PDE sweep (`lax_wendroff_step`) is now the larger cost, that's
expected — it wasn't touched here, and it's exactly what
[the next exercise](03-exercise-hardware-aware-optimization.md) is
about.
