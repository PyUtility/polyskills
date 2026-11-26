<div align = "center">

# Hooks

</div>

<div align = "justify">

`extensions/hooks/<Tool> (<Kind of Tool>)/` holds one hook per tool it serves. The only hook today is
`Better Comments (VS Code Extension)/`, two scripts that keep the comment tags of the `code-modification-rule` skill in
sync between the VS Code settings and this repository. Read this before changing it or adding a hook.

## How It Works

  * `pull.py` brings the tags of `settings.json.template` into the VS Code settings, and `push.py` proposes the tags
    added locally as a pull request, much like `git pull` and `git push`. The template is the source of truth.
  * Both run only when called; nothing registers them to run on their own. Each takes `--help`.
  * They use the standard library only and follow `python-code-format`, so they run the same on Windows, macOS, and
    Linux. They need Python 3.9 or later and a git client on the `PATH`, and `push.py` creates the pull request itself
    when a signed-in GitHub CLI (`gh`) is present.

## Commands

```shell
$ cd "extensions/hooks/Better Comments (VS Code Extension)"
$ python -m unittest discover -s tests -t .
```

On 2026-11-26 the suite ran 54 tests in about a minute.

## Pitfalls And Limits

  * The folder name holds spaces and parentheses, so quote it in every command.
  * CI runs neither these tests nor flake8 on this folder, because `.flake8` excludes `extensions/`. Run both by hand.
  * A new hook needs a folder named after its tool, a `README.md` that says when it runs and how to call it, a badge in
    `extensions/hooks/README.md`, and the `HOOKS` count badge of the root `README.md`.

</div>
