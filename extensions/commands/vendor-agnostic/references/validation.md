<div align = "center">

# Validation

</div>

<div align = "justify">

Run every check below at the end of each mode. Report the output of the script as it is, and each item you could not
check or fix. A check that did not run is not a pass.

## The Script

[`scripts/check.sh`](../scripts/check.sh) is read-only and needs only git. Run it from inside the repository, with the
vendors this run had to create (`all` without a vendor argument):

```shell
$ sh "<command folder>/scripts/check.sh" all
```

In PowerShell, let git start the shell it ships with:

```shell
$ git -c "alias.va=!sh '<command folder>/scripts/check.sh'" va all
```

Every `FAIL` is fixed. Every `WARN` is fixed, or explained in the report with the reason it stays. The script covers:

<div align = "center">

| Area | Proves |
| :---: | --- |
| `AGENTS.md` | Not empty, under 24,000 bytes, carries the "DO NOT read" sentence, at most ten guardrails, no `@` import, no frontmatter, every route resolves |
| Entry points | Under 15 lines, hand over to `AGENTS.md` in the form their vendor loads, nothing loaded twice |
| Skills and agents | Standard frontmatter, names that match, a registry row, no stray `.md` file that a tool would load |
| Vendor folders | Every pointer exists and matches its shared file; a link is stored, checked out, and resolved correctly, and no junction sits over it |
| Pages | Relative links resolve with the exact case, every page is reachable, records are dated, no paragraph stands in two files |
| Repository | Nothing of the layout is ignored by git, no template text is left, no old location remains, no two paths differ only in case |

</div>

## Nothing Was Lost

  - [ ] Each section and bullet of every file that was changed, moved, or deleted has its new place, or its reason for
    being dropped, in the migration map. For a deleted file, read it again with `git show HEAD:<file>` and tick it off
    line by line.
  - [ ] No fact was added that neither the old files nor the code contain.
  - [ ] Numbers, versions, names, dates, and commands read the same as before, unless the map says otherwise.
  - [ ] Every restriction an agent had (tools, paths, read-only) still stands somewhere its vendor enforces it.

## The Text Is True

  - [ ] Every command in `AGENTS.md` and `docs/README.md` runs, or its program, script, and flags exist.
  - [ ] Every path, anchor, and file name in the pages exists with the same spelling and case.
  - [ ] Each entry point holds only its import or directive, and notes that no other vendor could use.
  - [ ] The guardrails are the ones every task needs. Detail sits in pages.

## Machinery Still Works

  - [ ] Hooks and scripts that name a moved path were run once, or their tests were, and print no error.
  - [ ] The build, lint, and test commands of the repository give the same result as before the change.
  - [ ] Workflow path filters, `CODEOWNERS`, and ignore files name the new paths.
  - [ ] No search for an old path finds a hit outside `CHANGELOG.md`, decision records, and git history.

## What A New Session Sees

Ask the user to start a new session, because most tools load these files only at the start, and to look at:

<div align = "center">

| Tool | Where To Look | Expect |
| :---: | --- | --- |
| Claude Code | `/context` and `/agents`, and `/` for the skills | `AGENTS.md` listed as a memory file, every shared skill and agent |
| Gemini CLI | `/memory show`, `/skills list` | The text of `AGENTS.md`, every shared skill |
| OpenAI Codex | "List the instruction sources you loaded" | `AGENTS.md` once |
| Copilot CLI | `/instructions` | `AGENTS.md` and the entry point |
| Any other tool | Ask which project instructions it has, and which file it would read for a task from the routing table | The rules of `AGENTS.md`, and one page |

</div>

A tool that answers without the rules of `AGENTS.md` is wired wrongly, whatever the script says.

</div>
