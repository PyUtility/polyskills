---
name: python-code-format
description: >-
  Governs all Python code formatting, editing, reviews, modification, and creation from scratch. Always read the file in
  full before writing or modifying Python code, even for a small change. Use this skill when a user asks to create,
  edit, update, review or modify any content of a '*.py' file, or any Python code in a project that references this
  skill.
---

<div align = "center">

# Python Code Format

</div>

<div align = "justify">

This skill analyzes Python coding patterns and applies them consistently when creating, editing, or modifying Python
files. The skill is to be used when you are working with a `*.py` file extension.

## Getting Started

Before making any change to a `*.py` file, always use 4 spaces indentation (mandatory). Always use production style
coding, and try to reuse already existing code (DRY principle of coding).

  1. Read the **entire** target file first - understand context, imports, and existing style.
  2. Always follow the PEP 8 standard to write production grade code. Where this skill or the project `.flake8` differs
     from PEP 8 (for example `arg : int` or `ge = 10`), the skill and `.flake8` take precedence.
  3. Always check if .flake8 file is present in the project root and follow the linting standard. Create the file or
     align it with the template as described in the **Flake8 Configuration** section.
  4. Always try to use the Python agents when they are available - see the **Python Agents** section.
  5. Apply every rule before generating output. Read the entire skill file.

Never skip reading the skill or its resources even for small changes.

## Python Agents

Always try to use the Python agent suite from [PyUtility/polyskills](https://github.com/PyUtility/polyskills)
(`extensions/agents/python/`) for a Python change when it is available - only the agents the task needs, chosen with
the **Task Routing** table in `python-coding.md` (agent `python`), and always in its phase order. The main session is
the orchestrator and implements the change with this skill:

<div align = "center">

| Agent | Phase | Role |
| :---: | :---: | --- |
| `python-code-planning` | 1 | Plans the change and its todos before any code is written |
| (main session) | 2 | Implements the plan, following this skill |
| `python-code-reviewer` | 3A | Reviews the diff against this skill (read-only) |
| `python-code-debugger` | 3B | Reproduces failures and pins the root cause (read-only, in parallel with 3A) |
| `python-code-testing` | 4 | Locks correctness in with deterministic tests |
| `python-code-optimization` | 5 | Makes measured speed, memory, or I/O improvements |
| `python-code-security` | 6 | Runs the defensive security audit, the terminal gate |

</div>

Before the first Python change in a session, check that the agents the task needs are available - listed as subagents,
or present in `~/.claude/agents/` or `<project>/.claude/agents/`. A tool without subagent support counts as not
available. If any agent is missing, never continue silently: show this warning and ask the user how to proceed.

```text
WARNING: The Python agents are not available in this system:
python, python-code-planning, python-code-reviewer, python-code-debugger,
python-code-testing, python-code-optimization, python-code-security.
Fetch them from https://github.com/PyUtility/polyskills (extensions/agents/python/)
into ~/.claude/agents/ or <project>/.claude/agents/.
```

Always ask the user to choose one of these options, and recommend the first:

  1. **Fetch the agents automatically (recommended)** - once the user confirms, download them with the commands below,
     then check that they are listed (for example with `/agents` in Claude Code) before continuing.
  2. **Install the agents manually** - the user installs them from the repository above and confirms when they are
     ready.
  3. **Ignore the agents** - proceed with this skill alone, and state in the final summary that the agent phases were
     skipped.

```shell
$ git clone --depth 1 https://github.com/PyUtility/polyskills
$ cp polyskills/extensions/agents/python/*.md ~/.claude/agents/
```

Never download or install the agents without the user's confirmation, and ask again whenever they are still missing.

## Naming Convention

<div align = "center">

| Element/Attribute Name | Naming Convention | Example Names | Additional Remark(s) |
| :---: | :---: | :---: | --- |
| Module Files | `snake_case` | `calendar.py` | Try to use single word names. |
| Class Names | `PascalCase` | `LeavePlanner` `PersonConstruct` | |
| Function Names | `snake_case` | `long_weekends()` | |
| Private Method | `_leading_underscore` | `_generate_key` | Never use `__name__` - it is reserved for Python special methods. |
| Variable Names | `snake_case` | `first_name` | |
| Constants or ENUM Members | `SCREAMING_SNAKE_CASE` | `MONDAY` | |
| Loop/Comprehension Variables | Short Meaningful Name | `cur` `idx` `nxt` `key` `value` | |

</div>

IMPORTANT: If any code file or module is following a different naming convention (like `camelCase`) then preserve the
original format and write accordingly.

Try to use `enum.Enum` for constants that need to be grouped.

## Critical & Mandatory Rules

These rules are critical and mandatory. Always double check these rules are followed and maintained across the code or
module directory. The rules are always mandatory.

### File Header Rules

Every `*.py` file must begin with a module-level docstring that must follow the `reStructuredText` and `sphinx` rules.
The code documents will be generated using `sphinx` with `myst_parser` extension. Always follow the basic snippet.

```python
# -*- encoding: utf-8 -*-

"""
<Short One-Line Summary of the Module - Use Title Case>

<Multi-paragraph description: what the module does, why it exists,
how it fits in the package architecture, and any important usage
notes. Always use proper sentence casing.>

:NOTE: <Any critical behavioral notes or caveats.>
"""

import ...
```

Rules for import statements:

  * Standard library first, then third-party, then local imports.
  * Use standard alias names for module imports (like `import datetime as dt` `import pandas as pd`)
  * Always use absolute package paths - no relative imports.

### Line Length

Keep every line within **70 characters** by default. A line may extend up to the **hard maximum of 88 characters** only
for long words and links (a URL, a long identifier, or a file path) that cannot be split. When the project `.flake8`
sets a different `max-line-length`, the stricter of the two values is the hard maximum.

### Type Hinting

Always use type hints for input attributes and output for functions. Always place a space before and after the colon and
equal sign for type hints. When a signature does not fit on one line, break after the opening bracket, indent the
parameters one level deeper than `def`, and put the closing bracket with the return type on its own line at the `def`
indentation. Example:

```python
def function(arg1 : int, arg2 : str, ..., argN : int = 10) -> float:
    ...


def function_with_kwargs(
    arg1 : int, arg2 : str, ..., argN : int = 10, **kwargs
) -> float:
    ...
```

If a function does not return anything, then explicitly mention `-> None` in output type hint. Always annotate **every**
parameter and return type. For Python 3.9 and later use built-in generics (`list[int]`, `dict[str, int]`,
`tuple[int, ...]`) and `collections.abc.Callable`. Use the `typing` aliases (`List`, `Dict`, `Tuple`, `Callable`) only
when the project supports an older Python version (check `requires-python` in `pyproject.toml`) or the file already
uses them.

### Keyword Arguments & Field Constraints - Spacing Rule

Always place spaces around every mathematical operator. Aligning the `:` of annotations or the `=` of assignments across
a block of related lines is allowed (flake8 `E203` and `E221` are ignored). Examples of spacing around keywords, field
constraints, and alignment are as below.

```python
...

from pydantic import Field

x = (10 + 20) / 30
y : float = Field(..., ge = 0, le = 100)

first_name : str = "John"
age        : int = 30
```

### Docstring Format

Use `reStructuredText` style docstring always. Ensure that you always use `-` instead of `—` (never use em dash -
mandatory). Examples of docstring style for different sections are as below:

```python
def function(...) -> ...:
    """
    <Multi-paragraph that explains what the function does in brief and
    its intended usage. Explain why the function exists, what it does,
    any algorithm details and examples of usage in code-blocks if
    helpful. Can span multiple paragraphs if necessary.>

    :type  arg1: int
    :param arg1: Lorem ipsum dolor. Lorem ipsum dolor. Lorem ipsum
        dolor. Lorem ipsum dolor. Lorem ipsum dolor.

    :type  arg2: float
    :param arg2: ...

    **Keyword Arguments**

    <Short 2-3 lines explaining the usage and importance of keyword
    argument for the function.>

        * **kwarg1** (*int*): Lorem ipsum dolor. Lorem ipsum dolor.
            Lorem ipsum dolor. Lorem ipsum dolor. Lorem ipsum dolor.

        * **kwarg2** (*int*): ...

    **Example Usage**

    <For each example, provide a short 2-3 lines summary about the
    example and then use code-block.>

    .. code-block:: python

        ...

    :raises ...: Lorem ipsum dolor. Lorem ipsum dolor. Lorem ipsum
        dolor. Lorem ipsum dolor. Lorem ipsum dolor.

    :rtype:   <type>
    :returns: Lorem ipsum dolor. Lorem ipsum dolor. Lorem ipsum dolor.
        Lorem ipsum dolor. Lorem ipsum dolor. Lorem ipsum dolor.
    """

    ...


class ClassName:
    """
    <Multi-paragraph explaining what the class does, always try to
    use a base class architecture using ``abc.ABC`` to provide
    abstract and then inherit features to concrete class. The
    docstring can span multiple paragraphs.>

    :type  arg1: ...
    :param arg1: ...
    """

    def __init__(self, ...) -> None:
        ...


    def function(self, ...) -> ...:
        """
        <Follow the same function style docstring. Always explain what
        the function does.>
        """

        ...


    @property
    def my_property(self) -> ...:
        """
        <Follow the same function style docstring. Always explain what
        the function does.>
        """

        ...
```

Rules for docstring documentation:

  * Opening `"""` on its own line with the text starting on the next line, closing `"""` on its own line.
  * For attribute annotation use `:type  param: <type>` (two spaces before param name for alignment) followed by
    `:param arg: ...`. Always place one blank line between description and param block.
  * Separate every block (description, parameters, keyword arguments, examples, raises, and returns) with one blank
    line, and indent the continuation lines of a field by four spaces.
  * `:rtype:` then `:returns:` for return documentation. Also, use `:raises ...:` to document errors (if any) for the
    function.
  * If the function returns `None` (i.e. annotated `-> None`), omit the `:rtype:` and `:returns:` block entirely - do
    not document a `None` return.
  * Use double backticks for inline code in docstrings (for example ``` ``value`` ```). Use `:mod:`, `:class:`, `:func:`
    roles as in reStructuredText for cross-references.
  * Separate methods inside a class with two blank lines (flake8 `E303` is ignored).

### Comment Style

Do not put in-line comments unless the function block does a non-standard operation. Do not put comment to separate out
blocks of code unless you are explicitly asked to do so. Always use special tags as below for in-line comments when
doing a code refactoring or there is a major change (ignore for small changes).

```python
# ! critical / important note - something the reader must not miss
# ? informational note - explains a decision or points to a reference

# regular single-line comment - plain explanation

# .. versionchanged:: <yyyy-mm-dd> One Line Title Case Change Summary
```

Never add comments explaining obvious code. Only comment where intent is non-obvious, or does not follow standard
approach. A single space before an inline comment is allowed (flake8 `E261` is ignored).

### Comprehension Patterns

Keep a simple `list` or `dict` comprehension on one line, and split it across multiple lines only when it does not fit
the line limit. Never place a space just inside the brackets or braces (flake8 `E201` and `E202`). Example:

```python
days = [day for day in ... if ...]
days = {key : value for key, value in ... if ...}
```

## Module Structure & Rules

When working on a module, the following additional rules must be followed. A typical Python module directory structure
with important files is as follows:

```shell
.github/
    CODEOWNERS
    workflows/
        linting.yml # checks for code linting using .flake8
        publish.yml # auto-publish package in PyPI on GitHub Release
module/
    __init__.py
    api.py # public functions of the package
    submodule/
        __init__.py
        ...
    ...
    error/
        __init__.py
        exceptions.py
        warnings.py
    tests/
        __init__.py
        ...
.flake8
.gitignore
pyproject.toml
...
```

### Flake8 Configuration

The `.flake8` file in the project root is the linting standard for the code. The default configuration is
[`resources/.flake8.template`](./resources/.flake8.template), and its `extend-ignore` codes allow the spacing,
alignment, and blank line rules of this skill. Check the project root before writing any code and act as below:

  * **File is missing** - create `.flake8` from the template in the exact same layout. Replace `<package>` with the
    package name and `<additional-directory>` with a directory to skip (or remove that entry).
  * **File does not follow the template** - adjust it to the template layout (sections, comments, and indentation) while
    respecting every rule that is already in the file. Keep the existing `exclude`, `per-file-ignores`,
    `max-line-length`, and any other option values as they are - only adjust the structure.
  * **Existing `extend-ignore` codes** - never remove a code that is already in the file, even if the template does not
    have it. The final list is always the existing codes expanded with the template codes.
  * **Template codes missing from the file** - always ask the user for confirmation before adding them and proceeding
    further; never add them silently. If the user declines, keep the list as is and write code that passes the existing
    rules.

After writing code, run `flake8` (when available) on the changed files or package directories and fix every reported
violation. Never run a bare `flake8 .` - it also walks a virtual environment in the project root.

### Requirements Files

Create or update a requirements file **only** when the user asks for it - never create one automatically. Use
[`resources/requirements.txt.template`](./resources/requirements.txt.template) for runtime dependencies and
[`resources/requirements-dev.txt.template`](./resources/requirements-dev.txt.template) for development and linting
tools, and follow the same convention:

  * Open the file with a header comment that states its purpose and the exact `pip install` command.
  * Pin every package to an exact version (`package==x.y.z`) and write its name as published on PyPI, with any extras
    (for example `PyYAML` or `SQLAlchemy[asyncio]`).
  * Group packages under a `### Group Name ###` header with one blank line between groups, and keep packages without a
    comment in alphabetical order within the group.
  * Explain a package only when the reason is not obvious, in a comment directly above it - `# !` for a pin that must
    not move without re-verification, `# ?` for why or how the package is used. Put one blank line before each comment.
  * Keep development and linting tools in `requirements-dev.txt`, which starts with `-r requirements.txt` - anything in
    `requirements.txt` ships to production.
  * Keep every line of a requirements file within 79 characters.
  * When updating an existing file, apply the convention to the entries you add or change, and keep its existing
    groups, order, and comments unless the user asks to restructure it.

Test the requirements in a virtual environment **only** when the user asks for it (for example "test the environment",
"test the package", or "test the requirements"). Create the environment in a `venv` directory at the project root - if
`venv` already exists, ask the user before reusing or recreating it. Install with the command from the file's header
comment (including any flags such as `--only-binary=:all:`), then check for dependency conflicts:

```shell
$ python -m venv venv
$ venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
$ venv/bin/python -m pip check
```

On Windows, use `venv\Scripts\python` in place of `venv/bin/python`. When the user asks to test the package, also run
the project's test suite (for example `venv/bin/python -m pytest`) and `flake8` on the package directories from the same
environment.

### Module Level Initialization File

The module level initialization file (`module/__init__.py`) must follow the below snippet:

```python
# -*- encoding: utf-8 -*-

"""
<Short One-Line Summary of the Module - Use Title Case>
=======================================================

<Multi-paragraph description: what the module does, why it exists,
how it fits in the package architecture, and any important usage
notes. Always use proper sentence casing.>
"""

__version__ = "v1.0.0"

# init-time options registrations, use api.py for public functions

```

Do not create the directories from the structure above (such as `error/` or `tests/`) unless you are asked to. Always
try to use abstract methods (group abstract class under `submodule/base.py` file) whenever possible such that the code
can be easily extended.

## Quick Checklist Before Generating Python Code

  - [ ] Does the file start with a `# -*- encoding: utf-8 -*-` line and module docstring?
  - [ ] Are imports in the correct order (stdlib → third-party → local)?
  - [ ] Are all imports absolute (no relative imports)?
  - [ ] Do all type-hint annotations use a space before the colon (`name : type`)?
  - [ ] Does every function annotate its return type (`-> None` when nothing is returned)?
  - [ ] Is there a space before and after every mathematical operator?
  - [ ] Does every public method/class/function have a reST-style docstring?
  - [ ] Is there no em dash (`—`) in code, comments, or docstrings?
  - [ ] Are private methods prefixed with a single underscore (`_method`), never wrapped as `__method__`?
  - [ ] Is indentation consistently 4 spaces?
  - [ ] Are lines within the 70-character limit (up to a max. of 88 characters only for long words and links)?
  - [ ] Is PEP production style with DRY principle followed in writing code?
  - [ ] Is `.flake8` in the project root and aligned with the template (missing ignore codes confirmed by the user)?
  - [ ] Does the changed code pass `flake8` with the project configuration?
  - [ ] Was a requirements file created, updated, or tested in a `venv` only because the user asked for it?
  - [ ] Does every requirements file follow the templates (exact pins, `### Group ###` headers, `# !` / `# ?` notes)?
  - [ ] Did I use the Python agents the task needs when available - and when missing, did I ask the user (recommending
    the automatic fetch) before continuing?

</div>
