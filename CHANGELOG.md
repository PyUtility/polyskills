<h1 align = "center">CHANGELOG</h1>

<div align = "justify">

All notable changes to this project will be documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [PEP0440](https://peps.python.org/pep-0440/)
styling guide. For full details, see the [commit logs](https://github.com/PyUtility/autoholidays/commits).

## `PEP0440` Styling Guide

<details>
<summary>Click to open <code>PEP0440</code> Styilng Guide</summary>

Packaging for `PyPI` follows the standard PEP0440 styling guide and is implemented by the **`packaging.version.Version`** class. The other
popular versioning scheme is [`semver`](https://semver.org/), but each build has different parts/mapping.
The following table gives a mapping between these two versioning schemes:

<div align = "center">

| `PyPI` Version | `semver` Version |
| :---: | :---: |
| `epoch` | n/a |
| `major` | `major` |
| `minor` | `minor` |
| `micro` | `patch` |
| `pre` | `prerelease` |
| `dev` | `build` |
| `post` | n/a |

</div>

One can use the **`packaging`** version to convert between PyPI to semver and vice-versa. For more information, check
this [link](https://python-semver.readthedocs.io/en/latest/advanced/convert-pypi-to-semver.html).

</details>

## Release Note(s)

The release notes are documented, the list of changes to each different release are documented. The `major.minor` patch are indicated
under `h3` tags, while the `micro` and "version identifiers" are listed under `h4` and subsequent headlines.

<details>
<summary>Click to open <code>Legend Guidelines</code> for the Project CHANGELOG.md File</summary>

  * 🎉 - **Major Feature** : something big that was not available before.
  * ✨ - **Feature Enhancement** : a miscellaneous minor improvement of an existing feature.
  * 🛠️ - **Patch/Fix** : something that previously didn’t work as documented – or according to reasonable expectations – should now work.
  * ⚙️ - **Code Efficiency** : an existing feature now may not require as much computation or memory.
  * 💣 - **Code Refactoring** : a breakable change often associated with `major` version bump.

</details>

### PolySkills v2.0.0 | 2026-06-07

The `v2.0.0` line redesigns `polyskills` from a "skills-only fetcher" into a portable, multi-library
extension manager for LLM tools. A single source of truth (a remote repository) can now host
**skills**, **agents**, **commands**, and **hooks**, fetched into any project or system through a
hermetic, network-aware CLI. The implementation is layered (`polyskills.cli` → `polyskills.remote`
→ provider managers) so additional remote providers (GitLab, Bitbucket, self-hosted Git, etc.)
can be registered via the `_SOURCE_MANAGERS` registry without touching the dispatcher.

> [!CAUTION]
> **Breaking Release.** `v2.0.0` is a complete rewrite of `polyskills` and is **not** wire-compatible
> with `v1.x`. The legacy `polyskills <remote> --get-skills / --update <name> --directory ...` flag
> surface has been **removed** in favour of a structured sub-command CLI (`polyskills {sources, tools,
> list, manager} ...`). The `git tag skillName@vX.Y.Z` discovery convention from `v1.x` is also gone:
> extensions are now resolved as directories under a configurable `--source` (e.g. `./skills`,
> `./agents`) and pinned with `--version` (a tag, branch, or commit SHA). Old scripts must be
> rewritten — see the migration table at the end of this section.

#### 💣 Breaking Changes

  * **CLI surface rewritten.** The flat `polyskills <remote> --get-skills | --update <name>
    --directory ...` interface from `v1.0.0` has been removed. The new CLI is structured into
    sub-commands: `polyskills sources`, `polyskills tools`, `polyskills list <remote> <LIBRARY>`,
    and `polyskills manager <remote> --name <name> [--destination ...] <LIBRARY>`.
  * **Discovery model replaced.** Extensions are no longer discovered via `git tag
    skillName@vX.Y.Z`; they are directories under a `--source` path on the remote, pinned by a
    git ref via `--version` (default `master`). This removes the requirement that maintainers
    cut a tag per skill release.
  * **Default destination contract.** The legacy `--directory ".skills/"` flag is replaced by
    `-d / --destination`, which now defaults to `./<library>/<name>` (e.g.
    `./skills/sql-code-format`) instead of `.skills/`. The legacy default is **not** preserved.
  * **Tri-state collision policy.** A new `--exists {fail, overwrite, merge}` flag replaces the
    implicit overwrite behaviour of `v1.x`; the default is now `fail`, so silent clobbering is
    no longer possible. Existing automation that relied on the old overwrite-on-update behaviour
    must pass `--exists overwrite` explicitly.
  * **Authentication via env var.** `--token` is accepted on the CLI but is **always** overridden
    by the `POLYSKILLS_REMOTE_TOKEN` environment variable when set. `v1.x` had no environment
    fallback. Production callers should switch to the env var to keep tokens out of shell history.
  * **Python baseline raised.** Minimum supported interpreter is now **Python 3.12** (was 3.9 on
    `v1.x`). CPython 3.12.0–3.12.4 carries an upstream `argparse` regression that the CLI
    works around, but older interpreters are unsupported.
  * **History rewrite.** As noted in the `v1.0.0` deprecation banner, the entire pre-`v2`
    git history was removed during the refactor; users pinning to a specific `v1.x` SHA must
    fetch the legacy tarball from PyPI.

#### 🎉 Major Features

  * **Multi-library manager.** First-class support for four extension types — `skills`, `agents`,
    `commands`, `hooks` — selected as the trailing `LIBRARY` token of `polyskills manager` and
    `polyskills list`. Each maps to its own default source/destination directory.
  * **`list` sub-command.** `polyskills list <remote> <LIBRARY>` enumerates the available
    extensions on a remote (without downloading any content) so users can discover valid
    `--name` values before invoking `manager`.
  * **`sources` and `tools` sub-commands.** Two zero-network introspection commands print the
    registered remote providers (currently `github`) and the supported LLM tools, respectively.
  * **Pluggable remote providers.** `polyskills.remote.sources` exposes an abstract
    `SourceManager` with a concrete `GithubManager` implementation, wired through the
    `_SOURCE_MANAGERS` registry in `polyskills.cli`. New providers light up automatically once
    registered — no dispatcher changes required.
  * **Tarball-based extraction.** Extension contents are fetched as a single repository tarball
    (rather than per-file REST calls), which dramatically reduces request count for large
    libraries and stays well below GitHub's unauthenticated rate limit.
  * **Bundled extensions library.** The repository now ships a curated set of first-party
    extensions under `extensions/` — agents (`python-code-reviewer`, `python-code-planning`,
    `python-code-debugger`, `python-code-optimization`) and skills (`sql-code-format`,
    `markdown-format`, `git-commiter`) — exercised by the integration test suite.

#### ✨ Feature Enhancements

  * **Shared remote controls.** `--pagination`, `--token`, and `--version` are defined once via
    an `argparse` parent parser (`buildRemoteControls()`) and inherited by every remote-touching
    sub-command, so flag semantics stay consistent.
  * **POSIX-normalised paths.** Both `--source` and `--destination` are normalised through
    `pathlib.Path.as_posix()` before dispatch, eliminating Windows-vs-POSIX separator drift.
  * **Hermetic test runner.** `python -m polyskills.tests` discovers and runs the full suite
    (45 cases as of this release) from the package directory regardless of the caller's
    working directory, making the entry-point CI-friendly out of the box.

#### 🛠️ Patches & Fixes

  * **`~` and `$VAR`/`%VAR%` expansion.** `polyskills manager ... --destination
    ~/.claude/skills/<name>` previously created a literal `~` directory next to the current
    working directory because `pathlib.Path` performs no shell-style expansion on construction.
    A new `_expandUserPath()` helper (`os.path.expandvars` → `Path.expanduser()`) is now applied
    to `--source` and `--destination` for both `manager` and `list`, so shell-style paths from
    POSIX and Windows shells resolve to the user's home mirror. Defaults are preserved when the
    flag is omitted. _(commits `01f715d`, `662bd41`)_
  * **CPython 3.12.0–3.12.4 `argparse` regression.** `argparse.HelpFormatter._format_usage`
    raises `AssertionError` on long auto-generated usage lines for the `list` and `manager`
    sub-parsers. An explicit `usage=` string short-circuits the buggy path without changing
    user-facing semantics. _(commit `a7376ef`)_
  * **`list` positional registration.** The `LIBRARY` positional was missing on the `list`
    sub-parser, causing argparse to reject otherwise-valid invocations. _(commit `1379e15`)_
  * **Manager dispatch wiring.** `polyskills manager` now correctly delegates to
    `SourceManager.get(mode='extensions', ...)` with the documented keyword payload
    (`name`, `source`, `destination`, `version`, `formatter`, `exists`). _(commit `2275761`)_

#### 🧪 Testing & CI

  * **Hermetic CLI suite (`test_cli.py`).** Argparse construction, `_resolveManager` registry
    behaviour, the `cli.get` wrapper contract, and end-to-end `cli.main` dispatch are all
    covered without a single network call (`cli.get` is mocked). Includes the new
    `TestDestinationExpansion` regression class for the `~` / `$VAR` bug.
  * **Cross-platform skill-install suite (`test_skill_install.py`).** Validates the
    `~/.claude/skills/<name>` mirror path on Linux, macOS, and Windows, the `SKILL_FILENAME`
    constant, and POSIX path-separator compatibility.
  * **Live remote suite (`test_remote_sources.py`).** Exercises the real `GithubManager`
    against the `PyUtility/polyskills` repository to keep the contract honest.
  * **GitHub Actions workflow.** A CI workflow (`.github/`) runs `python -m polyskills.tests`
    on every push, gating merges on a green suite (45/45 as of `v2.0.0`).

#### ⚙️ Code Refactoring & Internals

  * Promoted `_extract()` to `polyskills.tests.base` so every concrete test case inherits the
    same tarball-extraction harness (commits `de5880f`, `adf7f45`).
  * Renamed `_buildRemoteCommonParser()` → `buildRemoteControls()` and moved it next to the
    sub-parsers it parents (commits `e479dd8`, `ba0bcc7`, `9852719`).
  * Refactored `SourceManager.get` to dispatch on a `mode` keyword (`list` vs. `extensions`)
    so the CLI never branches on provider type (commits `63c4382`, `d3abef9`, `811bc69`).

#### 📦 Installation

```shell
$ pip install "polyskills==2.0.0"

$ polyskills sources                                  # list supported remote providers
$ polyskills tools                                    # list supported LLM tools
$ polyskills list https://github.com/<owner>/<repo> skills
$ polyskills manager https://github.com/<owner>/<repo> \
    --name sql-code-format \
    --destination ~/.claude/skills/sql-code-format \
    --exists overwrite \
    skills
```

#### 🔁 `v1.x` → `v2.0.0` Migration

<div align = "center">

| `v1.0.0` Invocation | `v2.0.0` Equivalent |
| :--- | :--- |
| `polyskills <remote> --get-skills` | `polyskills list <remote> skills` |
| `polyskills <remote> --update <name> --directory ".skills/"` | `polyskills manager <remote> --name <name> --destination .skills/<name> --exists overwrite skills` |
| _(no equivalent)_ | `polyskills manager <remote> --name <name> agents` |
| _implicit overwrite_ | `--exists {fail, overwrite, merge}` (default `fail`) |
| `--directory ...` | `-d / --destination ...` (now expands `~`, `$VAR`, `%VAR%`) |
| _token on CLI only_ | `POLYSKILLS_REMOTE_TOKEN` env var (recommended) or `--token` |
| _tag-per-skill (`name@vX.Y.Z`)_ | `--version <ref>` pins the whole library at one git ref |

</div>

### PolySkills v1.0.0 | 2026-05-25

The world of AI is evolving fastm and agent workflows are the new *norms* to build awesome projects, or to create an entire
army of dedicate problem solver to run an entire organization. To help a LLM to produce the correct output in a desired format
or to do a certain tasks in a configured way an extension is necessary. The initial version aims to streamline the process of
management of different skills. The package is now available at [**`polyskills`**](https://github.com/PyUtility/polyskills) and
can be installed like:

```shell
$ pip install polyskills==1.0.0
$ polyskills "https://www.github.com/<owner>/<repository>" --get-skills
$ polyskills "https://www.github.com/<owner>/<repository>" --update <skill-name> --directory ".skills/"
```

The module is designed without any exotic dependency - the job: (I) fetch lists of skills defined under a remote version control
system with ``git tag skillName@vX.Y.Z` format, (II) add/update the skill in the required directory.

> [!WARNING] This version (v1.0.0) of the module is now deprecated. The advanced version v2 is developed. The module is a
> complete refactor and old codes are completely removed from history. Check the PyPI tarball for file details.

</div>
