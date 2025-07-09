<div align = "center">

# LLM Essentials - Library of Skills, Agents, Workflows

![Contributor Covenant](https://img.shields.io/badge/👩‍💻_Contributor%20Covenant-2.1-4baaaa.svg?style=plastic)
![Contributing Guidelines](https://img.shields.io/badge/🤝-Contributing_Guidelines-blue?style=plastic)

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

The project provides a curated list of AI [agents](./agents/), [skills](./skills/), and other essential tools that enhances the
way AI agents works and performs. In addition, the skills also provides different customization rules (e.g., generate an code
output the way you write code, or generate email content based on your own writing styles).

  * A categorized list of [AI Skills](./skills/) in a standard [Agent Skills](https://agentskills.io/home) format to give
    new capabilities and expertise.
  * A list of [AI Agents](./agents/) to break tasks into seperate functional groups that can work concurrently or in a
    sequential manner as per the design pattern.
  * A dedicated *open-source* Python framework to manage all above skills, agents, etc. from any version controlled remote
    repositories across different systems and projects using single source of truth.
  * A set of adapters to convert standard Agent Skills to other AI coding agents (which does not support native `SKILLS.md`,
    or `AGENTS.md` file) by converting files to prompts.

## 🚀 Getting Started

LLM Tools like Anthropic's Claude Code can directly work with the Agent Skills format that invokes `SKILLS.md` (or `AGENTS.md`)
file natively based on skill description or keywords defined in a settings file. However, some other tools may require an
adapter to safely convert to system prompts. The Python [`framework`](...) is designed to address the issue by importing the
required skills from any version controlled systems such that one single source of truth can be maintained across different
production environment or projects having the same functionalities - thus providing consistent output.

The package is hosted at [PyPI](...) and can be installed using the `pip` package manager as:

```shell
$ pip install ...
```

To install the package from source, you need to have `git` client available on your system and install the binaries using the
below command:

```shell
$ git clone ...
$ pip install ...
```

The `**library**` requires **Python 3.12+** and is designed to have minimal overheads, thus providing *long-term compatibility*
with the upcoming releases (requires [standard libraries](https://docs.python.org/3/library/index.html) which is shipped by
default) of Python language and AI tools.

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
