---
name: git-commiter
description: >-
  Governs every git commit message produced in this repository. Always invoked. Every commit subject **must** start with one or
  more emoji glyphs (e.g. `✨`, `🐛`, `🛠️`, `💣`, `📝`, `🧪`, `🤖`, `📜`, `⭐️`, `🚧`, `💡`) followed by an optional
  Conventional Commit type/scope and a concise imperative summary. Use this skill whenever the user asks to "create a commit",
  "commit the changes", "stage and commit", "write a commit message", "amend the commit", or any other request that produces a
  git commit. The skill encodes the exact emoji vocabulary, subject grammar, body structure (`Why` / `What` / `Style` /
  `Verification`), per-file commit policy, and the mandatory `Co-authored-by: Copilot` trailer observed across the project's
  history.
always_load: true
---

<div align = "center">

# Git Commiter

</div>

<div align = "justify">

This skill governs **every** git commit produced in this repository. The project enforces an emoji-prefixed subject line on
all commits, a structured commit body, and a per-file commit policy when several unrelated files change together. Read the
**entire** skill before staging or committing, even for a single-line change. Never invent emoji or commit grammar that is
not documented here.

## Getting Started

  1. Run `git status --short` to enumerate the working-tree changes - never commit blindly.
  2. Run `git diff --stat` (and `git diff <file>` for each file) to understand what actually changed.
  3. Decide the **commit topology**: one focused commit, or one commit per logically independent file.
  4. Pick the correct **emoji + Conventional Commit type** for each commit (see the vocabulary table below).
  5. Write the message to a temp file under `.git/` and commit with `git commit -F <file>` to avoid shell-quoting issues.
  6. Always append the mandatory `Co-authored-by: Copilot` trailer unless the user **explicitly** opts out.

Never skip reading this skill, even for a one-line change.

</div>

## Subject Line Grammar

<div align = "justify">

The commit subject is a **single line ≤ 72 characters** built from three parts in this exact order:

```
<emoji>[<emoji>...] <type>(<scope>): <imperative summary>
```

  * **`<emoji>`** *(mandatory)* - one or more glyphs from the vocabulary table. Multiple glyphs are concatenated with no
    separator (e.g. `✨🤖`, `🛠️🚧`, `🐛🛠️`).
  * **`<type>(<scope>)`** *(recommended)* - Conventional Commit type (`feat`, `fix`, `refactor`, `docs`, `test`, `chore`,
    `ci`, `build`, `perf`, `style`) and an optional parenthesised scope (`tests`, `agents`, `skills`, `cli`, `remote`).
  * **`<imperative summary>`** *(mandatory)* - lowercase, imperative mood ("add", "fix", "remove" - not "added", "fixes").
    No trailing period.

Subject must be on **line 1**, followed by **one blank line**, followed by the optional body. Never put the body on line 2.

</div>

## Emoji Vocabulary

<div align = "justify">

Use **only** the glyphs in this table. They mirror the existing repository history and must not be substituted with similar
Unicode lookalikes.

</div>

| Emoji | Meaning | Use When | Conventional Type |
| :---: | :--- | :--- | :---: |
| ✨ | New feature / capability added | Introducing a new module, class, public API, skill, agent, badge | `feat` |
| 🐛 | Bug fix | Fixing incorrect behaviour reproducible by a test or report | `fix` |
| 🛠️ | Refactor / non-bug technical fix | Renames, signature tweaks, internal cleanups, parameter additions | `refactor` |
| 💣 | Breaking refactor / removal | Deleting code, breaking API changes, extracting/promoting helpers | `refactor` |
| 📝 | Documentation change | README/SKILL/AGENT/CHANGELOG updates, docstring-only patches | `docs` |
| 📜 | Long-form documentation note | Adding a new README, design notes, or extensive prose | `docs` |
| 🧪 | Test addition or change | New unittest cases, fixtures, CI matrix updates that ship tests | `test` |
| 🤖 | CI / automation / workflow | `.github/workflows/*.yml`, `.flake8`, lint/build/release config | `ci` / `build` |
| ⭐️ | Badge or visual marker added | Skills README badge, README highlights | `docs` |
| 🚧 | Work-in-progress marker | Pair with another emoji to signal a placeholder or incomplete work | any |
| 💡 | Idea / proposal / new skill body | New skill content (commonly paired with ✨) | `feat` |

<div align = "justify">

Pair emoji freely when both apply: `✨🤖` (new agent file is an automation asset), `🐛🛠️` (a bugfix that is also a refactor),
`✨🚧` (new but incomplete scaffold), `💣🚧` (refactor still in flight). Always put the **primary** intent emoji first.

</div>

## Commit Body Template

<div align = "justify">

Whenever the diff is more than a trivial typo, write a structured body using the four-section template below. Each section
heading is followed by an underline of three dashes (matches existing project history). Keep lines wrapped to ~72 columns.

</div>

```
<emoji> <type>(<scope>): <imperative summary>

Why
---
One short paragraph stating the motivation. What was missing, broken,
or sub-optimal that justified this change.

What
----
- Bulleted list of the concrete changes.
- One bullet per file or per logical unit.
- Reference symbols / line numbers when useful (`_extract()`, `base.py`).

Style
-----
Note any project-style conventions applied (PEP-8, name : type spacing,
reST docstrings, markdown-format rules, single-underscore helpers).
Write "No formatting changes." if none.

Verification
------------
The exact command used to verify the change and its result, e.g.
`python -m unittest discover -v -s polyskills/tests -t .` -> 18 tests, OK.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Per-File Commit Policy

<div align = "justify">

When the working tree contains **multiple unrelated changes**, split them into separate commits - one per logically
independent file or feature. Stage explicitly with `git add <file>`; never use `git add -A` or `git add .` for a multi-file
change. The reviewer must be able to revert any one commit without collateral damage.

Group changes into a single commit only when they form **one atomic unit** (e.g. a test file plus the fixture it depends on,
or a feature plus the docs that describe it).

</div>

## Working-Tree Analysis Workflow

<div align = "justify">

Before writing any commit message, follow this exact sequence:

</div>

  1. **Inspect status** - `git status --short` to list `M`, `A`, `D`, `??` entries. If empty, stop and report
     "nothing to commit".
  2. **Inspect diffs** - `git diff` for unstaged, `git diff --staged` for staged, `git diff --stat` for a summary.
  3. **Classify each change** - assign a Conventional Commit type and an emoji from the table.
  4. **Choose topology** - one commit or several? Use the per-file policy above.
  5. **Draft messages** - subject + structured body for each commit.
  6. **Verify** - run the project's tests / linters before committing if the change touches code.
  7. **Commit** - via `git commit -F .git/COMMIT_MSG_<n>.txt`, then delete the temp file.
  8. **Confirm** - `git log --oneline -5` to verify the new commit(s) landed correctly.

## Commit Execution Recipe

<div align = "justify">

Because Windows shells (PowerShell, cmd) mangle multi-line strings and emoji glyphs, **always** write the commit message to
a temporary file under `.git/` and pass it via `-F`. Never use `git commit -m "..."` for non-trivial messages.

</div>

```python
# canonical Python recipe used throughout this repository
import os, subprocess

repo = "<absolute-path-to-repo>"
msg_path = os.path.join(repo, ".git", "COMMIT_MSG.txt")

with open(msg_path, "w", encoding = "utf-8") as f:
    f.write("""✨ feat(scope): one-line imperative summary

Why
---
...

What
----
- ...

Style
-----
...

Verification
------------
...

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
""")

subprocess.run(["git", "add", "<file-1>", "<file-2>"], cwd = repo, check = True)
subprocess.run(["git", "commit", "-F", msg_path], cwd = repo, check = True)
os.remove(msg_path)
```

## Reference Examples

<div align = "justify">

The project's existing history is the canonical reference. The commits below are exemplary - copy their shape, never their
content verbatim.

</div>

```text
🧪 test(tests): add cross-platform skill installation tests
💣 refactor(tests): promote _extract() to base + add USER_SKILL_ROOT/SKILL_FILENAME
📝 docs(skills): add markdown-format badge to skills README
✨💡 feat(skills): add markdown-format skill
✨🤖 feat(agents): add python-code-reviewer agent
🤖 added .github/workflows/publish.yml create PyPI release
🐛 bugfix: format string requires pagination; updated docstring
✨🚧 initialize polyskills/error/... and polyskills/extensions/... module
```

## Pre-Commit Hooks

<div align = "justify">

The repository ships a pre-commit hook that may **rewrite the commit SHA** and **prepend additional emoji** to the subject
(e.g. transforming `feat(...)` into `✨🤖 feat(...)`). This is expected. Always inspect the final subject with
`git log --oneline -1` after committing to confirm the result, and never re-amend solely to "fix" hook-injected emoji.

</div>

## Hard Don'ts

<div align = "justify">

  * Never commit without an emoji prefix - this is **mandatory** in every commit on every branch.
  * Never use `git add -A` / `git add .` when several unrelated files are dirty.
  * Never use `git commit -m` for a multi-line / structured body on Windows.
  * Never paste emoji from a thesaurus - use **only** the glyphs in the vocabulary table.
  * Never omit the `Co-authored-by: Copilot` trailer unless the user explicitly says "no co-author".
  * Never write past-tense or third-person subjects ("added", "fixes") - always imperative ("add", "fix").
  * Never include a trailing period on the subject line.
  * Never exceed 72 characters on the subject; wrap body at ~72.

</div>

## Quick Checklist

<div align = "justify">

Before invoking `git commit`, tick every box:

</div>

  * [ ] `git status --short` was inspected.
  * [ ] `git diff` (or `--staged`) was reviewed file-by-file.
  * [ ] Subject starts with one or more emoji from the vocabulary table.
  * [ ] Subject uses lowercase imperative mood, no trailing period, ≤ 72 chars.
  * [ ] Conventional Commit `type(scope)` is correct for the change.
  * [ ] Body uses `Why` / `What` / `Style` / `Verification` sections (for non-trivial diffs).
  * [ ] `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer is present.
  * [ ] Multi-file commits respect the per-file policy.
  * [ ] Tests / linters were run when the change touches code.
  * [ ] Commit was created via `git commit -F <tempfile>`, not `-m`.
  * [ ] `git log --oneline -1` was inspected after committing.
