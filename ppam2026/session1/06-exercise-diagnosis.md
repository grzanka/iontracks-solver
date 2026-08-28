# Exercise: diagnose before you optimize

*[↑ Session 1](README.md) · [← Prev: Measure](05-exercise-measurement.md) · Next: —*

Picking up where [the previous file](05-exercise-measurement.md) left off:
you should have a passing `pytest`, a `bench.py` baseline (wall time and
`k_s` noted), and a `sweep.csv` on disk, all inside the `(venv)` shell on
your `srun` node. This file brings the agent in to profile, plot, and
help you explain what you measured.

## Launch opencode

From inside `iontracks-solver`, with the venv still active:

```bash
opencode
```

This takes over the terminal with an interactive chat — the prompts
below are things you type there, not in the shell. Anywhere a step below
says **Terminal**, exit back out of opencode first (or use a second
terminal into the same node).

## Expect permission prompts

This is ground rule 1 from [the ground rules](03-agent-safety-rules.md)
in practice: opencode asks before running any shell command, it doesn't
just run it. Every task below will trigger at least one prompt like
this:

```
Thought: 3.0s

$ /net/tscratch/people/tutorial256/iontracks-solver/venv/bin/python -m
cProfile -s cumulative /net/tscratch/people/tutorial256/iontracks-
solver/bench.py --quiet 2>&1 | head -40

△ Permission required
  # Shell command

$ /net/tscratch/people/tutorial256/iontracks-solver/venv/bin/python -m
cProfile -s cumulative /net/tscratch/people/tutorial256/iontracks-
solver/bench.py --quiet 2>&1 | head -40

  Allow once   Allow always   Reject   ctrl+f fullscreen   ↕ select   enter confirm
```

Read the actual command before answering, same as reviewing a diff:

- **Allow once** — runs just this one call; you'll be asked again next
  time.
- **Allow always** — stops asking for this exact command for the rest
  of the session. Fine for something you expect to re-run a lot (like
  this profiling command), but don't reach for it out of habit — it's
  ground rule 4 ("never approve blindly") you'd be skipping.
- **Reject** — cancels it; tell the agent why in the chat and it'll try
  something else.

## Task

1. **opencode.** Profile the `bench.py` run — don't assume the
   parallelised loop is the hot path, check.

   <details>
   <summary>Example prompt</summary>

   ```
   Run bench.py under cProfile and summarize the top 10 functions by
   cumulative time. I want to know where the time goes, not just the
   total.
   ```
   </details>

2. **opencode**, then **Terminal**. Before trusting the `1 2 4 8` thread
   list from the sweep in the previous file, check what this node
   actually has:

   <details>
   <summary>Example prompt</summary>

   ```
   Before we talk about thread counts, check how many CPU cores and how
   much cache this node actually has.
   ```
   </details>

   If that turns up more cores than `1 2 4 8` covers, re-run the sweep
   yourself with the corrected list (swap in the agent's numbers):

   ```bash
   python sweep.py --threads 1 2 4 8 16 --out sweep.csv
   ```

3. **opencode.** Plot wall time and speedup vs. thread count from
   `sweep.csv`.

   <details>
   <summary>Example prompt</summary>

   ```
   Run sweep.py with --threads from 1 up to this node's core count,
   write sweep.csv, and plot wall time and speedup vs. thread count.
   ```
   </details>

4. **opencode**, or in your own notes. Write three to five sentences:
   where the time goes, whether adding threads helps, and why — grounded
   in what the profiler and plot showed, not in Amdahl's law recited from
   memory.

   <details>
   <summary>Example prompt</summary>

   ```
   Given the profiler output and that plot, explain in a few sentences
   why the speedup curve looks the way it does — cite the actual
   numbers, not Amdahl's law in the abstract.
   ```
   </details>

Once you're happy with the diagnosis, have the agent confirm nothing
about the *answer* changed along the way — only the timing:

<details>
<summary>Example prompt</summary>

```
Run pytest and confirm the answer didn't change, only the timing.
```
</details>

## More prompts to try

Starting points, not a script — adapt them to what the agent's already
told you.

`bench.py` only prints the final numbers — the `Result` object it
discards (`time_s`, `f_t`, `ks`, `positive_array`, `negative_array`, see
[`ion_chamber/state.py`](../../ion_chamber/state.py)) has the rest. Have
the agent write a small standalone script that calls `run_simulation`
directly to get at it — that's exploration, not the afternoon's "change
the solver."

- "Write a short script that calls `run_simulation` directly with the
  default config and plots `f_t` (collection efficiency) against
  `time_s`. I want to see the pulse and the clearance tail as visibly
  distinct regions on the charge-evolution curve."
- "From that same run, plot `k_s(t) = 1/f_t(t)` over time and tell me
  roughly when it's converged versus still settling."
- "Take the final `positive_array` and `negative_array` and plot a 2D
  slice through the mid-height of the gap, so I can see the radial ion
  density profile left behind."
- "Run it twice with `sampled_radius_cm` (or `dose_rate_Gy_s`) at two
  different values and plot both charge-evolution curves together — does
  the shape change, or just the final `k_s`?"

## What "done" looks like

A plot, a profiler summary, and a short written diagnosis you could hand
to someone else and have them understand what's slow and why, without
reading the code themselves. That diagnosis is what gets compared against
the reference solution in the 16:30 synthesis.

## Wrapping up

Leave things clean for the next exercise. First leave opencode's chat
(type `exit`, or press Ctrl+D, at its prompt) to drop back into the
regular shell, then:

```bash
deactivate
```

```bash
exit
```

That second `exit` leaves the `srun` shell and frees the node.
