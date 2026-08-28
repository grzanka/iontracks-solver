# Exercise: diagnose before you optimize

*[↑ Session 1](README.md) · [← Prev: Setup](04-setup.md) · Next: —*

The only goal this morning is a measurement-backed diagnosis. No code
changes yet — that's the afternoon session.

## Materials

- `ion_chamber/` — the solver under test.
- `bench.py` — one run, wall time and `k_s`.
- `sweep.py` — wall time across a range of thread counts, written to CSV.
- `tests/test_correctness.py` — checks against Jaffe theory; run it once
  now so everyone starts from a known-good baseline.

## Get set up on the node

You should already be on the Athena access node with `iontracks-solver`
cloned into `$SCRATCH` from [setup](04-setup.md). If not, do that first.

The access node isn't for running anything — grab an interactive node with
real CPUs (ask an organizer if the tutorial account/partition below
doesn't work for you). This exercise only needs CPUs:

```bash
srun -C memfs --time=2:00:00 -A tutorial -p tutorial --nodes=1 --ntasks-per-node=1 --cpus-per-task=16 --mem=120G --pty bash
```

What each flag does:

- `-C memfs` — not a hard requirement but an extra: ask for a node that
  also has `memfs`, RAM mapped as a filesystem for extremely fast
  volatile I/O (gone when the job ends).
- `--time=2:00:00` — walltime limit; the job is killed after 2 hours.
- `-A tutorial` — Slurm account to bill the job to (the shared tutorial
  account for this school).
- `-p tutorial` — partition (queue) reserved for the tutorial.
- `--nodes=1` — allocate one compute node.
- `--ntasks-per-node=1` — run a single task on that node (no MPI here).
- `--cpus-per-task=16` — give that task 16 CPU cores, for the solver's
  thread pool.
- `--mem=120G` — reserve 120 GB of RAM.
- `--pty bash` — run `bash` as an interactive shell on the allocated
  node, instead of a batch script.

`srun` blocks until a node is free.

<details>
<summary>Expected output</summary>

```
srun: job 3100383 queued and waiting for resources
srun: job 3100383 has been allocated resources
[athena][tutorial256@t0033 ~]$
```
</details>

The "queued and waiting" line may sit there for a while if the cluster is
busy — that's normal, just wait. Once resources are granted, your prompt
changes from `login01` (the access node) to a worker node name like
`t0033`. That's your signal that you're now on a compute node with real
CPUs, not the shared login node.

You can check your job is actually running with:

```bash
squeue --me
```

<details>
<summary>Expected output</summary>

```
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
           3100383  tutorial     bash tutorial  R       4:31      1 t0033
```
</details>

`ST` is the job state (`R` = running, `PD` = pending), `TIME` is elapsed
runtime against your `--time` limit, and `NODELIST` names the node(s)
it's running on — should match the hostname in your prompt.

This exercise doesn't need a GPU — stick with the one `srun` above. Don't
run a second `srun` on top of it; that would queue a second job instead
of replacing the first.

Move into the repo you cloned during setup:

```bash
cd $SCRATCH/iontracks-solver
```

The system Python is old (and so is the default `gcc`) — too old for this
project:

```bash
python --version
```

<details>
<summary>Expected output</summary>

```
Python 3.9.25
```
</details>

```bash
gcc --version
```

Run it and check for yourself — it'll be a much older release than the
`GCC/14.3.0` loaded below.

Load a current one through the module system instead. See what versions
are actually available rather than taking the one below on faith:

```bash
module spider Python
```

By default that output opens in `less` — quit it with `q`. To skip the
pager entirely, run `LMOD_PAGER=cat module spider Python` instead.

We'll use `3.13.5` for the rest of this exercise; any newer version you
spot works just as well:

```bash
module load GCC Python/3.13.5
```

```bash
python --version
```

<details>
<summary>Expected output</summary>

```
Python 3.13.5
```
</details>

```bash
gcc --version
```

Now reports `14.3.0`, matching the `GCC/14.3.0 loaded` line from the
module load above.

This module load is **not permanent** — it only applies to this shell.
Logging out, or starting a fresh `srun` session next time, puts you back
on Python 3.9.25 and the old `gcc`, so `module load GCC Python/3.13.5` is
something you run again every time you get a new session, before
creating the venv below.

Create and activate a virtualenv, then install the project:

```bash
python -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -e ".[dev]"
```

Your prompt should now show `(venv)`. That's what the rest of this
exercise runs inside.

## Task

1. Confirm the baseline is still correct:

   ```bash
   pytest
   ```

2. Time a single run:

   ```bash
   python bench.py
   ```

   Note the wall time and `k_s`.

3. Ask the agent to profile that same run — don't assume the parallelised
   loop is the hot path, check.

4. Sweep thread counts:

   ```bash
   python sweep.py --threads 1 2 4 8 --out sweep.csv
   ```

   Adjust the thread list to this node's actual core count (`nproc`, or
   whatever `--cpus-per-task` you got from `srun`) — have the agent check
   it rather than guessing.

5. Have the agent plot wall time and speedup vs. thread count from
   `sweep.csv`.

6. Write three to five sentences: where the time goes, whether adding
   threads helps, and why — grounded in what the profiler and plot showed,
   not in Amdahl's law recited from memory.

## Example prompts

Starting points, not a script — adapt them to what the agent's already
told you.

### Performance

- "Run `bench.py` under `cProfile` and summarize the top 10 functions by
  cumulative time. I want to know where the time goes, not just the
  total."
- "Before we talk about thread counts, check how many CPU cores and how
  much cache this node actually has."
- "Run `sweep.py` with `--threads` from 1 up to this node's core count,
  write `sweep.csv`, and plot wall time and speedup vs. thread count."
- "Given the profiler output and that plot, explain in a few sentences why
  the speedup curve looks the way it does — cite the actual numbers, not
  Amdahl's law in the abstract."
- "Run `pytest` and confirm the answer didn't change, only the timing."

### Data exploration

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

Leave things clean for the next exercise:

```bash
deactivate
```

```bash
exit
```

The second `exit` leaves the `srun` shell and frees the node.
