<div align = "center">

# Humanize Reference

</div>

<div align = "justify">

This reference backs the `humanize` skill. It holds the full lexical catalogue, the extended
structural and tonal tell lists, and the scoring rubric with a worked example. Load it when the inline
checklist in `SKILL.md` is not enough, or to score a passage. Every rule here is subordinate to the
three Non-Negotiables in `SKILL.md`: the immutable-content fence, deference to format skills, and
meaning preservation. A word on this list is a prompt to reconsider, never a forced swap. The right
word for the context always wins.

## Lexical Catalogue

These are words and phrases that recur in machine drafting. Replace them with the plainest accurate
wording, or cut them.

### Inflated Verbs

</div>

| Reconsider | Prefer |
| :---: | --- |
| delve into, dive deep into | look at, examine, study |
| leverage, utilize | use |
| harness, tap into | use, draw on |
| facilitate | help, ease, run |
| foster, cultivate | build, grow, encourage |
| streamline | simplify, speed up |
| underscore, highlight, emphasize | show, point to, stress |
| showcase | show, present |
| empower, enable | let, allow, give |
| embark on | start, begin |
| navigate (a problem) | handle, work through, solve |
| elevate, unlock | improve, open up, or cut |

### Inflated Nouns and Adjectives

<div align = "justify">

These add grandeur without meaning. Cut them, or replace them with a concrete detail.

</div>

| Reconsider | Prefer |
| :---: | --- |
| robust, comprehensive, holistic | name the actual property, or cut |
| seamless, effortless | cut, or say what makes it easy |
| powerful, cutting-edge, state-of-the-art | cut, or give a concrete capability |
| pivotal, crucial, vital, key, essential | cut, or show why it matters |
| myriad, plethora, a host of, a range of | a number, or the actual list |
| tapestry, landscape, realm, ecosystem, sphere | the literal place or field |
| testament, hallmark, cornerstone | shows, proves, or cut |
| innovative, revolutionary, transformative, game-changing | describe what it does instead |

### Signposting and Filler Phrases

| Reconsider | Prefer |
| :---: | --- |
| It is important to note that | (state the point directly) |
| It is worth mentioning that | (state the point directly) |
| In today's fast-paced world | (cut) |
| When it comes to X | About X, or For X |
| In order to | to |
| Due to the fact that | because |
| In the event that | if |
| A number of, a variety of | several, or the count |
| Needless to say, it goes without saying | (cut) |
| At the end of the day, ultimately | (cut, or state the conclusion) |

### Transitions Used on Autopilot

<div align = "justify">

Overused connectors create a mechanical drumbeat. Prefer a period, a simple conjunction, or no
transition at all.

</div>

| Reconsider | Prefer |
| :---: | --- |
| Moreover, Furthermore, Additionally | and, also, or a new sentence |
| However, Nevertheless (stacked) | but, yet, still |
| Consequently, Therefore (stacked) | so |
| Firstly, Secondly, Lastly | cut the labels, let order carry |

## Extended Structural Tells

<div align = "justify">

  * **Rule of three everywhere.** Triplets of nouns, adjectives, or clauses on every line. Vary the
    count to match the ideas.
  * **Uniform sentence length.** A run of sentences all 15 to 20 words long. Insert a short one.
  * **Uniform paragraph blocks.** Every paragraph the same size. Let some run short.
  * **List reflex.** Bulleting items that are not parallel or that read better as a sentence.
  * **Bold-label lists.** Every bullet opening with a bolded word and a colon, used mechanically.
  * **Mirror conclusions.** A final paragraph that restates the opening in new words.
  * **Negated-contrast frames.** "Not only X but also Y", "It is not just A, it is B", "From X to Y".
  * **Template intros.** "In this section we will explore", "This document aims to". Cut them and
    start with the content.

## Extended Tonal Tells

  * **Relentless positivity.** Everything is exciting, powerful, and valuable. Vary the temperature.
  * **Both-sides paralysis.** Presenting every trade-off with equal weight and never landing.
  * **Vague attribution.** "Studies show", "experts agree", "it is widely believed". Name the source
    or drop the claim.
  * **Over-explanation.** Spelling out what the reader already knows. Trust them.
  * **Customer-service warmth.** "Great question", "happy to help", "hope this helps". Cut it.
  * **Hedging stacks.** "It seems that it might possibly be the case that". Make the claim or do not.

## Scoring Rubric

<div align = "justify">

Use this to score a passage's writing quality out of 10. It measures craft, not an "AI-ness" number,
and it cannot be satisfied by damaging the text. The passing bar is **6 of 10 (60%)**. Accuracy is a
gate that sits above the score: if any fact, identifier, quote, or code token was altered, the
passage fails outright regardless of points.

</div>

| Signal | Measured As | Full | Half | Zero |
| :---: | --- | :---: | :---: | :---: |
| Lexical tells | catalogue hits per 100 words | 0 hits = 2 | 1 to 2 = 1 | 3+ = 0 |
| Sentence-length variance | stdev of sentence word counts (passages of five or more sentences) | >= 6 = 2 | 3 to 6 = 1 | < 3 = 0 |
| Hedging and signposting | filler hedges plus signposts per 100 words | <= 1 = 1.5 | 2 to 3 = 0.75 | 4+ = 0 |
| Punctuation | em dashes per 100 words and variety | 0 and varied = 1.5 | some = 0.75 | em-heavy = 0 |
| Specificity | concrete nouns, numbers, names vs vague nouns | mostly concrete = 1.5 | mixed = 0.75 | mostly abstract = 0 |
| Voice and stance | active-voice share and a committed point | active and a stance = 1.5 | one of two = 0.75 | passive and fence-sitting = 0 |

<div align = "justify">

A score of 6 or higher reads as competent human writing with no disqualifying cluster of tells. Below
6 means at least one signal is failing hard, usually uniform rhythm paired with lexical tells. Fix the
lowest-scoring signal first, then rescore.

For short passages (under about five sentences, such as a brief email or a one-line requirement note),
full burstiness is often neither achievable nor desirable. Do not force a clipped fragment in to widen
the spread. Award the variance points when the few sentences differ naturally, and never mark short
content down for reading clean. The same holds for specificity: when the source carries no concrete
facts, do not penalize prose for failing to invent them.

### Worked Example

Source draft (AI-flavored):

</div>

```text
It is important to note that our innovative platform leverages a comprehensive suite of
robust features to seamlessly empower teams to effortlessly navigate the complexities of
modern collaboration, ultimately fostering a more productive and engaging workplace
environment for all stakeholders involved.
```

<div align = "justify">

Score of the source: lexical 0 (innovative, leverages, comprehensive, robust, seamlessly, empower,
effortlessly, navigate, fostering), variance 0 (one long sentence), hedging 0.75, punctuation 1.5 (no
em dashes but flat), specificity 0 (no concrete noun), voice 0 (no real actor, no stance). Total about
2.25 of 10. Fails.

Humanized rewrite:

</div>

```text
Our platform does one thing: it keeps a team's messages, files, and decisions in a single
thread. No more hunting across four tools to find what someone said last Tuesday.
```

<div align = "justify">

Score of the rewrite: lexical 2 (no catalogue hits), variance 2 (a long sentence and a short
fragment), hedging 1.5, punctuation 1.5, specificity 1.5 (messages, files, decisions, "last
Tuesday"), voice 1.5 (active, a clear claim). Total 10 of 10. The rewrite asserts less than the
puffed-up original, which is correct: the original asserted nothing concrete, so nothing true was
lost.

</div>
