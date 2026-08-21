# Why an on-prem LLM

*[↑ Session 1](README.md) · [← Prev: Domain and code walkthrough](01-domain-and-code-walkthrough.md) · [Next: Ground rules →](03-agent-safety-rules.md)*

Three points that need to land before anyone opens a terminal.

- **Cost.** GLM 5.2 runs on Cyfronet's own hardware, served through
  PLGrid's [LLM Lab](https://llmlab.plgrid.pl/) — free for science, no
  personal API key, nothing metered for participants.
- **Data.** Code, prompts, and job scripts never leave Cyfronet's
  infrastructure. For several institutions represented in the room, that's
  a hard requirement, not a nice-to-have.
- **Capability.** GLM 5.2's coding ability is close enough to Claude
  Sonnet's that the exercises transfer: what people learn about directing
  an agent today applies to whichever model they use tomorrow.

## Not a chat window

This isn't "paste an error into a chat, paste the fix back into the
terminal." Participants drive opencode as an agent that reads the repo,
runs `pytest`/`bench.py`/`sweep.py`, and edits files directly. The skill
being taught is delegating the loop to the model under supervision, not
relaying text between two windows by hand — see
[the ground rules](03-agent-safety-rules.md) for what "under supervision"
means in practice.

Worth naming as the counterpoint to the abstract's "vibe coding" framing:
the point of the day isn't the specific model, it's the discipline of
using one — profiling instead of guessing, real hardware constraints
instead of assumptions, review instead of blind trust.
