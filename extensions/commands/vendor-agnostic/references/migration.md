<div align = "center">

# Migrating Content

</div>

<div align = "justify">

How to take an inventory, decide where each fact goes, and move it without losing one. Read it before the audit.

## Inventory

List what git tracks or would track (`git ls-files -co --exclude-standard`), the ignored files
(`git status --short --ignored`), and the submodules (`git submodule status`). From the lists, pick:

<div align = "center">

| Kind | Look For |
| :---: | --- |
| Instructions | `AGENTS.md`, `AGENTS.override.md`, `AGENT.md`, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/CLAUDE.md`, `GEMINI.md`, `QWEN.md`, `CONVENTIONS.md`, `.github/copilot-instructions.md`, `.github/instructions/`, `.cursorrules`, `.cursor/rules/`, `.windsurfrules`, `.windsurf/rules/`, `.clinerules`, `.roo/`, `.junie/`, `.kiro/`, `.continue/rules/`, `.amazonq/rules/`, `.goosehints`, `.rules`, `WARP.md` |
| Skills, agents, commands | `.claude/`, `.gemini/`, `.opencode/`, `.codex/`, `.cursor/`, `.github/skills`, `.github/agents`, `.github/prompts`, `.agents/`, `.agent/`, a root `SKILL.md`, and the same folders inside packages |
| Memory and notes | `.claude/MEMORY.md`, `.claude/docs/`, `.claude/rules/`, plans, notes, to-do files, prompt folders |
| Documentation | Every `README*` and `CONTRIBUTING*`, `docs/`, `doc/`, ADR folders, package READMEs |
| Machinery | Hooks, `settings.json`, `.mcp.json`, workflows, `CODEOWNERS`, ignore files, lint and format configuration, package manifests, scripts that name any of these paths |

</div>

Read every Markdown file of the inventory in full. In a large repository, take one top-level area at a time, or hand
each to a read-only subagent when the user allows subagents. Skip vendored code (`vendor/`, `node_modules/`), build
output, generated files, and submodules.

## The Migration Map

Show one row per section, not per file, whenever the sections of a file go to different places:

<div align = "center">

| Source | Destination | Action | Why |
| :---: | :---: | :---: | --- |
| `CLAUDE.md`, "Commands" | `AGENTS.md`, guardrails | Move | Every task needs them |
| `CLAUDE.md`, "Deploy" | `docs/ARCHITECTURE.md`, "Build And Deploy" | Merge | Also said in `README.md`, which disagrees on the target |
| `docs/architecture.md` | `docs/ARCHITECTURE.md` | Rename (`git mv`) | Name of the layout |
| `.claude/agents/keeper.md` | `.agents/agents/keeper.md` and a pointer | Split | Tool limit stays in the pointer |
| `notes/plan-2025.md` | none | Drop after approval | Superseded, and nothing in it is unique |

</div>

Below the table, list: the names and paths that will break and where they are used, the conflicts between sources with a
recommendation each, the files that stay and why, anything that looks like a secret (file and line only), and the files
that git ignores and that therefore stay untouched. Then wait.

## What Stays Where It Is

<div align = "center">

| File | Why |
| :---: | --- |
| Root `README.md` | GitHub, PyPI, npm, and container registries show it, and package manifests name it. It tells end users what the project is and links into `docs/`; technical detail moves out of it. |
| `LICENSE`, `NOTICE`, disclaimers, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CITATION.cff` | Legal and community files that other systems look up by name |
| `CHANGELOG.md`, `VERSION` | Release tooling reads them |
| `CONTRIBUTING.md` | GitHub links it from new issues and pull requests. Move its content to `docs/README.md` and leave a short pointer. |
| A README inside a package or an application | It documents that package where its readers are. Give it a routing row instead of moving it, and remove from it only what another page owns. |
| Settings, hooks, permissions, MCP configuration, vendor commands | Only their vendor can read them |
| `CLAUDE.local.md`, `*.local.*`, `.env*`, and everything git ignores | Personal or secret. Never read into a tracked file. |

</div>

## Where Content Goes

<div align = "center">

| Content | Destination |
| --- | :---: |
| A command or rule that every task needs, ten at most | `AGENTS.md`, guardrails |
| When to read a page | `AGENTS.md`, routing row |
| Purpose, domain terms, user flows, product rules | `docs/PRODUCT.md` |
| Design, tech stack, data flow, boundaries, build, deploy, CI, versioning | `docs/ARCHITECTURE.md` |
| Prerequisites, setup, environment variables, local commands, platform notes, the agent files | `docs/README.md` |
| Detail about one component | `docs/<component>.md`, in folders that mirror the code |
| A decision with its reason | `docs/decisions/XXXX-imperative-title.md` |
| A known gap, risk, open question, or wrong code comment | `docs/gaps-and-risks.md` |
| A task with its done criteria | `docs/tasks/<task>.md` |
| A repeatable workflow | `.agents/skills/<name>/SKILL.md` |
| A role with a mandate | `.agents/agents/<role>.md` |
| Anything only one vendor can use | That vendor's folder or entry point |
| Generic advice, restated code, a preamble, an outdated or repeated statement | Nowhere, with the reason in the map |

</div>

A page that would hold fewer than about 20 lines of prose is folded into the page above it. One past 200 lines is split
along its parts. `docs/gaps-and-risks.md` and `docs/tasks/` exist only when there is something to put in them. In a
public repository, and where `docs/` is published, a security weakness goes into the report and never into a page.

## Splitting An Always-Loaded File

Every line of the old `CLAUDE.md`, `GEMINI.md`, rules file, or prompt goes through this list, in order:

  1. Is it still true? Check the code. An outdated line is dropped, and the map says so.
  2. Does it apply to every task? It becomes a guardrail, unless ten already exist. Then the weakest one moves to a
     page.
  3. Does it apply when a certain path or topic is touched? It moves to the page of that topic, with a routing row.
  4. Can only one vendor use it? It stays with that vendor.

A rule with a `paths`, `globs`, or `applyTo` filter keeps its meaning as a routing row for the same paths.
`alwaysApply: true` makes a rule a candidate for a guardrail and nothing more.

## Skills, Commands, And Agents

  * **Skill**: move the whole folder with `git mv`. Keep the six standard frontmatter fields, and move every other key
    to the pointer. Rewrite tool names as actions, and vendor placeholders (`$ARGUMENTS`, shell-injection blocks) as
    prose: "the arguments the user gave".
  * **Skill inside a package**: it stays with its package, as `<package>/.agents/skills/<name>/`, with its pointer in
    `<package>/.claude/skills/<name>/` and a registry row that names the full path.
  * **Command**: one that any assistant could follow becomes a skill, and the command file is removed, because a skill
    shadows a command of the same name. One that needs a vendor feature stays where it is.
  * **Agent**: the body moves to `.agents/agents/<role>.md`. The tool list, model, and color move to the pointer, and
    the limits behind them are written out in **Boundaries**. Paths in the body that the migration renames are updated.
  * **Root `SKILL.md` used as an index**: its rows move to the registry, and the file goes, because skill installers
    read a root `SKILL.md` as a skill.

## Memory

A committed memory file of one vendor, such as `.claude/MEMORY.md`, stays and is imported from that vendor's entry
point. Facts in it that other tools need move out: preferences that hold for every task to the guardrails, decisions to
decision records, environment facts to `docs/README.md`. What remains is short, dated, and points at the pages. Never
copy the memory that a tool keeps outside the repository.

## Decisions

Decision records follow the `make-adr` skill, which owns them. The two templates in `resources/docs/decisions/` are
exact copies of its templates: change them there first, then copy them here. When `make-adr` is installed, its rules
govern every record this command writes or moves. What follows is the part a migration needs.

  * **Directory.** The decisions directory is the one `make-adr` recorded in the instruction files, or else the one
    that already holds records. Moving it into `docs/decisions/` is a row in the map like any other. When it moves,
    update the line or routing row that recorded it. When the user declines, the records stay where they are, the
    routing row in `AGENTS.md` names that directory, and the report explains the old-location warning of the check.
  * **Naming.** One file per decision, named `XXXX-imperative-title.md`: a four-digit sequence number, then the title
    in lowercase kebab-case, starting with its verb. "Use PostgreSQL for Sessions" becomes
    `0003-use-postgresql-for-sessions.md`, and `ADR Title` and the `#` heading read `Use PostgreSQL for Sessions`.
  * **Numbers.** A record that already carries a number keeps it. Decisions without one take the next free numbers in
    the order they were accepted, oldest first. A record is never deleted. A missing one is a question for the user,
    and the default is to renumber the records after the gap and update every link to them, as `make-adr` does.
  * **Content.** Write only what the old text states. A required section it says nothing about reads `Not assessed`,
    and an optional section it says nothing about is left out. A decision in force is `ACCEPTED`.
  * **Dates.** `Created On` holds the date the decision was accepted and its author. When the text has neither, take
    both from the commit that first stated it, `git log --follow --diff-filter=A --format="%as (%an)" -- <file>`.
    `git log -S "<phrase>"` finds a sentence that moved between files.
  * **Origin.** The last line of the summary names the file the record came from, its old name when it was renamed
    (commits, code comments, and issues still use it), and the file whose history gave the date. Update every
    reference inside the repository.
  * **Additions.** A decision that only adds to an existing record, and leaves everything it decided true, goes into
    that record: a dated entry under **ADR Additional Changes**, and `(added YYYY-MM-DD)` after each line it adds to
    another section.
  * **Replacements.** A decision that reverses or replaces part of a record gets a record of its own. The old record
    is superseded as a whole: it keeps its text, and only its status, its links, and its remark change.
  * **Renames.** A record named another way, such as `YYYY-MM-DD-<slug>.md`, two records that share a number, and a
    record in another layout are renamed or rewritten only when the user approves it in the map.
  * **Index.** The `README.md` of the directory, from its template: one row per record with its number, its slug
    linked to the file, its status flag, and its tags, and a row in the replacement table for each superseded record.

## Conflicts

When two sources disagree about what exists, the code decides. When they disagree about a rule, the decision with the
later date wins (its `Created On`, or the date of the addition that states it), whatever its number, and an undated
conflict is a question for the user. Never merge two versions into a third, and never settle a conflict silently.
While the question is open, it stands in `docs/gaps-and-risks.md`.

## Names And Case

  * Rename with `git mv`, also when only the case changes (`architecture.md` to `ARCHITECTURE.md`). On Windows and macOS
    a plain rename is invisible to git, so Linux and CI keep the old name and every new link breaks there.
  * Quote every path. Repository paths hold spaces, brackets, and parentheses.
  * Keep the line endings that `.gitattributes` asks for, and add no byte order mark.

## Re-Pointing

Search the whole repository for every old path, its file name, its folder, and strings that build it in code. Update
each hit in the same change: hooks, scripts, settings, workflows, `CODEOWNERS`, ignore files, lint and format
configuration, manifests, READMEs, and the bodies of skills and agents. Four are missed most often:

  1. **A hook that ignores `.claude/`** now sees every change under `.agents/`. Add the new folder to its list.
  2. **Path filters in workflows** (`paths`, `paths-ignore`) and `CODEOWNERS` patterns still name the old folders.
  3. **A documentation hook that maps code to pages** maps to pages that moved. Run it once after the change.
  4. **Package contents**. Check that `AGENTS.md`, `.agents/`, and `docs/` do not enter a published package by accident
     (`npm pack --dry-run`, the file list of a source distribution, `.dockerignore`).

## Deleting

  * Delete only tracked files, with `git rm`, after the last fact is placed and the user approved the row. Git history
    is the archive.
  * A unique but obsolete document the user wants to keep readable goes to `docs/archive/`, which no routing row names.
  * Never delete an untracked or ignored file. List it in the report.

</div>
