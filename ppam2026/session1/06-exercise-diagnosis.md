# Exercise: diagnose before you optimize

*[↑ Session 1](README.md) · [← Prev: Measure](05-exercise-measurement.md) · [Next: Session 2 →](../session2/01-reframing-the-question.md)*

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

This takes over the terminal with an interactive chat. Every step below
is a prompt you type there — the agent runs the actual commands (with
your approval, see below), so you shouldn't need to leave this chat.

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

For this exercise, pick **Allow once** every time — you'll see this
prompt often, and that's a feature, not friction: it's your chance to
inspect every command before it runs and actually watch how the agent
works, one step at a time, instead of taking the final answer on faith.

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

2. **opencode.** Before trusting the `1 2 4 8` thread list from the
   sweep in the previous file, check what this node actually has:

   <details>
   <summary>Example prompt</summary>

   ```
   Before we talk about thread counts, check how many CPU cores and how
   much cache this node actually has.
   ```
   </details>

   Watch out here: on a shared node, `lscpu` alone answers the wrong
   question. It reports the physical host — on Athena's CPU nodes, all
   128 cores across 2 sockets — not what Slurm actually handed *your*
   job. The `--cpus-per-task=16` from your `srun` command is enforced
   through a cgroup, and those 16 cores aren't necessarily one tidy
   contiguous block; they can be scattered across several NUMA nodes.
   Push the agent to check the allocation, not just the node:

   <details>
   <summary>Example prompt</summary>

   ```
   That's the whole physical node, not necessarily what Slurm gave this
   job. Check nproc, this process's actual CPU affinity (taskset -cp
   $$), and numactl --hardware, and tell me which NUMA node(s) our
   allocated cores actually sit on.
   ```
   </details>

   If the agent's answer is "spread across N NUMA nodes," that alone is
   worth a sentence in your diagnosis later — it explains why speedup
   might stall well before your core count runs out. Either way, have
   it re-run the sweep with the corrected list next.

3. **opencode.** Plot wall time and speedup vs. thread count from
   `sweep.csv`.

   <details>
   <summary>Example prompt</summary>

   ```
   Re-run sweep.py with --threads from 1 up to the number of cores
   actually allocated to this job (not the whole node), write sweep.csv,
   and plot wall time and speedup vs. thread count.
   ```
   </details>

4. **opencode.** There's no GUI on this node, so get the plot onto your
   own machine to actually look at it before writing anything down.

   <details>
   <summary>Example prompt</summary>

   ```
   I need to view the plot you just saved on my own laptop, not on this
   node. What's the exact command I should run, and from where, to copy
   it over?
   ```
   </details>

   The agent should point you at something like this, run from a
   terminal **on your laptop** — not inside opencode, and not by
   opening a new shell on the node itself:

   ```bash
   scp tutorialXXX@athena.cyfronet.pl:/net/tscratch/people/tutorialXXX/iontracks-solver/<plot-filename>.png .
   ```

   That works straight from your laptop to the login node's hostname —
   not the specific `t0033`-style worker node you `srun`'d into, which
   isn't reachable from outside — because `$SCRATCH` is shared storage
   both see. Swap in your own account number and whatever filename the
   agent actually used.

   One more gotcha, since you're about to copy a command out of a
   terminal: don't reach for **Ctrl+C** to do it. Inside opencode (and
   most terminal programs), Ctrl+C sends an interrupt signal — it can
   kill the very session you're trying to copy from, not copy anything.
   Select the text by dragging over it with your mouse instead, then
   use your terminal's own copy shortcut (or right-click → Copy); paste
   with Ctrl+V, Cmd+V, or a middle-click, depending on your setup.

5. **opencode**, or in your own notes. Write three to five sentences:
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

### Profiling

Deeper follow-ups once the initial `cProfile` summary from step 1 has
pointed at a suspect:

```
Profile bench.py with line_profiler on whichever function cProfile
flagged as hottest — I want line-by-line time, not just the
function-level view.
```

```
numba JIT-compiles on first call. Run bench.py twice back-to-back and
tell me how much of the first run's time was compilation overhead
versus the second run's steady-state time.
```

```
Re-profile with a larger pulse count (or more tracks) and check whether
the same functions still dominate, or whether the ranking shifts with
problem size.
```

### Scientific plots

`bench.py` only prints the final numbers — the `Result` object it
discards (`time_s`, `f_t`, `ks`, `positive_array`, `negative_array`, see
[`ion_chamber/state.py`](../../ion_chamber/state.py)) has the rest. Have
the agent write a small standalone script that calls `run_simulation`
directly to get at it — that's exploration, not the afternoon's "change
the solver."

```
Write a short script that calls run_simulation directly with the
default config and plots f_t (collection efficiency) against time_s. I
want to see the pulse and the clearance tail as visibly distinct
regions on the charge-evolution curve.
```

```
From that same run, plot k_s(t) = 1/f_t(t) over time and tell me
roughly when it's converged versus still settling.
```

```
Take the final positive_array and negative_array and plot a 2D slice
through the mid-height of the gap, so I can see the radial ion density
profile left behind.
```

```
Run it twice with sampled_radius_cm (or dose_rate_Gy_s) at two
different values and plot both charge-evolution curves together — does
the shape change, or just the final k_s?
```
