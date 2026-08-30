# Exercise: measure before you optimize

*[↑ Session 1](README.md) · [← Prev: Setup](04-setup.md) · [Next: Diagnose with the agent →](06-exercise-diagnosis.md)*

The only goal this morning is a measurement-backed diagnosis. No code
changes yet — that's the afternoon session. This file gets your baseline
numbers on the record; the next file brings the agent in to profile,
plot, and explain them.

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
spot works just as well. Lets check what is needed to load that Python module:

```bash
module spider Python/3.13.5
```

<details>
<summary>Expected output</summary>

```
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Python: Python/3.13.5
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Description:
      Python is a programming language that lets you work more quickly and integrate your systems more effectively.


    You will need to load all module(s) on any one of the lines below before the "Python/3.13.5" module is available to load.

      GCCcore/14.3.0
 
    This module provides the following extensions:

       flit_core/3.12.0 (E), packaging/25.0 (E), pip/25.1.1 (E), setuptools/80.9.0 (E), setuptools_scm/8.3.1 (E), tomli/2.2.1 (E), typing_extensions/4.14.0 (E), wheel/0.45.1 (E)

    Help:
      
      Description
      ===========
      Python is a programming language that lets you work more quickly and integrate your systems
       more effectively.
      
      
      More information
      ================
       - Homepage: https://python.org/
      
      
      Included extensions
      ===================
      flit_core-3.12.0, packaging-25.0, pip-25.1.1, setuptools-80.9.0,
      setuptools_scm-8.3.1, tomli-2.2.1, typing_extensions-4.14.0, wheel-0.45.1
```

</details>

We need to load proper GCC compiler before loading Python:

```bash  
module load GCC/14.3.0 Python/3.13.5
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
pip install --no-cache-dir -e ".[dev]"
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

Everything below runs directly in your shell — no agent yet, just
getting the numbers you'll hand to it in the next file.

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

   Note the wall time and `k_s` — you'll compare them against the sweep
   below, and again in the next file once the agent's involved.

3. Sweep thread counts:

   ```bash
   python sweep.py --threads 1 2 4 8 --out sweep.csv
   ```

   This runs the same simulation once per thread count in that list and
   writes wall time for each to `sweep.csv`:

   <details>
   <summary>Expected output</summary>

   ```
   threads=  1  repeat=0  wall=8.42s  ks=1.4554
   threads=  2  repeat=0  wall=8.54s  ks=1.4554
   threads=  4  repeat=0  wall=8.65s  ks=1.4554
   threads=  8  repeat=0  wall=8.75s  ks=1.4554

   wrote sweep.csv
   ```
   </details>

   `k_s` staying identical across rows is expected — threading changes
   how fast you get the answer, not the answer itself, and `pytest`
   already confirmed that answer is correct. Whether wall time going the
   *wrong* direction as threads increase is normal or a problem is
   exactly what the agent helps you figure out next — resist the urge to
   explain it yourself before you've profiled anything. `1 2 4 8` is also
   just a placeholder; whether it's the right range for *this* node is
   part of that same question.

You've now got a correctness check, a single-run baseline, and a
`sweep.csv` on disk. Head to
[the next file](06-exercise-diagnosis.md) to bring the agent in.
