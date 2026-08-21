# Why an on-prem LLM

*[↑ Session 1](README.md) · [← Prev: Domain and code walkthrough](01-domain-and-code-walkthrough.md) · [Next: Ground rules →](03-agent-safety-rules.md)*

Three points that need to land before anyone opens a terminal.

- **Cost.** GLM 5.2 runs on Cyfronet's own hardware, served through
  PLGrid's [LLM Lab](https://llmlab.plgrid.pl/) — free for science: no
  credit card, no subscription, no public-cloud usage. Everyone gets one
  LLM Lab access key for the day.
- **Data.** Code, prompts, and job scripts never leave Cyfronet's
  infrastructure. For several institutions represented in the room, that's
  a hard requirement, not a nice-to-have.
- **Capability.** GLM 5.2's coding ability is close enough to Claude
  Sonnet's that the exercises transfer: what people learn about directing
  an agent today applies to whichever model they use tomorrow.

## Let the agent run the loop

This isn't "paste an error into a chat, paste the fix back into the
terminal." Participants drive opencode as an agent: it reads the repo,
runs `pytest`/`bench.py`/`sweep.py` itself, reads the output, and — this is
the part vanilla "vibe coding" actually got right — retries and corrects
its own mistakes without anyone re-typing anything. A failing test becomes
the agent's next move, not a copy-paste round-trip through a browser tab.
That self-healing loop (call a tool, see it fail, fix it, call the tool
again) is what makes it more than autocomplete with extra steps.

What's different from open-ended vibe coding is where that loop points.
The abstract's "letting an AI agent produce software mostly on its own...
with little human interaction along the way" is exactly what today is
not: the same self-correcting loop gets aimed at measurement and
optimization instead of shipping a feature, one human-approved step at a
time — see [the ground rules](03-agent-safety-rules.md) for what
"approved" means in practice.
