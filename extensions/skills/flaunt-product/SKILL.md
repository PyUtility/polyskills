---
name: flaunt-product
description: >-
  Rewrites or drafts business prose so a product, project or result lands with senior executives as a
  bold, polished, high-impact story. It names deliverables like products, opens on the gap they close,
  leads with one headline number, lifts the vocabulary with current AI and industry terms, binds every
  technical and architecture detail into business language such as "end-to-end, AI-agnostic automated
  solution", and weaves in gracious credit to leadership, while every number, date, owner and
  capability stays true.
  Explicit-invoke only. Trigger phrases include the /flaunt-product command, "flaunt this", "make this
  sound impressive", "make it executive-ready", "make it boardroom-ready", "pitch this to leadership",
  "dress it up", "add buzzwords", "flatter management", "write to the MD / CEO / director", and
  "talking points for the leadership meeting". Runs alongside humanize-text, markdown-format or any
  format skill. Does a short web search for trending executive vocabulary only when the user explicitly
  asks for research. Never applies to code, commit messages, data files, or legal and safety text.
---

<div align = "center">

# Flaunt Product

</div>

<div align = "justify">

This skill turns a plain status update into a story senior leaders want to read twice. It borrows the
moves of the best internal launch emails and leadership briefs: give the work a name, open on the gap
it closes, lead with one number, and let every capability read like an outcome. The engine room stays
out of sight: leaders hear what the work achieves, in industry language, and never which language,
version or service built it. Then it thanks leadership with grace. One rule keeps it safe. Inflate the
frame, never the facts.

## Getting Started

  1. Confirm the trigger. This skill runs only when the user asks for it. It is never a silent governor.
  2. Read the **Non-Negotiables** before writing a word. They override every technique below.
  3. Pick the **mode** and the **audience tier** from the tables further down.
  4. Collect the facts first: what was built, what it does, who owns it, the numbers, the dates and
     the status. Write them down before dressing anything up.
  5. Apply the **Flaunt Playbook**, then the **Technical Translation**, then the **Vocabulary Ladder**,
     then the **Flattery Patterns**.
  6. Run the **Idempotency Test** and the **Quick Checklist** before returning the text.

## Non-Negotiables

These four rules are gates, not preferences.

  1. **Truth fence.** Never change numbers, dates, names, owners, statuses or scope. Never claim a
     technology, capability, customer or result that does not exist. Polish the framing, the verbs and
     the order, and leave the facts exactly as given. When a claim cannot be traced to the user's
     material, drop it.
  2. **Capability words are earned; vision words are free.** A capability word says what the product
     does today: AI-powered, agentic, autonomous, real-time, predictive. Use one only when it is
     literally true. A vision word speaks about direction, ambition or the industry: AI-ready, built
     for the agentic era, a step towards autonomous operations. Vision words can go wherever they read
     naturally.
  3. **No engine room.** The deliverable never names programming languages, versions, libraries,
     frameworks, APIs, backend services, databases, query languages, servers, file formats, code or
     architecture. Translate each into what it achieves with the **Technical Translation** table.
     Headline platform brands the organisation already celebrates may stay; their versions, components
     and plumbing go.
  4. **Idempotent by design.** Running this skill on its own output returns that output unchanged, or
     with trivial differences. Never stack a second elevated term on a phrase that already has one,
     never rename something already named, and never add flattery past the budget.

## Operating Modes

<div align = "center">

| Mode | Use When | Output |
| :---: | --- | --- |
| Rewrite | The user supplies text to dress up | The same content, re-framed and enriched, structure kept |
| Draft | The user gives facts and wants a new email, note or announcement | A complete piece built from the templates below |
| Talking Points | The user will present to a senior leader | Spoken lines in order, flattery lines and a "be ready" list |
| Research | The user explicitly asks to research current buzzwords | A short vetted term list, then the enriched text |

</div>

In Rewrite mode, keep the document's headings, order and mandated format unless the user asks
otherwise. The skill works inside the existing slots. It does not redesign the document.

## Audience Tiers

<div align = "center">

| Tier | Reader | Register |
| :---: | :---: | --- |
| Board / Chair | Owners, independent directors | Strategic and brief; stewardship and legacy language; one number, one ask |
| CXO / MD / ED | The top executive team | Vision-led, confident, crisp; credit leadership's direction; a clear ask |
| Function Head | VP, director, department head | Outcome-led with operational proof; name the teams involved |
| Peer | Colleagues in other functions | Collaborative; say what the work gives their team; invite review |

</div>

Address senior readers by title or name. Do not assume gender: avoid "Sir" or "Madam" unless the
user supplies the form of address.

## The Flaunt Playbook

  1. **Name it like a product.** Give an unnamed deliverable a short, memorable name and a role, such
     as `<Name>, the <domain> assistant` or `<Name> platform`. Name only what is unnamed. Never rename
     an official programme, and call something an agent only when it acts on its own.
  2. **Open on the gap, then close it.** One sentence names the pain. The next says the work closes
     it. A promise of one view of `<thing>` from `<start>` to `<finish>` is strong when it is true.
  3. **Lead with one headline number.** Delivered against committed, hours given back, value at stake
     or coverage. One number beats five.
  4. **Write capabilities as outcomes.** Open each bullet with a short verb phrase in bold, such as
     "Decide earlier", "Catch it before it costs", "Close the loop" or "See across silos", then give one
     line of concrete proof from the user's facts.
  5. **Show the cross-functional halo.** Name every function that benefits from the work or reads its
     output together. Shared ownership reads as scale.
  6. **Signal control and humility.** Add one line that shows governance, for example that every flag
     goes to its control owner for review and nothing is auto-concluded. It makes the ambition
     believable.
  7. **Close on a modest first step.** State what was run, on what scope, and who is reviewing it.
     Restraint at the end earns the confidence at the top.
  8. **Frame the ask as momentum.** "Two things would help us finish strongly" lands better than a
     list of needs. Keep it to two or three specific asks.
  9. **Credit the framework.** Tie the work to the leadership initiative, operating model or strategy
     the user's material names, and say how it shaped the result.

## Technical Translation

Executives buy outcomes, not stacks. Strip every technical term from the deliverable and bind what it
does into one industry phrase. The truth gate still applies: the phrase must hold at the level it is
stated.

<div align = "center">

| Technical Detail | Executive Phrase | Allowed When |
| :---: | :---: | --- |
| language, version, library, framework | in-house engineered, custom-built | Always |
| REST API, web or backend service, connector | seamless, plug-and-play integration | It exchanges data with other systems |
| SQL query, stored procedure, ETL job | automated data pipeline, intelligent data layer | It runs without manual steps |
| database, warehouse, data lake | enterprise data foundation, single source of truth | The data is consolidated and governed |
| script, macro, scheduled or batch job | end-to-end automation, hands-free workflow | It runs repeatably without manual steps |
| server, cloud, container, deployment | enterprise-grade, scalable platform | It is deployed for shared use |
| web app, portal, front end | digital platform, single-window experience | Always |
| login, SSO, role-based access | secure, enterprise-grade access | Access is controlled |
| Excel or CSV export, filters | self-serve insights, one-click export | Users can do it themselves |
| tests, validation scripts, UAT | rigorously validated, quality-assured | Tests or UAT took place |
| version control, code repository | audit-ready, version-controlled build | The work is under version control |
| prompts, model calls, LLM chain | GenAI-powered, AI copilot | A language model runs inside it |
| swappable model, vendor or source | AI-agnostic, vendor-agnostic, platform-agnostic | It is not locked to one provider |
| architecture diagram, tech stack | one line on what the whole solution delivers | Always (drop the diagram) |

</div>

  * Bind the parts into one phrase that covers the whole journey, for example "an end-to-end,
    AI-agnostic automated solution that takes `<input>` to `<outcome>` without manual effort". Name the
    outcome, not the components.
  * Technical metrics such as rows, queries or milliseconds stay out. Keep the business metric they
    support, such as coverage, turnaround or hours given back, when the user's material states it.
  * Name a technical item only when the user explicitly asks for it, and then only once.

## Vocabulary Ladder

Climb at most one rung per phrase. The **Allowed When** column is the truth gate.

<div align = "center">

| Plain | Elevated | Allowed When |
| :---: | :---: | --- |
| report, dashboard | decision cockpit, single view, insight layer | Always (framing) |
| rules, logic | decision engine, policy intelligence | Always (framing) |
| optimiser, solver | optimisation engine | Always |
| forecast, statistics | predictive analytics, demand sensing | A predictive model exists |
| tool with a language model | GenAI copilot, AI-powered assistant | A language model runs inside it |
| tool that acts on its own | agentic AI, autonomous agent | It takes actions without a human click |
| prototype | working proof of value | It runs on real data |
| pilot | controlled pilot, proof of value | Always |
| project | programme, transformation, initiative | Always |
| saves time | gives back `<n>` hours a month | The number is in the user's material |
| improved | step-change, structurally better | The gain is material and measured |
| plan, roadmap | journey, North Star, phased roadmap | Always (vision) |
| the future | the agentic era, AI-first, frontier AI, superintelligence | Vision sentences only |

</div>

  * Use at most two elevated terms per sentence and one per noun phrase.
  * Keep the acronyms the reader already uses, and spell out a new acronym once.
  * Prefer one strong term to three weak ones. Name the headline platform brands the organisation
    already celebrates, since familiar names carry weight with leaders, but never their versions,
    components or plumbing.

## Flattery Patterns

Specific credit lands and generic praise sounds hollow. Credit the direction, the framework or the
standard a leader set, never personal traits.

<div align = "center">

| Pattern | Example Line |
| :---: | --- |
| Credit the vision | "What you are seeing is the vision of an insight-led `<function>` taking shape." |
| Credit the standard | "Your emphasis on measurable outcomes shaped every milestone in this note." |
| Credit the framework | "The new `<framework>` sharpened how we work, from activity to outcomes." |
| Credit the direction | "The clarity of direction from leadership made it far easier to align `<team>` and `<team>`." |
| Credit the user lens | "We built it the way you would want it used: simply, every day, by every `<user>`." |
| Forward credit | "With your continued guidance, we are confident this becomes the benchmark for `<domain>`." |

</div>

  * Budget: one flattery line per section, or one per 150 words, whichever allows fewer. Opening and
    closing lines count.
  * Never invent a leader's action, decision, quote or approval. Credit only what the user's material
    supports, or keep the credit general, such as "leadership's direction".
  * Thank once, early. Repeated gratitude reads as nerves.

## Templates

### Executive Email

```text
Subject: <Name>, the <role>: <one-line promise>

<Title or name>,

<One sentence on the gap.> <Name> closes it by <the promise>.

What it does
  * <Verb-phrase lead-in>: <concrete proof>.
  * <Verb-phrase lead-in>: <concrete proof>.
  * <Verb-phrase lead-in>: <concrete proof>.

As a first step, <what was run, on what scope>, shared with <reviewer> for review.

<Sign-off>
```

### Talking Points

```text
Opening    Thank once; credit the framework or the direction.
Headline   One number: delivered against committed, and the target date.
Delivered  Three to five wins, each written as an outcome.
Next       What lands next, grouped by date.
Insight    One sharp lesson that shows judgement.
Ask        Two or three specific requests, framed as momentum.
Close      Forward credit and confidence.
Flattery   Three or four lines to weave in, within budget.
Be Ready   Likely questions (lapsed dates, cost, risk), each with a safe, true answer.
```

### Document Enrichment

  * Add an Executive Summary at the top if none exists: what the work is, the headline number, what
    lands next and the ask.
  * Upgrade verbs and nouns along the ladder inside existing sentences, keeping headings and structure.
  * Collapse each technical paragraph into one executive line. If the format mandates a technical
    section, keep its heading and write the content at outcome level.
  * Place one flattery line in the summary and one in the close, within budget.

## Research Mode

Run this only when the user explicitly asks to research trending terms, for example "research the
buzzwords", "find the latest industry terms" or "what are leaders saying this year".

  1. Run two or three web searches for current executive vocabulary in the user's domain and year, such
     as `<domain> AI buzzwords <year>` or `<industry> leadership keynote themes <year>`.
  2. Keep five to ten terms that recur across sources, with a one-line meaning for each.
  3. Pass every term through the truth gate. Capability terms go only where they are true. The rest go
     into vision sentences, where a fresher umbrella term may replace a stale one.
  4. Show the user the vetted list (term, meaning, where it will be used) with the enriched text.
  5. Do not quote, name or attribute public figures or sources inside the deliverable.

## Idempotency Test

Before returning, re-read the output as if it were fresh input.

  * Would the ladder still add something? If a phrase already sits on an elevated rung, leave it.
  * Is any technical term left? Translate it. Never re-translate a phrase already in executive language.
  * Was anything named twice, or renamed when it already had a name? Revert it.
  * Is the flattery budget exceeded? Remove the weakest line.
  * Did any number, date, owner or status drift from the source? Restore it.

If the input already passes these checks and the Quick Checklist, return it unchanged and say so in
one line.

## Composition With Other Skills

This skill stands alone and needs no other skill. When the user runs it alongside another, split the
work this way.

<div align = "center">

| Skill | It Governs | This Skill Governs |
| :---: | --- | --- |
| humanize-text | Rhythm, punctuation, tics, sentence variety | Vocabulary, framing and flattery (its hype rule yields here) |
| markdown-format | File structure, headings, lists, tables, wrapping | The wording inside the slots it leaves open |
| Document skills | Layout, styles and file mechanics | The words in each text frame |
| Code and commit skills | Everything | Nothing; never apply this skill to code, commits or data |

</div>

When two skills disagree about a sentence, the truth fence wins first, the format skill second, and
this skill decides the wording.

## What Not To Do

  * Do not fabricate metrics, customers, awards, approvals or quotes.
  * Do not call a report "AI", a script "an agent", or a batch job "real-time".
  * Do not name programming languages, versions, APIs, databases, servers, file formats or architecture
    in the deliverable. Say what they achieve instead.
  * Do not bury the ask, and do not ask for more than three things.
  * Do not stack buzzwords. A "next-gen AI-powered agentic hyper-automation platform" impresses no one.
  * Do not flatter personal traits, repeat thanks or overrun the flattery budget.
  * Do not rename official programmes, change headings the user asked to keep, or reorder a mandated
    format.
  * Do not use em dashes. Use a comma, a colon, parentheses or a full stop.

## Quick Checklist

  - [ ] Did the user explicitly ask for this skill?
  - [ ] Are all numbers, dates, names, owners and statuses identical to the source?
  - [ ] Is every capability word (AI-powered, agentic, real-time, predictive) literally true?
  - [ ] Is the deliverable free of technical wording, versions and architecture detail?
  - [ ] Does the piece open on the gap and lead with one headline number?
  - [ ] Does each capability bullet read as an outcome, with concrete proof?
  - [ ] Is the flattery specific, within budget and free of invented actions?
  - [ ] Is the ask specific, framed as momentum and limited to three items?
  - [ ] Is the form of address gender-neutral unless the user supplied one?
  - [ ] Would a second run of this skill change nothing?
  - [ ] If Research mode ran, did the user see the vetted term list?

</div>
