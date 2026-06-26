---
name: god-mode
description:
  Explicitly-invoked maximum-rigor protocol for high-stakes, genuinely hard tasks. Runs a structured
  clarify-research-plan-build-validate-audit loop with scaled subagent fan-out and an accuracy-gated
  iterate-until-good quality bar. Invoke ONLY on explicit request, never on routine work. Trigger
  phrases include the /god-mode command, "god mode", "go all out", "maximum effort", "give it all",
  "do your absolute best", "pull out all the stops", "no shortcuts on this one". Emphasis alone is not
  the trigger; an explicit request for the protocol is. Do not auto-invoke for trivial edits, quick
  questions, or one-line changes.
---

<div align = "center">

# God Mode

</div>

<div align = "justify">

The stakes are real and the bar is the best work you are capable of. Treat this task as the one that
matters, hold nothing back, and refuse to ship anything you would be embarrassed to defend. That is
the hook, and here is the honest part: that energy is decorative. High-stakes and role-play framing
shows no reliable quality gain on modern models and has failed independent replication. Every real
improvement below comes from structure, not drama. So feel the stakes if it helps, then ignore them
and run the protocol.

## When To Use This And When Not To

This skill is explicit-invoke only. It is not a governor and it is not always on. Run it when the
user asks for it by command or phrase and the task genuinely warrants depth.

Do not run the full protocol for trivial work: one-line edits, quick factual questions, formatting
fixes, or anything a single focused pass settles. If god-mode is invoked on something trivial, do the
task well at normal effort and say plainly that god-mode added no value here. Manufacturing ceremony
for a small task is a failure, not a flex.

## The Protocol

Run these phases in order. Phases 2 through 8 are gated by the complexity you read in Phase 1, so a
simple task collapses most of the machinery and a hard task earns all of it.

  1. **Frame And Scope.** Restate the task in one or two sentences. Classify it as Light, Standard, or
    Deep from concrete cues, not from how the request was phrased. Light is a single file, well
    specified, reversible, no research. Standard touches several files or carries some unknowns. Deep
    is ambiguous, multi-step, cross-cutting, or research-heavy. State the level in one line. This
    classification is the master cost governor for everything that follows.
  2. **Clarify.** List the unknowns and the assumptions they force. Ask the 2 to 4 highest-leverage
    questions only when an answer would change the approach or the cost. If nothing is genuinely
    ambiguous, state your assumptions and proceed. Never spend a research or fan-out round on
    something one user question would settle.
  3. **Research.** Ground in reality before you design. Scale it: Light reads the directly relevant
    files; Standard reads code plus targeted searches; Deep composes `/deep-research`. Prefer reading
    and tool use over memory, and cite what you actually checked. Fan out only for genuinely
    independent strands.
  4. **Plan.** Decompose explicitly: the smallest correct sequence of steps. Before building, write
    the success criteria and one concrete example of a passing result, and state how you will
    validate. For Deep work, write the plan as a checklist the later phases tick off.
  5. **Build.** Execute the plan in scoped steps. If reality diverges from the plan, update the plan
    vis rather than silently widening scope. Defer to the format and code skills as you build.
  6. **Validate And Iterate.** This is the core loop. Run real checks: tests, the build, `/verify` for
    behavior, and a re-read against the success criteria. Score the result against these dimensions:
    correctness, completeness, clarity, efficiency, and edge-case coverage, each rated 1 to 10. The bar
    is every dimension at 8 of 10 or higher with the accuracy gate passing. Stop when the bar is met,
    or stop after 3 rounds if it is not. A round counts as "stable" if no new weaknesses are
    identified and scores do not improve by more than 0.5 points; two consecutive stable rounds
    signal diminishing returns, but do not override the 3-round cap. Fix the lowest real weakness
    first in each iteration.
  7. **Audit.** Review adversarially, separate from validation. Try to break the result and surface
    assumptions you never checked. Compose `/code-review`, `/security-review` when a security surface
    is touched, and `/simplify` once correctness is settled. For Light work this is a quick pass, not
    a fan-out.
  8. **Report.** State honestly what you did, the final scores, what the accuracy gate caught and how
    you fixed it, the residual risks and unverified assumptions, and the real cost relative to the
    task. If the bar was not met within the round cap, say so and hand back the best result with the
    gaps named. Never report a score the work did not earn.

The technique cheat-sheet, the rubric anchors, and a worked validation round live in
[references/playbook.md](references/playbook.md).

## Scale Rigor To The Task

Scale rigor to the task. Do not fan out on trivial work. Rigor is a dial, not a switch, and spending
is real: agents use roughly 4 times the tokens of plain chat and multi-agent fan-out roughly 15
times. Models tend to over-delegate, so fan-out is a deliberate choice you justify, never a default.

  * Light: one agent, a few tool calls, no subagents, no formal scoring. One rubric read is enough.
  * Standard: a single agent with an optional second validation loop.
  * Deep: fan-out and the full loop are justified by genuine breadth or hard reasoning.

## Complexity Classification And Scope Mapping

The classification made in Phase 1 governs the entire protocol. Use this table as your single authoritative reference for what applies at each level:

<div align = "center">

| Dimension | Light | Standard | Deep |
| :---: | --- | --- | --- |
| **Research** | Read directly relevant files only; cite all sources | Read files plus targeted searches; cite all sources | Compose `/deep-research`; multi-source verified research |
| **Planning** | Outline the steps; success criteria optional for simple tasks | Write success criteria and one concrete passing example | Write plan as checklist; success criteria with examples |
| **Building** | Single scoped step; no replanning needed | Scoped steps with visible replanning if reality diverges | Multiple steps with iterative replanning; defer to format skills |
| **Validation loops** | One pass: tests, build, re-read | One pass plus optional second loop | Full three-round iterate-and-score loop with accuracy gate |
| **Audit depth** | Quick adversarial pass only | Targeted audit of high-risk areas | Full audit; compose `/code-review`, `/security-review`, `/simplify` |
| **Subagent fan-out** | None | None; optional single validation agent | Fan-out for independent research strands or candidate solutions |
| **Score-and-iterate** | No formal scoring required | Optional scoring if helpful | Full scoring loop; bar is 8/10+ on all dimensions or stop at 3 rounds |
| **Report expectations** | Brief summary of what was done | Statement of what was done, scores if generated, residual risks | Honest final scores, accuracy gate status, residual risks, real cost breakdown |

</div>

## Subagent And Fan-Out Guidance

Fan out only for work that is genuinely independent: separate research strands, distinct candidate
solutions worth comparing, or a large surface that parallelizes cleanly. Do not fan out for
sequential or dependent steps, and do not fan out on trivial tasks.

  * Give each subagent a single clear objective and a defined return contract.
  * Reconcile divergent outputs in the main thread; never just concatenate them.
  * When several candidates are cheap, sample a few and reconcile or vote rather than trusting one.
  * Turn up extended thinking only for genuinely hard, multi-step reasoning. It can hurt easy tasks,
    so do not reach for it by reflex.

## Composition With Existing Skills

Reuse the specialists. Do not reimplement what a skill already does.

<div align = "center">

| Phase | Compose With | Why |
| :---: | --- | --- |
| Research | `/deep-research` | Multi-source, fact-checked, cited research with built-in verification |
| Validate | `/verify` | Run the app and observe real behavior instead of claiming it works |
| Audit | `/code-review` | Correctness bugs and reuse or efficiency findings on the diff |
| Audit | `/security-review` | Security review when the change touches a security surface |
| Audit | `/simplify` | Quality-only cleanup once correctness is settled |
| Build | format and code skills | `markdown-format`, `python-code-format`, `sql-code-format`, `git-commiter`, `humanize` |

</div>

### Handling Unavailable Or Failed Composed Skills

If a composed skill is unavailable, returns an error, or produces no output:

  1. **Note the gap clearly** in the Report phase, naming the missing skill and what it would have checked.
  2. **Describe the manual substitute** you performed instead: what you looked for and what you checked.
  3. **Mark the work as unverified** on that dimension. Do not claim the score if the specialist skill was supposed to run.
  4. **For Light tasks**, skip the specialist audit; the gap is acceptable for the classification.
  5. **For Standard or Deep tasks**, the gap is a residual risk; state it plainly.

Precedence: when a governor skill owns the artifact, it is authoritative on structure, required
tokens, and formatting. God-mode orchestrates sequencing and rigor only; it never overrides a
governor or strips a token one requires.

## Honesty And Safety Guardrails

These are gates, not preferences. The high-stakes framing never licenses crossing them.

  * Report real results only. Never fabricate a score, a passing test, a citation, or a result to
    clear the bar. A fabricated pass is an automatic accuracy-gate failure.
  * Winning never overrides honesty, safety, or user control. Maximum effort is not permission to cut
    corners, skip verification, or hide uncertainty.
  * Irreversible or destructive actions, such as deleting data, force-pushing, schema changes, or
    anything affecting production, always require explicit user confirmation. God-mode raises the
    confirmation bar, it never lowers it.
  * If clearing the bar would require an unsafe or dishonest step, stop and report the conflict
    instead of proceeding. Surface uncertainty rather than paper over it.

## Quick Checklist

  - [ ] Was god-mode explicitly invoked, and is the task non-trivial enough to deserve it?
  - [ ] Did I classify Light, Standard, or Deep and scale effort to it instead of fanning out by default?
  - [ ] Did I ground in real reading or research before planning, and cite what I checked?
  - [ ] Did I write success criteria and one concrete passing example before building?
  - [ ] Did the accuracy gate pass, with no broken test and no altered fact, independent of the score?
  - [ ] Did I score against the rubric, fix the lowest real weakness first, and respect the 3-round cap?
  - [ ] Did I avoid gaming the judge, keeping scores honest and never degrading work to raise a number?
  - [ ] Did I defer to the format and code governor skills on their artifacts?
  - [ ] Did I confirm any irreversible action and never fabricate to hit the bar?
  - [ ] Did the final report state real scores, residual risks, and real cost?

</div>
