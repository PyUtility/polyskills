<div align = "center">

# Agent Suites

</div>

<div align = "justify">

`extensions/agents/` holds two suites of seven Claude Code subagents, one for Python (`python/`) and one for SQL
(`sql/`). Read this before changing an agent or adding a suite. The guide for users is `extensions/agents/README.md`.

## How The Suites Work

  * Each suite has an orchestrator and six specialists for planning, review, debugging, testing, optimization, and
    security. The orchestrator routes a task to only the agents it needs.
  * The phases run in a fixed order: planning first, the reviewer and the debugger in parallel, then testing,
    optimization, and the security audit last. Each phase gates the next.
  * The frontmatter sets `name`, a `description` with trigger phrases, `tools`, `model`, and `color`. The planning,
    reviewer, and debugger agents carry no `Write` or `Edit` grant, so they can read but never change the tree.
  * The SQL suite detects the database flavor (PostgreSQL, MS-SQL, or MySQL) and its version before anything else.

## Pitfalls And Limits

  * A file name is not the agent's name. `python-coding.md` registers as `python`, `sql-coding.md` as `sql`, and
    `python-planning.md` as `python-code-planning`.
  * Codex has no subagent model, so `AGENTS.md` points Codex users at the skills instead.
  * A change to how an agent is routed usually touches the matching format skill too, because that skill tells the
    model when to call the suite.
  * The `AGENTS` badge of the root `README.md` counts the agents, 14 on 2026-11-26.

</div>
