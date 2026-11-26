---
name: make-adr
description: >-
  Takes an architecture decision from an open problem to a written record. It researches the problem against the
  repository and the web, sets out the alternatives and their trade-offs, and works through them with the user, round
  by round, until the user confirms the decision. Only then does it write the architecture decision record (ADR),
  `XXXX-imperative-title.md`, in the repository's decisions directory (`docs/decisions/` unless one exists), confirmed
  with the user once and recorded in the instruction files, and indexes it in `README.md`. A decision that adds to a
  record goes into it as a dated additional change; a major change gets a new record that supersedes the old one. It
  also accepts and deprecates records. Starts only when the user asks. Trigger phrases: the /make-adr command, "create
  an ADR", "write an architecture decision record", "record this decision", "help me decide between X and Y and record
  it", "add this to ADR 0004", "supersede ADR 0004", "deprecate ADR 0004".
---

<div align = "center">

# Make ADR

</div>

<div align = "justify">

An architecture decision record (ADR) captures one important decision: the forces behind it, the options weighed, the
choice, and what follows from it. It is written for the engineer, or the coding assistant, who meets the code years
later without the conversation that produced it. This skill decides before it writes. It researches the problem, puts
the alternatives in front of the user, and keeps the conversation going until the user is satisfied with the decision.
A new topic gets a numbered record, a decision that adds to an existing record joins it as a dated change, and a major
change gets a new record that supersedes the old one. An index lets a coding assistant find every record of an area by
its tags.

## Getting Started

  1. Start only when the user asks: the `/make-adr` command, or a request for an ADR or for help with a decision that
     should end in one. You may suggest a record when a conversation settles an architecture decision, but start only
     after the user agrees.
  2. Read this file and both templates in [resources/](resources/) in full, and each reference as you reach its step:
     [research](references/research.md) and [record](references/record.md).
  3. Find the decisions directory (see **Location**). Read its `README.md` and every record that shares a tag or a
     topic with the request, in full: they show the next number, a record the decision adds to or replaces, and any
     accepted decision it would contradict. When one of them is still proposed, tell the user before the first round
     (see **Proposed Records**).
  4. Pick the task (see **Tasks**). A new decision runs the full **Decision Loop**; a status change does not. When a
     record already covers the topic, whether the decision adds to it or replaces it is settled at the **Confirm**
     step, once the outcome is final (see **Add or Supersede**).
  5. Write nothing to the decisions directory until everything is finalized: no draft, no index row, and no reserved
     number.
  6. When the user or the project has a Markdown format skill, apply it to every file this skill writes. The templates
     follow a common layout, and an installed format skill wins over them.

## Location

A repository keeps one decisions directory, relative to its root (`git rev-parse --show-toplevel`, or the working
directory outside a git repository). Take the first that applies:

  1. **Named by the user**: a directory the user asks for explicitly in this request, as in "put it in
     `architecture/adr/`".
  2. **Recorded**: the directory an earlier run recorded (see **Recording the Directory**), or a path written in an
     `.adr-dir` file at the root.
  3. **Already in the repository**: a directory that already holds decision records, in any layout. Look for one named
     `decisions`, `adr`, or `adrs`, such as `docs/decisions/`, `docs/adr/`, `doc/adr/`, or
     `docs/architecture/decisions/`, and for any directory of numbered `NNNN-<title>.md` files that each state a
     decision and its status. When more than one exists, ask the user which one to use.
  4. **The default**: `docs/decisions/`, when none applies.

  * Confirm the directory with the user before anything is written whenever nothing is recorded yet, or the user names
    a directory other than the recorded one. Say in the same question where it will be recorded.
  * Never start a second decisions directory next to an existing one, and never move, rename, renumber, or reformat an
    existing record unasked.
  * A new directory gets a `README.md` from [resources/README.md.template](resources/README.md.template), together
    with the first record. An existing directory without one gets it too, with a row for every record already there.
  * Records in another layout, such as `adr-tools` records with a `## Status` heading or date-named files, stay as
    they are. New records go into the same directory in this skill's layout and take the next number, and the index
    reads each old record's status from its text and shows `-` for its tags. Say so in the first-time confirmation.

The default layout:

```text
docs/decisions/
    README.md                       index: every record with its status and tags, and each replaced record
    0001-imperative-title.md        one record per decision, with its dated additional changes
    0002-imperative-title.md
```

### Recording the Directory

Once the user confirms the directory, record it where the next run, and every other assistant, will find it, so that
nobody has to ask again:

  * **The instruction file** of the repository: `AGENTS.md` when it exists, because every assistant reads it;
    otherwise each of `CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md` that exists. When none exists,
    ask which one to create, and recommend `AGENTS.md`.
  * **The assistant's memory** for the project, when it keeps one.

When the file already names the decisions directory, such as a routing row for why something is the way it is, that
row is the record: update it when the directory changes, and add nothing. Otherwise add one plain line to its rules,
without `@` and without HTML:

```markdown
  * Architecture decision records live in `docs/adr/`, numbered `XXXX-imperative-title.md` and indexed in
    `docs/adr/README.md`. Add or change one with the make-adr skill.
```

Later runs read the record and use the directory without asking, unless the user names another one or the directory
is gone. Then confirm and record again.

## Tasks

<div align = "center">

| Task | Asked As | Decision Loop | What Changes |
| :---: | --- | :---: | --- |
| Create | "write an ADR on how users log in" | Full | A new record and its index row |
| Add | "we also picked Clerk as the login provider" | Full | A dated additional change in the existing record, its tags and links, and its index row |
| Supersede | "we are retiring Clerk for a self-hosted auth service" | Full | A new record; the old record's status, links, and remark; the index |
| Accept | "accept ADR 0006" | No | The record's status and its index flag, and the supersede that waited for it, if any |
| Deprecate | "deprecate ADR 0006" | No | The record's status, a dated remark with the reason, and its index flag |
| Repair | "fix the ADR index" | No | The index, rebuilt from the records; no record changes |

</div>

A new decision arrives in one of two shapes. An **open problem** ("Redis or PostgreSQL for sessions?") runs every step
of the loop. A **decision already taken** ("record that we chose PostgreSQL") gets the research all the same: the
viable alternatives are found and compared before the choice is written down, and the record names them and why they
lost. Never follow the user's preference without that comparison. Report a serious risk the research finds, and leave
the choice to the user.

## Add or Supersede

When a record already covers the topic, the new decision either adds to it or replaces part of it, and that decides
where it is written. One test sorts them: **does anything the existing record decided stop being true?**

<div align = "center">

| The New Decision | Example | Where It Goes |
| --- | --- | --- |
| **Adds** to the record: settles a detail it left open, picks within a choice it made, or adds a driver, a scope area, or a check, while everything it decided stays true | The login record chose an external identity provider, and the new decision picks Clerk as that provider | Into the existing record, as a dated entry under **ADR Additional Changes** |
| **Replaces** part of the record: reverses, retires, or swaps a choice it made or added, changes the architecture, or makes one of its consequences or scope lines untrue | Clerk is retired for a self-hosted authentication service | A new record, and the old one is marked superseded |

</div>

  * A decision that needs a migration away from what the record set up is a replacement.
  * When the test does not settle it, ask the user and recommend a new record: a reversal written as an addition hides
    inside an old file.
  * Which of the two it is gets settled at the **Confirm** step and never earlier, even when the request names one:
    until the outcome is final, nobody knows whether the decision adds or replaces.
  * Only an accepted or a proposed record takes additions. A superseded or deprecated one takes none: add to the
    newest record of its chain, or start a new one.
  * When the additions outweigh the original decision, recommend a new record that brings them together and
    supersedes the old one.

[references/record.md](references/record.md) shows how an addition is written into a record.

## Proposed Records

A proposed record on the topic, or a proposed addition in one, is a decision already in progress. Tell the user before
the first round: name the record, its date, and what it proposes. Then do what the user chooses:

  * **Fix or amend it**: the decision stays in that record. Run the loop on it and edit it in place, since a proposed
    record is still open.
  * **Supersede it**: write the new record, and mark the proposed one superseded, with its remark.
  * **Leave it**: keep it as it is, and go on only when the new decision does not touch it.

The same alert comes at the **Confirm** step when a new `PROPOSED` record would supersede an accepted one, because the
old record would then send readers to a decision nobody has accepted yet. Supersede it at once only when the user says
so. Otherwise the old record stays `ACCEPTED`, and the supersede completes when the new record is accepted.

## Decision Loop

The loop runs in the chat, one round at a time. Every round ends with a question, and the loop moves on only when the
user answers. At the end of each round, show the **decision brief**: the problem, the drivers and constraints, the
options still in play and those dropped, the leading option with its reason, and the open questions.

  1. **Frame.** Restate the problem in two or three sentences, and collect the drivers and hard constraints from the
     request and the repository: the stack, the scale, the deployment, and the records already on the topic. Ask
     first only when you cannot tell what is being decided. Otherwise go on, and list what you assumed in the first
     round.
  2. **Research.** Find the alternatives and the evidence for each, tailored to this repository, as
     [references/research.md](references/research.md) describes. Include doing nothing whenever it is a real choice.
  3. **Compare and Recommend.** Present each option with its strengths and weaknesses, each tied to a driver and
     backed by a source, or marked unverified when no source could be reached. Recommend one and say why. Ask the
     user to choose, to correct a driver, to question a finding, to add an option, or to send an option for deeper
     research.
  4. **Iterate.** Each answer starts a new round: research what it raised, revise the comparison and the brief, and ask
     again. A new driver or constraint can bring back a dropped option, so check those as well.
  5. **Confirm.** When the user settles on an option, show what will be written and where: a new record, an addition
     to an existing record, or a new record that supersedes one. Show the title or the entry, the chosen option and
     its reason, the scope, the migration, the status, the tags, and the file path, and the consequences and the
     enforcement when the rounds discussed them. Ask whether to write it.
  6. **Write.** Only an explicit confirmation of the finalized decision, such as "yes, write it" or "I'm satisfied",
     ends the loop. Write the
     record or the addition and update the index (see [references/record.md](references/record.md)), then report the
     path and the index row. Until the change is committed, apply the user's corrections in place.

Rules for every round:

  * Nothing is written until everything is finalized: the chosen option, whether it adds or replaces, and every
    required section, each confirmed by the user. A request to "just write it" before then does not end the loop: name
    what is still open, settle it, and confirm. A required point that stays unknown is written as `Not assessed` only
    when the user agrees to that at the **Confirm** step.
  * Ask three or four focused questions at most, each with your recommended answer. Use the assistant's question tool
    when it has one; otherwise ask in the chat.
  * Ask only what the repository and the research cannot answer.
  * The consequences and the enforcement of a decision go into the record only when the user discussed them in the
    rounds. Do not ask about them just to fill the record.
  * Never take silence, a reply on another topic, or agreement with one finding as the final confirmation.
  * Set the status at the confirmation: `ACCEPTED` when the user calls the decision final, `PROPOSED` when it still
    needs the approval of others.
  * When the user drops the decision ("leave it", "never mind"), stop and write nothing.

## Statuses

<div align = "center">

| `ADR Status` | Index Flag | Meaning |
| :---: | :---: | --- |
| `PROPOSED` | 🚧 | Settled with the user and waiting for the approval of others; the text may still change |
| `ACCEPTED` | ✅ | In force |
| `DEPRECATED` | ❌ | No longer applies, and no record replaces it |
| `SUPERSEDED (ADR-XXXX)` | 🛠️ | Replaced by the newer record named in the brackets |

</div>

  * An accepted record keeps everything it says: nothing in it is reworded or removed, apart from a typo, a broken
    link, and a proposed addition, which stays open until it is accepted and then loses its `(Proposed)` marker. It
    grows only by dated additional changes (see **Add or Supersede**), and its status, tags, links, and remark change.
  * A proposed record may be edited until it is accepted; an additional decision still gets its dated entry. When the
    edit touches the decision itself, run the loop again. Accepting it changes the status and the index flag, and
    completes a supersede that waited for it (see **Proposed Records**).
  * A record in another layout changes its status where it states it, such as under its `## Status` heading.
  * A superseded or deprecated record carries a **remark** as the first line of its body, inside the `justify` div, so
    that a reader meets it before the decision. Ask for the reason when the user gave none:
    `**Superseded On:** YYYY-MM-DD - by [ADR-0012](0012-use-a-self-hosted-auth-service.md): <the reason>`, or
    `**Deprecated On:** YYYY-MM-DD - <the reason>`.
  * Superseded means a newer record takes its place; deprecated means it stops applying and nothing replaces it.
  * The template has no rejected status. A proposal that is turned down is deprecated the same way.

## Naming and Numbering

  * **Number**: four digits, zero-padded, one above the highest number in the directory; the first record is `0001`.
  * **No deletion**: a record is never deleted. A gap in the numbers, an index row without its file, or a deletion in
    `git log --diff-filter=D -- <directory>` means one was. Stop and ask the user what to do. The default is to
    renumber the records after the gap so that the numbers run without a hole, renaming each file with `git mv`, and to
    update every link to them: the index, the `ADR-XXXX` references and links in other records, and every other file
    in the repository that names them. Say that commits and issues outside the repository keep the old numbers.
  * **Title**: a short imperative phrase in Title Case that names the choice, not the problem: "Use PostgreSQL for
    Session Storage", not "Session Storage Discussion". The same text goes in `ADR Title` and in the `#` heading. An
    addition never changes the title or the file name.
  * **Slug**: the title in lowercase kebab-case, ASCII only, without punctuation, starting with the verb:
    `0007-use-postgresql-for-session-storage.md`. Keep it under about 50 characters by dropping filler words.
  * **Reference**: name a record as `ADR-0007` in frontmatter values, and link to its file in the body.
  * **Collision**: when two branches add the same number, the record merged second takes the next free number, and its
    links and index row move with it.

## Superseding a Record

  1. Run the full loop for the new decision. Its summary says what changed and why, and it restates every part of the
     old record and of its additional changes that still holds, so that the newest record is complete on its own. Its
     `Related Link(s)` names the old record.
  2. In the old record, set the status to `SUPERSEDED (ADR-<new number>)`, add the new record to its
     `Related Link(s)`, and add the remark (see **Statuses**). Change nothing else in it.
  3. In the index, set the old row's flag to 🛠️, add the new row, and add a row to the replacement table.

A record is superseded as a whole, even when the new decision replaces only part of it: step 1 carries the rest
forward, so that a reader never has to combine two records. When the new record is `PROPOSED`, steps 2 and 3 wait for
its acceptance, unless the user chose to supersede at once (see **Proposed Records**).

## The Index

The `README.md` of the decisions directory lists every record. Keep its text from the template and any text the user
added; change only the two tables.

  * **Records table**: one row per record, in number order: the number (`0007`), the slug linked to its file
    (`[use-postgresql-for-session-storage](0007-use-postgresql-for-session-storage.md)`), the status flag, and the
    tags exactly as in the record. An addition that brings new tags updates them in the row.
  * **Replacement table**: one row per replacement, the old file and the new one, both linked. A chain keeps every row
    (`0002` to `0005`, then `0005` to `0009`), and no row is ever removed. It stays empty until a record is replaced.
  * Every record has exactly one row, every row points to a file that exists, and every flag matches the status in
    the record. **Repair** rebuilds both tables from the records and reports each row it changed.

## Resources

<div align = "center">

| File | Use It For |
| :---: | --- |
| [`resources/XXXX-imperative-title.md.template`](resources/XXXX-imperative-title.md.template) | One decision record |
| [`resources/README.md.template`](resources/README.md.template) | The index, written once when the directory is created |
| [`references/research.md`](references/research.md) | Researching the options and presenting them in a round |
| [`references/record.md`](references/record.md) | Filling the frontmatter and each section, writing an addition, and the checks before saving |

</div>

The templates mark a value to fill as `[...]` and an instruction block as `{ ... }`, and the record template carries
guidance notes in italics. Three of its sections are optional, and the note under each says when it stays:
**ADR Additional Changes**, **Consequences & Trade-Offs**, and **Compliance, Enforcement & Validation** (see
**Sections** in [references/record.md](references/record.md)). Replace every placeholder, replace the instruction block
with the text it asks for, and delete the notes and every example.

## What Not To Do

  * Do not start the skill, or its research, on your own initiative.
  * Do not write a record, an addition, a draft, or an index row before the user confirms the decision.
  * Do not put a record anywhere but the directory **Location** gives, and do not start a second decisions directory.
  * Do not record the decisions directory in an instruction file or a memory before the user confirms it.
  * Do not follow the user's preferred option without researching and comparing the alternatives.
  * Do not present your recommendation as the decision before the user chose it.
  * Do not reword or remove what an accepted record says: add a dated change, or supersede it.
  * Do not write a reversal or a replacement as an additional change.
  * Do not delete a record, and do not renumber or rename one unless the user chose it for a missing record.
  * Do not put an internal name, code, or any other private detail into a web search or a fetched URL.
  * Do not invent a driver, a figure, an option, a source, a metric, or a check. What the loop did not establish is
    written as not assessed.
  * Do not copy text from a source into the record. Summarize it and link it.

## Quick Checklist

  - [ ] Did the user ask for the record, and did I read the index and the related records before the first round?
  - [ ] Was the research tailored to the drivers, the constraints, and the stack of this repository, with a source, or
    an unverified mark, for each claim, and did it look beyond the option the user preferred?
  - [ ] Did I tell the user about every proposed record on the topic, and act on their choice?
  - [ ] Did every round end with a question and an up-to-date decision brief?
  - [ ] When a record already covered the topic, did the user confirm whether the decision adds to it or replaces it?
  - [ ] Was everything finalized and confirmed by the user before anything was written?
  - [ ] Did every web search use generic terms only, and did I ask before starting more than two subagents?
  - [ ] When a record was missing, did I ask the user, and update every link after a renumbering?
  - [ ] Is the record in the directory the user named, else the recorded or existing one, else `docs/decisions/`, and
    was the directory confirmed with the user and recorded the first time?
  - [ ] Is a new record's number the next free one, in four digits, with a slug that starts with the verb and matches
    the title?
  - [ ] Does an addition have its dated entry, with every inserted line dated and nothing earlier reworded or removed?
  - [ ] Are the optional sections present only with content: additional changes after an addition, and consequences
    and enforcement only when the user discussed them?
  - [ ] For a supersede, does the new record carry forward what still holds, and does the old one have its status,
    remark, link, flag, and replacement row?
  - [ ] Do the checks in [references/record.md](references/record.md) pass?
  - [ ] Does the index have one row per record, in order, with each flag and its tags matching the record?

</div>
