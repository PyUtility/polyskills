<div align = "center">

# Versions And Releases

</div>

<div align = "justify">

The package, the changelog, and the two plugins each carry a version. Read this before a release, a version bump, or a
change to a plugin manifest.

## Where The Versions Live

<div align = "center">

| File | Value On 2026-11-26 | Read By |
| :---: | :---: | --- |
| `polyskills/__init__.py` (`__version__`) | `v2.1.0` | `pyproject.toml` through `[tool.setuptools.dynamic]`, and the `polyskills/<version>` User-Agent |
| `CHANGELOG.md` | `v2.1.0`, 2026-06-27 | People |
| `.claude-plugin/marketplace.json` and `extensions/.claude-plugin/plugin.json` | `2.0.0` | Claude Code |
| `extensions/.codex-plugin/plugin.json` | `2.0.0` | Codex |

</div>

## Releasing The Package

  1. Bump `__version__` and add the release to `CHANGELOG.md`.
  2. Publish a GitHub release. `publish.yml` builds the distributions with `python -m build` and publishes them to PyPI
     through the `PyPI Release` environment with trusted publishing (`id-token: write`), so no PyPI secret is stored.

## The Changelog

  * It follows Keep a Changelog with PEP 440 versions, and the `markdown-format` skill holds its template.
  * Each `major.minor` release gets an `###` heading in the form `PolySkills vX.Y.Z | YYYY-MM-DD`, a short description,
    and `####` sections. The newest release goes on top.
  * The legend emoji (🎉, ✨, 🛠️, ⚙️, 💣) open list items, never headings.

## The Plugins

  * **Claude Code**: `.claude-plugin/marketplace.json` lists the plugin `llm-essentials` with the source
    `./extensions`. Its manifest, `extensions/.claude-plugin/plugin.json`, sets `commands` to an empty list and loads
    `./commands/` through `skills`; see `extensions/commands.md`.
  * **Codex**: `.agents/plugins/marketplace.json` points at `./extensions`, and `extensions/.codex-plugin/plugin.json`
    loads `./skills`. `AGENTS.md` is the entry point Codex reads in this repository, and it lists the skills.
  * The descriptions and keywords of the manifests name the kinds of content the plugin carries. Update them when a new
    kind of extension arrives.

## Pitfalls And Limits

  * The plugin versions and the package version have drifted apart; `gaps.md` holds the open question.

</div>
