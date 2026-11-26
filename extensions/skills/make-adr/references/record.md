<div align = "center">

# Writing the Record

</div>

<div align = "justify">

Write the record only when everything is finalized (see **Decision Loop** in [SKILL.md](../SKILL.md)). Every fact in
it comes from the decision loop: the repository, the research and its sources, or the user. Copy
[resources/XXXX-imperative-title.md.template](../resources/XXXX-imperative-title.md.template) to
`<directory>/<number>-<slug>.md`, fill it as described below, and update the index (see **The Index** in
[SKILL.md](../SKILL.md)). A decision that adds to an existing record goes into that record instead (see **Writing an
Additional Change**).

## Frontmatter

<div align = "center">

| Field | Value |
| :---: | --- |
| `ADR Title` | The imperative title, the same text as the `#` heading |
| `ADR Status` | `PROPOSED` or `ACCEPTED`, as set at the confirmation |
| `Created On` | `YYYY-MM-DD (Author Name)`: the date the record was first created, from the system clock, and the name from `git config user.name`. Ask for the name when git has none, and never write an email address. It never changes, because every addition carries its own date |
| `Document Tag(s)` | Two to five lowercase kebab-case tags, comma-separated, for the areas, technologies, and qualities the decision touches. Reuse the tags in the index before adding a new one: a coding assistant finds records by them |
| `Related Link(s)` | Related records as `ADR-0004`, issue and pull request URLs, and the main sources of the research. One value stays on the line; several go in a YAML list, one per line. `None` when there are none |

</div>

The frontmatter is YAML, so keep every value plain text, on its line or in a YAML list. Double-quote the whole value,
never one item of a comma-separated list, when it does not start with a letter (`Created On` excepted) or when it is
only `yes`, `no`, `on`, `off`, `true`, `false`, or `null`. Unquoted, YAML reads such a value as a list, a map, an
alias, a tag, a boolean, or nothing. A value that contains ` #` is cut at the `#`, and one that contains `: ` breaks
the parse, so write no Markdown links there, and give an issue as its full URL rather than as `#12`.

```yaml
Document Tag(s): "*nix, auth, login"
Related Link(s):
  - ADR-0004
  - "@scope/package"
  - https://www.postgresql.org/docs/16/
```

## Sections

<div align = "center">

| Section | What to Write |
| :---: | --- |
| Summary (replaces the `{ ... }` block, no heading) | Two or three paragraphs on the technical and business forces behind the decision, for an engineer who joins in two years and knows nothing of today's discussion. Then a list: the current bottleneck, risk, or missing capability, and what happens if nothing is done |
| ADR Additional Changes | Optional, and absent from a new record: delete the section. It returns with the first addition (see **Writing an Additional Change**) |
| Decision Drivers & Constraints | The drivers confirmed in the loop, each as a bold label and a measurable requirement. The four labels in the template are examples: keep those that apply, add others, and delete the rest |
| Considered Options | Every option the user weighed, with a one-sentence summary each, and doing nothing when it was a real choice. Use the same option names throughout the record |
| Detailed Comparison | ✅ and ❌ bullets for each option, every bullet tied to a named driver, with its source linked where the research backs it, or `(unverified)` where no source could be reached. Give each option its real weaknesses: an option without one usually means the comparison is unfinished |
| Decision Outcome | One sentence: the chosen option, and why it meets the drivers better than the others |
| Scope & Boundaries | Where the decision applies, and where it does not, with the exceptions |
| Consequences & Trade-Offs | Optional: only when the user discussed the consequences in the loop. Otherwise delete the section, and Migration & Rollout Impact stays a `###` heading under Decision Outcome, after Scope & Boundaries. A later addition that brings the section back puts it in its template place, just above Migration & Rollout Impact, which then sits under it again. When present, what the decision gives and what it costs, with at least one ❌, since every decision costs something |
| Migration & Rollout Impact | How existing code and data move over, step by step, or `Greenfield only; no migration required` |
| Compliance, Enforcement & Validation | Optional: only when the user discussed how the decision is enforced and validated; otherwise delete the section. When present, the check that keeps the decision from eroding (a CI rule, a test, a lint rule, a policy), the metric that shows it worked, and the event that reopens it. Where nothing automated exists, say how it is enforced, such as in review. Never name a check that does not exist |

</div>

  * Keep every required section, so that all records read alike. When one does not apply, say so in one line with the
    reason.
  * A required point that stays unknown reads `Not assessed`, with the reason, only when the user agreed to that at the
    **Confirm** step. Never fill it with a guess.
  * Write an optional section only when the loop gave it content: **ADR Additional Changes** after an addition, and
    the other two when the user discussed their topic. Otherwise leave it out, with no guess and no `Not assessed`.
  * Remove all template text: every `[...]` placeholder, the `{ ... }` block, the italic notes, and every example.
  * Write plain, specific sentences, and name the versions, numbers, and owners the loop established.
  * When the web was unavailable, the summary says so in one line, so that a reader knows why some points are marked
    `(unverified)`.

## Writing an Additional Change

An additional decision joins the record it adds to, after the loop and the user's confirmation. Everything already in
the record stays word for word: the addition only adds lines.

  1. **List it.** Add an entry to **ADR Additional Changes**, below the summary. When the section is missing, add it
     there, where the template places it. Entries run in date order, oldest first, and each is one short paragraph:
     what was decided, the options it beat and why, and what it added to the record.

     ```markdown
     ## ADR Additional Changes

       * 2026-12-03: Use Clerk as the identity provider, chosen over Auth0 and Amazon Cognito for its prebuilt
         sign-in components and its price at our number of monthly active users. Adds a cost driver, a lock-in
         consequence, and a check that keeps every call to Clerk inside `auth/`.
     ```

  2. **Fold it in.** Add each new line to the section it belongs to (a driver, a scope line, a consequence, a
     migration step, a check) and end it with `(added YYYY-MM-DD)`. Considered Options, Detailed Comparison, and
     Decision Outcome belong to the first decision: the choice and the options of an addition stay in its entry. When
     a line belongs to an optional section the record left out, add that section in its template place.
  3. **Update the frontmatter.** Add the new tags to `Document Tag(s)` and the new links and sources to
     `Related Link(s)`. `ADR Title`, `ADR Status`, and `Created On` stay as they are.
  4. **Update the index row** when the tags changed.

An addition that still needs the approval of others starts `YYYY-MM-DD (Proposed):`; drop the marker once it is
accepted. The `git diff` shows that change, and its commit message says that the addition moved from proposed to
accepted. An addition to a proposed record is dated the same way: `Created On` keeps the date the record was first
created, and the entries carry the dates of everything added since.

## Records in Another Layout

A record written before this skill, such as an `adr-tools` record with `## Status` and `## Context` headings, keeps its
layout and is never reformatted unasked.

  * Its status changes where it states it, such as under its `## Status` heading, and a remark goes on the first line
    below its title.
  * An addition goes into an **ADR Additional Changes** section placed after its first section, with no frontmatter to
    update.
  * Its index row takes the status from its text and shows `-` for the tags.

## Checks Before Saving

  - [ ] The file is `<number>-<slug>.md` in the decisions directory, and the slug matches the title.
  - [ ] The frontmatter parses as YAML, and `ADR Title` matches the `#` heading.
  - [ ] No template text is left: every `[` outside code opens a Markdown link, no line is a bare `{` or `}`, and no
    line starts with `*(`.
  - [ ] Each ✅ and ❌ names a driver, and the outcome names one of the considered options.
  - [ ] Every number, version, and claim traces back to the repository, a source, or the user, or is marked
    `(unverified)`.
  - [ ] A new record has no **ADR Additional Changes** section.
  - [ ] **Consequences & Trade-Offs** and **Compliance, Enforcement & Validation** appear only when the user discussed
    them, and **Migration & Rollout Impact** is there either way.
  - [ ] An addition has its dated entry, every line it inserted ends with `(added YYYY-MM-DD)`, and `git diff` of the
    record shows only added lines, apart from the tags and links in the frontmatter and a `(Proposed)` marker dropped
    on acceptance.
  - [ ] A superseded or deprecated record has its remark as the first line of its body.
  - [ ] The index has the new row, and its flag and tags match the record.
  - [ ] The Markdown format holds: lines within 120 characters, `  * ` lists, no em or en dash, and both div wrappers.

</div>
