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

2. **opencode.** `insert_track` has two named inefficiencies in
   `solver.py`'s own module docstring — point the agent at both.

   <details>
   <summary>Example prompt</summary>

   ```
   insert_track loops over the entire xy plane and calls exp() at every
   point, for every track, even though the Gaussian falls off fast
   around each track's (x, y). Rewrite it to only touch a bounded
   window around each track, sized to a few track radii (b2), and skip
   the rest of the grid entirely.
   ```
   </details>

   <details>
   <summary>Example prompt</summary>

   ```
   Separately: the 2D Gaussian in insert_track is separable --
   exp(-((i-x)^2+(j-y)^2)*h2/b2) factors into exp(-(i-x)^2*h2/b2) times
   exp(-(j-y)^2*h2/b2). Precompute the 1D exponential factors along each
   axis once per track instead of calling exp() inside the nested loop.
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
