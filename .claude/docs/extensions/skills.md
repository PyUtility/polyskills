<div align = "center">

# Skills

</div>

<div align = "justify">

`extensions/skills/<name>/` holds one Agent Skill per folder: a `SKILL.md`, plus `resources/`, `references/`, or
`rules/` where the skill needs them. Read this before adding, changing, or registering a skill.

## How A Skill Is Built

  * **Frontmatter.** `name` matches the folder name in kebab-case. `description` says when the skill applies and ends
    with its trigger phrases, within the 1,024 characters the Agent Skills standard allows. A Claude Code key such as
    `disable-model-invocation` or `argument-hint` appears only where a skill needs it, as in `extend-init`.
  * **Body.** A Getting Started list, the rules, and a closing Quick Checklist, inside the `markdown-format` wrappers.
  * **Invocation.** The format skills (`python-code-format`, `sql-code-format`, `dbml-code-format`,
    `markdown-format`, `git-commiter`) and `humanize-text` apply whenever their kind of file or text is touched. The
    explicit-invoke skills (`code-modification-rule`, `flaunt-product`, `noadmin-auto-mode`, `god-mode`,
    `extend-init`) start only when the user asks, and their descriptions say so. `make-adr` starts on any request for
    a decision record.
  * **Templates.** Each skill names its own placeholder markers, so read the skill before filling one of its
    templates.

## Registering A Skill

Adding, renaming, or removing a skill updates, in the same change:

  1. The badges of `extensions/skills/README.md`, in alphabetical order.
  2. The `SKILLS` count badge of the root `README.md`.
  3. The skills table of `AGENTS.md`, when Codex can use the skill.

## Skills That Depend On Each Other

  * `python-code-format` sends Python changes to the agent suite in `extensions/agents/python/`, and
    `sql-code-format` does the same for SQL; see `extensions/agents.md`.
  * `humanize-text` refines only the prose that `markdown-format`, `git-commiter`, and the code format skills leave
    open.
  * `code-modification-rule` runs alongside a language skill, and the Better Comments hook keeps its comment tags in
    sync with VS Code; see `extensions/hooks.md`.
  * `make-adr` owns decision records, and `/vendor-agnostic` keeps exact copies of its two templates. Change them in
    `make-adr` first, then copy them over; see `extensions/commands.md`.
  * `extend-init` and `/vendor-agnostic` build rival layouts. Do not run `extend-init` on a repository that
    `/vendor-agnostic` set up.

## Pitfalls And Limits

  * Two spellings exist for the guidance folder: `reference/` in `dbml-code-format` and `sql-code-format`, and
    `references/` in the newer skills. Keep the one the skill already uses.
  * The registrations have drifted; `gaps.md` lists the skills missing from the badges or from `AGENTS.md`.

</div>
