---
name: markdown-format
description: >-
  Governs all Markdown file creation, editing, reviews, and modification. Always read the file in full before writing or
  modifying any Markdown content, even for a small change. The skill applies the exact conventions visible throughout this
  repository: `<div align = "center">` title banners, `<div align = "justify">` body wrappers, Shields.io badges, emoji
  section headings (README-tier files only), `:---:` centred table columns, 2-space indented lists and checklists, ATX-style
  headings, and fenced code blocks with explicit language specifiers. Use this skill when the user asks to create, edit,
  update, or review any `*.md` file - including `README.md`, `SKILL.md`, `AGENT.md`, `CHANGELOG.md`, and documentation
  pages. Trigger phrases: "create/edit/update the readme", "write documentation", "update the markdown",
  "add a changelog entry", "create a skill file", "create an agent file".
---

<div align = "center">

# Markdown Format

</div>

<div align = "justify">

This skill governs every `*.md` file in the repository: `README.md`, `SKILL.md`, `AGENT.md`, `CHANGELOG.md`, and any other
documentation page. Read the **entire** target file before making any change, even a single-line edit. Apply every rule
below before generating output.

## Getting Started

  1. Read the **entire** target file first - understand the existing headings, div structure, badge order, and list style.
  2. Identify the *file role* (README, SKILL/AGENT, CHANGELOG, or general doc) - each has distinct layout rules.
  3. Always follow the conventions in this skill. Never invent new layout patterns.
  4. Apply every rule before generating output. Never skip reading the skill even for a small change.

---

## Universal Rules (All `*.md` Files)

These rules apply to every Markdown file regardless of role.

### HTML Div Wrappers

Every Markdown file in this repository uses two HTML div wrappers. Always include both and never merge them.

```markdown
<div align = "center">

# Title in Title Case

</div>

<div align = "justify">

Body content goes here.

</div>
```

Rules for div wrappers:

  * Always put a space before and after the `=` operator: `<div align = "center">` not `<div align="center">`.
  * Always put a blank line immediately after the opening `<div ...>` tag and immediately before the closing `</div>` tag.
  * The `center` div contains **only** the primary heading and optional badges - never body text.
  * The `justify` div wraps the **entire** body from the first section heading to the last paragraph.

### Headings

  * Use ATX style (`#` prefix) exclusively - never setext underline style.
  * Use Title Case for all heading text.
  * The primary heading (`# Title`) lives inside the `center` div only; all section headings (`##`, `###`) live inside
    the `justify` div.
  * Do not skip heading levels (i.e. do not go from `##` straight to `####`).
  * Horizontal rules (`---`) may be used to visually separate major top-level sections within the `justify` div.

### Lists and Checklists

  * Unordered lists use `  * ` (two spaces + asterisk + space).
  * Ordered lists use `  1. ` (two spaces + number + period + space) for every item - let the renderer auto-increment.
  * Checklists use `  - [ ] ` (two spaces + hyphen + space + brackets + space).
  * Indent sub-items by four additional spaces relative to the parent item.
  * Separate a list from the preceding paragraph with a single blank line and from the following paragraph with a single
    blank line.

### Tables

Use this column alignment pattern consistently:

| Column Type | Alignment Specifier | When to Use |
| :---: | :---: | --- |
| Label / identifier / enum | `:---:` (centered) | Short categorical values |
| Description / prose | `---` (left-aligned) | Explanatory text |
| Numeric (counts, sizes) | `---:` (right-aligned) | Numbers for comparison |

  * Always include a header row and a separator row.
  * Pad cells with a single space on each side: `| content |` not `|content|`.
  * Do not use HTML tables - use Markdown pipe tables only.

### Code Blocks

  * Always use triple-backtick fenced blocks - never indented code blocks.
  * Always specify the language identifier on the opening fence. Use `text` for plain terminal output or unknown formats.
  * Common language identifiers used in this repo: `python`, `sql`, `shell`, `json`, `markdown`, `yaml`, `text`.
  * Prefix interactive shell commands with `$` inside `shell` blocks.

### Emphasis and Inline Code

| Markup | Use Case | Examples |
| :---: | :---: | --- |
| `` `backtick` `` | Inline code, file paths, CLI args, config keys | `` `SKILL.md` ``, `` `--token` ``, `` `main()` `` |
| `*single asterisk*` | Technical terms on first use, module/package names | `*bundled package*`, `*open standard*` |
| `**double asterisk**` | Important callouts, required keyword args, warnings | `**name**`, `**Parallel**` |
| `~~strikethrough~~` | Deprecated content only | |

  * Do not use em dashes (`-`) - use a hyphen-minus (`-`) always.
  * Do not use HTML `<b>`, `<i>`, `<em>`, `<strong>` inline - use Markdown emphasis only.

### Links

  * Always use inline style: `[visible text](url)` - never bare URLs, never reference-style links.
  * For local files use relative paths: `[SKILL.md](python-code-format/SKILL.md)`.
  * For external links include the full `https://` scheme.

---

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

  * `style=plastic` is mandatory - never use `flat`, `flat-square`, or `for-the-badge`.
  * The color `003B57` (dark teal blue) is the default for skill and agent badges in this repo.
  * Use `%20` to encode spaces within label or text segments.
  * Place all badges inside the `center` div, each on its own line, with a blank line between the heading and the first
    badge block.
  * Wrap every badge in a link to the relevant file or URL: `[![Label](badge-url)](target-link)`.

### Section Emoji Prefix

README-tier files use a single emoji prefix on every `##` section heading. Pick an emoji that is semantically related to
the section's content and is not already used by another section in the same file. Common assignments in this repo:

| Emoji | Typical Section Title |
| :---: | --- |
| 🧠 | Introduction, Background |
| 🚀 | Getting Started, Quick Start |
| 🤖 | Project Capabilities, Agents |
| ⚖️ | License |
| ⚠️ | Disclaimer, Warnings |
| 🧭 | Orchestration, Navigation |
| 📦 | Installation, Registration |
| 🧪 | Testing, Verification |

  * Do **not** use emoji prefixes on `###` or deeper sub-headings.
  * Do **not** use emoji in `SKILL.md`, `AGENT.md`, or `CHANGELOG.md` section headings.

---

## SKILL.md and AGENT.md Layout

`SKILL.md` and `AGENT.md` files follow the universal rules plus these specific requirements.

### YAML Frontmatter

Every `SKILL.md` and `AGENT.md` must open with YAML frontmatter between `---` markers:

```yaml
---
name: skill-or-agent-name
description:
  One or more sentences that tell the LLM *when* to invoke this skill or agent. Include specific trigger phrases at the
  end. The description can span multiple indented lines - use 2-space indent for continuation lines.
---
```

Rules for frontmatter:

  * `name` must be kebab-case and match the directory name exactly.
  * `description` must include concrete trigger phrases so the LLM can auto-invoke.
  * Never add extra frontmatter keys beyond `name` and `description` unless the Agent-Skills standard explicitly supports
    them (e.g. `allowed-tools`).
  * The frontmatter block must be the very first content in the file - no blank line before the opening `---`.

### Body Structure

After the frontmatter, follow this section order:

  1. `<div align = "center">` containing `# Skill/Agent Name` (Title Case, matching `name` in frontmatter).
  2. `<div align = "justify">` containing at minimum: a short intro paragraph, **Getting Started** (numbered rules),
     main content sections, and a **Quick Checklist** at the very end.
  3. The **Quick Checklist** must use `  - [ ]` items and test the most likely failure modes.

  * Do **not** use emoji prefixes in `SKILL.md` or `AGENT.md` section headings.
  * Do **not** add a `---` horizontal rule between sections in SKILL/AGENT files - reserve those for README-tier files.

---

## CHANGELOG.md Layout

`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com) conventions adapted for this repo.

### Entry Template

```markdown
## [vX.Y.Z] - YYYY-MM-DD

### Added
  * Description of new feature or file.

### Changed
  * Description of modified behaviour.

### Fixed
  * Description of bug fix.

### Removed
  * Description of removed content.
```

  * Version headings use `## [vX.Y.Z] - YYYY-MM-DD` - the `##` level only, never `#` or `###`.
  * List items inside a version section use `  * ` (two spaces + asterisk).
  * Only include subsections (`### Added`, `### Changed`, etc.) that have at least one entry for that release.
  * The unreleased section (if present) uses `## [Unreleased]`.

---

## Quick Checklist Before Generating Markdown

  - [ ] Did I read the entire target file before making any change?
  - [ ] Is the `<div align = "center">` banner present with a blank line after the opening tag?
  - [ ] Is the `<div align = "justify">` wrapper present with a blank line before the closing tag?
  - [ ] Are all headings in Title Case and using ATX (`#`) style?
  - [ ] Do `README.md` section headings have an emoji prefix at `##` level only?
  - [ ] Are all badges using `style=plastic` and wrapped in a link?
  - [ ] Do all fenced code blocks have an explicit language specifier?
  - [ ] Are unordered list items using `  * ` (2 spaces + asterisk)?
  - [ ] Are checklists using `  - [ ] ` (2 spaces + hyphen)?
  - [ ] Are table label columns centred (`:---:`) and description columns left-aligned (`---`)?
  - [ ] Is there no em dash anywhere - only hyphen-minus (`-`)?
  - [ ] Does `SKILL.md` / `AGENT.md` have a YAML frontmatter block as the very first content?
  - [ ] Does the `name` key in frontmatter match the directory name in kebab-case?

</div>
