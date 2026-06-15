<div align = "center">

# LLM Essentials - Library of Skills, Agents, Workflows

[![GitHub Issues](https://img.shields.io/github/issues/PyUtility/polyskills?style=plastic)](https://github.com/PyUtility/polyskills/issues)
[![GitHub Forks](https://img.shields.io/github/forks/PyUtility/polyskills?style=plastic)](https://github.com/PyUtility/polyskills/network)
[![GitHub Stars](https://img.shields.io/github/stars/PyUtility/polyskills?style=plastic)](https://github.com/PyUtility/polyskills/stargazers)
[![GitHub Stars](https://img.shields.io/github/contributors/PyUtility/polyskills?style=plastic)](https://github.com/PyUtility/polyskills/contributors)
[![LICENSE File](https://img.shields.io/github/license/PyUtility/polyskills?style=plastic)](https://github.com/PyUtility/polyskills/blob/master/LICENSE)
[![PyPI Latest Release](https://img.shields.io/pypi/v/polyskills.svg?style=plastic)](https://pypi.org/project/polyskills)
![Contributor Covenant](https://img.shields.io/badge/👩‍💻_Contributor%20Covenant-2.1-4baaaa.svg?style=plastic)
![Contributing Guidelines](https://img.shields.io/badge/🤝-Contributing_Guidelines-blue?style=plastic)

![SQLite](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Python (v3)](https://img.shields.io/badge/-Python%20v3-3776AB?logo=python&logoColor=white)
![Markdown Files](https://img.shields.io/badge/-Markdown%20Files-000000?logo=markdown&logoColor=white)
![GIT Commits](https://img.shields.io/badge/-GIT%20Commits-F03C2E?logo=git&logoColor=white)

</div>

<div align = "justify">

A curated collection of AI agents, skills, workflows, etc., that can work across industries - providing Python-based utility
functions to synchronize the library across multiple systems using a version-controlled system. The project also provides
connectors for universal loading across different LLM tools (Anthropic's Claude Code, CodeX, Cursor AI, etc.) that can read skills
either directly (Claude Code) or follow prompts based control. 🤖✨

## 🧠 Introduction to LLM Library

Artificial Intelligence (AI) systems are revolutionizing the way industries operate. From everyday tasks to specialized,
automated tasks - AI brings efficiency, innovation, and scalability. With the release of [Claude Skills](https://claude.com/skills),
[AI Agent Skills](https://agentskills.io/home) and other niche, fast-paced developments in this space - it is now a fundamental
requirement to maintain a unified, standardized repository of these capabilities.

### 🤖 Project Capabilities

The project provides a curated list of AI [agents](./library/agents/), [skills](./library//skills/), and other essential tools
that enhances the way AI agents works and performs. In addition, the skills also provides different customization rules (e.g., 
generate an code output the way you write code, or generate email content based on your own writing styles).

  * A categorized list of [AI Skills](./library//skills/) in a standard [Agent Skills](https://agentskills.io/home) format to
    give new capabilities and expertise.
  * A list of [AI Agents](./library/agents/) to break tasks into seperate functional groups that can work concurrently or in a
    sequential manner as per the design pattern.
  * A dedicated *open-source* Python framework to manage all above skills, agents, etc. from any version controlled remote
    repositories across different systems and projects using single source of truth.
  * A set of adapters to convert standard Agent Skills to other AI coding agents (which does not support native `SKILLS.md`,
    or `AGENTS.md` file) by converting files to prompts.

## 🚀 Getting Started

LLM Tools like Anthropic's Claude Code can directly work with the Agent Skills format that invokes `SKILLS.md` (or `AGENTS.md`)
file natively based on skill description or keywords defined in a settings file. However, some other tools may require an
adapter to safely convert to system prompts. The Python [`framework`](./polyskills/) is designed to address the issue by importing
the required skills from any version controlled systems such that one single source of truth can be maintained across different
production environment or projects having the same functionalities - thus providing consistent output.

### 📦 Installation

The package is hosted at [PyPI](http://pypi.org/project/polyskills/) and can be installed using the `pip` package manager as:

```shell
$ pip install polyskills
```

To install the package from source, you need to have `git` client available on your system and install the binaries using the
below command:

```shell
$ git clone https://github.com/PyUtility/polyskills
$ pip install . # cd into polyskills; editable install using -e
```

The `**library**` requires **Python 3.12+** and is designed to have minimal overheads, thus providing *long-term compatibility*
with the upcoming releases (requires [standard libraries](https://docs.python.org/3/library/index.html) which is shipped by
default) of Python language and AI tools.

### 🧰 CLI Overview

Once installed, the `polyskills` command is exposed on the system `PATH`. Use the `--help` flag at any level to discover
documentation for all sub-commands and flags. The CLI is organized around four sub-commands:

| 🔖 Command | 🎯 Purpose |
| :--- | :--- |
| `tools` | List the supported LLM tools (e.g., Claude Code, GitHub Copilot) and exit. |
| `sources` | List the supported remote source providers (e.g., GitHub) and exit. |
| `list` | Enumerate available extensions under a remote `<source>` directory, no download. |
| `manager` | Fetch a single extension (`skills` / `agents`) from the remote into a local directory. |

```shell
$ polyskills --help          # top level documentation and sub-commands
$ polyskills manager --help  # documentation for the 'manager' sub-command
```

### 🔍 Discover Supported Tools and Sources

The `tools` and `sources` sub-commands are *terminal*, i.e., they print and exit. Use them to validate that a target LLM
tool or remote provider is supported before running a fetch.

```shell
$ polyskills tools
>> Available LLM Tools:
>> 01. CLAUDE_CODE - https://claude.com/product/claude-code
>> 02. GITHUB_COPILOT - https://github.com/features/copilot

$ polyskills sources
>> Available Sources:
>> 01. GITHUB - https://www.github.com/
```

### 📜 List Extensions on a Remote

Use the `list` sub-command to enumerate the immediate child directories under a remote `--source` path without downloading
any content. The required positional `LIBRARY` argument selects the extension family (`skills`, `agents`, `commands`,
`hooks`) and also supplies the default `--source` directory (`./<library>`) when `--source` is omitted.

```shell
$ polyskills list https://github.com/PyUtility/polyskills skills \
      --source ./extensions/skills
>> Available skills at `extensions/skills` (version = master):
>>     >> 01. git-commiter
>>     >> 02. markdown-format
>>     >> 03. python-code-format
>>     >> 04. sql-code-format

$ polyskills list https://github.com/PyUtility/polyskills agents \
      --source ./extensions/agents --version master
```

### 📥 Fetch an Extension with `manager`

The `manager` sub-command downloads a single extension (`skills` or `agents`) into a destination directory. The library
type is selected via a sub-sub-parser (`skills` / `agents`) and the extension name comes from `-n / --name`. When
`--destination` is not provided, the CLI defaults to `./<library>/<name>`.

```shell
$ polyskills manager https://github.com/PyUtility/polyskills \
      --source ./extensions/skills \
      --name python-code-format \
      --destination ./.claude/skills/python-code-format \
      skills

$ polyskills manager https://github.com/PyUtility/polyskills \
      --source ./extensions/agents \
      -n python-code-reviewer \
      -d ./.claude/agents/python-code-reviewer \
      agents
```

The `--exists` flag controls behavior when the destination directory already exists and is non-empty:

  * 🛑 `fail` (default) - raise `FileExistsError`, leave the destination untouched.
  * 🧹 `overwrite` - remove the destination tree and re-extract from scratch.
  * 🛠 `merge` - extract on top of the existing tree, overwriting on conflict.

### 🔐 Authentication and Pagination

For private or self-hosted repositories, an authentication token is required. The token is resolved with the following
precedence (highest first):

  1. Environment variable `POLYSKILLS_REMOTE_TOKEN` (recommended for CI / production).
  2. The `--token` CLI flag (discouraged outside local testing - the value may leak into shell history).

```shell
$ $env:POLYSKILLS_REMOTE_TOKEN = "ghp_xxx"   # PowerShell
$ export POLYSKILLS_REMOTE_TOKEN="ghp_xxx"   # bash / zsh

$ polyskills list https://github.com/<org>/<private-repo> skills \
      --source ./extensions/skills --pagination 100
```

The `--pagination` flag (defaults to `100`, the GitHub maximum) tunes how many entries are returned per REST API page
during enumeration. The `--version` flag (defaults to `master`) pins the fetch to an exact tag or commit SHA so the
extension content is reproducible across systems.

### 🐍 Programmatic Usage

In addition to the CLI, every primitive is exposed as a Python API so the same workflow can be embedded inside automation
scripts, CI pipelines, or notebooks.

```python
from pathlib import Path

from polyskills.cli import get, listExtensions
from polyskills.remote.sources import SourceControl

control = SourceControl(pagination = 100, token = None)

names = listExtensions(
    remote = "https://github.com/PyUtility/polyskills",
    library = "skills",
    source = Path("./extensions/skills"),
    version = "master",
    control = control,
)

get(
    remote = "https://github.com/PyUtility/polyskills",
    name = "python-code-format",
    source = Path("./extensions/skills"),
    destination = Path("./.claude/skills/python-code-format"),
    version = "master",
    exists = "overwrite",
    control = control,
)
```

## ⚖️ Project License

This project is licensed under the [MIT License](...). Permission is granted to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the software. The software is provided “as is”, without warranty of any kind,
express or implied. See the LICENSE file for full details.

## ⚠️ Project Disclaimer

The project provides a curated lists of skills, agents, etc. which can alter the performance of AI tools significantly. AI makes
mistakes and the tools listed here can worsen the performance. Please read, verify and research before using any content.

AI tools often charges based on token consumptions (approx. number of input + output words) and using contents from this library
may significantly increase the consumption cost. Always check and track usage of the model with/without using the skills.

</div>
