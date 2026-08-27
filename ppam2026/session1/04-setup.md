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

## Installing and configuring opencode yourself

Not needed today — Athena already has this done for you. Use this if you
want opencode on your own machine afterwards, or want to see how the
workshop setup was built.

**Install.** Run the official installer:

```bash
curl -fsSL https://opencode.ai/install | bash
```

It downloads the `opencode` binary to `~/.opencode/bin/opencode` and adds
that directory to your `PATH` by editing your shell's rc file (`.bashrc`,
`.zshrc`, ...), so open a new shell (or `source` the rc file) before the
`opencode` command is found. Pass `--no-modify-path` if you'd rather wire
up `PATH` yourself.

opencode's own config and state live outside that install directory. A
project carries its own config as `opencode.json` and `.opencode/plugins/`
at its root — that's what we use below, so the PLGrid setup only applies
while you're working in this repo. (Login state is separate again: it's
saved to `~/.local/share/opencode/auth.json` regardless.)

**Configure it for PLGrid LLM Lab, per-project.** This is exactly what's
already set up for you on Athena. The provider plugin and model/agent
config come from
[plgrid-llmlab-opencode](https://github.com/groundnuty/plgrid-llmlab-opencode);
a copy of the two files that matter (`opencode.json` and
`.opencode/plugins/plgrid.js` — its `AGENTS.md` is skipped) is vendored in
this repo at [`opencode-plgrid/`](opencode-plgrid/), so you don't need to
clone that repo separately — just this one (see
[`05-exercise-diagnosis.md`](05-exercise-diagnosis.md) if you haven't
cloned it yet):

- [ ] Activate the Forge service on your PLGrid account at
      <https://portal.plgrid.pl/services/111>, then generate an API key at
      <https://llmlab.plgrid.pl> under **Grants → Generate API Key**.
- [ ] From the root of your `iontracks-solver` checkout, drop the vendored
      config into the project itself:

```bash
cp -r ppam2026/session1/opencode-plgrid/.opencode .
```

```bash
cp ppam2026/session1/opencode-plgrid/opencode.json .
```

- [ ] Authenticate, pasting the API key you generated above when prompted:

```bash
opencode providers login -p plgrid
```

- [ ] Verify it can see the PLGrid models:

```bash
opencode models plgrid
```

The repo's README also documents which of its models actually do
agentic work reliably (a few of the 15 don't support tool calls at all,
and one is fast but has produced silently-wrong code) — worth a skim
before you pick a default for real work.

opencode also supports a machine-wide config under `~/.config/opencode/`,
applying to every project at once — not covered here, since this training
sticks to the per-project setup above.
