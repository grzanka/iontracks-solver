# Wrap-up

*[↑ Session 3](README.md) · [← Prev: Security retrospective](03-security-retrospective.md) · Next: —*

Closing points to leave the room with.

## The agent as an analysis-and-optimization tool, not autocomplete

The abstract's framing of "vibe coding" — an agent producing software
mostly on its own, with little human interaction along the way — was
deliberately not what today practiced. Every hands-on block instead
pointed the same self-correcting tool-use loop
([session1/02](../session1/02-why-onprem-llms.md)) at something narrower
and more checkable: profile this run and explain the shape
([session1/06](../session1/06-exercise-diagnosis.md)), diagnose what's
algorithmically wasteful before touching code
([session2/02](../session2/02-exercise-algorithmic-optimization.md)),
justify a thread count against this job's actual hardware
([session2/03](../session2/03-exercise-hardware-aware-optimization.md)).
The same agent, aimed at measurement and optimization instead of feature
delivery, with a human approving each step — that's the skill meant to
transfer past today.

## The case for on-prem LLMs

[Session 1's pitch](../session1/02-why-onprem-llms.md) was cost, data
locality, and capability: free access through PLGrid's LLM Lab, nothing
leaving Cyfronet's infrastructure, and coding ability close enough to
Claude Sonnet's that the habits practiced today transfer to whichever
model participants use tomorrow. Today was the test of that last claim —
did GLM 5.2 actually hold up across a full day of profiling, diagnosis,
and optimization work, or did it need more hand-holding than expected?

## Pointers

- This repository — clone it, keep working on the solver past today, or
  reuse it as a template for a different agent-assisted performance
  exercise: the top-level [`README.md`](../../README.md) has the quick
  start.
- [PLGrid's LLM Lab](https://llmlab.plgrid.pl/) — the on-prem model
  access used today, available beyond the workshop for PLGrid users.
- [PPAM 2026](https://ppam.edu.pl/) — the conference this tutorial is
  part of, for the rest of the program.
