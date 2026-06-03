<div align = "center">

# AI Agents Extensions

[![Python Code Planning](https://img.shields.io/badge/Python-%20Code%20Planning-003B57?style=plastic&logo=python)](python-code-planning/AGENT.md)
[![Python Code Reviewer](https://img.shields.io/badge/Python-%20Code%20Reviewer-003B57?style=plastic&logo=python)](python-code-reviewer/AGENT.md)
[![Python Code Debugger](https://img.shields.io/badge/Python-%20Code%20Debugger-003B57?style=plastic&logo=python)](python-code-debugger/AGENT.md)
[![Python Code Optimization](https://img.shields.io/badge/Python-%20Code%20Optimization-003B57?style=plastic&logo=python)](python-code-optimization/AGENT.md)

</div>

<div align = "justify">

Agents are *task-scoped specialists* that the orchestrator (Claude Code, CodeX, Cursor AI, etc.) delegates work to during a
multi-step Python change. Where a *skill* teaches the LLM **how** to format or shape code, an *agent* teaches the LLM
**when to think** and **with which discipline**. Each agent ships as a folder with an `AGENT.md` file containing YAML
frontmatter (`name`, `description`) and a markdown body of operating rules - identical in shape to the skills under
`extensions/skills/` and to the open standard at [Agent Skills](https://agentskills.io/home).

This directory ships the four-stage Python code-quality pipeline:

  * [`python-code-planning/`](python-code-planning/AGENT.md) - decomposes a request into dependency-ordered todos.
  * [`python-code-reviewer/`](python-code-reviewer/AGENT.md) - high signal-to-noise read-only diff review.
  * [`python-code-debugger/`](python-code-debugger/AGENT.md) - root-cause-first failure investigation.
  * [`python-code-optimization/`](python-code-optimization/AGENT.md) - measure-then-cut performance and DRY pass.

## 🧭 Orchestration Matrix

The four agents form a small **DAG**. Phase numbers are sticky: an agent never runs before its dependencies, and agents in
the same phase can be invoked concurrently because they are read-only and share no writes.

| Phase | Agent | Mode | Depends On | Mutates Code? |
| :---: | :---: | :---: | :---: | :---: |
| 1 | `python-code-planning` | Sequential (alone) | - | No (writes plan + todos only) |
| 2 | (Implementation by main agent) | Sequential | Phase 1 | Yes |
| 3a | `python-code-reviewer` | **Parallel with 3b** | Phase 2 | No (read-only) |
| 3b | `python-code-debugger` | **Parallel with 3a** | Phase 2 | No (read-only) |
| 4 | `python-code-optimization` | Sequential (alone) | Phases 3a + 3b green | Yes (only after correctness gate) |

### Why These Pairings

  * **Planning runs first and alone.** Every downstream agent needs the acceptance criteria, the file inventory, and the
    expected test surface that planning produces.
  * **Reviewer and debugger run in parallel.** Both are non-mutating investigators that read the same diff. There are no
    shared writes, so concurrency doubles signal per round-trip without conflict risk - exactly the pattern used in this
    repo when the unittest suite was being added.
  * **Optimization runs last and alone.** Optimising before correctness is confirmed wastes work because the reviewer's or
    debugger's findings can invalidate the optimisation target. Running it concurrently with the investigators is also
    forbidden for the same reason.

### Visual Pipeline

```text
                +----------------------+
                |    1. PLANNING       |
                | python-code-planning |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |  2. IMPLEMENTATION   |
                |    (main agent)      |
                +----------+-----------+
                           |
              +------------+-------------+
              |                          |
              v                          v
   +----------------------+   +----------------------+
   |    3a. REVIEWER      |   |    3b. DEBUGGER      |
   | python-code-reviewer |   | python-code-debugger |
   +----------+-----------+   +-----------+----------+
              |                           |
              +-------------+-------------+
                            |  (both green)
                            v
                +--------------------------+
                |     4. OPTIMIZATION      |
                | python-code-optimization |
                +--------------------------+
```

### Anti-Patterns to Avoid

  * Invoking the reviewer or debugger **before** planning - they will review against unwritten acceptance criteria.
  * Invoking the optimizer **in parallel** with the reviewer or debugger - their findings can invalidate the
    optimisation target.
  * Skipping planning for "small" changes that touch more than one file - the most expensive bugs come from changes
    that *felt* small.
  * Asking the reviewer to "also fix" findings - it is read-only by contract; route the fix back through implementation.

## 📦 Registering Agents (Claude Code)

Each agent ships an `AGENT.md` (mirroring the `SKILL.md` convention used under `extensions/skills/`). For Claude Code,
register agents in `~/.claude/settings.json` so they auto-load when the description matches the user request:

```json
{
  "agents": {
    "global": [
      {
        "name": "python-code-planning",
        "description": "...",
        "agent_path": "~/.claude/agents/python-code-planning/AGENT.md",
        "trigger_keywords": ["plan", "design", "scope", "break down", "architect"],
        "always_load": false
      }
    ]
  }
}
```

Repeat for `python-code-reviewer`, `python-code-debugger`, and `python-code-optimization`. For tools that do not support
Agent-Skills natively, the `polyskills` framework can convert these `AGENT.md` files into system prompts at install time.

## 🧪 Testing the Agent Suite

Smoke-test the suite end-to-end on a real change in this repository:

  1. Ask the orchestrator: *"Plan how to add a new ValidSources entry for GitLab."* - expect `python-code-planning` to
     produce todos and an orchestration table.
  2. Implement the change in the main conversation.
  3. Ask: *"Review and debug the diff."* - expect `python-code-reviewer` and `python-code-debugger` to run concurrently
     and return findings independently.
  4. Once both report green, ask: *"Optimize the new code path."* - expect `python-code-optimization` to refuse if no
     measurable bottleneck exists, and otherwise to attach a baseline / target measurement block.

If any of those steps deviates from the expected agent, the orchestrator's keyword-matching is mis-configured - re-check
the `description` fields and registration entries above.

</div>
