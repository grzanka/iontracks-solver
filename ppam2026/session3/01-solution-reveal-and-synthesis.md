# Solution reveal and synthesis

*[↑ Session 3](README.md) · Prev: — · [Next: Discussion: the agent's hardware reasoning →](02-hardware-reasoning-discussion.md)*

Coffee break is over; nobody needs to be at a terminal for this block.

## Compare notes before revealing anything

Ask around the room first, don't lead with the answer:

- What did your agent diagnose as the hot function this morning
  ([session1/06](../session1/06-exercise-diagnosis.md))? Did everyone land
  on `insert_track`, or did some sweeps point elsewhere?
- What was the algorithmic fix
  ([session2/02](../session2/02-exercise-algorithmic-optimization.md))
  your agent proposed and implemented? Bounded window, separated Gaussian,
  both, something else?
- What single-thread speedup did that fix measure at, isolated from any
  threading question?
- What thread count did your agent end up recommending
  ([session2/03](../session2/03-exercise-hardware-aware-optimization.md)),
  and at what grid size? Did that answer change as `--radius-um` grew?

Differences between participants are the interesting part — a run on a
job with cores packed on one NUMA node and a run with cores scattered
across several are legitimately different problems, not a right and a
wrong answer.

## The reference

The optimized reference implementation lives in a separate repo,
[grzanka/IonTracks-PulsedProton-Python](https://github.com/grzanka/IonTracks-PulsedProton-Python)
— the same bounded-window, separated-Gaussian fix this afternoon's
exercise was steering everyone toward, plus a hardware-aware threading
call. It's deliberately not linked from anywhere participants could stumble
onto it earlier in the day: pointing to it before now would have turned
session 2 into transcription instead of diagnosis.

Walk through it against what the room found:

- Does the reference's algorithmic fix match what participants'
  agents converged on independently, or did some agents find a
  different-but-valid way to cut the same waste?
- How does the reference's measured speedup compare to the room's
  numbers? Differences are worth digging into rather than smoothing
  over — a slower measured speedup can mean a less thorough fix, or it
  can mean a noisier node.
- How far does the reference get toward
  [session 1's "full detector scale" target](../session1/01-domain-and-code-walkthrough.md)
  (2.65 mm radius, 538×538×206 voxels, ~178 million tracks/pulse) — in an
  actual completed run, or in the same kind of reasoned estimate the
  hardware-aware exercise asked for?

## What this synthesis is for

Not a scoreboard. The point of comparing against a reference after the
fact — rather than handing it out up front — is that everyone already has
their own measurements to check it against, which is a fundamentally
different (and more durable) way to learn "was my reasoning right" than
being told the answer first.
