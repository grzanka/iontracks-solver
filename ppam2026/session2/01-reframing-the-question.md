# Reframing the question

*[↑ Session 2](README.md) · [← Prev: Session 1](../session1/06-exercise-diagnosis.md) · [Next: Exercise: algorithmic optimization →](02-exercise-algorithmic-optimization.md)*

Talking points before anyone reopens opencode.

## Where the morning left off

Session 1's diagnosis, in one line: the sweep showed wall time flat or
slightly *worse* with more threads, profiling pointed at track
deposition (not the parallelised PDE sweep) as the actual hot loop, and
the hardware check found this job's cores scattered across several NUMA
nodes rather than one contiguous block. None of that was guessed — it
came from `cProfile`, `lscpu` vs. `nproc`/`taskset`, and `numactl`.

That diagnosis is the only legitimate starting point for what follows.
"Make it faster" is not a plan; "the deposition kernel scans the whole
grid for every track when the Gaussian only touches a small neighbourhood
of it" is.

## Two different kinds of optimization

This afternoon splits deliberately into two exercises, in this order:

1. **Algorithmic** ([02](02-exercise-algorithmic-optimization.md)) — fix
   what's wasteful about the *serial* cost of the hot loop, independent
   of any hardware question. A better algorithm on one core beats a
   worse one on sixteen.
2. **Hardware-aware** ([03](03-exercise-hardware-aware-optimization.md))
   — only once the algorithm is no longer the obvious waste does it make
   sense to ask *how* (and whether) to parallelize, using this specific
   job's actual core count, cache sizes, and NUMA layout as constraints,
   not textbook assumptions.

Doing hardware-aware work first would mean tuning thread counts around a
loop you're about to throw away. Session 1's sweep already showed what
happens when the "obvious thing to try" (parallelise the loop that looks
hot) doesn't match where the time actually goes — the same trap applies
here at the strategy level, not just the profiler level.

## Ground rules still apply

Nothing from [session 1's ground rules](../session1/03-agent-safety-rules.md)
expires at lunch. The difference this afternoon: the agent is about to
touch `ion_chamber/solver.py` for real. Rule 2 (read every diff) and rule
3 (commit before and after each change) stop being abstract advice and
become the thing that makes it safe to let the agent iterate quickly —
a bad edit is a `git diff` and a `git reset` away from gone, but only if
there was a commit to reset to.

`tests/test_correctness.py` is the check that matters most now: it
compares against closed-form Jaffe theory, and its own docstring says it
plainly — "if it drifts, the change broke the physics, not just the
speed." Re-run it after every change, not just at the end.

## What "faster" is actually for

[Session 1's walkthrough](../session1/01-domain-and-code-walkthrough.md)
already named the real target: today's default grid (60 µm sampled
radius, 20×20×206 voxels) is a *reduced* stand-in for a real Markus-type
chamber at 2.65 mm radius — 538×538×206 voxels, on the order of 730×
the memory and nearly 2000× the tracks per pulse. That gap — "runs on a
laptop" vs. "resolves an actual detector" — is what optimization work is
actually buying, not a smaller number in a benchmark table. Keep that in
mind for the end of [exercise 3](03-exercise-hardware-aware-optimization.md).
