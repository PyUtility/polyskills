---
name: markdown-format
description: >-
  Governs all Markdown file creation, editing, reviews, and modification. Always read the file in full before writing or
  modifying any Markdown content, even for a small change. The skill applies the exact conventions visible throughout
  this repository: `<div align = "center">` title banners, `<div align = "justify">` body wrappers, Shields.io badges,
  emoji section headings (README-tier files only), `:---:` centred table columns, 2-space indented lists and checklists,
  ATX-style headings, and fenced code blocks with explicit language specifiers. Use this skill when the user asks to
  create, edit, update, or review any `*.md` file - including `README.md`, `SKILL.md`, `AGENT.md`, `CHANGELOG.md`, and
  documentation pages. Trigger phrases: "create/edit/update the readme", "write documentation", "update the markdown",
  "add a changelog entry", "create a skill file", "create an agent file".
---

<div align = "center">

# Markdown Format

</div>

<div align = "justify">

This skill governs every `*.md` file in the repository: `README.md`, `SKILL.md`, `AGENT.md`, `CHANGELOG.md`, and any
other documentation page. Read the **entire** target file before making any change, even a single-line edit. Apply every
rule below before generating output. Two files are exceptions: `CLAUDE.md` (see **CLAUDE.md Exception**) and
`CODE_OF_CONDUCT.md`, which is copied verbatim from its template (see **CODE_OF_CONDUCT.md**).

## Getting Started

  1. Read the **entire** target file first - understand the existing headings, div structure, badge order, and list
     style.
  2. Identify the *file role* (README, SKILL/AGENT, CHANGELOG, `CODE_OF_CONDUCT.md`, `CLAUDE.md`, or general doc) -
     each has distinct layout rules.
  3. Always follow the conventions in this skill. Never invent new layout patterns.
  4. Apply every rule before generating output. Never skip reading the skill even for a small change.

## Universal Rules (All `*.md` Files)

These rules apply to every Markdown file regardless of role.

### Line Length

  * Wrap every line at **120 characters** by default - hard-wrap prose, list items, and continuation lines at or before
    column 120, preserving the existing indentation on continuation lines. The frontmatter `description` block follows
    the same limit.
  * A line may extend up to the **hard maximum of 128 characters** only for long words and links (a URL, a file path, or
    an inline-code span) that would otherwise be split. Never let a wrappable line run past 128 characters.
  * Exceptions: a table row, a Shields.io badge line, and a line inside a fenced code block cannot be wrapped - keep
    these intact even when they exceed 128 characters.

### HTML Div Wrappers

Every Markdown file in this repository (except `CLAUDE.md`) uses two HTML div wrappers. Always include both and never
merge them.

```markdown
<div align = "center">

# Title in Title Case

</div>

<div align = "justify">

Body content goes here.

<div align = "center">

| Column | Column |
| :---: | --- |
| Value | Value |

</div>

More body content.

</div>
```

Rules for div wrappers:

  * Always put a space before and after the `=` operator: `<div align = "center">` not `<div align="center">`.
  * Always put a blank line immediately after the opening `<div ...>` tag and immediately before the closing `</div>`
    tag.
  * The top `center` div contains **only** the primary heading and, in a README, optional badges - never body text.
  * The `justify` div wraps the **entire** body from the first section heading to the last paragraph.
  * Wrap every table in its own `<div align = "center">` block nested inside the `justify` div - the only div allowed
    inside the body.

### Headings

  * Use ATX style (`#` prefix) exclusively - never setext underline style.
  * Use exactly one `#` (H1) heading per file - the title. Every other heading is `##` or deeper.
  * Use Title Case for all heading text.
  * The primary heading (`# Title`) lives inside the `center` div only; all section headings (`##`, `###`) live inside
    the `justify` div.
  * Do not skip heading levels (i.e. do not go from `##` straight to `####`).
  * Horizontal rules (`---`) may be used to visually separate major top-level sections within the `justify` div.

### Lists and Checklists

  * Unordered lists use `  * ` (two spaces + asterisk + space).
  * Ordered lists use `  1. ` (two spaces + number + period + space), numbered in sequence (`1.`, `2.`, `3.`).
  * Checklists use `  - [ ] ` (two spaces + hyphen + space + brackets + space).
  * Indent sub-items by four additional spaces relative to the parent item.
  * Separate a list from the preceding paragraph with a single blank line and from the following paragraph with a single
    blank line.

### Tables

Center every column with `:---:`, except a descriptive or remarks column, which is left-aligned with `---`:

<div align = "center">

| Column Type | Alignment Specifier | When to Use |
| :---: | :---: | --- |
| Label, identifier, enum, number, or short value | `:---:` (centered) | Every column that is not prose |
| Description, remarks, or prose | `---` (left-aligned) | Sentences and explanatory text |

</div>

  * Never use `:---` or `---:` - a column is either centered or a left-aligned descriptive column.
  * Wrap every table in a `<div align = "center">` block inside the `justify` div (see **HTML Div Wrappers**).
  * Always include a header row and a separator row.
  * Pad cells with a single space on each side: `| content |` not `|content|`.
  * Do not use HTML tables - use Markdown pipe tables only.

### Code Blocks

  * Always use triple-backtick fenced blocks - never indented code blocks.
  * Always specify the language identifier on the opening fence. Use `text` for plain terminal output or unknown
    formats.
  * Common language identifiers used in this repo: `python`, `sql`, `shell`, `json`, `markdown`, `yaml`, `text`.
  * When a format skill exists for the language in a code block (for example `python-code-format` for `python` blocks or
    `sql-code-format` for `sql` blocks), the code inside the block must follow that skill's rules - spacing, naming,
    docstrings, and its own line-length limit - exactly as in a source file.
  * Prefix interactive shell commands with `$` inside `shell` blocks.

### Emphasis and Inline Code

<div align = "center">

| Markup | Use Case | Examples |
| :---: | --- | --- |
| `` `backtick` `` | Inline code, file paths, CLI args, config keys | `` `SKILL.md` ``, `` `--token` ``, `` `main()` `` |
| `*single asterisk*` | Technical terms on first use, module/package names | `*bundled package*`, `*open standard*` |
| `**double asterisk**` | Important callouts, required keyword args, warnings | `**name**`, `**Parallel**` |
| `~~strikethrough~~` | Deprecated content only | |

</div>

  * Do not use em dashes (`—`) - use a hyphen-minus (`-`) always.
  * Do not use HTML `<b>`, `<i>`, `<em>`, `<strong>` inline - use Markdown emphasis only.

### Links

  * Always use inline style: `[visible text](url)` - never bare URLs, never reference-style links.
  * For local files use relative paths: `[SKILL.md](python-code-format/SKILL.md)`.
  * For external links include the full `https://` scheme.

## README.md Layout

`README.md` files (top-level and directory-level) follow this specific layout on top of the universal rules.

### Structure Template

```markdown
<div align = "center">

# Title in Title Case

[![Badge One](badge-url)](link-target)
[![Badge Two](badge-url)](link-target)

</div>

<div align = "justify">

Short one-paragraph description of what the directory or project contains.

## 🚀 Section One

...

## 📦 Section Two

...

</div>
```

### Badge Style

All badges use the Shields.io static badge format with these fixed parameters:

```text
https://img.shields.io/badge/<Label>-%20<Text>-<COLOR>?style=plastic&logo=<LOGO>
```

  * Add badges only when creating or editing a `README.md` - never add them to any other file. If another file already
    has badges, keep them and apply the rules below to them.
  * `style=plastic` is mandatory - never use `flat`, `flat-square`, or `for-the-badge`.
  * Color each badge with the **official brand color** of the tool, service, or technology it represents - set both the
    `<COLOR>` segment and the matching `&logo=<LOGO>` slug to that brand.
  * When a badge has no associated brand (for example the `HOOKS`, `SKILLS`, `AGENTS`, and `COMMANDS` count badges in
    the root `README.md`), pick any distinct color - a Shields.io named color such as `purple`, `orange`, `red`, or
    `blue`, or a hex value - that no other badge in the same group already uses.
  * Use `%20` to encode spaces within label or text segments.
  * Place all badges inside the `center` div, each on its own line, with a blank line between the heading and the first
    badge block.
  * Wrap every badge in a link to the relevant file or URL: `[![Label](badge-url)](target-link)`.

Common brand colors used in this repo (hex without the leading `#`, paired with the Shields.io logo slug):

<div align = "center">

| Brand / Service | Color | Logo Slug |
| :---: | :---: | :---: |
| Python | `3776AB` | `python` |
| PyPI | `3775A9` | `pypi` |
| Git | `F05032` | `git` |
| GitHub | `181717` | `github` |
| GitHub Actions | `2088FF` | `githubactions` |
| PostgreSQL | `4169E1` | `postgresql` |
| SQLite | `003B57` | `sqlite` |
| Markdown | `000000` | `markdown` |
| Grammarly | `15C39A` | `grammarly` |
| Starship | `DD0B78` | `starship` |
| Anthropic / Claude | `D97757` | `anthropic` |

</div>

For any brand not listed here, use the color from that project's brand guidelines or its
[Simple Icons](https://simpleicons.org) entry.

### Section Emoji Prefix

Emoji prefixes belong only on `##` headings of README-tier files, and only when the file already uses them. If any `##`
heading in the file has an emoji, give every `##` heading a single emoji prefix; if none does, do not add emoji. Pick an
emoji that is semantically related to the section's content and is not already used by another section in the same
file. Common assignments in this repo:

<div align = "center">

| Emoji | Typical Section Title |
| :---: | :---: |
| 🧠 | Introduction, Background |
| 🚀 | Getting Started, Quick Start |
| 🤖 | Project Capabilities, Agents |
| ⚖️ | License |
| ⚠️ | Disclaimer, Warnings |
| 🧭 | Orchestration, Navigation |
| 📦 | Installation, Registration |
| 🧪 | Testing, Verification |

</div>

  * Never use emoji on `###` or deeper headings - only `##` headings carry an emoji.
  * Do **not** use emoji in `SKILL.md`, `AGENT.md`, `CHANGELOG.md`, or `CLAUDE.md` section headings.

## SKILL.md and AGENT.md Layout

`SKILL.md` and `AGENT.md` files follow the universal rules plus these specific requirements.

### YAML Frontmatter

Every `SKILL.md` and `AGENT.md` must open with YAML frontmatter between `---` markers:

```yaml
---
name: skill-or-agent-name
description: >-
  One or more sentences that tell the LLM *when* to invoke this skill or agent. Include specific trigger phrases at the
  end. The description can span multiple indented lines - use 2-space indent for continuation lines.
---
```

Rules for frontmatter:

  * `name` must be kebab-case and match the directory name exactly.
  * `description` must include concrete trigger phrases so the LLM can auto-invoke.
  * Never add extra frontmatter keys beyond `name` and `description` unless the Agent-Skills standard explicitly
    supports them (e.g. `allowed-tools`).
  * The frontmatter block must be the very first content in the file - no blank line before the opening `---`.

### Body Structure

After the frontmatter, follow this section order:

  1. `<div align = "center">` containing `# Skill/Agent Name` (Title Case, matching `name` in frontmatter).
  2. `<div align = "justify">` containing at minimum: a short intro paragraph, **Getting Started** (numbered rules),
     main content sections, and a **Quick Checklist** at the very end.
  3. The **Quick Checklist** must use `  - [ ]` items and test the most likely failure modes.

  * Do **not** use emoji prefixes in `SKILL.md` or `AGENT.md` section headings.
  * Do **not** add a `---` horizontal rule between sections in SKILL/AGENT files - reserve those for README-tier files.

## CHANGELOG.md Layout

Build a new `CHANGELOG.md`, or restructure an existing one when the user asks, from
[`resources/CHANGELOG.md.template`](./resources/CHANGELOG.md.template). The template is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and carries two variants:

  * **Python project** - keep the `{PYTHON: ...}` text (the project adheres to PEP 440) and the
    `{{ ### FOR PYTHON PROJECT:: ... }}` block, a collapsible `PEP0440` Styling Guide with the PyPI-to-semver mapping
    table.
  * **Non-Python project** - keep the `{NOT PYTHON: ...}` text (the project adheres to Semantic Versioning) and drop the
    Python-only block.

Detect the variant from the project - a `pyproject.toml`, `setup.py`, or `setup.cfg` marks a Python package. If it is
unclear (no packaging file, or a mixed-language repository), ask the user which variant to use before writing the file.
Then:

  * Remove the variant markers and replace every placeholder (`{repository}`, `v{}`, the release title and date, and
    the `<...>` descriptions).
  * Keep the **Release Note(s)** section and its collapsible legend: 🎉 major feature, ✨ feature enhancement, 🛠️
    patch/fix, ⚙️ code efficiency, and 💣 code refactoring.
  * Give each `major.minor` release a `###` heading, `` ### <Release Title> | `vX.Y.Z` (<yyyy-mm-dd>) ``, followed by a
    short description and a `  * ` list whose items start with the matching legend emoji. Patch (`micro`) releases and
    version identifiers go under `####` headings.
  * Add the newest release at the top of the release notes. Legend emoji start list items - never put them in headings.

## CODE_OF_CONDUCT.md

Create a `CODE_OF_CONDUCT.md` only when the user asks for one. Copy
[`resources/CODE_OF_CONDUCT.md.template`](./resources/CODE_OF_CONDUCT.md.template) exactly - it is the
[Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct.html) as published in the
[typhed `.github` repository](https://github.com/typhed/.github/blob/master/.github/CODE_OF_CONDUCT.md). Do not apply
the other rules in this skill to it: its reference-style links, list markers, line wrapping, and Contributor Covenant
badge stay exactly as they are. Never edit an existing `CODE_OF_CONDUCT.md` unless the user asks.

## CLAUDE.md Exception

`CLAUDE.md` (and `CLAUDE.local.md`) is not a page for people to read. Claude Code loads it into the model context as
instructions at the start of every session - every `CLAUDE.md` from the working directory up to the root, plus one in a
subdirectory when Claude works on files there (see the [Claude Code memory
docs](https://code.claude.com/docs/en/memory)). Decoration in this file costs context on every request, and some syntax
has a special meaning, so this skill governs it only in part. When creating or editing a `CLAUDE.md`:

  * Do **not** add the `center` and `justify` div wrappers, badges, or emoji heading prefixes. Only block-level HTML
    comments (`<!-- ... -->`) are stripped before loading; any other HTML reaches the model as raw text.
  * Do **not** add YAML frontmatter. It has no meaning in `CLAUDE.md` - only `.claude/rules/*.md` files read
    frontmatter, and only the `paths:` field.
  * Any `@path` outside a code span or fenced code block is parsed as an import of that file. Keep real imports outside
    code, and wrap every other literal `@` (an @-handle, a decorator) in backticks.
  * Keep the file short and specific - the official guidance is under 200 lines, using plain headings and bullet lists.
  * Claude Code edits the file itself (`/init`, or a request to remember something), so keep a flat layout that new
    content can be appended to.
  * The remaining universal rules still apply: ATX headings in Title Case, `  * ` lists, fenced code blocks with a
    language, inline links, no em dash, and the 120-character line limit.

## Quick Checklist Before Generating Markdown

  - [ ] Did I read the entire target file before making any change?
  - [ ] Is the `<div align = "center">` banner present with a blank line after the opening tag?
  - [ ] Is the `<div align = "justify">` wrapper present with a blank line before the closing tag?
  - [ ] Are all headings in Title Case and using ATX (`#`) style?
  - [ ] Are lines within the 120-character limit (up to a max. of 128 characters only for long words and links)?
  - [ ] Is there exactly one `#` (H1) heading in the file?
  - [ ] In `README.md`, are emoji used only on `##` headings, and only when the file's `##` headings already use them?
  - [ ] Are badges used only in a `README.md` (or where a file already has them), with `style=plastic`, their brand
    color (or a distinct color without a brand), and a link?
  - [ ] Do all fenced code blocks have an explicit language specifier?
  - [ ] Does the code in each block follow the format skill for its language (if one exists)?
  - [ ] Are unordered list items using `  * ` (2 spaces + asterisk)?
  - [ ] Are checklists using `  - [ ] ` (2 spaces + hyphen)?
  - [ ] Is every table wrapped in its own `<div align = "center">` block inside the `justify` div?
  - [ ] Is every table column centered (`:---:`) except descriptive or remarks columns (`---`), with no `:---` or
    `---:`?
  - [ ] Is there no em dash anywhere - only hyphen-minus (`-`)?
  - [ ] Does `SKILL.md` / `AGENT.md` have a YAML frontmatter block as the very first content?
  - [ ] Does the `name` key in frontmatter match the directory name in kebab-case?
  - [ ] Was a `CHANGELOG.md` built from the template, with the Python or non-Python variant confirmed with the user when
    unclear?
  - [ ] Was a `CODE_OF_CONDUCT.md` created only on request and copied verbatim from the template?
  - [ ] Is a `CLAUDE.md` free of div wrappers, badges, emoji headings, and frontmatter, with every literal `@` in
    backticks?

</div>
