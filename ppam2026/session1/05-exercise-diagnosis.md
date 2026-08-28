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
are actually available rather than taking the one below on faith
(`LMOD_PAGER=cat` skips the `less` pager `module spider` opens by
default):

```bash
LMOD_PAGER=cat module spider 'Python'
```

<details>
<summary>Expected output</summary>

```
-----------------------------------------------------------------------------------------------------------------------
  Python:
-----------------------------------------------------------------------------------------------------------------------
    Description:
      Python is a programming language that lets you work more quickly and integrate your systems more effectively.

     Versions:
        Python/2.7.18-bare
        Python/2.7.18
        Python/3.9.5-bare
        Python/3.9.5
        Python/3.9.6-bare
        Python/3.9.6
        Python/3.10.4-bare
        Python/3.10.4
        Python/3.10.8-bare
        Python/3.10.8
        Python/3.11.3
        Python/3.11.5
        Python/3.12.3
        Python/3.13.1
        Python/3.13.5
     Other possible modules matches:
        GitPython  IPython  Python-DVUploader  Python-bundle-PyPI  flatbuffers-python  meson-python  protobuf-python  ...

-----------------------------------------------------------------------------------------------------------------------
  To find other possible module matches execute:

      $ module -r spider '.*Python.*'

-----------------------------------------------------------------------------------------------------------------------
  For detailed information about a specific "Python" package (including how to load the modules) use the module's full name.
  Note that names that have a trailing (E) are extensions provided by other modules.
  For example:

     $ module spider Python/3.13.5
-----------------------------------------------------------------------------------------------------------------------
```
</details>

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

Creates a `venv/` directory holding an isolated copy of the Python
3.13.5 interpreter and its own `pip`, separate from anything else on the
node. No output on success, and your prompt doesn't change yet.

```bash
source venv/bin/activate
```

Puts `venv/bin` at the front of `PATH` for this shell, so `python` and
`pip` resolve to the venv's copies instead of the module-loaded system
ones. Your prompt gains a `(venv)` prefix:

<details>
<summary>Expected output</summary>

```
(venv) [athena][tutorial256@t0003 iontracks-solver]$
```
</details>

```bash
pip install -e ".[dev]"
```

Installs this repo into the venv in **editable** mode (`-e`) — code
changes take effect immediately, no reinstall needed — along with the
`dev` extra from `pyproject.toml` (`pytest`, `matplotlib`), on top of the
core dependencies (`numpy`, `numba`, `pandas`, `scipy`, `mpmath`). Expect
a couple minutes of `Collecting ...`/`Building wheel ...` lines, ending
with `Successfully installed iontracks-solver-0.1.0 ...` and the rest of
the dependency list.

That `(venv)` prompt is what the rest of this exercise runs inside.

## Task

1. Confirm the baseline is still correct:

   ```bash
   pytest
   ```

   This runs `tests/test_correctness.py` (checks the solver against
   Jaffe theory) and `tests/test_smoke.py` (checks it runs at all
   end-to-end without crashing) — 3 tests total, all should pass:

   <details>
   <summary>Expected output</summary>

   ```
   =================================================== test session starts ===================================================
   platform linux -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
   rootdir: /net/tscratch/people/tutorial256/iontracks-solver
   configfile: pyproject.toml
   collected 3 items

   tests/test_correctness.py .                                                                                         [ 33%]
   tests/test_smoke.py ..                                                                                              [100%]

   ==================================================== 3 passed in 3.84s ====================================================
   ```
   </details>

   If anything fails here, stop and sort it out before going further —
   everything else in this exercise assumes this baseline is correct.

2. Time a single run:

   ```bash
   python bench.py
   ```

   `bench.py` runs one simulation of a pulsed-beam ion chamber and
   prints its setup, then progress, then the result. The setup lines
   describe the physics scenario (particle, chamber geometry, the small
   sub-volume being sampled, the simulation grid, and the pulse timing);
   the `step N/1622  f = ...` lines are progress, showing the collection
   efficiency `f` falling as recombination sets in during the pulse and
   settling as ions clear afterwards; the last two lines are what you
   actually need for this exercise — wall time and `k_s`:

   <details>
   <summary>Expected output</summary>

   ```
   Particle              : proton @ 60.0 MeV/u (LET = 0.00114 keV/um, track radius b = 20 um)
   Chamber               : gap = 0.2 cm, V = 300.0 V (E = 1500 V/cm)
   Sampled sub-volume    : radius = 60 um, area = 0.000113 cm^2
   Grid                  : 20 x 20 x 206 voxels (10 um/voxel), 2.5 MiB peak
   Time step dt          : 382.6 ns (Courant 0.947)
   Pulse                 : 540.0 us (1412 steps), 91047 tracks, 50.0 Hz, 1 pulse(s)
   Total simulated time  : 621 us (1622 steps)

     step 1/1622  f = 0.9999
     step 82/1622  f = 0.8761
     step 163/1622  f = 0.7809
     ...
     step 1621/1622  f = 0.6871
     (8.41 s, 1 thread(s))

   Wall time (1 thread(s)): 8.41 s
   Collection efficiency f      = 0.6871
   Recombination factor  k_s = 1/f = 1.4554
   ```
   </details>

   Note the wall time and `k_s` — you'll want them to compare against
   the sweep in step 4.

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
