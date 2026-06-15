<div align = "center">

# LLM Essentials - Codex Instructions

</div>

<div align = "justify">

This repository ([`PyUtility/polyskills`](https://github.com/PyUtility/polyskills)) curates reusable
[Agent Skills](https://agentskills.io/home) and agents under [`extensions/`](./extensions/). This
`AGENTS.md` is the natively-discovered entry point for [OpenAI Codex](https://developers.openai.com/codex);
it is loaded automatically whenever Codex runs inside this repository. For Claude Code, the same content
is published as a plugin via [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json).

## 🧰 Available Skills

The canonical skills live under [`extensions/skills/`](./extensions/skills/). Each is a standard
`SKILL.md` (with YAML frontmatter) and applies only when its description matches the task at hand.

| 🔖 Skill | 🎯 Applies When |
| :--- | :--- |
| `git-commiter` | Creating, amending, or writing any git commit message in this repository. |
| `markdown-format` | Creating, editing, or reviewing any `*.md` file (README, SKILL, AGENT, docs). |
| `python-code-format` | Creating, editing, or reviewing any `*.py` file or Python code. |
| `sql-code-format` | Creating, editing, or reviewing any `*.sql` file (PostgreSQL flavour). |

> [!NOTE]
> The Python *agent suite* under [`extensions/agents/python/`](./extensions/agents/python/) targets
> Claude Code's subagent model, which Codex does not implement. Use the skills above with Codex; the
> agent behaviour can be invoked via the `polyskills` CLI adapter (prompt conversion) if needed.

## 📥 Loading the Skills into Codex

Pick whichever path matches your Codex build:

  1. **Plugin marketplace (plugin-aware Codex).** Register this repository as a marketplace and install
     the bundled plugin:

     ```shell
     $ codex plugin marketplace add PyUtility/polyskills
     $ codex plugin add llm-essentials@polyskills
     ```

  2. **`polyskills` CLI (any Codex build).** Fetch individual skills into your Codex skills directory.
     The CLI is the project's single source of truth and supports private remotes and version pinning:

     ```shell
     $ pip install polyskills
     $ polyskills manager https://github.com/PyUtility/polyskills \
           --source ./extensions/skills \
           --name python-code-format \
           --destination ~/.codex/skills/python-code-format \
           skills
     ```

  3. **Manual copy (native discovery).** Copy any skill folder from
     [`extensions/skills/`](./extensions/skills/) into `~/.codex/skills/` (user-level) or
     `.agents/skills/` (project-level); Codex discovers `SKILL.md` files there at startup.

## 🔗 References

  * Project documentation - [`README.md`](./README.md)
  * Skills directory - [`extensions/skills/`](./extensions/skills/)
  * Codex plugin manifest - [`extensions/.codex-plugin/plugin.json`](./extensions/.codex-plugin/plugin.json)
  * Codex marketplace - [`.agents/plugins/marketplace.json`](./.agents/plugins/marketplace.json)

</div>
