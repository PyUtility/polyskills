<div align = "center">

# Polyskills Package

</div>

<div align = "justify">

The `polyskills` package (`polyskills/`) is the command-line tool and Python API that fetches one extension, such as a
skill or an agent, from a git remote into a local directory and records the fetch. Read this before changing the CLI,
the remote download, or the tracking database. The tests are covered in `testing.md`.

## How It Works

A `manager` call passes through four layers, each with one job:

  1. **Parse.** `main()` in `polyskills/cli.py` builds the parser with `buildParser()` and hands the arguments to
     `_dispatch()`. The subcommands are `tools`, `sources`, `list`, `manager`, and `records`.
  2. **Dispatch.** `tools` and `sources` print and exit. `records` reads the tracking database and contacts no remote.
     `list` and `manager` resolve TLS first: without a flag, `requests` uses its trust store and honours
     `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE`; `--no-verify` turns verification off, and `--request-cert` pins the
     `certifi` authorities.
  3. **Fetch.** `_resolveManager()` takes the first class in `_SOURCE_MANAGERS` whose `remotePattern` matches the
     remote URL. `get()` or `listExtensions()` then calls `SourceManager.get()` in the mode `extensions` or `list`.
     `GithubManager` streams `https://api.github.com/repos/<owner>/<repo>/tarball/<version>` into a temporary file and
     extracts only the members under `<source>/<name>`.
  4. **Record.** Unless `--no-tracking` is set, the CLI records every fetch, failed ones included, through
     `polyskills.database.tracker`.

`get()` and `listExtensions()` are also the public Python API that the root `README.md` shows.

### Defaults

  * `--source` defaults to `./<library>` and `--destination` to `./<library>/<name>`. Both expand `~` and environment
    variables, so `--destination ~/.claude/skills/<name>` works on every system.
  * `--exists` decides what happens to a destination that is not empty: `fail` (the default) raises, `overwrite`
    removes it first, and `merge` extracts on top of it.
  * `--version` defaults to `master` and also takes a tag or a commit SHA.
  * The token comes from `POLYSKILLS_REMOTE_TOKEN` first, then from `--token`.

### Safety Limits

The download treats the remote as untrusted. The limits sit at the top of `polyskills/remote/sources.py`:

<div align = "center">

| Limit | Value | Guards Against |
| :---: | :---: | --- |
| Compressed archive | 100 MiB | A download that fills the disk |
| Extracted content | 500 MiB in total | Gzip and tar bombs |
| Tag pages | 100 | A server that keeps sending `next` links |
| Timeouts | 30 s per request, 60 s per download | A server that never answers |
| Member paths | Inside the destination | Path traversal; a member that escapes raises `ExtractionError` |

</div>

### Errors

`polyskills/error/exceptions.py` defines `PolyskillsError` and its subclasses `ValidationError` (also a `ValueError`),
`RemoteError`, and `ExtractionError`. `main()` turns any exception into `[ERROR] <message>` on stderr with exit status
1, and Ctrl-C into exit status 130. Set `POLYSKILLS_DEBUG` to see the traceback instead.

### Tracking Database

  * SQLite at `~/.polyskills/records.db`. `POLYSKILLS_DB_PATH` overrides the path, and a read-only query never creates
    the directory.
  * The models in `polyskills/database/models.py` are `Source`, `Library`, `Remote`, `Extension`, `Installation`,
    `Environment`, and `FetchEvent`. The schema is normalised, so each fact lives in one table.
  * `tracker.py` exposes `record_fetch`, `list_installations`, and `get_installation`. Every write is best-effort: a
    fault becomes one warning per process and never changes the fetch result or the exit status.
  * Each fetch event records whether the CLI or the Python API made it; the CLI calls `set_invocation_context("cli")`.

## Adding A Remote Provider

  1. Add the provider to `ValidSources` in `polyskills/remote/sources.py`; the `sources` subcommand prints that enum.
  2. Subclass `SourceManager` as `GithubManager` does. `remotePattern`, `remoteAPI`, `headers`, `_getTags`,
     `_getExtensions`, and `_listExtensions` are abstract. Override `resolveCommit` too when the provider can resolve a
     reference to a commit SHA; the base returns `None`, and the database then records no SHA.
  3. Register the class in `_SOURCE_MANAGERS` in `polyskills/cli.py`, where `_resolveManager()` finds it.
  4. Keep every safety limit above, and add tests that mock the network (see `testing.md`).

## Pitfalls And Limits

  * GitHub is the only provider today. `SupportedTools` in `polyskills/apps/tools.py` lists the assistants that the
    `tools` subcommand prints: Claude Code and GitHub Copilot.
  * `polyskills/extensions/__init__.py` holds a docstring that explains skills, agents, and hooks, and no code.
  * The version is the string `__version__` in `polyskills/__init__.py`, which `pyproject.toml` reads; see
    `release.md`.
  * `.flake8` sets 88 columns and ignores the house-style spacing codes, such as `E251` for `key = value` arguments
    and `E125` for the signature indentation.

</div>
