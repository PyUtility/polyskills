---
name: python-code-format
description:
    Governs all Python code formatting, editing, reviews, modification, and creation from scratch. Always read the file in full
    before writing or modifying Python code, even for a small change. Use this skill when a user asks to create, edit, update,
    review or modify any content of a '*.py' file, or any Python code in a project that references this skill.
---

<div align = "center">

# Python Code Format

</div>

<div align = "justify">

This skill analyzes Python coding patterns and applies them consistently when creating, editing, or modifying Python files.
The skill is to be used when you are working with a `*.py` file extension.

## Getting Started

Before making any change to a `*.py` file, always use 4 spaces indentation (mandatory). Always use production style coding, and
try to reuse already existing codes (DRY principle of coding).

  1. Read the **entire** target file first - understand context, imports, and existing style.
  2. Always follow PEP standard to write production grade codes.
  3. Always check if .flake8 file is present and follow the linting standard.
  4. Apply every rule before generating output. Read the entire skill file.

Never skip reading the skill or reference even for small changes.

## Naming Convention

| Element/Attribute Name | Naming Convention | Example Names | Additional Remark(s) |
| :---: | :---: | :---: | --- |
| Module Files | `snake_case` | `calendar.py` | Try to use single word names. |
| Class Names | `PascalCase` | `LeavePlanner` `PersonConstruct` | |
| Function Names | `snake_case` | `long_weekends()` | |
| Private Method | `__double_underscore__` | `__generate_key__` | |
| Variable Names | `snake_case` | `first_name` | |
| Constants or ENUM Members | `SCREAMING_SNAKE_CASE` | `MONDAY` | |
| Loop/Comprehension Variables | Short Meaningful Name | `cur` `idx` `nxt` `key` `value` | |

## Critical & Mandatory Rules

These rules are critical and mandatory. Always double check these rules are followed and maintained across the code or module
directory. The rules are always mandatory.

### File Header Rules

Every entry `*.py` file must begin with a module-level docstring that must follow the `reStructuredText` and `sphinx` rules. The
code documents will be generated using `sphinx` with `myst_parser` extension. Always follow the basic snippet.

```python
# -*- encoding: utf-8 -*-

"""
<Short One-Line Summary of the Module - Use Title Case>

<Multi-paragraph description: what the module does, why it exists,
how it fits in the package architecture, and any important usage
notes. Always use proper scentence casing.>

:NOTE: <Any critical behavioral notes or caveats.>
"""

import ...
```

Rules for import statements:

  * Standard library first, then third-party, then local imports.
  * Use standard alias names for module imports (like `import datetime as dt` `import pandas as pd`)
  * Always use absolute package paths - no relative imports.

### Type Hinting

Always use type hints for input attributes and output for functions. Always place a space before and after the colon and equal
sign for type hints. Example:

```python
def function(arg1 : int, arg2 : str, ..., argN : int = 10, ...) -> float:
    ...
```

If a function does not return anything, then explictly mention `-> None` in output type hint. Always use `typing` module for
type hints for `Tuple`, `Callable`, `List`, and `Dict` attributes. Always annotate **every** parameter and return type.

### Keyword Arguments & Field Constrints - Spacing Rule

Always place spaces around every mathematical operators. Try to use `enum.Enum` for constants that needs to grouped. Example
of spacing around keywords, field constraints, etc. are as below.

```python
...

from pydantic import Field

x = (10 + 20) / 30
y : float = Field(..., ge = 10, le = 10)
```

### Docstring Format

Use `reStructuredText` style docstring always. Ensure that you always use "-" instead of "—" (never use em dash - mandatory).
Example of docstring style for different sections are as below:

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

        * **kwarg1** (*int*): ...

    **Example Usage**

    <For exach example, provide a short 2-3 lines summary about the
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
    use a base class architecutre using `abc.ABC` to provide abstract
    and then inherit features to concrete class. The docstring can
    span multiple paragraphs.>

    :type  arg1: ...
    :param arg1: ...
    """

    def __init__(self, ...) -> None:
        ...


    def function(self, ...) -> ...:
        """
        <Follow the same function style docsrting. Always explain what
        the function does.>
        """

        ...


    @property
    def my_property(self) -> ...:
        """
        <Follow the same function style docsrting. Always explain what
        the function does.>
        """

        ...
```

Rules for docstring documentation:

  * Opening `"""` on same line as start, closing `"""` on its own line.
  * For attribute annotation use `:type  param: <type>` (two spaces before param name for alignment) followed by `:param arg: ...`.
    Always place one blank line between description and param block.
  * `:rtype:` then `:return:` for return documentation. Also, use `:raises ...:` to document errors (if any) for the function.
  * Use ``backticks`` for inline code references in docstrings. Use `:mod:`, `:class:`, `:func:` block as in reStructuredText
    for cross-references.

### Comment Style

Do not put in-line comments unless the function block does a non-standard operation. Do not put comment to separate out blocks
of code unless you are explictly asked to do se. Always use special tags as below for in-line comments when doing a code
refactoring or there is a major change (ignore for small changes).

```python
# ! critical / important note - something the reader must not miss
# ? informational / curiosity note - explains a decision or points to a reference

# regular single-line comment - plain explanation

# ..versionchanged:: <yyyy-mm-dd> Single Line Title Case Explain Change
```

Never add comments explaining obvious code. Only comment where intent is non-obvious, or does not follow standard approach.

### Comprehension Patterns

Simple `list`, `dict` comprehension can be kept inline but can span multiple lines when short and easily understood. Example
for comprehension is as below.

```python
days = [ day for day in ... if ... ]
days = { key : value for key, value in ... if ... }
```

## Module Structure & Rules

When working on a module, the following additional rules must be followed. A typical Python module directory structure with
important files are as follows:

```shell
.github/
    CODEOWNERS
    workflows/
        linting.yml # checks for code linting using .flake8
        publish.yml # auto-publish package in PyPI on GitHub Release
module/
    __init__.py
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

### Module Level Initialization File

The module level initialization file (`module/__init__.py`) must follow the below snippet:

```python
# -*- encoding: utf-8 -*-

"""
<Short One-Line Summary of the Module - Use Title Case>
=======================================================

<Multi-paragraph description: what the module does, why it exists,
how it fits in the package architecture, and any important usage
notes. Always use proper scentence casing.>
"""

__version__ = "v1.0.0"

# init-time options registrations, use api.py for public functions

```

Do not create default directory unless you are asked to do so. Always try to use abstract methods (group abstract class under
`submodule/base.py` file) whenever possible such that the code can be easily extended.

## Quick Checklist Before Generating Python Code

  - [ ] Does the file start with a `# -*- encoding: utf-8 -*-` line and module docstring?
  - [ ] Are imports in the correct order (stdlib → third-party → local)?
  - [ ] Do all type-hint annotations use a space before the colon (`name : type`)?
  - [ ] Is there a space before and after all mathematical operator?
  - [ ] Does every public method/class/function have a reST-style docstring?
  - [ ] Are private methods prefixed with double underscores `__method__`?
  - [ ] Is indentation consistently 4 spaces?
  - [ ] Are lines within the 88-character limit?
  - [ ] Is PEP production style with DRY principle followed in writing code?
  - [ ] Check for .flake8 raise error if file is present in the root of the project.

</div>
