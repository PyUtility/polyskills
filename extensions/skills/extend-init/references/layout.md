<div align = "center">

# Layout Of The Documents Tree

</div>

<div align = "justify">

How to decide what becomes a document, where it lives, what it holds, and how `CLAUDE.md` routes to it. Every path
below is relative to the docs root (`docs=`, default `.claude/docs/`).

## Principles

  1. **Route, do not load.** `CLAUDE.md` names the document for a task, and Claude reads it only when the task needs it.
  2. **One component, one document.** A component is a part of the code that a task usually changes on its own: a
     package, a service, an app, a module with its own entry point, a database schema, a pipeline stage, an
     infrastructure stack.
  3. **Mirror the code.** Group directories follow the code's own directories and file names follow the component
     names, so a code path points straight at its document.
  4. **One hop.** A task needs the router plus one document. Two is the ceiling: an overview and a member, or a member
     and a cross-cutting guide.

## Finding The Components

Walk the repository from the top and treat a directory as a component when one of these holds:

  * It has its own manifest, entry point, or build target (`pyproject.toml`, `package.json`, `go.mod`, a
    `Dockerfile`, a `main` module, an initialization script).
  * It has its own README, owner, version, or changelog.
  * Tasks change it without touching its siblings, and a reader needs context the code alone does not give.

Leave out vendored code, generated files, build output, and directories that only hold data.

## Drawing The Tree

<div align = "center">

| Situation | Layout |
| :---: | --- |
| A component that stands alone | `<component>.md` at the level of its parent group, or at the root |
| Two or more components under one code directory | A directory `<group>/` with one `<member>.md` each |
| Members that share conventions, a run recipe, or a contract | Add the overview `<group>/<group>.md` |
| A member too large for one document | Turn it into `<group>/<member>/` with its own members |
| A topic that spans the code: testing, the Claude Code setup, known gaps, a glossary | `<topic>.md` at the root |

</div>

  * Keep the tree at most three directories deep below the root.
  * A directory with one document is noise. Flatten it to a single file unless more members are planned.
  * Name files in lower-case kebab-case after the component or its code directory, without a numeric prefix. Avoid
    catch-all names such as `notes.md`, `misc.md`, or `other.md`.
  * When the code uses a naming quirk (a host name as a folder, brackets, spaces), name the document after the
    component and give the exact code path inside it.

## Sizing

<div align = "center">

| File | Target | Act When |
| :---: | :---: | --- |
| `CLAUDE.md` | About 100 lines | Over 200 lines: move detail into documents |
| Memory file | About 60 lines | Over 100 lines: move detail into documents and drop resolved items |
| Document | 40 to 150 lines | Over 200 lines: split along its parts. Under 20 lines of prose: fold it into its overview or parent |
| Overview | Under 60 lines | Holds only what the members share, never a copy of a member |

</div>

## What A Document Holds

Write what a reader cannot get quickly from the code, and point at the code for the rest:

  * Its purpose and when to read it ("read this before changing ...").
  * The invariants and contracts other parts depend on, and the order in which things run or build.
  * The commands that apply only to this component.
  * Pitfalls, limits, and decisions, each with its reason and, where known, its date.
  * Links to related documents by their path from the docs root, for example `see <group>/<member>.md`. Never copy
    another document's content.

Leave out restated code, full API listings, and anything a quick read of the source gives. A generated inventory (a
list of files or objects that a script keeps current) may close a document, between markers the script owns.

## The Routing Table

The table in `CLAUDE.md` has two columns: what the task touches, and the document to read.

  * Paths in the `Read` column are relative to the docs root, and the sentence above the table names the root once.
  * Write one row per task area. When sibling documents mirror sibling code directories, a single pattern row covers
    them: `<code-dir>/<name>/` routes to `<group>/<name>.md`, followed by the list of names.
  * A row may name an overview and a member together: `<group>/<group>.md`, then `<group>/<member>.md`.
  * Every row points at a file that exists, and every document is reachable from a row, directly, through a pattern,
    or through its overview.
  * Order rows from the most common task to the least common, with the cross-cutting topics last.

## Migrating Existing Content

  1. List every section and bullet of the old `CLAUDE.md` and of any old documents.
  2. Give each item a destination: it stays in `CLAUDE.md`, moves to a named document, merges into the memory, or is
     dropped with a reason (outdated, duplicated, generic).
  3. Check the list once more after writing: every item is placed or deliberately dropped.
  4. Keep the owner's wording where it is accurate. Rewrite only what is wrong, stale, or in the wrong place.

</div>
