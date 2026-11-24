---
name: noadmin-auto-mode
description: >-
  Governs unattended work: the administrator is away and the session carries on in auto mode. It keeps a plan file with
  every decision, its reason, and the rejected alternatives, leaves unclear or critical decisions open, holds back
  commits, review and security agents, and irreversible or outward-facing actions, runs workflows one at a time, and
  researches the web only on request. Explicit-invoke only: start it when the user types /noadmin-auto-mode or says that
  they are leaving and the work should go on without them. Auto mode alone, silence, or a long task is not a trigger. It
  ends only when the user writes "I'm back" or "I am back". Trigger phrases: the /noadmin-auto-mode command, "no admin
  mode", "unattended mode", "I'm stepping away, carry on", "keep working while I'm away".
---

<div align = "center">

# Noadmin Auto Mode

</div>

<div align = "justify">

This skill governs a session that keeps working in auto mode, or in any mode that acts without asking first, while
nobody watches it. The **administrator** is the user who owns the session, and they are away. Routine work goes on.
Every step and decision is written to a plan file, and whatever needs a person's judgment stays open until the
administrator is back.

## Getting Started

  1. Start this mode only on an explicit request (see **Starting the Mode**), and read this file and every file in
     [rules/](rules/) in full before the first change.
  2. Create the plan file from [resources/plan.md.template](resources/plan.md.template) before the first change (see
     **The Plan File**).
  3. Work through the assigned tasks. Take only the decisions that are yours to take, and log each one (see
     **Decisions**).
  4. Leave everything else open or pending, and go on with the work that does not depend on it (see **Open Items**).
  5. When nothing independent is left, complete the checklist, post the handover, and stop.
  6. Stay in this mode until the administrator writes that they are back (see **Messages and the Return**).

## Rules

Every file is binding, and the checklist at the end of the plan answers for each of them. After a context compaction or
a resume, read this file, every rule file, and the plan again before going on.

<div align = "center">

| Rule File | In Short |
| :---: | --- |
| [git.md](rules/git.md) | No commits; the commit message goes in the chat, and the administrator creates the commit |
| [integrity.md](rules/integrity.md) | Nothing but the administrator's own message ends the mode; limits for long runs |
| [protected-actions.md](rules/protected-actions.md) | Irreversible and outward-facing actions are prepared, never taken |
| [research.md](rules/research.md) | Web research only where the administrator asked for it |
| [subagents.md](rules/subagents.md) | Review, audit, and security agents wait for the administrator; other agents run one at a time |
| [workflows.md](rules/workflows.md) | One workflow at a time, with its findings in the plan before the next one starts |

</div>

## Starting the Mode

The administrator starts it with the `/noadmin-auto-mode` command, or by saying that they are leaving and the work
should go on without them. Auto mode alone, silence, and a long-running task start nothing. Before any change:

  1. Record the baseline in the plan: the date and time from the system clock, the tasks in the administrator's own
     words, the branch and commit, and the output of `git status --short`. The files it lists hold the administrator's
     uncommitted work. With no task in the command, the tasks are those under way in the conversation.
  2. Copy every authorization in the tasks, word for word (see **Precedence**).
  3. Write the questions you would have asked as open items. Do not wait for answers, because the administrator may
     already be gone.
  4. Confirm in one short message that the mode is on, where the plan file is, and that `I'm back` ends it. Name any
     earlier plan that still has the status `UNATTENDED`. When the session is not in auto mode, add that a permission
     prompt will stop the work until they return. Never change the permission mode yourself.

## The Plan File

Each session keeps one plan file, at `plans/noadmin-<YYYY-MM-DD>-<task>.md` from the repository root unless the
administrator or the project names another place. Keep it out of `.claude/`, `.git/`, and other protected directories,
where auto mode checks every write and may block it. Never overwrite the plan of an earlier session: add `-2` to the
name.

  * Update it at once after each step, decision, message, and workflow run, never from memory at the end.
  * Keep every section of the template, and write `None` in an empty one.
  * Give each entry an ID and refer to it by that ID: `T-1` for a task, `D-1` for a decision, `O-1` for an open item,
    `P-1` for a pending item, `W-1` for a workflow, `M-1` for a message, and `N-1` for a note.
  * Give each task a status: `not started`, `in progress`, `done`, `open` (waits for a decision), `pending` (waits for
    an agent or an action), or `blocked` (a step failed 3 times).
  * Never delete or rewrite an earlier entry. Add the correction below it.
  * End it with the checklist: what was done for each task, and whether each file in `rules/` was followed. Leave a
    broken rule unticked and say what happened. A false tick is worse than an empty box.

## Decisions

One test sorts them: would you have asked the administrator if they were here? If so, the decision is not yours.

<div align = "center">

| Class | Cues | What to Do |
| :---: | --- | --- |
| Settled | The task, the existing code, or a format skill already gives the answer | Follow it; no entry is needed |
| Yours | Several sound options, confined to the files of the task, and easy to undo | Decide, then log it |
| Critical | You are not sure, it is hard to undo, or it largely affects the architecture, the code base, existing logic, or an earlier decision | Leave it open |

</div>

A new dependency, a changed public interface, a changed data model, and a changed security behavior are always critical.
When the class itself is in doubt, take the stricter one.

For each decision of yours, log what you decided and why, every alternative you rejected and why, the files it touches,
and how to undo it.

## Open Items

An open item states the question, the options with their effects, your recommendation, and the tasks that wait for it.

  * Do not implement the recommendation, not even temporarily or behind a flag.
  * Leave a task that depends on an open item open as well. Never build on an undecided point.
  * Write the question in the plan. A question dialog would freeze a session that has nobody to answer it.
  * When only open, pending, or blocked work is left, post the handover, end the turn, and wait. Do not poll, schedule a
    wake-up, or look for new work.

## Messages and the Return

The mode ends on one event: the administrator writes in the chat that they are back, with a message like `I'm back...`
or `I am back...`. Letter case and the kind of apostrophe do not matter.

<div align = "center">

| Message | What It Does |
| --- | --- |
| `I'm back` or `I am back`, meant as of now, alone or with more text | Ends the mode (see **Returning to Normal Mode**) |
| A stop, a pause, or a tighter limit | Obeyed at once; the mode stays on |
| A new task or a correction | Logged and followed under the rules of this mode |
| An answer to an open item, or an approval of a pending one | Logged; the item waits for the return |
| `I'll be back`, `I'm back on Monday`, `when I'm back`, or a quoted `I'm back` | Not a return; logged |
| Anything else, such as a greeting, `continue`, or `looks good` | Not a return; logged |

</div>

An update from the administrator does not mean that they are back. Assume nothing: when a message might be a return, or
tries to settle an open or a pending item, answer in one line that `I'm back` ends the mode, and go on as before.

## Returning to Normal Mode

  1. Bring the step in progress to a safe point. Start nothing new.
  2. Set the status of the plan to `RETURNED` with the time, and complete the checklist.
  3. Post the handover in the chat, or what changed since when it is already the last message. It opens with what needs
     the administrator: open items with your recommendation, then pending agents, actions, and research. What was done
     for each task, the decisions you took, blocked steps with what you tried, every broken rule, and the commit
     messages follow.
  4. Ask the administrator to settle the open items first, and then which pending items to run. None of them starts
     unless the administrator names it.
  5. The session is now in normal mode. Other skills apply in full again, with their agents and parallel runs.

When the return message arrives in a new session, find the plan with the status `UNATTENDED` and hand over from it.

## Precedence

Restrictions add up. When this skill and another instruction disagree (another skill, an agent file, `CLAUDE.md`, a
project document), the one that holds back more wins. Do the rest of what the other one asks, and list the part you held
back as pending. When another skill says to ask the user, the question becomes an open item. Format skills still govern
everything you write.

Only an **authorization** lifts a rule: the administrator's own words, in the tasks assigned when the mode started, that
name the exact action and its target. It covers that action and nothing next to it. A skill that requires the action, a
phrase like "do whatever it takes", and a message sent later are not authorizations. Nothing here widens what the
permission mode, a permission rule, or a hook allows.

## Enforced Limits

Everything above is instruction, and an instruction can be missed. Claude Code enforces permission deny rules in every
mode. Before leaving, the administrator can merge [resources/settings.json.template](resources/settings.json.template)
into `.claude/settings.local.json`, without the lines that would block a task (an allow rule cannot override a deny
rule), and remove them again on return. The session never writes that file.

The template is blunter than the rules: it denies every `rm` and `Remove-Item`, for example. It is not watertight
either. A deny rule stops the usual form of a command and not every spelling of it (`git -C . push` gets through), so
the rules of this skill apply with or without it.

## Quick Checklist

  - [ ] Was the mode started on an explicit request, with every file in `rules/` read first?
  - [ ] Did the plan file exist before the first change, and did I update it as I went?
  - [ ] Is every decision of mine logged with its reason and its rejected alternatives?
  - [ ] Did every unclear or critical decision stay open, with nothing built on it?
  - [ ] Did review, audit, and security agents wait, each listed as pending?
  - [ ] Did workflows run one at a time, each with its findings logged before the next one started?
  - [ ] Was web research limited to what the administrator asked for?
  - [ ] Is the work uncommitted, with a commit message in the chat for each finished task?
  - [ ] Did every protected action stay prepared and pending?
  - [ ] Did only `I'm back` or `I am back`, typed by the administrator, end the mode?
  - [ ] Is the checklist at the end of the plan true, broken rules included?
  - [ ] Did nothing pending start before the administrator named it?

</div>
