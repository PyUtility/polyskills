<div align = "center">

# AI Commands Extensions

[![Vendor Agnostic](https://img.shields.io/badge/Vendor-%20Agnostic-2E7D32?style=plastic)](vendor-agnostic/SKILL.md)

</div>

<div align = "justify">

A command is a task the user starts by name, such as `/vendor-agnostic`. Unlike a skill it never starts on its own: it
does one large job when it is called, and nothing otherwise. Each command is a folder with a `SKILL.md`, because a
command with templates and references has to find them: Claude Code gives a skill folder its own path, and gives none to
a single command file.

## Available Commands

<div align = "center">

| Command | Arguments | Purpose |
| :---: | :---: | --- |
| [`/vendor-agnostic`](vendor-agnostic/SKILL.md) | `[vendor ...] [links=pointer\|symlink]` | Moves a repository to one shared layer (`AGENTS.md`, `.agents/`, `docs/`) with thin entry points for Claude Code, Gemini CLI and Antigravity, and GitHub Copilot |

</div>

## Installing a Command

Install the folder where your tool looks for **skills**, under its own name:

```shell
$ polyskills manager https://github.com/PyUtility/polyskills \
      --source ./extensions/commands \
      --name vendor-agnostic \
      --destination ~/.claude/skills/vendor-agnostic \
      skills
```

  * Codex, Cursor, OpenCode, Gemini CLI, and GitHub Copilot read skills from `.agents/skills/` in a project, so
    `--destination ./.agents/skills/vendor-agnostic` serves them.
  * The Claude Code plugin of this repository carries the commands as `/llm-essentials:<command>`.
  * Do not copy the folder into `~/.claude/commands/`. There, Claude Code turns every `.md` file of the references into
    a command of its own, and the command cannot find its templates.

## Adding a Command

  1. Create `<command>/SKILL.md`, with `disable-model-invocation: true` and an `argument-hint` in the frontmatter, so
     that only the user starts it. Add `agents/openai.yaml` with `allow_implicit_invocation: false` for Codex.
  2. Put templates into `resources/` with the suffix `.template`, references into `references/`, and scripts into
     `scripts/`.
  3. Add a badge and a table row for the command to this file, and update the `COMMANDS` count badge of the root
     `README.md`.

The plugin manifest loads this folder through its `skills` key and sets `commands` to an empty list. Without the empty
list, Claude Code scans the folder for single command files, and this `README.md` would become a command as well.

</div>
