---
name: code-modification-rule
description: >-
  Adds dated modification annotations - `refactor`, `..versionadded::`, and `..versionchanged::` - to the header of a
  changed file, in the comment syntax of any programming language. Explicit-invoke only: apply it only when the user
  calls it (the /code-modification-rule command) or asks for it by name, never by default and never on its own
  initiative. It extends, and runs alongside, a language skill such as python-code-format or sql-code-format. Trigger
  phrases include the /code-modification-rule command, "add modification notes", "annotate the change", "add a
  versionadded note", "add a versionchanged note", and "add a refactor note". Sets up or checks the Better Comments
  extension only when the user explicitly asks for it.
---

<div align = "center">

# Code Modification Rule

</div>

<div align = "justify">

The skill records *what changed and when* directly in the header of a modified file, with three annotations in
reStructuredText style. It is language-agnostic: an annotation uses the comment marker of the file's language, so the
same rule works for SQL, Python, JavaScript, and any other language. It is an **extension**, applied only when the
user explicitly invokes it; alongside a language skill, the language skill decides the header layout and the line
limits, and this skill only adds the annotation lines.

## Getting Started

  1. Apply the skill only when it is explicitly invoked (`/code-modification-rule`, or the user asks for it by name).
     Never add an annotation on your own, and never as the default of another skill.
  2. Read the **entire** target file and its header. When a language skill is active, follow its header layout and line
     limits.
  3. Pick the annotation for each change (see **Annotations**) and write it as the last lines of the header, above its
     closing line.
  4. Recommend the Better Comments extension (see **Better Comments**); set it up or check it only when the user
     explicitly asks.

## Annotations

Use the below annotations, in reStructuredText docstring style, as the last lines of the header (above the closing
line) using the below template for the use cases:

<div align = "center">

| Annotation | Use When | Example |
| :---: | --- | :---: |
| `refactor` | The code was restructured without changing what it does | `refactor 2026-10-29 Split the loader in two.` |
| `..versionadded::` | A new field, column, parameter, function, or option was added | `..versionadded:: 2026-10-29 Added is_active.` |
| `..versionchanged::` | An existing field or behaviour was changed | `..versionchanged:: 2026-10-29 Rounds to four places.` |

</div>

Every annotation follows the same template - `<comment-marker> <annotation> <YYYY-MM-DD> <short-description>`:

  * Write the annotation exactly as listed in the table.
  * Use the date of the change in ISO format (`YYYY-MM-DD`), today's date for a new change.
  * Keep the description to one short sentence that fits the line limit of the language skill.
  * Write one annotation per change, the newest last, and never edit or delete an earlier annotation.
  * When the file has no header, ask the user whether to add one (following the language skill) before annotating it.

## Comment Markers

Inside a header that is a block comment, start the annotation with the line-comment marker of the language; inside a
docstring header (Python) or the block comment of a language without a line-comment marker, write it bare at the start
of the line:

<div align = "center">

| Language Family | Marker | Annotation Line |
| :---: | :---: | :---: |
| SQL, Lua, Haskell | `--` | `-- ..versionadded:: <date> <description>` |
| C, C++, C#, Java, JavaScript, TypeScript, Go, Rust, Kotlin, Swift, PHP | `//` | `// ..versionadded:: <date> <description>` |
| Shell, R, Ruby, Perl, YAML, TOML, PowerShell | `#` | `# ..versionadded:: <date> <description>` |
| LaTeX, MATLAB, Erlang | `%` | `% ..versionadded:: <date> <description>` |
| Lisp, Clojure, INI, Assembly | `;` | `; ..versionadded:: <date> <description>` |
| Python (docstring header), HTML, XML, Markdown, CSS | none | `..versionadded:: <date> <description>` |

</div>

For example, in the header of a SQL file:

```sql
/*********************************************************************
<Description of the object, as the language skill requires.>

-- ..versionadded:: 2026-10-14 Vendor text, unit and active flags.
-- ..versionchanged:: 2026-10-29 Prices now keep four decimals.
*********************************************************************/
```

A language skill may also place an annotation as an in-line comment at the change itself (`python-code-format` does);
when that skill is active, follow its placement as well.

## Comment Tags

These are the five default tags of Better Comments, which any comment can start with; they are colored as soon as the
extension is installed:

<div align = "center">

| Tag | Meaning | Example |
| :---: | --- | :---: |
| `!` | A critical note the reader must not miss | `# ! Run before the seed files.` |
| `?` | An informational note that explains a decision or points to a reference | `# ? See the vendor docs.` |
| `*` | A highlighted note | `// * Hot path - keep it simple.` |
| `todo` | Work that is still to do | `-- todo: add the retry.` |
| `//` | Commented-out code, shown struck through | `# // old_call()` |

</div>

## Better Comments

This skill was developed for the [Better
Comments](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments) extension of VS Code
(`aaron-bond.better-comments`), which colors a comment by its leading tag, so the annotations and tags above stand out
from the code. Recommend installing it once, when the annotations are first written - never install it yourself.

NOTE: Out of the box, Better Comments highlights only its five default tags (`!`, `?`, `//`, `todo`, and `*`). The
annotation tags of this skill (`refactor`, `..versionadded::`, `..versionchanged::`) are **additional** tags, colored
only once they are in the `better-comments.tags` setting of VS Code. The setting lists every tag with its color:

<div align = "center">

| Tag | Color | Kind |
| :---: | :---: | :---: |
| `!` | `#FF2D00` | Default |
| `?` | `#3498DB` | Default |
| `//` | `#474747` | Default |
| `todo` | `#FF8C00` | Default |
| `*` | `#98C379` | Default |
| `refactor` | `#D19184` | Annotation |
| `..versionadded::` | `#2F7694` | Annotation |
| `..versionchanged::` | `#2F7694` | Annotation |

</div>

Every entry of the setting has the same shape, and only `//` is struck through (`"strikethrough": true`):

```json
{
    "tag": "..versionadded::",
    "color": "#2F7694",
    "strikethrough": false,
    "underline": false,
    "backgroundColor": "transparent",
    "bold": false,
    "italic": false
}
```

Set up, sync, or share the tags only when the user explicitly asks for it, with the Better Comments
[hooks](https://github.com/PyUtility/polyskills/tree/master/extensions/hooks/Better%20Comments%20%28VS%20Code%20Extension%29)
of this repository: `pull.py` syncs the tags into the VS Code settings, and `push.py` proposes the tags added locally as
a pull request.

## Working With Other Skills

  * The skill never runs on its own; invoke it explicitly, alone or with a language skill, for example
    `/sql-code-format /code-modification-rule` or `/python-code-format /code-modification-rule`.
  * The language skill owns the header layout, its width, and the line limits; this skill only adds annotation lines
    inside them.
  * When a language skill defines its own annotation placement, follow both: the header lines of this skill and the
    in-line comments of the language skill.

## Quick Checklist

  - [ ] Was the skill explicitly invoked, never applied by default?
  - [ ] Is every annotation `refactor`, `..versionadded::`, or `..versionchanged::`, written exactly as listed?
  - [ ] Does every annotation carry an ISO date and one short description?
  - [ ] Are the annotations the last lines of the header, above its closing line, with the newest last?
  - [ ] Does every annotation use the comment marker of the language (or none in a docstring or block-only comment)?
  - [ ] Does every line respect the line limit of the active language skill?
  - [ ] Did I leave every earlier annotation untouched?
  - [ ] Did I recommend Better Comments without installing it, and run the hooks only on explicit request?

</div>
