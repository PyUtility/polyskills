<div align = "center">

# God Mode Playbook

</div>

<div align = "justify">

This reference backs the `god-mode` skill. It holds the technique cheat-sheet, the full scoring
rubric, and one worked validation round. Load it from Phase 4 onward, or whenever you need the exact
rubric. Everything here is subordinate to the Honesty And Safety Guardrails in `SKILL.md`: these are
tools for doing better work, never for inflating a score.

A grounding fact worth repeating. The techniques below have measurable effects in published work;
motivational framing (stakes, tips, expert role-play) does not reliably. When you want more quality,
reach for structure here, not for theatrics.

## Technique Cheat-Sheet

Pick the technique that fits the task. Most are cheap; a few cost real tokens, noted in the row.

</div>

| Technique | Use When | Cost |
| :---: | --- | :---: |
| Plan-and-solve | Multi-step tasks where missing a step is the main risk: plan the steps, then solve them | low |
| Step-back | The concrete problem is fiddly: derive the general principle first, then apply it | low |
| Least-to-most | Compositional problems: solve the smallest subproblem, feed it into the next | low |
| Self-consistency | High-stakes answers with several solution paths: sample a few, reconcile or vote | medium |
| ReAct grounding | Facts or external state matter: interleave reasoning with real tool calls and reads | medium |
| Evaluator-optimizer | Quality matters and you can score it: generate, score, revise, repeat to the cap | medium |
| Extended thinking | Genuinely hard, multi-step reasoning only. It can hurt easy tasks, so do not default to it | high |

<div align = "justify">

Use the cheapest technique that fits. Self-consistency and extended thinking earn their cost only on
hard problems where a wrong answer is expensive.

## Scoring Rubric

Score the result on five dimensions, 0 to 10 each. The bar is every dimension at 8 or higher. Score
the work against these fixed criteria; never rewrite the criteria to fit the work, and never degrade
the work to move a number.

</div>

| Dimension | Measures | Passing At 8 | Scores 0 When |
| :---: | --- | --- | --- |
| Correctness | Works and is factually right | Verified by a test or direct observation, no known defects | A claim is wrong or a test fails |
| Completeness | Stated requirements met | Every requirement and success criterion is satisfied, edge cases named | A stated requirement is missing |
| Clarity | Result and explanation are clear | A competent reader follows it without re-asking | The reader must reverse-engineer intent |
| Efficiency | Avoids needless waste | No obvious redundancy, and complexity fits the problem | The work is clearly wasteful or over-engineered |
| Edge-case coverage | Boundary and failure cases handled | Foreseeable edge cases are handled or explicitly flagged | A likely edge case silently breaks the result |

<div align = "justify">

The accuracy gate sits above the score and is a hard pass or fail. Any round that introduces a
factual error, breaks a test, regresses working behavior, alters a true claim, or reports a result
that did not happen fails outright, regardless of the five numbers. A high score never buys back a
broken fact.

Stop condition: pass when every dimension is 8 or higher and the gate passes, or when two consecutive
rounds produce stable scores. Round cap: three. After the cap, stop and hand back the best result
with the remaining gaps named. Refinement plateaus and can even degrade, and the same model scoring
its own work is a real blind spot, so more rounds are not safer.

Judge-noise caveat: a single model scoring its own output carries position, verbosity, and
self-preference bias, and scores wobble across runs. Treat single-point movements as noise, anchor on
the rubric descriptions rather than a bare number, and on high-stakes work get an independent pass
from a fresh subagent or `/code-review` rather than trusting one self-score.

## Worked Validation Round

A Standard task: add a helper that returns the median of a list of numbers, with tests.

Round 1. The draft returns the middle element by index. Self-scoring against the rubric: Clarity 9,
Efficiency 9, Completeness 7, Edge-case coverage 6 (no even-length or empty-list handling), Correctness fails. The accuracy gate catches it:
the new test for an even-length list fails, because the median of an even count is the average of the
two middle values, not a single element. Gate result is FAIL, so the round does not pass no matter
what the other numbers say. Highest-leverage fix: handle even-length input and the empty list.

Round 2. The helper sorts, averages the two central values for even counts, and raises on empty
input; tests cover odd, even, single, and empty. Re-score: Correctness 9 (tests pass), Completeness
9, Clarity 9, Efficiency 8, Edge-case coverage 9. Gate passes. Every dimension is at or above 8, so the loop
stops at round 2. The report states the scores, notes that the gate caught the even-length bug in
round 1, and flags that very large inputs were not benchmarked.

</div>
