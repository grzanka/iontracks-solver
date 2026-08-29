# opencode cheatsheet

*[↑ Session 1](README.md) · [← Prev: Diagnose](06-exercise-diagnosis.md) · [Next: Session 2 →](../session2/01-reframing-the-question.md)*

A reference doc, not a new exercise: commands, permission modes, and
agent/subagent mechanics for everything used so far this morning,
gathered in one place. Nothing here is a new ground rule; dip back in
whenever a command or a config knob isn't obvious.

## Docs

- [opencode.ai/docs](https://opencode.ai/docs/) — docs home
- [CLI reference](https://opencode.ai/docs/cli/)
- [Permissions](https://opencode.ai/docs/permissions/)
- [Rules (`AGENTS.md`)](https://opencode.ai/docs/rules/)
- [Agents](https://opencode.ai/docs/agents/)
- [Config (`opencode.json`)](https://opencode.ai/docs/config/)
- [Source](https://github.com/sst/opencode)

## Everyday commands

| Command | Does |
|---|---|
| `opencode` | Launch the interactive TUI in the current directory |
| `opencode run "prompt"` | One-shot, non-interactive: send a prompt, print the reply, exit |
| `opencode models` | List models available with no login (opencode's own cloud, not Cyfronet) |
| `opencode models plgrid` | List Cyfronet/PLGrid-hosted models (needs step below) |
| `opencode providers login -p plgrid` | Authenticate against LLM Lab with a PLGrid token |
| `opencode --agent <name>` / `run --agent <name>` | Use a specific agent (e.g. this repo's `reviewer`, `researcher`) |
| `opencode --model <provider/model>` / `-m` | Override the default model for the session |
| `/exit` or `Ctrl+C` | Leave the TUI |

`opencode run` is what you'd reach for in a batch script or a one-off
question where the full TUI is overkill — same permission system applies,
it just prints instead of drawing a UI.

## Agents and subagents

opencode agents come in two modes, and that mode decides *how you reach
them* — not what they're for.

- **`primary`** — can be your *current* agent, driving the whole
  conversation. Only one is active at a time; you switch between them.
- **`subagent`** — never drives on its own. It's invoked for a single
  task, reports back, and control returns to whichever primary agent you
  were in.

### Cycling primary agents: `Tab`

**Tab** in the TUI cycles through primary agents:

```
Build → Architect → Chat → Plan → (back to Build)
```

| Agent | Origin | What it is |
|---|---|---|
| `build` | opencode built-in | The default — full edit + bash access, gated by this repo's permission rules. |
| `plan` | opencode built-in | Can't edit real files (only its own plan-file path), can't delegate to `general`. |
| `architect` | **added in this repo's `opencode.json`** | Can't edit anything, but *can* delegate freely — plans, then hands the edit to `fastfix`/`general` and the check to `reviewer`. |
| `chat` | **added in this repo's `opencode.json`** | All tools denied, plain conversation — a workaround for PLGrid models without function-calling support (Bielik v2.6, PLLuM, QwQ-32B, Qwen3-VL). |

opencode also runs three more built-in primaries internally
(`compaction`, `summary`, `title` — context compaction, session
summaries/titles) that don't appear on the Tab cycle; you never drive a
session as one of them.

### Calling subagents: `@name`, or delegation

Subagents never show up on Tab, however you invoke them. Two ways to
reach one:

1. **Direct mention** — type `@researcher <question>` (or `@reviewer`,
   `@fastfix`, `@general`, `@explore`) in the chat with whatever primary
   agent you're currently in. It runs, reports back, and you're still in
   `build` (or wherever you were) right afterward.
2. **Delegation** — a primary agent with `task` permission hands work to
   a subagent itself. `architect` does this by design; the built-in
   slash commands do it too — `/explain` delegates to `researcher`,
   `/review` delegates to `reviewer`.

| Subagent | Origin | Can edit? | Can run bash? | Use it for |
|---|---|---|---|---|
| `researcher` | **added in this repo** | no | only `rg`/`grep`/`find`/`ls` | "explain what this code does" — file:line-grounded, can't touch anything. Introduced in [session1/06](06-exercise-diagnosis.md). |
| `reviewer` | **added in this repo** | no | no | a second, read-only pass over a diff before committing. Suggested in [session2/02](../session2/02-exercise-algorithmic-optimization.md). |
| `fastfix` | **added in this repo** | yes | yes (normal rules) | small, well-specified mechanical edits — fast model, tight brief. |
| `general`, `explore` | opencode built-in | yes / read-heavy | yes | opencode's own general-purpose workhorses for delegated work or search. |

### The mental model

**Primary = who's "driving" right now** (Tab switches this). **Subagent
= a tool the current driver reaches for** and gets control back from
immediately after. If `@researcher` (or any other subagent) doesn't show
up when you press Tab, that's not a missing config — subagents are
defined with `"mode": "subagent"` in `opencode.json` specifically so
they're never a driving seat, only a tool.

## Permission modes: allow / ask / deny

Every tool call opencode wants to make (edit a file, run a shell command,
fetch a URL, ...) resolves to one of three states, configured in
`opencode.json` under `"permission"`, matched by pattern (most specific
wins — see this repo's own config for a worked example, `rm -rf *` denied
even though `bash: "*"` is otherwise `"ask"`):

- **`allow`** — runs with no prompt.
- **`ask`** — opencode stops and shows you the exact command/edit; you
  approve once, approve-for-the-rest-of-the-session, or reject.
- **`deny`** — blocked outright, no prompt, no override from the CLI.

Defaults lean permissive (most things are `allow` unless a project's
config narrows them); `ask` is what you opt into for anything you want a
human to see before it runs.

## `--auto` mode — read this before you touch it

`opencode --auto` (also `opencode run --auto "..."`, and the TUI's
command palette → *Enable auto-approve permissions*) auto-approves every
permission request that would otherwise be `ask`. **Explicit `deny` rules
still block**, so `--auto` is not "no permissions at all" — but it *is*
"no human sees this before it runs," which is exactly the property that
makes an agent dangerous on a shared account.

**Today's rule (see [the ground rules](03-agent-safety-rules.md)): nobody
runs `--auto` or enables auto-approve.** Concretely, on Athena that
means:

- A malformed or runaway `sbatch` on a shared allocation isn't
  hypothetical — the agent drafts, a human reads and submits.
- A repo's `deny` list is only as good as whoever wrote it; the tutorial
  config here denies `rm -rf *`, `git push *`, `git rebase*`,
  `git reset --hard*` — but that list was written by us, for this repo,
  today. Don't assume it, or any config you didn't read, covers
  everything destructive on a system you don't fully control.
- `ask` is also where you catch the agent about to do something correct
  syntactically and wrong in intent (right command, wrong branch; right
  idea, wrong file). `--auto` removes that checkpoint along with the
  friction.

If you want to experiment with `--auto` later, on your own machine, on a
project you own: start from a config with real `deny` rules for anything
irreversible or outward-facing (force-pushes, `rm -rf`, job/deploy
submission, secrets access), not from an empty permission block.

## Security notes

- **Read every diff before accepting it** — the point of `ask` mode is
  wasted if you approve without reading.
- **Commit before and after agent-driven changes.** Cheap checkpoints,
  and the only reliable way to `git diff` one step instead of three.
- **MCP servers and plugins run code you didn't write** — this repo's
  `opencode.json` enables one (`context7`, for library docs lookups);
  treat adding a new one the same as adding a new dependency: check what
  it is before turning it on.
- **Secrets go in environment variables, not config files.** `opencode.json`
  supports `{env:VAR_NAME}` interpolation — never paste a token directly
  into a committed file.
- **`.env` files are unreadable by the agent by default.** That's a
  deliberate guardrail; don't special-case it away for convenience.
- **Subagents can be scoped down.** This repo's `reviewer` and
  `researcher` agents deny `edit` and most of `bash` entirely (see
  `opencode.json`) — a narrowly-scoped subagent is safer by construction
  than remembering to be careful with a general one.

## Where this repo's config lives

- `opencode.json` — model defaults, MCP servers, custom commands
  (`/check`, `/review`, `/explain`), permission rules, and the
  project-specific agents from the section above (`chat`, `architect`,
  `reviewer`, `researcher`, `fastfix`).
- `AGENTS.md` — project-specific instructions loaded into every session
  automatically (see the [Rules docs](https://opencode.ai/docs/rules/)).
- `.opencode/plugins/` — the plugin code the `opencode.json` config above
  refers to.
