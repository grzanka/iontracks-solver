# Performance Engineering with a Coding Agent: A Real HPC Case Study

A tutorial at [PPAM 2026](https://ppam.edu.pl/) (16th International Conference
on Parallel Processing and Applied Mathematics), given by **Klemens Noga** and
**Leszek Grzanka** (ACK Cyfronet AGH, EuroCC3).

## Abstract

"Vibe coding" — letting an AI agent produce software mostly on its own,
calling tools, testing, and fixing its own mistakes in a loop, with little
human interaction along the way — is everywhere right now. This tutorial
looks at a different use of the same AI agents: hands-on practice in data
analysis and exploration, and in performance engineering under real hardware
constraints on an actual HPC system.

Partial differential equations (PDEs) are a common way to model reality
across physics and other fields, and getting a PDE solver to run correctly
and effectively on real hardware is one of the most demanding engineering
tasks. This tutorial works through one such example: our own implementation
of a solver — computing the recombination correction factor for a pulsed
proton beam in an ionization chamber — with a physically validated
simulation, an analytic correctness check, and a slow, naive implementation
to start from.

Participants work on that naive implementation using
[opencode](https://opencode.ai/), an AI coding agent that can use several
models hosted directly on Cyfronet's infrastructure — including GLM 5.2,
whose coding ability is similar to Claude Sonnet's — at no cost to the user.
All data and tasks stay within Cyfronet's infrastructure. Three skills matter
here: using the agent as a data-analysis tool (profile, plot, and explain a
run instead of hand-typing matplotlib), directing it toward optimization that
is both algorithmic and hardware-aware (using Athena's real core count,
cache size, and NUMA layout as constraints, not guesses), and using it
safely — permissions, review discipline, and version control, so it can't do
real damage.

The full tutorial writeup, including the detailed agenda below, is in
[`workshop-EuroCC3-HPC.pdf`](workshop-EuroCC3-HPC.pdf).

## Tutorial agenda

**11:00–13:30 — Infrastructure, safety, and diagnosis**
([materials](session1/))

- Introduction to the domain problem, and a walkthrough of the naive
  implementation of the PDE solver.
  ([notes](session1/01-domain-and-code-walkthrough.md))
- Cyfronet-hosted LLMs: why running GLM 5.2 on-premises matters — free at
  this scale, data never leaves the cluster, coding ability similar to
  Claude Sonnet's. ([notes](session1/02-why-onprem-llms.md))
- Using an agent safely: permission modes, reviewing diffs before accepting
  them, git commits as checkpoints, never approving destructive commands or
  job submissions blindly — the rules for the rest of the day.
  ([notes](session1/03-agent-safety-rules.md))
- Setup: Athena account, opencode + GLM 5.2 token, a quick "hello agent"
  test — and the day's submission rule: the agent drafts job scripts,
  participants review and submit them by hand.
  ([checklist](session1/04-setup.md))
- Orientation: the problem we're solving, how the starting code works, and
  the materials everyone begins with — the code itself, a way to measure
  performance, and a way to check the results are still correct.
- Hands-on: treat the agent as a lab assistant, not an author — "run the
  sweep, plot wall time and speedup vs. thread count, explain the shape" —
  and write a short diagnosis based on the output.
  ([exercise](session1/05-exercise-measurement.md))
- Reference: an opencode cheatsheet — commands, permission modes, and
  agent/subagent mechanics for everything used this morning.
  ([cheatsheet](session1/07-opencode-cheatsheet.md))

**14:20–16:00 — Optimization: algorithmic and hardware-aware**
([materials](session2/))

- Reframing the question: instead of "make it faster," have the agent check
  the hardware it's running on — cores, cache, NUMA layout.
  ([notes](session2/01-reframing-the-question.md))
- Hands-on: algorithmic optimization — restructuring the hot loop.
  ([exercise](session2/02-exercise-algorithmic-optimization.md))
- Hands-on: hardware-aware optimization — deciding how, and whether, to
  parallelize. ([exercise](session2/03-exercise-hardware-aware-optimization.md))
- Re-run the timing harness and the correctness check after every change.

**16:30–18:00 — Solution reveal, security debrief, and wrap-up**
([materials](session3/))

- Synthesis: compare each participant's findings against the optimized
  reference. ([notes](session3/01-solution-reveal-and-synthesis.md))
- Discussion: where the agent's hardware reasoning held up under
  measurement, where it didn't, and how participants told the difference.
  ([notes](session3/02-hardware-reasoning-discussion.md))
- Security retrospective: LLMs executing risky commands, why the rules held,
  and what to take away for using coding agents on shared HPC accounts.
  ([notes](session3/03-security-retrospective.md))
- Wrap-up: agent as an analysis-and-optimization tool, not autocomplete; the
  case for on-prem LLMs; pointers to the reference repo.
  ([notes](session3/04-wrap-up.md))

## Conference day schedule — Sunday, August 30, 2026

Tutorials day at the Lecture Center of the Poznań University of Technology.

| Time | Session |
|---|---|
| from 10:40 | Registration — Lecture Center of the Poznań University of Technology |
| from 11:00 | **Tutorials** |
| 13:30–14:20 | Lunch |
| from 14:20 | Continuation of classes |
| 16:00–16:30 | Coffee break |
| 16:30–18:00 | Continuation of classes |
| from 19:30 | Concert at the Lecture Center and welcome reception at Poznań Supercomputing and Networking Center, including a tour of the supercomputing facilities |

## Materials

- [`workshop-EuroCC3-HPC.pdf`](workshop-EuroCC3-HPC.pdf) — abstract and agenda
  (the source for this page)
- [Top-level README](../README.md) — the solver, the task, and how to run it
- [PPAM 2026 conference site](https://ppam.edu.pl/)
