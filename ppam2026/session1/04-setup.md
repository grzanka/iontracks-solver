# Setup

*[↑ Session 1](README.md) · [← Prev: Ground rules](03-agent-safety-rules.md) · [Next: Exercise →](05-exercise-measurement.md)*

## Resources

- Athena supercomputer, hosted at ACK Cyfronet: 48 GPU nodes, each with 128
  CPU cores (2× AMD EPYC 7742) and 1 TB RAM, plus 8× NVIDIA A100-SXM4-40GB
  GPUs (384 GPUs total).
- Access via SSH (terminal on Linux/macOS, PowerShell or a terminal app on
  Windows) — the access node is reachable from the internet, worker nodes
  are reached from there via SLURM interactive jobs.
- [LLM Lab](https://llmlab.plgrid.pl/) inference service (LLM models hosted
  on Cyfronet hardware), reachable both from Athena and from your own
  laptop, free for scientists.

## Accounts

- Tutorial accounts, valid for a few days, are provided to participants —
  they include access to Athena (including GPU nodes) and to LLM Lab.
  Credentials aren't handed out at registration — they're distributed
  via Slack instead, as an account number and password per participant;
  the invite link to join the workspace is shared during the session.
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

Replace `XXX` with the account number from the credentials posted in
Slack (see [Accounts](#accounts) above) — not something handed out at
registration. This drops you on the Athena **access node** — expect a
banner and a shell prompt; don't run anything heavier than `git` or
`curl` here, actual computation happens later on a worker node via
`srun`.

### 2. Clone the exercise repo

`$SCRATCH` is shared storage visible from both the access node and worker
nodes, so cloning here now means it's already in place once you `srun`
into a compute node in the next exercise:

```bash
cd $SCRATCH
```

Clone the repo:

```bash
git clone https://github.com/grzanka/iontracks-solver.git
```

`git clone` prints the usual "Cloning into 'iontracks-solver'... done" and
a few progress lines.

Move into the checkout:

```bash
cd iontracks-solver
```

You should now be inside it, with `ion_chamber/`, `bench.py`, and
`opencode.json` all present (`ls` to confirm).

### 3. Install opencode

```bash
curl -fsSL https://opencode.ai/install | bash
```

This downloads the `opencode` binary to `~/.opencode/bin/opencode` and
adds that directory to your `PATH` by editing your shell's rc file
(`.bashrc`, `.zshrc`, ...). That edit only takes effect in shells started
*after* it runs — your current SSH session already sourced `.bashrc`
before the install, so it never picks up the change.

<details>
<summary>What happens if you try <code>opencode</code> right now</summary>

```
opencode
-bash: opencode: command not found
```
</details>

Log out (`exit` or `logout`) and SSH back into Athena to pick up the
updated `PATH`. Once you're back in, confirm it's found:

```bash
opencode models
```

This lists the free models opencode ships preconfigured with out of the
box — no login needed, e.g. `opencode/big-pickle`,
`opencode/nemotron-3-ultra-free`. These run on opencode's own cloud, not
on Cyfronet hardware — we won't use them; the next step adds the
Cyfronet-hosted PLGrid models on top.

opencode's own machine-wide config lives under your home directory, but
this repo carries its own per-project config in `opencode.json` and
`.opencode/plugins/` (already there from the clone above), which is what
lets opencode talk to the Cyfronet-hosted LLM.

### 4. Authenticate against LLM Lab

Log back in after step 3's relogin, and you land in your **home
directory** (`~`), not the project checkout — SSH always drops you there
fresh, it doesn't remember where you `cd`'d to last time. Go back into
the repo first:

```bash
cd $SCRATCH/iontracks-solver
```

The `plgrid` provider isn't a thing opencode knows about globally — it's
defined by this repo's `opencode.json` and `.opencode/plugins/`, so the
login command only works from inside the project directory.

Grab your LLM Lab access token — organizers hand these out for tutorial
accounts; on your own PLGrid account, generate one yourself at
<https://llmlab.plgrid.pl> under **Grants → Generate API Key** (Forge must
be activated first, at <https://portal.plgrid.pl/services/111>). Then run:

```bash
opencode providers login -p plgrid
```

Paste the token when prompted. opencode confirms the login and stores it
for future sessions — you won't be asked again on this account.

If you run that command from anywhere outside the project (like your
home directory right after logging back in), opencode has no idea what
`plgrid` is:

<details>
<summary>What goes wrong outside the project directory</summary>

```
opencode providers login -p plgrid

┌  Add credential
Error: Unknown provider "plgrid"
```
</details>

If you see that, `cd` into `$SCRATCH/iontracks-solver` and try again.

### 5. Verify it can see the models

```bash
opencode models plgrid
```

Expect a list of PLGrid-hosted models. We'll use **GLM 5.2**
(`zai-org/GLM-5.2-FP8`, 1M-token context, ~750 GB VRAM, comparable to
Claude Sonnet in benchmarks) as the default.

### 6. Say hello to the agent

Listing models only confirms opencode knows they exist — it doesn't
confirm a prompt actually makes it to GLM 5.2 and back. Launch opencode:

```bash
opencode
```

Once it's up, send it a one-line prompt, e.g. `What model are you, and
what files are in this repo?` It should name GLM 5.2 (or the PLGrid model
you're on) and correctly list this checkout's contents
(`ion_chamber/`, `bench.py`, ...) — proof the round trip to Cyfronet's
hardware and back actually works, not just that credentials were
accepted. `Ctrl+C` (or `/exit`) to leave once you've seen a reply.

You're set — head to the [exercise](05-exercise-measurement.md).
