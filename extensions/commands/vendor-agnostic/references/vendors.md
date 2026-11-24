<div align = "center">

# Vendors

</div>

<div align = "justify">

What each vendor reads, what this command creates for it, and the traps. Checked against the documentation listed under
**Sources** in November 2026, and for Claude Code 2.1.278 by experiment. Vendors change these files often: when the
documentation of a vendor disagrees with this page, follow the documentation and say so in the report.

<div align = "center">

| Vendor | Reads `AGENTS.md` | Entry Point To Create | Reads `.agents/skills/` | Reads `.agents/agents/` |
| :---: | :---: | :---: | :---: | :---: |
| Claude Code | Only when no `CLAUDE.md` exists, and not in every session | `CLAUDE.md` | No | No |
| Gemini CLI | Only when its settings name the file | `GEMINI.md` | Yes | No (`.gemini/agents/`) |
| Antigravity | Yes | None | Yes, one level deep | Yes |
| OpenCode | Yes | None | Yes | No (`.opencode/agents/`) |
| GitHub Copilot | Most surfaces | `.github/copilot-instructions.md` | Yes | No (`.github/agents/`) |
| OpenAI Codex | Yes | None | Yes | No (`.codex/agents/`) |
| Cursor | Yes | None | Yes | No (reads `.claude/agents/`) |

</div>

With no vendor argument, create every entry point in the table and the Claude Code links, and nothing else: the registry
in `AGENTS.md` lets every other tool use the shared agents by reading their files. The native agent files below are
written only for a vendor the user named.

## Shared Frontmatter

A shared file is read by several parsers at once, so it holds only what all of them agree on.

  * **Shared skill**: `name`, `description`, and, when needed, `license`, `compatibility`, `metadata`, `allowed-tools`.
    These are the six fields of the Agent Skills standard. The name is lower case with single hyphens, at most 64
    characters, and equal to the folder name. The description has at most 1,024 characters.
  * **Shared agent**: `name` and `description`. `model: inherit` is the only other value that Claude Code, Cursor,
    Gemini CLI, and Antigravity all accept.

The keys that collide, and why they stay out:

<div align = "center">

| Key | Claude Code | Antigravity | Gemini CLI | OpenCode | Copilot | Cursor |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `tools` | Claude tool names | Own names; an unknown one can hang the agent | Own names, as a list | Not a field; permissions instead | Aliases; unknown names ignored | Not a field |
| `model` | `opus`, `sonnet`, ... | `inherit`, `flash`, `pro` | A Gemini model | `provider/model` | A Copilot model | `inherit` or a Cursor model |
| `color` | A color name | Not a field | Not a field | A hex value | Not a field | Not a field |
| `skills` | Skill names | Paths | Not a field | Not a field | Not a field | Not a field |

</div>

A migrated agent often carries a tool limit. Never drop it: a read-only reviewer that inherits every tool has become a
security problem. Move the limit to the pointer or the native file of each vendor, and repeat its intent in the
**Boundaries** section of the shared file, where every tool can read it.

## Claude Code

  * **Create**: `CLAUDE.md` from [`CLAUDE.md.template`](../resources/CLAUDE.md.template), and the links of
    [links.md](links.md).
  * The line `@AGENTS.md` has to stand outside code. A sentence that asks Claude to read `AGENTS.md` loads nothing.
  * Keep `CLAUDE.md` even though Claude Code can read `AGENTS.md` by itself. That needs version 2.1.277 or later (some
    sessions 2.1.281), and it stops as soon as anyone adds a personal `CLAUDE.local.md`. The import works everywhere and
    never loads the file twice.
  * An `@path` **inside** `AGENTS.md` is expanded too, up to four hops deep, into every session. Wrap every literal `@`
    in backticks.
  * Block-level HTML comments are removed before loading. Other HTML reaches the model as text.
  * Any `.md` file under `.claude/commands/` becomes a slash command, a `README.md` included. An agent file without a
    `name` is skipped. A skill and a command with the same name resolve to the skill.
  * `.claude/skills/` in a package is found when Claude touches a file there.
  * Keys that only Claude Code reads (`disable-model-invocation`, `argument-hint`, `paths`, `context`, `model`, `hooks`
    on a skill; `tools`, `disallowedTools`, `permissionMode`, `color` on an agent) belong in the pointer.

## Gemini CLI And Antigravity

On 2026-06-18, Gemini CLI stopped serving free, Pro, and Ultra accounts, whose users move to Antigravity. It still works
with a Gemini Code Assist Standard or Enterprise license and with paid API keys. One `GEMINI.md` serves both tools.

  * **Create**: `GEMINI.md` from [`GEMINI.md.template`](../resources/GEMINI.md.template). Gemini CLI expands the import.
    Antigravity loads `AGENTS.md` by itself and only rewrites the reference to a path, so nothing loads twice.
  * Never write `@[label](AGENTS.md)` in `GEMINI.md`: Antigravity inlines that form. Never also list `AGENTS.md` under
    `context.fileName` in `.gemini/settings.json`.
  * **`.gemini/`**: keep what is there (settings, `commands/*.toml`) for Gemini CLI. Create nothing in it unless the
    user runs Gemini CLI. Antigravity reads no `.gemini/` folder in a project; offer to turn its commands into skills.
  * Antigravity cuts a rule file at 24,000 bytes, and demotes the largest ones past 20,000 tokens in total. It does not
    read an `AGENTS.md` below the folder that was opened, so the root file has to be enough.
  * Antigravity reads the whole `.agents/` folder: `rules/`, `hooks.json`, `mcp_config.json`, `AGENTS.md`, and every
    `.md` file in `agents/`. Put nothing else in there.
  * **Named only**: for Gemini CLI, `.gemini/agents/<role>.md` with `name`, `description`, `kind: local`, its own
    `tools` list, and the pointer directive as the body.

## OpenCode

  * **Create**: nothing. OpenCode reads `AGENTS.md` and then ignores `CLAUDE.md` in the same directory.
  * `.opencode/` keeps its configuration. Never list `AGENTS.md` or `docs/**` under `instructions` in `opencode.json`:
    everything there loads in every session.
  * OpenCode reads `.claude/skills/` and `.agents/skills/`. For the same name, `.agents/skills/` wins, so a pointer does
    no harm. It loads any `.md` file that sits directly in a skills folder as a skill.
  * An agent without `mode` becomes a primary agent, and a Claude-style `tools` list has been reported to stop OpenCode
    1 from starting. That is why agents are never linked into `.opencode/agents/`.
  * **Named only**: `.opencode/agents/<role>.md`:

```markdown
---
description: {the description of the shared agent}
mode: subagent
permissions:
  - action: edit
    resource: "*"
    effect: deny
---

Read `.agents/agents/{role}.md` from the repository root in full. It is your system prompt: follow it as written.
```

## GitHub Copilot

  * **Create**: `.github/copilot-instructions.md` from
    [`copilot-instructions.md.template`](../resources/copilot-instructions.md.template).
  * Write the pointer as a sentence with a link. Copilot CLI expands an `@path` in this file, and it loads `AGENTS.md`
    on its own as well.
  * The cloud agent, code review on GitHub, Copilot CLI, and chat in VS Code read `AGENTS.md`. Chat on GitHub.com, in
    Visual Studio, JetBrains IDEs, and Eclipse does not: it reads `copilot-instructions.md`, where a pointer carries no
    rules unless the chat can open files. Put this limit in the report, and do not copy rules into the file.
  * `.github/instructions/*.instructions.md` is path-scoped and has no equivalent elsewhere. Move its content to a page
    with a routing row for the same paths, and leave a short pointer file with the same `applyTo`.
  * Copilot reads `.github/skills`, `.claude/skills`, and `.agents/skills`.
  * **Named only**: `.github/agents/<role>.agent.md` with `description`, its `tools`, and the pointer directive as the
    body. Unknown tool names are ignored there.

## OpenAI Codex

  * **Create**: nothing. Codex reads `AGENTS.md` from the repository root down to the working directory, at most one
    file per directory, and stops at 32 KiB in total.
  * A file named `AGENTS.override.md` replaces `AGENTS.md` beside it, and an empty `AGENTS.md` is skipped.
  * Codex scans `.agents/skills` in every directory from the working directory up to the root. Its custom prompts are
    deprecated in favor of skills.
  * **Named only**: `.codex/agents/<role>.toml`. A custom agent inherits the sandbox of its parent, so a read-only role
    is only as read-only as the session that starts it.

```toml
name = "{role}"
description = "{the description of the shared agent}"
developer_instructions = """
Read `.agents/agents/{role}.md` from the repository root in full. It is your system prompt: follow it as written.
"""
```

## Cursor

  * **Create**: nothing. Cursor reads `AGENTS.md`, nested ones included, and combines them.
  * It reads skills from `.agents/skills`, `.cursor/skills`, `.claude/skills`, and `.codex/skills`, so a pointer may
    show up beside the shared skill. Both lead to the same file.
  * It reads agents from `.cursor/agents` and `.claude/agents`, so the Claude pointers serve it. It has no `tools` key:
    `readonly: true` is its only limit.
  * `.cursor/rules/*.mdc` moves into the shared layer (see [migration.md](migration.md)), and `AGENTS.md` replaces it.

## Other Tools

A tool that reads `AGENTS.md` works without a file. For one that does not, create its own instruction file, under 15
lines, that hands over to `AGENTS.md`, and only when the user names the tool. Look its file name and import syntax up in
its documentation first. Never guess them.

## Sources

  * Claude Code: [memory](https://code.claude.com/docs/en/memory), [skills](https://code.claude.com/docs/en/skills),
    [subagents](https://code.claude.com/docs/en/sub-agents), [permissions](https://code.claude.com/docs/en/permissions).
  * Gemini CLI: [context files](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md),
    [skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md),
    [subagents](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md),
    [the move to Antigravity](https://developers.googleblog.com/en/an-important-update-transitioning-gemini-cli-to-antigravity-cli/).
  * Antigravity: [rules](https://antigravity.google/docs/rules), [subagents](https://antigravity.google/docs/subagents),
    [customization discovery](https://antigravity.google/docs/customization-discovery).
  * OpenCode: [rules](https://opencode.ai/docs/rules/), [agents](https://opencode.ai/docs/agents/),
    [skills](https://opencode.ai/docs/skills/).
  * GitHub Copilot:
    [instruction support](https://docs.github.com/en/copilot/reference/custom-instructions-support),
    [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions),
    [custom agents](https://docs.github.com/en/copilot/reference/custom-agents-configuration).
  * OpenAI Codex: [AGENTS.md](https://developers.openai.com/codex/guides/agents-md),
    [skills](https://developers.openai.com/codex/skills), [subagents](https://developers.openai.com/codex/subagents).
  * Cursor: [rules](https://cursor.com/docs/rules), [skills](https://cursor.com/docs/skills),
    [subagents](https://cursor.com/docs/subagents).
  * Standards: [AGENTS.md](https://agents.md/), [Agent Skills](https://agentskills.io/specification).

</div>
