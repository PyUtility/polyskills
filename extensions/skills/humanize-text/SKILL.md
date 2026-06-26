---
name: humanize-text
description:
  Governs the writing quality of natural-language prose generated in this repository, and runs on
  demand as the /humanize command to rewrite text the user pastes in. Acts as a default style
  governor so emails, documentation, commit-body prose, pull-request descriptions, comments,
  changelog entries, and general writing read as clear, deliberate human writing rather than
  generic model output. The skill cuts filler, hedging, and signposting, drops assistant-politeness
  tics, varies sentence rhythm, prefers active voice and concrete detail, and adapts register to the
  content type, never at the cost of accuracy. Use this skill whenever the user asks to "humanize",
  "make this sound human", "make it sound less like AI", "remove the AI tone", "rewrite this
  naturally", "tighten this up", "make it read better", or to draft or edit an email, README, PRD,
  requirement note, commit message, or PR description. In governor mode, applies silently to prose
  output without announcement. This does not apply to structured outputs such as JSON, YAML, error
  messages, or tool responses where prose style is not the primary concern.
always_load: true
---

<div align = "center">

# Humanize

</div>

<div align = "justify">

This skill shapes the natural-language prose generated in this repository so it reads like clear,
deliberate human writing, and it also runs as the `/humanize` command to rewrite text on request.
The aim is craft, not disguise. Good writing is specific, varied, and willing to take a position,
and that is what makes it read as human. Accuracy always outranks style: never trade a true,
precise statement for a smoother one.

## Getting Started

  1. Decide the **mode**. Governor mode shapes prose you are already generating. `/humanize` mode
     rewrites text the user pasted in.
  2. Read the **Non-Negotiables** below before changing a single word. They override every stylistic
     rule that follows.
  3. Identify the **content type** (email, technical doc, code-adjacent text, general prose) and set
     the register from the table further down.
  4. Apply the **Core Principles**, then sweep the **AI-Tells Checklist**.
  5. Run the **Self-Review Pass**. In `/humanize` mode, return only the rewritten text unless the
     user asked for an explanation, and preserve meaning, quotes, code, and names exactly.

Never skip the Non-Negotiables, even for a one-line change.

## Non-Negotiables

These three rules are the spine of the skill. They are gates, not preferences.

  1. **Immutable-content fence.** Never alter the characters inside code fences or inline code,
     anything inside quotation marks or blockquotes, identifiers (function, variable, class, API,
     and flag names, file paths, environment variables), proper nouns, numbers, units, versions,
     URLs, or citation strings. Humanize touches the connective prose around these things only. If a
     rewrite would change any of them, revert that part. When a sentence contains an immutable token
     (inline code, identifier, quoted string), rewrite only the words outside that token. Do not
     restructure the sentence in a way that would require moving or rephrasing the token itself.
  2. **Deference to format skills.** When another skill governs the artifact, it is authoritative on
     structure, required tokens, and formatting, and humanize only refines the free prose in the
     slots it leaves open. See the precedence table below.
  3. **Meaning preservation.** Change how something is said, never what it asserts. Do not alter a
     claim's scope, quantifiers, modality (`may`, `must`, `should`), or confidence level. Add no new
     claims and drop no existing conditions. When unsure, keep the original wording.

<div align = "center">

| Artifact | Governing Skill | What Humanize May Touch |
| :---: | :---: | --- |
| Git commit subject or body | `git-commiter` | Only the prose inside a body paragraph. Never the emoji prefix, the section layout, or the trailer. |
| Any `*.md` file | `markdown-format` | Only the sentence-level prose. The div wrappers, headings, list markers, and em-dash ban win. |
| `*.py` file | `python-code-format` | Comment and docstring wording only. Code is immutable. |
| `*.sql` file | `sql-code-format` | Comment wording only. Statements are immutable. |

</div>

Humanize is a subordinate prose refiner, not a structural authority. If a governing skill requires a
token, keep it.

## Operating Modes

In **governor mode** the skill works silently while you draft. Never announce that you humanized
anything, even if the user asks. For one-line replies and short status notes, limit edits to
removing assistant tics and replacing overused lexical tells. Do not restructure sentences or vary
rhythm. Leave prose that already reads well unchanged: returning the text untouched is a valid
outcome.

In **`/humanize` mode** the skill rewrites the supplied text. Do not expand the scope, add claims,
or invent detail the source did not contain. Return the rewritten text by default, and summarise the
changes only when the user asks. If the entire supplied text falls within the immutable-content
fence (e.g., it is a code block, a URL, or consists only of identifiers), return it unchanged and
add a single sentence: "No prose to rewrite. All content is protected."

## Core Principles

  * **Cut words that do no work.** If a sentence reads the same without a word, remove it.
  * **Vary sentence length on purpose.** Uniform medium-length sentences are the single strongest
    tell. In any passage of three or more sentences, write at least one short sentence of roughly six
    words or fewer, and let at least one run long. Never leave three sentences in a row at about the
    same length. This comes from real phrasing, not from gimmicky fragments or deliberate errors.
    Read it aloud, and if the beat is flat and even, break it.
  * **Use active voice with a named actor.** "The service retries the request" beats "the request is
    retried."
  * **Prefer concrete specifics.** Name the thing, the number, the date, the tool. Replace "a range
    of options" with the actual options.
  * **Take a position, then qualify it.** State the point and add a real caveat. Do not present both
    sides with equal weight and no conclusion.
  * **Lead with the point.** Drop throat-clearing openers and conclusions that only restate the
    opening. End on the last real idea, not a summary label.
  * **Prefer the plain word.** Use the shortest accurate word. Reach for a longer one only when it is
    genuinely more precise.

## AI-Tells Checklist

Sweep these layers after drafting. The full lexical catalogue and extended lists live in
[references/word-swaps.md](references/word-swaps.md).

### Lexical

Overused vocabulary signals machine drafting. Replace it with the plainest accurate word. A
representative subset:

<div align = "center">

| Reconsider | Prefer |
| :---: | --- |
| delve into, dive deep | look at, examine, study |
| leverage, utilize, harness | use |
| facilitate, enable seamless | help, let, support |
| robust, comprehensive, holistic | drop it, or name the actual quality |
| navigate the landscape, in the realm of | in, within, for |
| a testament to, underscores, highlights | shows, proves |
| pivotal, crucial, vital, key | drop it, or show why it matters |

</div>

Do not swap a word that is technically correct in context. The right word always wins over the rule.

### Structural

  * Break the rule of three when ideas do not come in threes. Not every list needs exactly three
    items, and not every noun needs two adjectives.
  * Vary paragraph length. Avoid a wall of same-sized blocks.
  * Use prose where prose belongs. Convert a bulleted list back to sentences when the items are not
    genuinely parallel.
  * Drop mirror-image scaffolding: "Not only X but also Y", "From A to B", and conclusions that
    restate the introduction.

### Tonal

  * Cut relentless positivity and vague hype adjectives ("powerful", "exciting", "game-changing").
  * Stop fence-sitting. "On one hand, on the other hand" with no verdict reads as evasion.
  * Stop over-explaining the obvious. Trust the reader.

### Punctuation

  * Do not lean on semicolons to chain clauses the model could not commit to splitting.

### Assistant Tics

  * Delete openers like "Certainly!", "Great question!", and "I'd be happy to".
  * Delete closers like "I hope this helps", "Feel free to reach out", and "Let me know if you need
    anything else".
  * Delete "It's important to note that" and "It's worth mentioning that": just state the thing.
  * Stop asking permission mid-text ("Would you like me to..."). Make the statement.

## Register Adaptation

Register follows the audience and the medium. Do not impose one "humanized voice" on everything.

<div align = "center">

| Content Type | Cues | Keep | Cut |
| :---: | --- | --- | --- |
| Email and business comms | A person, a thread, an ask | One clear ask, a subject that states it, contractions | "I hope this finds you well", "just circling back", padded apologies |
| Technical docs (README, PRD, notes) | Skimmed for facts | Exact terms, versions, numbers; neutral precise tone | Marketing voice, "comprehensive guide" framing, hype adjectives |
| Code-adjacent (commits, PRs, comments) | Read by maintainers | Imperative mood, the reason for the change | Restating what the code does; defer structure to `git-commiter` |
| General prose | A reader, not a spec | Rhythm, voice, a point of view | Filler, hedging, generic openers and closers |

</div>

Contractions are on for email and casual prose and off for formal docs, specs, and legal or safety
text.

## What Not To Do

  * Do not change facts, figures, identifiers, paths, or versions to make a sentence flow.
  * Do not fabricate detail, anecdotes, or sources to add "texture".
  * Do not inject deliberate typos, grammar errors, or fake hesitation. Rhythm comes from clear
    thinking, not from damage.
  * Do not alter quotes, code blocks, log output, or command snippets.
  * Do not over-edit a sentence that is already clear and accurate. Leave it.
  * **Keep protected hedges.** Probability, scope, warnings, and normative language in safety, legal,
    security, or compliance text are precision, not filler. De-hedging targets only empty softeners
    ("I think maybe perhaps"), never a real statement of uncertainty.

## Scope and Non-Goals

This skill optimizes writing quality. It is not a tool for evading AI-detection systems, it is not
tuned or measured against them, and it must not be used to misrepresent the authorship of work
submitted for assessment or to disguise who wrote code. The whole approach rests on writing well, not
on hiding anything.

## Self-Review Pass

Before emitting humanized text, confirm every box.

  - [ ] Meaning, facts, identifiers, and code are unchanged.
  - [ ] Em dashes: banned in `*.md` files; reduced to near zero elsewhere, replaced by a period, comma, parentheses, or colon. Punctuation varies and does not lean on semicolons.
  - [ ] Sentence lengths vary: at least one short sentence and one longer one, and no run of three at about the same length.
  - [ ] No overused lexical tells remain.
  - [ ] No assistant tics and no conclusion that only restates the opening.
  - [ ] Active voice and concrete specifics dominate.
  - [ ] Register matches the audience and medium.
  - [ ] Necessary hedges in safety, legal, or technical statements are intact.
  - [ ] Nothing was fabricated to add texture.

If a passage is borderline, score it with the rubric in
[references/word-swaps.md](references/word-swaps.md) and fix the lowest-scoring signal first.

## Quick Checklist

  - [ ] Did I read the Non-Negotiables before editing?
  - [ ] Did I leave every fenced, quoted, and identifier token exactly as written?
  - [ ] Did I keep every token a governing skill requires (commit emoji, div wrappers, trailers)?
  - [ ] Does the rewrite assert exactly what the original asserted, no more and no less?
  - [ ] Did I vary sentence length and cut the lexical, tonal, and assistant tells?
  - [ ] Did I set the register from the content type rather than impose one voice?
  - [ ] Did I keep protected hedges and avoid fabricating detail?

</div>
