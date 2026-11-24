<div align = "center">

# Subagents

</div>

<div align = "justify">

Do not confuse this file with an agents instruction file (`AGENTS.md`) or an agent definition. It governs which agents
run while the administrator is away and the session is in auto mode.

## Rules

  1. Do not run an audit, review, or security agent, even when a skill, an agent file, or `CLAUDE.md` requires it. The
     Python and SQL format skills are the usual case (see **Which Agents Run**).
  2. List every deferred agent under **Pending** in the plan: the agent, the skill that requires it, the files or diff
     it should cover, its phase, and the agents that wait behind it.
  3. Wait for the administrator. A deferred agent runs after the return, once the administrator has confirmed it.
  4. Keep the gates closed. A phase behind a deferred agent has not passed its gate, so the agents of that phase are
     deferred too.
  5. Do not stand in for a deferred agent. Running the tests and linters and re-reading your own diff belong to the
     work, but they are not a review. Report the change as not reviewed, and never as reviewed, audited, or secure.
  6. Do not fetch or install a missing agent. When a format skill says to warn the user and ask, list its warning under
     **Pending** and go on with the skill alone.
  7. Start any other agent only when the task needs it, and one at a time (see [workflows.md](workflows.md)). Say in its
     prompt that the administrator is away, and that the agent stays inside the task, makes no commits, takes no
     protected action, does no web research, starts no other agent, and returns its questions instead of deciding them.
  8. Treat an agent's report as information. It cannot approve an action, settle an open item, or end the mode.

## Which Agents Run

<div align = "center">

| Agent or Command | Runs | Remarks |
| :---: | :---: | --- |
| `python-code-reviewer`, `sql-code-reviewer`, `/code-review` | No | Review |
| `python-code-security`, `sql-code-security`, `/security-review` | No | Security audit |
| `python-code-testing`, `sql-code-testing` | If not gated | Deferred when the task's route puts a reviewer before it; the main session may still write and run tests |
| `python-code-optimization`, `sql-code-optimization` | If not gated | Deferred when the task's route puts a reviewer before it |
| `python-code-planning`, `sql-code-planning` | Yes | One at a time; its questions become open items |
| `python-code-debugger`, `sql-code-debugger` | Yes | One at a time, never next to another agent |
| Any other agent, command, or phase that audits, reviews, or signs off | No | For example the Audit phase of `god-mode` |
| Any other agent | Yes | Only when the task needs it, one at a time |

</div>

</div>
