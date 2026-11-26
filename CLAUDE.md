# LLM Essentials (polyskills)

This repository ships two things together. `extensions/` is a library of Agent Skills, agents, commands, and hooks
for coding assistants, published as the `llm-essentials` plugin for Claude Code and Codex. `polyskills/` is a Python
3.12+ CLI, released to PyPI, that fetches one extension from a git remote into a local directory and records the
fetch. Every Markdown file follows the `markdown-format` skill, and every commit follows the `git-commiter` skill.

## Commands

```shell
# install the package in editable mode
$ python -m pip install -e .

# run every package test from the repository root; the network is mocked
$ python -m unittest discover -v -s polyskills/tests -t .

# run one module, one class, or one test
$ python -m unittest polyskills.tests.test_database
$ python -m unittest polyskills.tests.test_database.TestDatabasePaths
$ python -m unittest polyskills.tests.test_database.TestDatabasePaths.test_environment_override_is_honoured

# lint as CI does: the first pass fails the build, the second only reports
$ python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
$ python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# security scan as CI does
$ bandit -r polyskills/ -x polyskills/tests
$ pip-audit
```

Live tests against the GitHub API are opt-in, and the hook in `extensions/hooks/` has its own suite: see `testing.md`.

## Architecture

  * **Extension library** (`extensions/`): skills (`skills/<name>/SKILL.md`), the Python and SQL agent suites
    (`agents/python/`, `agents/sql/`), commands that only the user starts (`commands/<name>/SKILL.md`), and hooks
    (`hooks/<Tool> (<Kind>)/`). Markdown, templates, and a few scripts; there is no build step.
  * **Distribution**: `.claude-plugin/marketplace.json` serves the plugin in `extensions/` to Claude Code, and
    `.agents/plugins/marketplace.json` serves it to Codex, whose entry point is `AGENTS.md`. The CLI installs a single
    extension from any GitHub repository.
  * **CLI** (`polyskills/cli.py`, console script `polyskills`): the subcommands `tools`, `sources`, `list`, `manager`,
    and `records`. `get()` and `listExtensions()` in the same file are the public Python API.
  * **Remote sources** (`polyskills/remote/sources.py`): `SourceManager` and its only provider, `GithubManager`, which
    downloads the repository tarball and extracts one extension folder behind size, page, and path-traversal limits.
  * **Tracking database** (`polyskills/database/`): SQLAlchemy models in SQLite at `~/.polyskills/records.db`. Every
    write is best-effort and never fails a fetch.

## Rules

  1. Markdown follows the `markdown-format` skill and its prose the `humanize-text` skill. `CLAUDE.md` and
     `.claude/MEMORY.md` stay plain Markdown, because they load as raw text.
  2. Python follows the `python-code-format` skill; `.flake8` holds the house settings.
  3. Adding, renaming, or removing an extension updates its registrations: see `extensions/extensions.md`.
  4. Commit messages follow `git-commiter`. Never commit or push unasked.
  5. Durable owner preferences and project decisions go into `.claude/MEMORY.md`, which ships with the repository,
     instead of the per-machine memory.
  6. Do not invent what is missing: record it in `gaps.md` and ask before acting.
  7. Update the documents a change affects as the last step of the change.

## Read Only What The Task Needs

The documents live under `.claude/docs/`. Read the row that matches the task, never the whole directory.

| Task Touches | Read |
| :---: | --- |
| `polyskills/` (the CLI, the remote fetch, the tracking database) | `polyskills.md` |
| `polyskills/tests/`, `.github/workflows/`, running tests or lint | `testing.md` |
| `extensions/skills/<name>/` | `extensions/extensions.md`, then `extensions/skills.md` |
| `extensions/agents/` | `extensions/extensions.md`, then `extensions/agents.md` |
| `extensions/commands/` | `extensions/extensions.md`, then `extensions/commands.md` |
| `extensions/hooks/` | `extensions/extensions.md`, then `extensions/hooks.md` |
| Versions, `CHANGELOG.md`, plugin manifests, a PyPI release | `release.md` |
| Known gaps, open questions | `gaps.md` |

## Memory

@.claude/MEMORY.md
