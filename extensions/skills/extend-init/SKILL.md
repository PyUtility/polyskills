---
name: extend-init
description: >-
  Builds, migrates, or repairs a routed Claude Code context for a repository: a short `CLAUDE.md` that sends each task
  to one document in a docs directory (default `.claude/docs/`), one document per component in directories that mirror
  the code, and an optional project memory file (default `.claude/MEMORY.md`) that `CLAUDE.md` imports and that is
  filled from Claude Code's per-machine auto memory. Explicit-invoke only: run it when the user types /extend-init or
  asks for the skill by name, never on your own initiative and never as a side effect of /init or another task.
  Trigger phrases: the /extend-init command, "run extend-init", "use the extend-init skill", "extend-init this
  repository".
disable-model-invocation: true
argument-hint: "[docs=<dir>] [memory=<file>|off] [import-memory=on|off] [mode=auto|create|migrate|refresh]"
---

<div align = "center">

# Extend Init

</div>

<div align = "justify">

Claude Code's `/init` writes everything it learns into one `CLAUDE.md`, and that file is loaded on every request. This
skill keeps `CLAUDE.md` small. The detail moves into a tree of documents that Claude reads only when a task needs them,
and `CLAUDE.md` becomes a router: a summary, the common commands, a few rules, and a table that maps each kind of task
to one document. Project memory, when enabled, lives in the repository and travels with every clone.

## Getting Started

  1. Run this skill only when the user invoked it: the `/extend-init` command, or a request that names the skill. Never
     start it on your own, never fold it into `/init`, and never apply its layout to another task unasked.
  2. Read this whole file, then the reference for each step as you reach it: [layout](references/layout.md),
     [memory](references/memory.md), and [validation](references/validation.md).
  3. Parse the arguments (see **Parameters**). Anything not given takes its default.
  4. Read every file you will change in full before changing it: `CLAUDE.md`, `CLAUDE.local.md`, the docs directory,
     the memory file, and any hook, script, or setting that names a document path.
  5. When the user or the project has a Markdown format skill or a prose skill, apply it to every file this skill
     writes. The templates follow a common layout, and an installed format skill wins over them.
  6. Ask before you delete, rename, or move a file the user wrote, and before you copy anything from the per-machine
     memory into a file that git tracks.

## Parameters

Arguments are `key=value` pairs after the command, in any order, for example `/extend-init docs=docs/claude
memory=off`.

<div align = "center">

| Key | Default | Meaning |
| :---: | :---: | --- |
| `docs` | `.claude/docs/` | Root directory of the documents, relative to the repository root. Every path in the routing table is relative to it. |
| `memory` | `.claude/MEMORY.md` | Project memory file that `CLAUDE.md` imports. `off` writes no memory file and no import line. |
| `import-memory` | `on` | Fold durable entries from Claude Code's per-machine auto memory into the project memory. Ignored when `memory=off`. |
| `mode` | `auto` | `create`, `migrate`, or `refresh`; `auto` picks one from what already exists (see **Modes**). |

</div>

## Target Layout

```text
CLAUDE.md                     router: summary, commands, rules, routing table, memory import
<memory>                      optional project memory, imported by CLAUDE.md
<docs>/
    <component>.md            a component that stands alone
    <group>/
        <group>.md            optional overview: what the members share
        <member>.md           one document per member
        <subgroup>/
            <member>.md
    <topic>.md                cross-cutting topics: the Claude Code setup, testing, known gaps
```

The tree mirrors how the code is organized, so the document for a code path is easy to guess. A component gets its own
file, and a set of related components gets a directory. [references/layout.md](references/layout.md) has the rules for
drawing the tree, naming the files, sizing them, and building the routing table.

## Modes

<div align = "center">

| Mode | Picked By `auto` When | What Happens |
| :---: | :---: | --- |
| `create` | No `CLAUDE.md` exists | Survey the repository and write the router, the documents, and the memory. |
| `migrate` | `CLAUDE.md` exists without a routing table, or holds detail that belongs in documents | Split the existing content into documents without losing a fact, then rewrite `CLAUDE.md` as a router. |
| `refresh` | `CLAUDE.md` already routes into the docs directory | Validate everything against the code, fix what drifted, and restructure where the tree no longer fits the code. |

</div>

## Workflow

  1. **Survey.** List the top-level directories, then the build, test, lint, and run commands from the manifests, CI
     workflows, and READMEs. Note existing documents, `.claude/rules/`, hooks, and settings. In a large repository,
     hand each top-level area to a read-only subagent and keep only its conclusions.
  2. **Draw the tree.** Decide the components and groups with [references/layout.md](references/layout.md). In
     `migrate` and `refresh`, map every section of the old content to its new home so that nothing is dropped. Show the
     planned tree with each move or rename, and wait for the user's go-ahead before the first move.
  3. **Write the documents** from [resources/doc.md.template](resources/doc.md.template) and, for a group overview,
     [resources/overview.md.template](resources/overview.md.template). Write only facts you checked against the code.
     Record what is missing or unclear in the gaps document instead of guessing.
  4. **Write `CLAUDE.md`** from [resources/CLAUDE.md.template](resources/CLAUDE.md.template). Keep only what every
     session needs; everything else goes into a document and gets a row in the routing table.
  5. **Write the memory** (unless `memory=off`) from [resources/MEMORY.md.template](resources/MEMORY.md.template), then
     import the per-machine memory when `import-memory=on`. Follow [references/memory.md](references/memory.md).
  6. **Re-point references.** Search the repository for every old document path (hooks, scripts, settings, CI,
     READMEs, the documents themselves) and update each one in the same change. A hook that maps code paths to
     documents must map to the new paths.
  7. **Validate** with [references/validation.md](references/validation.md) and fix what fails.
  8. **Report** the final tree, what moved, what the memory gained, and every gap you recorded instead of filling.

## What Stays In CLAUDE.md

`CLAUDE.md` is loaded into context on every request, so each line costs tokens on every turn. Keep it under 200 lines
and aim for about 100.

  * **Keep**: one paragraph on what the repository is, the commands a session runs most, a few lines of architecture,
    the rules that apply to every task, the routing table, and the memory import.
  * **Move to a document**: anything that matters only when a task touches one component, such as build order, schema
    or API details, test results, design history, or long command lists.
  * **Drop**: generic advice any competent engineer follows, text copied from a README, and the `/init` preamble
    ("This file provides guidance to Claude Code...").
  * **Format**: plain Markdown only. HTML wrappers, badges, and front matter reach the model as raw text, so leave them
    out. Wrap every literal `@` in backticks, because `@path` outside code imports that file.

## Resources

<div align = "center">

| File | Use It For |
| :---: | --- |
| [`resources/CLAUDE.md.template`](resources/CLAUDE.md.template) | The router at the repository root |
| [`resources/MEMORY.md.template`](resources/MEMORY.md.template) | The project memory file |
| [`resources/doc.md.template`](resources/doc.md.template) | One component document |
| [`resources/overview.md.template`](resources/overview.md.template) | The overview of a group directory |
| [`references/layout.md`](references/layout.md) | Drawing the tree, naming, sizing, the routing table, migrating old content |
| [`references/memory.md`](references/memory.md) | The project memory and the import from the per-machine memory |
| [`references/validation.md`](references/validation.md) | The checks that end every run |

</div>

Templates mark a placeholder as `{name}` and an optional block as `{{ OPTIONAL: <when> ... }}`. Replace every
placeholder, and either keep an optional block without its markers or delete it whole.

## What Not To Do

  * Do not pour the documents back into `CLAUDE.md`, and do not import them with `@`: an import loads on every request,
    the same as inline text.
  * Do not split so finely that a typical task needs three documents.
  * Do not invent facts, commands, or components to fill a template slot. Leave the slot out and record the gap.
  * Do not copy per-machine memory into the project without the user's confirmation, and never copy secrets or
    personal details.
  * Do not edit or delete the per-machine memory files.

## Quick Checklist

  - [ ] Did the user invoke the skill explicitly?
  - [ ] Did I read every file I changed, in full, before changing it?
  - [ ] Is `CLAUDE.md` under 200 lines, free of HTML and front matter, with one routing row per task area?
  - [ ] Does every routing row point to a document that exists, and is every document reachable from a row?
  - [ ] Does the docs tree mirror the code, with one document per component and directories only for groups?
  - [ ] Did a `migrate` or `refresh` keep every fact of the old content, or record why it was dropped?
  - [ ] Did the user approve each move, rename, and deletion before it happened?
  - [ ] Is the memory file written and imported from `CLAUDE.md`, or skipped because `memory=off`?
  - [ ] Did the user confirm every entry imported from the per-machine memory, with no secrets or personal details?
  - [ ] Were every hook, script, and setting that names a document path updated?
  - [ ] Did every check in [references/validation.md](references/validation.md) pass?

</div>
