<div align = "center">

# AI Skills Extensions

[![Git Commiter](https://img.shields.io/badge/Git-%20Commiter-003B57?style=plastic&logo=git)](git-commiter/SKILL.md)
[![Markdown Format](https://img.shields.io/badge/Markdown-%20Format-003B57?style=plastic&logo=markdown)](markdown-format/SKILL.md)
[![Python Code Format](https://img.shields.io/badge/Python-%20Code%20Format-003B57?style=plastic&logo=python)](python-code-format/SKILL.md)
[![SQL Code Format](https://img.shields.io/badge/SQL-%20Code%20Format-003B57?style=plastic&logo=postgresql)](sql-code-format/SKILL.md)

</div>

<div align = "justify">

Skills are a *bundled package* of domain knowledge + instructions (plus an optional scripts/assets) that the LLM loads
on-demand when a task matches its description. Typically a folder with a SKILL.md (front matter: name, description,
optional allowed-tools) plus supporting files. LLM tools may have different formats in which they accept skills -
either as a *prompt* or as a *agent skills* format, etc.

## Claude Code Skills

Claude Code (& Claude Web) allows skills to be defined at different scope level - enterprise, personal, project and also as
a plugin (for more details check [documentations](https://code.claude.com/docs/en/skills)). It is recommended that the
personalization skills defined in this repository are to be installed at the personal (`~/.claude/skills/...`) directory, such
that every project can access the same.

Claude Code uses *open standard* [Agent Skills](https://agentskills.io/home) which works across multiple AI tools. Additional
features like [*invocation control*](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill),
[subagent execution](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent) are extended from the standard format
that provides superpowers to the Claude Code. Every skill needs a `SKILL.md` file with two parts: YAML frontmatter
(between `---` markers) that tells Claude when to use the skill, and markdown content with instructions Claude follows when
the skill is invoked. The **`name`** field becomes the `/slash-command`, and the description helps Claude decide when to
load it automatically.

### Testing Claude Skill

A skill can be tested in two ways: (i) letting Claude invoke it automatically by asking somethind that matches the description
of the skill, or (ii) invoke it directly with the skill name `/skill-name <optional> additional details` from the terminal.

### Registering Claude Skill Globally

Claude Code is configured to read the global skills from the `~/.claude/skills/.../SKILL.md` file, and the same can be
registered in the (global/personal) **`~/.claude/settings.json`** file. Add or merge the skill in the below format:

```json
{
  ...

  "skills": {
    "global": [
      {
        "name": "...",
        "description": "...",
        "skill_path": "~/.claude/skills/.../SKILL.md",
        "trigger_keywords": [...],
        "always_load": false
      },
      ...
    ]
  }
  ...
}
```

### Global Claude Initialization File

A global `CLAUDE.md` file can also be created (recommended) under `~/.claude/CLAUDE.md` with the skill for reference. Add the
content in the format below:

```markdown
...

## Global ... Skill
When the user asks to *...*, you must:

  1. First ...
  2. Second ...

This skill governs:
  - ...
  - ...

DO NOT SKIP reading the skill file even for a small change.
```

The **last line** ensures that the skill file is always read, but doing so **will increase token consumption**. This is an
optional setting, and is recommended to be used in a production environment.

</div>
