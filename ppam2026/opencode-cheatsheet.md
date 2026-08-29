# opencode cheatsheet

*[↑ PPAM 2026 workshop](README.md) — reference material, not part of the
agenda. Nothing here is required reading; dip in when a command or a
config knob isn't obvious.*

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

**Today's rule (see [session1's ground rules](session1/03-agent-safety-rules.md)):
nobody runs `--auto` or enables auto-approve.** Concretely, on Athena that
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
  (`/check`, `/review`, `/explain`), permission rules, and agent
  definitions (`chat`, `reviewer`, `researcher`, `architect`, `fastfix`).
- `AGENTS.md` — project-specific instructions loaded into every session
  automatically (see the [Rules docs](https://opencode.ai/docs/rules/)).
- `.opencode/plugins/` — the plugin code the `opencode.json` config above
  refers to.
