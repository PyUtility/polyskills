<div align = "center">

# Commands

</div>

<div align = "justify">

`extensions/commands/<name>/` holds commands: skills that only the user starts by name. The only one today is
`/vendor-agnostic`. Read this before changing it or adding a command. The guide for users is
`extensions/commands/README.md`.

## How A Command Is Built

  * A command is a folder with a `SKILL.md` whose frontmatter sets `disable-model-invocation: true` and an
    `argument-hint`, and an `agents/openai.yaml` with `allow_implicit_invocation: false` for Codex.
  * Templates go in `resources/` with the suffix `.template`, references in `references/`, and scripts in `scripts/`.
  * The plugin loads the folder through the `skills` key of `extensions/.claude-plugin/plugin.json` and sets `commands`
    to an empty list. Without that list, Claude Code would turn `extensions/commands/README.md` into a command.
  * Installed by hand, a command goes into a skills directory, never into `~/.claude/commands/`, where every reference
    file would become a command of its own.

## The Vendor-Agnostic Command

`/vendor-agnostic` moves a repository to one routed `AGENTS.md`, shared skills and agents under `.agents/`, pages under
`docs/`, and a thin entry point for each vendor.

  * `scripts/check.sh` validates the result and writes nothing. It is POSIX `sh` and `awk` with no arrays, no `local`,
    and no interval expressions, so dash, busybox, BSD awk, and mawk all run it. On Windows, run it with the `sh` of
    Git for Windows.
  * `.gitattributes` keeps every `*.sh` file at LF line endings, also in a Windows checkout.
  * Its two decision templates in `resources/docs/decisions/` are exact copies of the `make-adr` templates. Change them
    in `extensions/skills/make-adr/resources/` first, then copy them over. `check.sh` knows the `make-adr` placeholders
    and flags a half-filled record under `docs/decisions/`.

## Pitfalls And Limits

  * `check.sh` checks the repository it runs in (`git rev-parse --show-toplevel`). Test a change in a scratch git
    repository, not in this one.
  * The template markers differ inside the command: `{name}` and `{{ OPTIONAL: ... }}` in its own templates, the
    `make-adr` markers in the two decision templates.

</div>
