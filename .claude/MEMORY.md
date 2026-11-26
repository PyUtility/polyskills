# Project Memory

Durable memory for every session in this repository, kept in git so that it survives a new machine, account, or
checkout path. `CLAUDE.md` imports it, so it loads on every request: keep it short and put the detail in
`.claude/docs/`.

## Owner Preferences

  * For a design change to a skill or a command, and for review findings, list the items first (with a 0-10 score and
    research against published standards when asked) and wait for the owner's decision on each before editing. The
    owner often approves a subset and holds the rest, so implement only what was approved and name what still waits.
  * When a rule change touches what a template holds, update the template in the same change, unasked. The owner had
    to ask for this more than once.

## Environment

  * The checkout path holds spaces, brackets, and parentheses: quote every path in shell commands.

## Decisions And Changes

  * 2026-11-26: Decision records follow the `make-adr` skill. `/vendor-agnostic` keeps exact copies of its two
    templates, changed in `make-adr` first; see `extensions/commands.md`.

## Open Items

  * The plugin versions, the registrations, and the defects listed in `gaps.md` wait for the owner.
