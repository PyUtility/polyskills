<div align = "center">

# Testing And CI

</div>

<div align = "justify">

The package tests live in `polyskills/tests/` and run with `unittest`. The Better Comments hook has a suite of its own,
covered in `extensions/hooks.md`. Read this before adding a test, changing a workflow, or running the live tests.

## Commands

```shell
# every package test, from the repository root; either form works
$ python -m unittest discover -v -s polyskills/tests -t .
$ python -m polyskills.tests

# one module, one class, or one test
$ python -m unittest polyskills.tests.test_cli
$ python -m unittest polyskills.tests.test_database.TestDatabasePaths
$ python -m unittest polyskills.tests.test_database.TestDatabasePaths.test_environment_override_is_honoured

# the live tests as well (Git Bash or POSIX shell)
$ POLYSKILLS_RUN_LIVE=1 python -m unittest discover -v -s polyskills/tests -t .
```

## How The Suite Works

  * The default run is hermetic. The CLI, path, and security tests mock the network and build archive fixtures in
    memory, so they need no connection.
  * `polyskills/tests/__init__.py` points `POLYSKILLS_DB_PATH` at a file in the system temp directory before any test
    runs, so no test touches `~/.polyskills/records.db`. A value set outside wins, through `os.environ.setdefault`.
  * Live tests use `GithubManagerTestCase` from `base.py` and are skipped unless `POLYSKILLS_RUN_LIVE=1`. They fetch
    `sql-code-format` from `PyUtility/polyskills` at `master` into a temporary directory.
  * Behind a TLS-intercepting proxy, also set `POLYSKILLS_NO_VERIFY=1`. `POLYSKILLS_REMOTE_TOKEN` raises the GitHub rate
    limit from about 60 to about 5,000 requests an hour.

<div align = "center">

| Module | Covers | Network |
| :---: | --- | :---: |
| `test_cli.py` | The parser, the dispatch, and `main()` end to end | Mocked |
| `test_database.py` | Path resolution, the schema, and the tracker | None |
| `test_security.py` | TLS forwarding, archive path traversal, the size caps, the pagination cap | Mocked |
| `test_remote_sources.py` | `GithubManager.get()` in the modes `tags` and `extensions` | Live |
| `test_skill_install.py` | The per-platform skill path, and an extraction into a temporary directory | None and live |

</div>

On 2026-11-26 the default run took about 7 seconds: 75 tests, 10 of them skipped as live.

## Continuous Integration

<div align = "center">

| Workflow | Runs On | Does |
| :---: | :---: | --- |
| `tests.yml` | Push and pull request to `master` | `unittest` on Python 3.12, 3.13, and 3.14 |
| `linting.yml` | Push and pull request to `master` | Two flake8 passes on Python 3.12 to 3.14 |
| `security.yml` | Push and pull request to `master` | `bandit` on `polyskills/` without the tests, then `pip-audit` |
| `publish.yml` | A published GitHub release | Builds the distributions and publishes them to PyPI (see `release.md`) |

</div>

  * Every action is pinned to a commit SHA, with its tag in a comment. Keep that form when you bump one.
  * CI runs neither the hook tests nor the `check.sh` of `/vendor-agnostic`. Run them by hand when you change those
    files.

## Pitfalls And Limits

  * Only `E9`, `F63`, `F7`, and `F82` fail the lint build. The second pass reports at 127 columns and never fails,
    although `.flake8` sets 88.
  * `.flake8` excludes `extensions/`, `docs/`, and `.claude/`, so CI lints only the package.
  * `bandit` skips the tests, because their dummy tokens trip false positives.

</div>
