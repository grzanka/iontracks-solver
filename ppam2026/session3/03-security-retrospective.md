# Security retrospective

*[↑ Session 3](README.md) · [← Prev: Discussion: the agent's hardware reasoning](02-hardware-reasoning-discussion.md) · [Next: Wrap-up →](04-wrap-up.md)*

[Session 1's ground rules](../session1/03-agent-safety-rules.md) were
stated once, at 11:00, and then had to hold for seven hours of an agent
actually editing files and proposing commands on a shared HPC account.
This is where that gets checked.

## Questions for the room

- **Permission mode.** Did anyone see opencode propose a command they
  wouldn't have approved on reflection? What was it, and what caught it
  — the permission prompt itself, or something about the command that
  looked wrong at a glance?
- **Diffs.** Rule 2 was read every diff before accepting it. Did that
  habit catch anything — a change broader than what was asked for, a
  correctness-affecting edit disguised as a speed one? Session 2's
  exercise explicitly asked people to confirm "only the speed" changed,
  not the physics — did anyone's diff review actually catch a case where
  that wasn't true?
- **Commits as checkpoints.** Did anyone use a commit to back out of an
  agent-driven change that didn't work out? What made that easy or hard
  in practice?
- **Job submission.** The day's rule was: the agent drafts an `sbatch`
  script, a human reads it and submits it. Did anyone's agent draft
  something that needed correcting before it went anywhere near
  `sbatch` — wrong partition, wrong resource request, wrong time limit?
- **Destructive commands.** Rule 4 named `rm -rf` and force-pushes
  specifically. Did opencode ever propose one? Shared accounts make the
  blast radius of "approved without reading" much bigger than a laptop
  — did that risk feel abstract going in, and concrete by 16:30?

## Why the rules held (or didn't)

The rules in session 1 weren't about distrusting GLM 5.2 or Claude
specifically — they're the same habits that make sense for any coding
agent with tool access, on any shared account. If something slipped
through today despite the rules, that's more informative than a clean
run: it names exactly which habit needs to be tighter next time, and for
whom.

## Takeaways for shared HPC accounts generally

What from today's rules is specific to this exercise (a training repo,
a tutorial partition, a low-stakes solver), and what's a baseline any
lab running agentic coding tools on a shared cluster account should
adopt regardless of the workload? Naming that boundary out loud is the
point of this block — the rules should travel past today even though
the ionization-chamber solver won't.
