<div align = "center">

# Workflows

</div>

<div align = "justify">

A workflow is a run with steps of its own that the session starts and waits for: a subagent, a phase of an agent suite,
the Workflow tool, the multi-phase protocol of a skill, or a background job.

## Rules

  1. Run workflows one after another, never in parallel. This overrides a parallel step of another skill, such as a
     fan-out in `god-mode` or the reviewer and debugger pair of the agent suites. Run its parts in the order they are
     listed.
  2. After each workflow, update the plan at once with the detailed findings (see **Log Entry**). Only then start the
     next one.
  3. When a tool runs its work in the background, wait for the result and start nothing else in the meantime.
  4. When the findings change what should follow, update the plan first, and log the decision or the open item they led
     to.
  5. When a workflow fails, log the error. A workflow that depends on it is blocked, and an independent one may run
     next. A retry counts as an attempt (see [integrity.md](integrity.md)).
  6. Read-only calls in the main session, such as reading several files at once, are not workflows and may be batched.

## Log Entry

<div align = "center">

| Field | Holds |
| :---: | --- |
| ID and name | `W-1` and the name of the workflow |
| Purpose | The task it serves and the question it answers |
| Input | The files, the diff, or the prompt it received |
| Time | Start and end, from the system clock |
| Outcome | `done`, `partial`, `failed`, or `blocked` |
| Findings | Each finding with its evidence: file and line, command output, or link |
| Plan changes | The `D`, `O`, and `P` entries it led to, and the workflow that runs next |

</div>

</div>
