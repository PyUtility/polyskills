<div align = "center">

# Project Memory

</div>

<div align = "justify">

Claude Code keeps two kinds of memory. This skill writes the project memory and reads the other one.

<div align = "center">

| Memory | Where | Shared | Loaded |
| :---: | :---: | :---: | --- |
| Project memory (this skill) | The `memory=` path, default `.claude/MEMORY.md`, in git | With every clone | Every session, through the `@` import in `CLAUDE.md` |
| Auto memory (Claude Code) | `~/.claude/projects/<slug>/memory/`, on one machine | No | By Claude Code, through its own `MEMORY.md` index |

</div>

## Settings

  * `memory=<file>` (default `.claude/MEMORY.md`): the file is created when it is missing, and the last section of
    `CLAUDE.md` imports it as `@<file>`, a path relative to `CLAUDE.md`.
  * `memory=off`: no file and no import. Remove an existing import line only after the user confirms, and leave the
    file itself in place unless they ask to delete it.
  * `import-memory=on` (default): once the file exists, fold in the auto memory of this repository.

## What Belongs In It

The file loads on every request, so it holds only short, durable facts that steer behavior. Aim for about 60 lines.

<div align = "center">

| Section | Holds |
| :---: | --- |
| Owner Preferences | How the owner wants work done: corrections and confirmed approaches, each with its reason |
| Environment | Machine and tool facts that commands depend on, written so that they hold on every machine |
| Decisions And Changes | Dated one-line decisions, newest first, each pointing at the document with the detail |
| Open Items | What is pending or known to be missing, pointing at the gaps document |

</div>

Keep these out of it:

  * Facts about the code. They belong in a document, next to their component.
  * Generated output such as sync logs, test results, or change lists. Write those to a file that is not imported.
  * Secrets, credentials, tokens, and personal details. The file is committed.
  * Paths that exist on one machine only, such as a home directory with a user name in it. Write `$HOME/...`, a
    variable, or every known location.
  * HTML wrappers and front matter. The import loads the file as raw text, so it follows the same plain format as
    `CLAUDE.md`.

## Importing The Auto Memory

Use this when a repository already has a history with Claude Code but never used this skill, and again on later
`refresh` runs to pick up what Claude Code saved in the meantime.

  1. **Find the directory.** Take the absolute path of the repository root and replace every character that is not a
     letter or a digit with `-`; on Windows `C:\work\my app` becomes `C--work-my-app`. Look for `<slug>/memory/` under
     `$CLAUDE_CONFIG_DIR/projects/` when that variable is set, then under `~/.claude/projects/`, and compare names
     without regard to case, since the case of a drive letter varies. When the session's system prompt names a memory
     directory, use that one. If nothing matches, or the directory is empty, say so and go on without an import.
  2. **Read everything.** Read the index `MEMORY.md`, every file it lists, and any other `*.md` file in the directory.
     Topic files usually open with front matter holding `name`, `description`, and a `type`.
  3. **Sort each entry** with the table below.
  4. **Filter.** Drop entries the project memory or a document already states, entries the code or git history
     already records, and entries that are no longer true: check that every file, function, flag, or command an entry
     names still exists. Never copy a secret.
  5. **Confirm.** Show the user each entry you plan to add, one line each with its target section, and write only
     after they agree. Keep the owner's wording where it is clear, and convert relative dates to absolute ones.
  6. **Leave the source alone.** Do not edit or delete the auto memory files. Tell the user which entries now live in
     the project, so that they can prune the per-machine copy if they want to.

<div align = "center">

| Auto Memory Type | Goes To | Note |
| :---: | :---: | --- |
| `feedback` | Owner Preferences | Keep the reason in a few words |
| `project` | Decisions And Changes, or Open Items | Dated, newest first |
| `reference` | The document of the component it concerns, or Environment | Links to dashboards, tickets, or outside documentation |
| `user` | Nowhere by default | Personal: copy only what the owner explicitly approves |
| No type | Judged by its content | The same rules apply |

</div>

## Merging Into An Existing Memory File

  * Add each entry to its matching section, and do not reorder or reword entries that are still true.
  * When an imported entry contradicts an existing one, keep the newer fact only if the code confirms it, and ask the
    user when it does not.
  * When the file grows past about 100 lines, move detail into documents and leave a one-line pointer behind.

</div>
