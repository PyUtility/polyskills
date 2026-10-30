<div align = "center">

# Validation

</div>

<div align = "justify">

Run every check below at the end of each mode. In `refresh` mode the checks are the main work: run them first, fix what
fails, then run them again. Report each failure you could not fix, with the file and line.

## Structure

  - [ ] `CLAUDE.md` is under 200 lines, has one H1 heading, and holds no HTML, badges, or front matter.
  - [ ] The memory file (unless `memory=off`) is plain Markdown of about 60 lines, imported once from `CLAUDE.md`.
  - [ ] Every path in the routing table resolves to a file under the docs root.
  - [ ] Every document under the docs root is reachable from a routing row, a pattern row, or its overview.
  - [ ] The tree is at most three directories deep, no directory holds a single document, and no file has a catch-all
    name.
  - [ ] No document runs past 200 lines, and no paragraph appears in more than one file.

## Truth

  - [ ] Every command in `CLAUDE.md` and the documents runs as written, or at least its program, script, subcommands,
    and flags exist (read the script's argument parser or its `--help`).
  - [ ] Every file and directory a document names exists, with the same spelling and case.
  - [ ] Versions, tags, names, and counts agree across `CLAUDE.md`, the memory file, the documents, and the manifests.
  - [ ] No machine-specific path (a home directory with a user name, a drive only one machine has) appears where
    `$HOME`, a variable, or a relative path would work.
  - [ ] Each document still matches its code. Start with the code that changed after the document did, for example
    `git log --since=<date the document last changed> -- <code path>`. In a large repository, give each group to a
    read-only subagent and ask for inaccuracies with file and line evidence.
  - [ ] Every gap the documents list is still open. Remove the ones the code has resolved.

## References

  - [ ] No file in the repository names a document path that no longer exists. Search hooks, scripts, settings, CI
    workflows, READMEs, and the documents for the old file names, the docs root, and bare document names.
  - [ ] A hook or script that maps code to documents maps every code path to a document that exists, and its tests or
    a dry run pass.

## Format

  - [ ] Each written file follows the installed Markdown format skill, if there is one.
  - [ ] The prose follows the installed prose skill, if there is one.
  - [ ] Every literal `@` in `CLAUDE.md` outside the memory import sits inside backticks.

</div>
