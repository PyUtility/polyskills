---
name: vendor-agnostic
description: >-
  Refactors a repository's documentation, agent personas, skills, and vendor configuration into one token-optimized,
  vendor-agnostic layout: a routed `AGENTS.md`, entry points under 15 lines for Claude Code, Gemini CLI and Antigravity,
  and GitHub Copilot, shared skills and agents under `.agents/`, and one page per topic under `docs/`. OpenCode, Codex,
  and Cursor read the shared layer directly. A vendor name wires only that vendor; without one, every vendor is wired.
  Explicit-invoke only: run it when the user types /vendor-agnostic or asks for the command by name, never on your own
  initiative and never as a side effect of another task. Trigger phrases: the /vendor-agnostic command, "run
  vendor-agnostic", "make this repository vendor-agnostic".
disable-model-invocation: true
argument-hint: "[vendor ...] [links=pointer|symlink]"
---

<div align = "center">

# Vendor Agnostic

</div>

<div align = "justify">

Every coding assistant looks for its instructions in a file of its own, so a repository that several of them work in
collects copies: `CLAUDE.md`, `GEMINI.md`, rules files, prompts. The copies drift apart, and each one is loaded on every
request. This command moves the repository to one shared layer that every assistant reads, plus a thin entry point for
each vendor that needs one.

## Getting Started

  1. Run this command only when the user invoked it: `/vendor-agnostic`, or a request that names it.
  2. Read this whole file, then each reference when its step begins: [migration](references/migration.md),
     [vendors](references/vendors.md), [links](references/links.md), and [validation](references/validation.md).
  3. Find the folder of this command. Your tool names it when it loads this file (Claude Code calls it the base
     directory). The templates are in `resources/` and the check is in `scripts/`. When they are not there, look in the
     skill folders of the project and of the user. When they are nowhere, stop and say so. Never rebuild a template from
     memory.
  4. Change nothing before the user has approved the migration map of step 2. Reading is free.
  5. Ask when a source is unclear, two sources disagree, or a move could break something you cannot see. Guessing costs
     more than a question.
  6. The format skills the user or the project has installed govern every file this command writes. `AGENTS.md` and the
     entry points are the exception: models read them as raw text on every request, so they are plain Markdown, without
     HTML wrappers, badges, or frontmatter.
  7. A hook or a permission that denies a write has answered. Stop and report it. Never take another route around it.

## Arguments

```text
/vendor-agnostic [vendor ...] [links=pointer|symlink]
```

The arguments are whatever the user typed after the command name, in any order.

<div align = "center">

| Argument | Values | Default | Meaning |
| :---: | :---: | :---: | --- |
| `vendor` | `claude`, `gemini`, `copilot`, `opencode`, `codex`, `cursor` | Every vendor | The assistants to wire. Name the one in use to get only its files, or several. |
| `links` | `pointer`, `symlink` | `pointer` | How `.claude/` reaches `.agents/` (see [links](references/links.md)) |

</div>

  * Letter case does not matter. `claude-code` and `anthropic` mean `claude`; `gemini-cli`, `antigravity`, and `google`
    mean `gemini`; `github-copilot` and `github` mean `copilot`; `openai` means `codex`.
  * An unknown vendor stops the run. List the known ones and ask.
  * A vendor argument limits what is **wired**, never what is **read**. The shared layer is always built from every
    source in the repository, whichever vendor wrote it. The files of the vendors that were not named stay as they are,
    and the report names those that now repeat the shared layer.

## Target Layout

```text
AGENTS.md                        master routing index: guardrails, registry, routing table
SKILLS.md                        only when the registry passes 15 rows
CLAUDE.md                        entry point: imports AGENTS.md
GEMINI.md                        entry point: imports AGENTS.md (Gemini CLI, Antigravity)
README.md                        for end users; stays at the root
.agents/
    agents/<role>.md             shared agent roles
    skills/<name>/SKILL.md       shared skills
.claude/
    agents/, skills/             pointer files to .agents/ (or symlinks with links=symlink)
    settings.json, hooks/, commands/, MEMORY.md      Claude-only files stay here
.gemini/, .opencode/, .codex/, .cursor/              vendor-only files stay here
.github/copilot-instructions.md  entry point: names AGENTS.md
docs/
    README.md                    setup, local development, repository overview, the agent files
    ARCHITECTURE.md              system design, tech stack, data flow, boundaries
    PRODUCT.md                   domain logic, user flows, product requirements
    decisions/                   README.md and one YYYY-MM-DD-<slug>.md per decision
    <component>.md, <group>/     one page per component, mirroring the code
    gaps-and-risks.md, tasks/    only when there is something to hold
```

Create a folder only when it holds a file. `.agents/agents/` and `.agents/skills/` always exist, with a `.gitkeep` while
they are empty, and hold no other loose file.

## Rules

### Rule 1: Zero-Bloat Initialization Files

`CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md` hold no project prose, architecture, coding standard, or
repeated rule. Each stays under 15 lines: the hand-over to `AGENTS.md`, plus what no other vendor could use.

  * `CLAUDE.md` hands over with the line `@AGENTS.md`, and `GEMINI.md` with `@./AGENTS.md`. A sentence is not enough:
    Claude Code loads nothing for "read AGENTS.md first".
  * `copilot-instructions.md` hands over with a sentence and a link, because Copilot CLI would load an import twice.

### Rule 2: Strict Single Source Of Truth

Every fact, rule, workflow, and decision stands in exactly one file. Everything else points at it.

  * Overlapping sources are merged into one canonical page, and the sources are removed once their last unique fact is
    placed. No stale copy stays behind.
  * A vendor folder that needs shared content points at it. It never holds a copy.
  * The documentation records what exists. When a page and the code disagree, the code wins.

### Rule 3: Progressive Disclosure And Conditional Fetching

`AGENTS.md` is a routing table and not a knowledge dump. It has three parts, and it stays under 200 lines and 24,000
bytes:

  1. **Universal Guardrails**: the commands and rules every task needs, ten bullets at most.
  2. **Shared Agents And Skills Registry**: one row per file in `.agents/`, with a one-line trigger.
  3. **Documentation Routing Table**: task intents and code paths, each with the page to read.

It tells the assistant, word for word:

> DO NOT read all files in `docs/` or `.agents/` upfront. Match the user's request against the routing table below and
> read ONLY the specific target file(s) required for the active task.

Every path in it is a code span or a link. A bare `@path` in `AGENTS.md` is loaded into every session of Claude Code and
Copilot CLI, which defeats the rule.

### Rule 4: Nothing Lost, Nothing Weakened

  * Every section and bullet of the old files has a place in the new ones, or a reason in the migration map.
  * A limit on an agent (its tools, its paths, read-only) is never dropped because the shared file cannot express it. It
    moves to the file its vendor enforces.
  * Ignored, personal, and secret files are never read into a tracked one. A secret found in a tracked file is reported
    by file and line, without its value.
  * Hooks, settings, permissions, and workflows keep doing what they did. A path they name is updated in the same
    change.
  * Source code is not touched. A wrong comment or docstring is recorded, not fixed.

## Modes

The mode follows from the repository. State it before the map.

<div align = "center">

| Mode | When | What Happens |
| :---: | --- | --- |
| Create | No instruction file exists | Survey the code and the READMEs, and write the layout |
| Migrate | Instruction files or scattered documents exist, and `AGENTS.md` does not route | The full workflow |
| Refresh | `AGENTS.md` already routes into `docs/` | Run the check, show what would change, and after approval fix what drifted and wire the vendors that were named. Nothing is restructured. |

</div>

## Workflow

### Step 1: Preflight

  1. The directory is in a git repository with at least one commit. Without one nothing can be undone: stop, and offer
     to create it.
  2. `git status --short` is empty. Otherwise ask the user to commit or stash first. Never do it for them. Offer a
     branch such as `chore/vendor-agnostic`, and create it only when they agree.
  3. Run `scripts/check.sh` with the vendors for the baseline (see [validation](references/validation.md)).
  4. Find out whether `docs/` is published: `mkdocs.yml`, `docusaurus.config.*`, `docs/conf.py`, `.readthedocs.y*ml`,
     `_config.yml`, or a Pages workflow. Decisions, gaps, and agent notes would go public with it. Ask whether to
     exclude the new pages from the site or to use another root.
  5. `git check-ignore -v` names no path of the target layout. Where one is ignored, put a narrower ignore rule into the
     map, because an ignored `AGENTS.md` looks fine and is never committed.
  6. Read the hooks and permissions that fire on edits, so that none of them surprises you halfway.

### Step 2: Audit And Inventory

Follow [migration](references/migration.md). Read every Markdown file, vendor folder, prompt, rule, and script of the
inventory in full, and present the **migration map**: a `Source -> Destination` row for each section that moves, with
the action and the reason. Below it, list what would break, the conflicts, the files that stay, and any secret by
location. Then stop and wait. Continue only with what the user approved.

### Step 3: Scaffold And Link

  1. Create `.agents/agents/` and `.agents/skills/`, with a `.gitkeep` in one that stays empty, and the `docs/` pages
     the map names.
  2. Rename with `git mv`, also when only the case changes. Before any edit, offer to commit the pure renames on their
     own: git follows the history of a file only when the rename and the edit are in separate commits.
  3. Wire `.claude/skills` and `.claude/agents` when Claude Code is among the vendors, in the mode of `links=`. Never
     put a junction where git tracks a symlink: ordinary git commands then delete the shared files.

### Step 4: Consolidate And Migrate

Work one destination file at a time, and tick its rows off in the map.

  1. Architecture, tech stack, and boundaries go to `docs/ARCHITECTURE.md`; product rules and domain logic to
     `docs/PRODUCT.md`; onboarding, environment, and local commands to `docs/README.md`; component detail to its page.
  2. Historical decisions become dated records. When the text has no date, take it from `git log` and say so in the
     record.
  3. Reusable workflows become `.agents/skills/<name>/SKILL.md`, and personas `.agents/agents/<role>.md`, with the
     shared frontmatter of [vendors](references/vendors.md). Keys of one vendor go to its pointer.
  4. Write only what you checked against the code. Keep the owner's wording where it is accurate.
  5. Remove a source with `git rm` once its last row is ticked.

### Step 5: Generate Thin Entry Points

Write `AGENTS.md` first, then the entry points of the vendors, from the templates and [vendors](references/vendors.md).
Replace every placeholder, and keep an optional block without its markers or delete it whole. Delete a row or a
guardrail that names a page the repository does not have.

### Step 6: Re-Point

Search the repository for every old path and update each hit: hooks, scripts, settings, workflows, `CODEOWNERS`, ignore
files, manifests, READMEs, skill and agent bodies. [migration](references/migration.md) lists the four that are missed
most often.

### Step 7: Verify

Run every check of [validation](references/validation.md), and fix what fails. Run the build, lint, and tests of the
repository, and compare them with the state before the change.

### Step 8: Report

Keep it short, in this order:

  1. What needs the user: open conflicts, secrets found, files that could not be deleted, machine setup.
  2. The final layout, and what moved, merged, or was dropped with its reason.
  3. Each vendor: what it reads now, and its known limits.
  4. The output of the check script, with a reason for each `WARN` that stays, and each check that could not run.
  5. The commits you propose for what is not committed yet. Commit only when the user asks, with the commit rules of the
     project.

## Vendors In Short

<div align = "center">

| Vendor | This Command Creates | Traps |
| :---: | --- | --- |
| `claude` | `CLAUDE.md`; `.claude/skills` and `.claude/agents` | Reads nothing under `.agents/`; loads every `@path` |
| `gemini` | `GEMINI.md` | Antigravity reads `.agents/agents/` itself, and an unknown tool name can hang it |
| `copilot` | `.github/copilot-instructions.md` | Some chats read only this file |
| `opencode` | Nothing; `.opencode/agents/` when named | Any loose `.md` file in a skills folder becomes a skill |
| `codex` | Nothing; `.codex/agents/` when named | `AGENTS.override.md` replaces `AGENTS.md`; 32 KiB in total |
| `cursor` | Nothing | Reads the Claude pointers; `readonly` is its only limit |

</div>

## Resources

<div align = "center">

| File | Use It For |
| :---: | --- |
| [`resources/AGENTS.md.template`](resources/AGENTS.md.template) | The routing index |
| [`resources/SKILLS.md.template`](resources/SKILLS.md.template) | The registry, once it passes 15 rows |
| [`resources/CLAUDE.md.template`](resources/CLAUDE.md.template), [`GEMINI.md.template`](resources/GEMINI.md.template), [`copilot-instructions.md.template`](resources/copilot-instructions.md.template) | The entry points |
| [`resources/SKILL.md.template`](resources/SKILL.md.template), [`agent.md.template`](resources/agent.md.template) | A shared skill, a shared agent |
| [`resources/pointer-skill.md.template`](resources/pointer-skill.md.template), [`pointer-agent.md.template`](resources/pointer-agent.md.template) | The Claude Code pointers |
| [`resources/docs/`](resources/docs/) | The pages: `README`, `ARCHITECTURE`, `PRODUCT`, a component page, gaps and risks, decisions, tasks |
| [`references/migration.md`](references/migration.md) | Inventory, the map, where content goes, re-pointing, deleting |
| [`references/vendors.md`](references/vendors.md) | What each vendor reads, shared frontmatter, native agent files |
| [`references/links.md`](references/links.md) | Pointer files, symlinks, and why junctions are banned |
| [`references/validation.md`](references/validation.md), [`scripts/check.sh`](scripts/check.sh) | The checks that end every run |

</div>

Templates mark a placeholder as `{name}` and an optional block as `{{ OPTIONAL: <when> ... }}`.

## Working With Other Skills

  * A format skill decides how a page looks, a prose skill how it reads, and a commit skill how it is committed. This
    command decides what the files are and where they live.
  * `extend-init` builds a Claude-only layout with the router in `CLAUDE.md`. After this command has run, `AGENTS.md` is
    the router, so do not run `extend-init` on the same repository.

## What Not To Do

  * Do not change, move, or delete a file before its row in the map was approved.
  * Do not write a rule into an entry point because one vendor cannot follow the pointer. Report the limit.
  * Do not copy `.agents/` into a vendor folder, and do not link the whole `.claude` folder.
  * Do not put a `README.md`, an index, or notes into `.agents/agents/` or `.agents/skills/`: tools load them.
  * Do not add tool names, models, or colors to a shared agent, or vendor keys to a shared skill.
  * Do not move the root `README.md`, the license, or any file another system looks up by name.
  * Do not invent facts, commands, or pages to fill a template. Leave the slot out and record the gap.
  * Do not edit user-level files such as `~/.claude/`, and do not commit or push unasked.

## Quick Checklist

  - [ ] Did the user invoke the command, and did I find its templates instead of rebuilding them?
  - [ ] Was the tree clean, and did the user approve the migration map before the first change?
  - [ ] Is every entry point under 15 lines, with a hand-over its vendor really loads?
  - [ ] Does `AGENTS.md` hold at most ten guardrails, the registry, the routing table, and the "DO NOT read" sentence?
  - [ ] Does every fact stand in one file, with every old copy gone?
  - [ ] Do shared skills and agents carry only shared frontmatter, with every old limit kept in a vendor file?
  - [ ] Do the vendor folders point at `.agents/` in a way that works on every machine the repository is cloned to?
  - [ ] Did every hook, workflow, ignore file, and manifest that named an old path get the new one?
  - [ ] Did the check script end without a `FAIL`, and did the build and tests give the same result as before?
  - [ ] Does the report name every limit, every open conflict, and every check that did not run?

</div>
