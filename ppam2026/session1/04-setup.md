# Setup

*[↑ Session 1](README.md) · [← Prev: Ground rules](03-agent-safety-rules.md) · [Next: Exercise →](05-exercise-diagnosis.md)*

## Resources

- Athena supercomputer, hosted at ACK Cyfronet: XXX CPU nodes (?? cores,
  ?? RAM each), YYY GPU nodes (ZZZ GPUs, model ??, ?? VRAM).
- Access via SSH (terminal on Linux/macOS, PowerShell or a terminal app on
  Windows) — the access node is reachable from the internet, worker nodes
  are reached from there via SLURM interactive jobs.
- LLM Lab inference service (LLM models hosted on Cyfronet hardware),
  reachable both from Athena and from your own laptop, free for
  scientists.

## Accounts

- Tutorial accounts, valid for a few days, are provided to participants —
  they include access to Athena (including GPU nodes) and to LLM Lab.
- If you already have a PLGrid account with Athena and LLM Lab activated,
  these same materials work with that account instead.
- You can also run everything on your own laptop, limited by whatever
  hardware you have there — most likely no large core count.

## Software

- **opencode** — an open-source "AI coding agent" terminal application (it
  also has a GUI, unused today) that talks to both free inference services
  (like Cyfronet's LLM Lab) and paid ones (like Claude).
- **Visual Studio Code** — an open-source IDE; it can also be pointed at
  LLM Lab.

## Get set up

### 1. Log into Athena

```bash
ssh tutorialXXX@athena.cyfronet.pl
```

Replace `XXX` with the number you were given at registration. This drops
you on the Athena **access node** — expect a banner and a shell prompt;
don't run anything heavier than `git` or `curl` here, actual computation
happens later on a worker node via `srun`.

### 2. Clone the exercise repo

```bash
cd $SCRATCH
```

```bash
git clone https://github.com/grzanka/iontracks-solver.git
```

```bash
cd iontracks-solver
```

`$SCRATCH` is shared storage visible from both the access node and worker
nodes, so cloning here now means it's already in place once you `srun`
into a compute node in the next exercise. `git clone` prints the usual
"Cloning into 'iontracks-solver'... done" and a few progress lines; you
should end up inside the checkout, with `ion_chamber/`, `bench.py`, and
`opencode.json` all present (`ls` to confirm).

### 3. Install opencode

```bash
curl -fsSL https://opencode.ai/install | bash
```

This downloads the `opencode` binary to `~/.opencode/bin/opencode` and
adds that directory to your `PATH` by editing your shell's rc file
(`.bashrc`, `.zshrc`, ...). Open a new shell — or log out and back in via
SSH — before the `opencode` command is found.

opencode's own machine-wide config lives under your home directory, but
this repo carries its own per-project config in `opencode.json` and
`.opencode/plugins/` (already there from the clone above), which is what
lets opencode talk to the Cyfronet-hosted LLM.

### 4. Authenticate against LLM Lab

Grab your LLM Lab access token — organizers hand these out for tutorial
accounts; on your own PLGrid account, generate one yourself at
<https://llmlab.plgrid.pl> under **Grants → Generate API Key** (Forge must
be activated first, at <https://portal.plgrid.pl/services/111>). Then run:

```bash
opencode providers login -p plgrid
```

Paste the token when prompted. opencode confirms the login and stores it
for future sessions — you won't be asked again on this account.

### 5. Verify it can see the models

```bash
opencode models plgrid
```

Expect a list of PLGrid-hosted models. We'll use **GLM 5.2** (xx context,
yyy VRAM, comparable to Claude Sonnet in benchmarks) as the default.

You're set — head to the [exercise](05-exercise-diagnosis.md).
