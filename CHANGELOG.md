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

### PolySkills v2.0.0 | Unreleased

  * 🎉 **Local Tracking Database** - `polyskills` now ships a versioned SQLite tracking database at
    `~/.polyskills/polyskills.db` that records every extension fetch performed through either the CLI tool or the
    direct Python API. The database is created lazily on first import and is engineered to be best-effort: any
    failure to open or write is downgraded to a one-shot `RuntimeWarning` so the install path is never broken by a
    tracking error. The schema (`PRAGMA user_version = 1`) ships three tables - `meta`, `extensions`, `events` - and
    is materialised through idempotent `CREATE TABLE IF NOT EXISTS` DDL so repeat imports are no-ops.
  * ✨ **Invocation Context** - the new `events.invoked_via` column distinguishes fetches triggered from the CLI
    (`"cli"`) from fetches triggered through the Python API (`"api"`).

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

> [!WARNING] This version (v1.0.0) of the module is now deprecated. The advanced version v2 is currently being developed. The
> module is a complete refactor and old codes are completely removed from history. Check the PyPI tarball for file details.

</div>
