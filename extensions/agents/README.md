<div align = "center">

# AI Agents Extensions

[![Python Coding Agents](https://img.shields.io/badge/Python-%20Coding%20Agents-003B57?style=plastic&logo=python)](python/python-coding.md)

</div>

<div align = "justify">

Agents are *task-scoped specialists* that an orchestrator (Claude Code, Codex, Cursor, and the like) delegates work to
during a multi-step code change. Where a *skill* teaches the model **how** to shape code, an *agent* teaches it **when to
think**, **how to think**, and **with which discipline**. The agents here are grouped by programming language into a
directory such as [python/](python/), and each agent ships as a `<language>-<usage>.md` file with YAML frontmatter that
sets its default model, color, and tool grants, followed by the orchestration it must follow.

## 🧠 What Is an Agent

A skill is loaded on demand and answers a formatting or shaping question. An agent is a role with a mandate: it decides
when to act, what evidence it needs, and what it refuses to do. Each agent file opens with frontmatter that Claude Code
reads to register and route it.

| Frontmatter Key | Purpose | Example |
| :---: | --- | :---: |
| `name` | The identifier you invoke or delegate to | `python-code-planning` |
| `description` | When to invoke, including trigger phrases | *"plan", "design", "scope out"* |
| `tools` | Comma-separated tool grants; omit to inherit all | `Read, Grep, Glob, Bash` |
| `model` | `opus`, `sonnet`, `haiku`, or `inherit` | `opus` |
| `color` | Label color in the agent picker | `blue` |

The body after the frontmatter is the agent's operating manual: when to run, its mission, the format its findings take,
and the confidence bar it holds itself to. Read-only agents (planning, reviewer, debugger) carry no `Write` or `Edit`
grant, so they can investigate but never mutate the tree.

## 🚀 Getting Started

  1. Open the language folder for your work, for example [python/](python/), and read
     [python-coding.md](python/python-coding.md) first. It is the entry point and defines the full pipeline.
  2. Install the agents where your tool can find them (see *Registering Agents* below).
  3. Delegate work either by naming an agent directly or by describing a task that matches its `description` and letting
     the orchestrator route it. A planning request lands on `python-code-planning`; a stack trace lands on
     `python-code-debugger`.
  4. Let each phase gate the next. Nothing gets optimized or hardened until the correctness phases are green.

### The Python Agent Suite

Seven agents cover a Python change end to end. Phases `3A` and `3B` run at the same time; every other phase is sequential.

| Agent | Role | Phase | Writes Code |
| :---: | --- | :---: | :---: |
| `python-code-planning` | Decomposes the ask into a dependency-ordered plan and todos | 1 | No |
| (main session) | Implements the plan | 2 | Yes |
| `python-code-reviewer` | Flags real bugs, broken contracts, and security issues | 3A | No |
| `python-code-debugger` | Reproduces failures and pins the root cause | 3B | No |
| `python-code-testing` | Locks correctness in with deterministic tests | 4 | Yes |
| `python-code-optimization` | Improves speed, memory, or I/O behind the correctness gate | 5 | Yes |
| `python-code-security` | Runs the defensive security audit, the terminal gate | 6 | Yes |

### Orchestration Pipeline

Your main session is the orchestrator. It invokes each agent in phase order, running the reviewer and debugger together
because both are read-only and share no writes.

```text
1  python-code-planning        plan + todos, read-only
2  main session implements     writes code
3  python-code-reviewer   ||   python-code-debugger   (parallel, read-only)
4  python-code-testing         locks in correctness
5  python-code-optimization    measured speedups only
6  python-code-security        defensive audit, terminal gate
```

A subagent cannot spawn other subagents, so the DAG in [python-coding.md](python/python-coding.md) is a specification the
main session follows, not something one agent runs on its own. The gate between phases is the point: the optimizer refuses
to touch code the reviewer and debugger have not cleared, and the security audit runs last, on code that is already
correct and already fast.

## 📦 Registering Agents

Unlike skills, agents need no entry in `settings.json`. Claude Code discovers them from two directories and registers each
by its frontmatter `name`:

  * `~/.claude/agents/` - personal agents, available in every project.
  * `<project>/.claude/agents/` - project agents, checked in alongside the code they serve.

Copy the agent files into one of those directories, or run `/agents` to add and edit them interactively:

```shell
$ cp extensions/agents/python/*.md ~/.claude/agents/
```

This repository keeps the files grouped under `python/` for readability. If your Claude Code version does not discover
nested folders, flatten the `*.md` files into the `agents/` root. Once registered, confirm the suite is visible with the
`/agents` command before you delegate.

</div>
