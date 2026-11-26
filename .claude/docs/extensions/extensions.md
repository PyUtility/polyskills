<div align = "center">

# Extension Library

</div>

<div align = "justify">

`extensions/` holds everything the repository ships to coding assistants: skills, agents, commands, and hooks. Nothing
here is built. The files are Markdown, templates, and a few scripts, read by Claude Code, by Codex, and by the
`polyskills` CLI that installs them one folder at a time.

## Members

<div align = "center">

| Document | Code | Read When |
| :---: | :---: | --- |
| `extensions/skills.md` | `extensions/skills/` | Adding, changing, or registering a skill |
| `extensions/agents.md` | `extensions/agents/` | Changing the Python or SQL agent suites |
| `extensions/commands.md` | `extensions/commands/` | Changing `/vendor-agnostic`, or adding a command |
| `extensions/hooks.md` | `extensions/hooks/` | Changing the Better Comments hook, or adding a hook |

</div>

## Shared Conventions

  * Each extension is a folder named after it, and `polyskills manager --name <folder>` installs exactly that folder.
    A folder therefore holds everything its extension needs.
  * Markdown follows the `markdown-format` skill. A `SKILL.md` or an agent file opens with YAML frontmatter, then the
    `center` and `justify` div wrappers, uses no emoji in its headings, and ends with a Quick Checklist.
  * Templates carry the suffix `.template` and live in `resources/`. Long guidance lives in `references/`, or in
    `reference/` in older skills, and is read only when a step needs it.
  * Each kind has a `README.md` index with one Shields.io badge per extension, and the root `README.md` has a count
    badge per kind: `HOOKS`, `SKILLS`, `AGENTS`, and `COMMANDS`. Adding, renaming, or removing an extension updates
    both in the same change.
  * The plugins ship the whole folder; `release.md` covers the manifests.

</div>
