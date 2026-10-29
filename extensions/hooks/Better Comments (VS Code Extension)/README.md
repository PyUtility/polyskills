<div align = "center">

# Better Comments Hooks

[![Python](https://img.shields.io/badge/Python-%203.9%2B-3776AB?style=plastic&logo=python)](https://www.python.org)
[![Git](https://img.shields.io/badge/Git-%20Client-F05032?style=plastic&logo=git)](https://git-scm.com)
[![Better Comments](https://img.shields.io/badge/Better-%20Comments-007ACC?style=plastic&logo=visualstudiocode)](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments)

</div>

<div align = "justify">

Two git-like hooks keep the tags of the [Better
Comments](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments) extension of VS Code in sync
with this repository: `pull.py` brings the tags of [`settings.json.template`](./settings.json.template) into the VS Code
settings, and `push.py` proposes the tags added locally as a pull request. The template is the source of truth for the
annotation tags of the `code-modification-rule` skill. The hooks run **only when they are called** - they are never
registered to run automatically.

## Requirements

  * Python 3.9 or later - the hooks use the standard library only and run the same on Windows, macOS, and Linux.
  * A git client on the `PATH` - the hooks read the remote through git, so its proxy, certificate, and credential setup
    applies. Git 2.25 or later clones only the hook folder; older versions clone the whole tip of the branch.
  * Optional: the [GitHub CLI](https://cli.github.com) (`gh`), signed in, so `push.py` creates the pull request itself.

## Calling the Hooks

Run a script from this folder, or from the repository root with its path:

```shell
$ python pull.py --help
$ python "extensions/hooks/Better Comments (VS Code Extension)/pull.py" --dry-run
```

On Windows, the Python launcher `py` works in place of `python`. An AI assistant runs the hooks only when you ask for
it, for example "pull the Better Comments tags" - it can run `pull.py` for you, but run `push.py` yourself, as it asks
for confirmation in an interactive terminal.

## Pull the Tags

`pull.py` clones the tip of the remote branch into a temporary folder, compares the tags of the template with the
`better-comments.tags` of the VS Code settings, and writes the merged tags back:

<div align = "center">

| Tag | Without `--force` | With `--force` |
| :---: | :---: | :---: |
| Only in the remote | Added | Added |
| Only in the local settings | Kept | Kept |
| In both, with a different style | Pull rejected, nothing written | Overwritten with the remote value |

</div>

```shell
$ python pull.py --dry-run
$ python pull.py
$ python pull.py --force
```

Only the `better-comments.tags` value is rewritten - every other setting, the comments outside that value, the byte
order mark, and the line endings of the file stay as they are, and the previous file is kept as `settings.json.bak`. A
comment inside the old `better-comments.tags` value is dropped, as the value is written again. A second pull with no
remote change writes nothing, and a read-only settings file is never changed.

## Push the Tags

`push.py` proposes the tags that are only in the local settings and, with `--include-changed`, the local values of the
tags that differ from the remote. Nobody pushes to the default branch: after you confirm, the hook commits the proposed
template on a new `better-comments/<date>-<tags>` branch, pushes it, and opens the pull request - with `gh` when it is
installed, otherwise with the compare page of GitHub in the browser (the URL is always printed).

```shell
$ python push.py
$ python push.py --include-changed
$ python push.py --fork https://github.com/<user>/polyskills.git
```

Without write access to the remote, the push is refused with exit code `4`: fork the repository on GitHub and run the
hook again with `--fork`. The hook always asks before it pushes, and aborts without an interactive terminal. In Git Bash
(mintty), run it as `winpty python push.py`, or use PowerShell or the Command Prompt.

## Options

<div align = "center">

| Option | Hook | Description |
| :---: | :---: | --- |
| `--settings PATH` | Both | The VS Code settings file, by default the user settings of VS Code |
| `--workspace` | Both | Use `.vscode/settings.json` of the current folder |
| `--remote URL` | Both | The repository with the template, by default `https://github.com/PyUtility/polyskills.git` |
| `--ref BRANCH` | Both | The branch of the remote, by default `master` - also the base of the pull request |
| `--force` | `pull.py` | Overwrite the local tags that differ from the remote (the local-only tags are kept) |
| `--dry-run` | `pull.py` | Report the changes and write nothing |
| `--include-changed` | `push.py` | Also propose the local values of the tags that differ from the remote |
| `--fork URL` | `push.py` | Push the branch to this fork of the remote |

</div>

The user settings of VS Code are read from the default path of each platform. Insiders, VSCodium, Flatpak, and portable
installs keep their settings elsewhere - pass that file with `--settings`.

<div align = "center">

| Platform | Settings File |
| :---: | :---: |
| Windows | `%APPDATA%\Code\User\settings.json` |
| macOS | `~/Library/Application Support/Code/User/settings.json` |
| Linux | `$XDG_CONFIG_HOME/Code/User/settings.json` or `~/.config/Code/User/settings.json` |

</div>

## Exit Codes

<div align = "center">

| Code | Meaning |
| :---: | --- |
| `0` | Done, or nothing to do |
| `1` | Rejected - `pull.py` found conflicts, or `push.py` was declined or had no terminal to ask |
| `2` | Invalid usage, settings, or template |
| `3` | A git, network, or branch failure |
| `4` | The remote refused the push - use `--fork` |
| `130` | Interrupted |

</div>

## Tests

The tests need git but never the network: they run each hook against a local bare repository, in a temporary home
folder with its own git configuration, so they never touch the real VS Code settings.

```shell
$ cd "extensions/hooks/Better Comments (VS Code Extension)"
$ python -m unittest discover -s tests -t .
```

</div>
