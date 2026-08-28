# ppam2026/session1

Every markdown file here carries a one-line nav right under its H1:
`↑ Session 1` linking to `README.md`, plus `Prev`/`Next` linking to the
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
