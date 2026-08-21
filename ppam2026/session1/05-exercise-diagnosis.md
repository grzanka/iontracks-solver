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

Log in:

```bash
ssh tutorialXXX@athena.cyfronet.pl
```

The login node isn't for running anything — grab an interactive node with
real CPUs (ask an organizer for the actual `-A` grant if the one below
doesn't work):

```bash
srun -C memfs --pty --time=2:00:00 -A <your-grant> -p plgrid-gpu-a100 --gres=gpu:a100:1 --cpus-per-task=32 --mem=80G bash
```

Clone the repo onto scratch:

```bash
cd $SCRATCH
```

```bash
git clone https://github.com/grzanka/iontracks-solver.git
```

```bash
cd iontracks-solver
```

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
