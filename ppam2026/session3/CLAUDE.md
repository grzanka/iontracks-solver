# ppam2026/session3

Same conventions as [`session1/CLAUDE.md`](../session1/CLAUDE.md), copied
here since this directory can be edited independently:

Every markdown file here carries a one-line nav right under its H1:
`↑ Session 3` linking to `README.md`, plus `Prev`/`Next` linking to the
adjacent numbered file (use `—` for whichever end doesn't apply). Keep
`README.md`'s numbered list as the source of truth for ordering — when
adding, removing, or reordering a file, update that list and fix the
neighbors' nav links.

Shell commands meant to be copy-pasted go one per ` ```bash ` block —
never stack multiple commands in one fenced block. A reader who clicks
"copy" on a code block should get exactly one command on their clipboard,
not a multi-line script.

Terminal output (command results, transcripts, error messages) goes in a
plain (unlabeled) fenced block wrapped in `<details><summary>...</summary>`
— e.g. `<summary>Expected output</summary>` for a success case, or a
short description of the failure for a "what goes wrong" case. This keeps
it visually and structurally distinct from the `bash` blocks above it,
which are always meant to be typed; collapsing it by default also keeps
long transcripts from cluttering the page. Never put output inside a
` ```bash ` block.

This session is plenary, not hands-on — there's no opencode step and no
"Resume your session" boilerplate like session2's exercise files. Don't
add task lists with Terminal/opencode step labels here; these are
discussion notes for the instructors to talk from, not exercises for
participants to work through. Don't add a "What 'done' looks like" or
"Wrapping up" section to any file — the workshop's own wrap-up is
[04-wrap-up.md](04-wrap-up.md), and per-file end-of-exercise summaries
were tried and dropped in session1/session2 (see their git history).
