# Discussion: the agent's hardware reasoning

*[↑ Session 3](README.md) · [← Prev: Solution reveal and synthesis](01-solution-reveal-and-synthesis.md) · [Next: Security retrospective →](03-security-retrospective.md)*

Session 2's hardware-aware exercise asked participants to push the agent
for a concrete thread-count recommendation grounded in *this job's*
`lscpu`/`nproc`/`taskset`/`numactl` output, not textbook Amdahl's-law
reasoning. This is where that gets checked against what actually
happened.

## Questions for the room

- Where did the agent's hardware reasoning hold up? Did a claim like
  "per-step overhead dominates at this grid size" or "cores are scattered
  across NUMA nodes, so parallel overhead eats the win" actually match
  the sweep numbers it was reasoning about?
- Where didn't it hold up? Did anyone catch the agent asserting something
  about cache size, NUMA layout, or expected speedup that a re-run
  contradicted?
- How did people tell the difference? The exercise's ground rule was
  "explain using this run's numbers" rather than accepting a general
  rule of thumb — did that habit actually catch bad reasoning in
  practice, or did some plausible-sounding explanations slip through
  unchallenged?
- Did anyone's agent change its recommendation when `--radius-um` grew
  (more work per PDE step, same NUMA layout)? Was that shift consistent
  with what a bigger working set relative to cache size would predict?

## The general pattern

An LLM will produce a confident-sounding hardware explanation whether or
not it's grounded in the numbers actually in front of it — that's not a
GLM 5.2 or Claude-specific failure, it's a property of how these models
answer questions. The habit this afternoon was built around — always ask
for the specific run's numbers, not a general justification — is the
mitigation, and it generalizes past today's solver to any performance
work done with an agent: profiler output and hardware topology are
ground truth, the agent's narrative about them is a hypothesis to check,
not a conclusion to accept.
