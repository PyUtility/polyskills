<div align = "center">

# Known Gaps

</div>

<div align = "justify">

What the documents could not settle, and what the repository gets wrong today. Nothing here was fixed on a guess: each
item waits for the owner. Remove an item once it is resolved.

## Open Questions

  * **Plugin versions.** The three plugin manifests say `2.0.0` while the package is `v2.1.0`. It is not settled
    whether the plugin keeps a version of its own.
  * **Registrations.** `extend-init` has no badge in `extensions/skills/README.md` and no row in `AGENTS.md`, and
    `god-mode` and `humanize-text` have no row in `AGENTS.md`. Some of them may not suit Codex, so ask before adding.

## Known Defects

  * `README.md` links to `./library/agents/` and `./library//skills/`, which do not exist. The folders are
    `extensions/agents/` and `extensions/skills/`.
  * The `list` example in `README.md` shows four skills; the repository has twelve.
  * `CHANGELOG.md` points its commit log at `PyUtility/autoholidays`, another repository.
  * `tests.yml` passes `GITHUB_TOKEN` to raise the rate limit but never sets `POLYSKILLS_RUN_LIVE`, so CI runs no live
    test.

</div>
