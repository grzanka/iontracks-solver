# Setup

*[↑ Session 1](README.md) · [← Prev: Ground rules](03-agent-safety-rules.md) · [Next: Exercise →](05-exercise-diagnosis.md)*

Get this done before 11:00 if possible — the session doesn't have much
slack for account provisioning.

- [ ] **Get on Athena.** Two ways in, both give you real CPU and GPU
      resources for the day:
  - browser: <https://jupyterhub.athena.cyfronet.pl/>
  - terminal: `ssh tutorialXXX@athena.cyfronet.pl` (replace `XXX` with the
    number you were given at registration)
- [ ] **opencode is already installed** on Athena for this workshop — no
      install step needed. For docs (e.g. if you want it on your own
      machine afterwards), see <https://opencode.ai/>.
- [ ] **GLM 5.2 access is already configured** — your LLM Lab token is set
      up for you, so opencode should talk to the model with no extra
      configuration. If you want to see how that wiring works, or set it
      up yourself later, there's a ready-made opencode + LLM Lab config at
      <https://github.com/groundnuty/plgrid-llmlab-opencode>.
- [ ] **Hello-agent test.** Open opencode in this repo and ask it to list
      the files in `ion_chamber/` and summarize `solver.py` in three
      sentences. If that works, the tool chain is fine.
- [ ] **Re-read the submission rule** in
      [`03-agent-safety-rules.md`](03-agent-safety-rules.md) — it applies
      from the first job onward, not just the optimization session.

Didn't get a `tutorialXXX` account or can't reach either endpoint above?
Ask an organizer before 11:00, not after.
