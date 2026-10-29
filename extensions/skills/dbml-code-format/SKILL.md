---
name: dbml-code-format
description: >-
  Governs all DBML schema diagram creation, editing, reviews, and modification from scratch for *.dbml files. Always
  read the file in full before writing or modifying DBML. Use this skill when a user asks to "create/edit/update/review
  a DBML file" or any database schema diagram in a project that references this skill. Applies to
  dbdiagram.io-compatible DBML (free-tier only).
---

<div align = "center">

# DBML Code Format

</div>

<div align = "justify">

This skill governs the authoring of production-quality ER schema diagrams in DBML
(Database Markup Language) as used with [dbdiagram.io](https://dbml.dbdiagram.io/home).
The output must be free-tier compatible - no enterprise or premium-only features.

## Getting Started

  1. Read the target `.dbml` file in full before making any change.
  2. Cross-reference [`reference/general.md`](./reference/general.md) for the complete free-tier syntax.
  3. When the database has SQL files, keep every schema, table, and constraint name identical to its SQL definition,
     named as `sql-code-format` requires.
  4. Apply every rule below, then run the **Quick Checklist** before returning the file.

## Core Rule - Lowercase Everything

**All DBML keywords, settings, and identifiers must be written in lowercase.**
This applies without exception, even to reserved DBML words:

```text
table, ref, note, indexes, tablegroup, project,
pk, not null, unique, increment, default, database_type
```

DBML parsers (including dbdiagram.io) are case-insensitive for keywords;
lowercase is the enforced house style for this project. The casing rules of
`sql-code-format` (uppercase SQL keywords and functions) do not apply inside a
`.dbml` file - a SQL expression such as a `now()` default stays lowercase too.

## Note Blocks - English Capitalisation (Mandatory)

The lowercase-everything rule applies **only to DBML syntax** - keywords,
identifiers, type names, and settings inside `[...]`. It does **not** apply
to prose text inside `note: '''...'''` blocks.

Inside every `note:` block, use normal English capitalisation:

  * **Markdown headings** (`##`, `###`) → Title Case.
  * **Body paragraphs** → Sentence case (capital first letter, then normal).
  * **Bullet point labels** (especially bold labels like `**Parents:**`) → Capital first letter.
  * **Proper nouns, acronyms, standards** → Always capitalised as in English
    (e.g. `ISO-3166`, `UUID`, `UN M49`, `CBDC`, `MIT`, `FX`, `CTE`, `WAL`).
  * **Table cell content** → Sentence case or Title Case depending on context.

```dbml
// correct - prose follows English rules inside note blocks
note: '''
## Data Source Master (`mw` = Master-World)

Master list of external data providers that populate transactional tables.

### Relationships

- **Referenced by** `events.forex_rate_tx.data_source_id` via
  `fk_forex_rate_data_source` (`on update cascade`, `on delete restrict`).
'''

// wrong - do NOT carry the lowercase-everything rule into notes
note: '''
## data source master (`mw` = master-world)

master list of external data providers that populate transactional tables.

### relationships

- **referenced by** `events.forex_rate_tx.data_source_id` via ...
'''
```

## Indentation - 2 Spaces (Mandatory)

Use **2 spaces** for every level of indentation throughout the `.dbml` file.
Never use tabs. This applies to:

  * Column definitions inside a `table { }` block.
  * Settings and entries inside `indexes { }` blocks.
  * Content inside `tablegroup { }` blocks.
  * Lines inside multi-line `note: '''...'''` blocks.

```dbml
table core.country_mw {
  country_code  char(3)  [pk]  // pk_country_code  ← 2-space indent

  indexes {
    (iso2_code)  [unique, name: 'uq_iso2']  // ← 2-space indent inside indexes
  }

  // ← Title Case heading and Sentence case body, 2-space indent in the note
  note: '''
  ## Country Master

  Description here.
  '''
}
```

## File Header (Project Block - Mandatory)

Every `.dbml` file must begin with a `project` block that describes the database:

```dbml
project <project_name> {
  database_type: '<flavor>'
  note: '''
  # <Database Name>

  <Multi-paragraph description: purpose, schema layout, naming conventions,
  any logical-replication or publication notes, and CI/CD references.>
  '''
}
```

Use triple single-quotes (`'''`) for all multi-line notes.
Markdown is rendered in dbdiagram.io notes - use it for headers, tables, and emphasis.

## Table Declarations

Always prefix table names with the schema:

```dbml
table <schema>.<table_name> {
  ...
}
```

Never omit the schema prefix.

## Column Format

Each column follows this pattern:

```text
column_name   data_type   [settings]   // constraint_name
```

Rules:

  * **One column per line** - no grouping.
  * **Settings** in `[...]` brackets: `[pk]`, `[not null]`, `[unique]`,
    `[default: value]`, `[increment]`, `[ref: > schema.table.column]`.
  * **Constraint names** as same-line `//` comments immediately after the `]`.
  * Use spaces to align the `//` comment column across a table for readability.

### Primary Keys

```dbml
record_id  integer  [pk, increment]  // pk_record_id · generated always as identity
code       char(3)  [pk]             // pk_code
```

A composite primary key goes in the `indexes` block, named `cpk_<description>`
as in `sql-code-format`: `(col1, col2)  [pk, name: 'cpk_<description>']`.

### Unique Constraints

```dbml
column_name  varchar(64)  [not null, unique]  // uq_column_name
```

### Foreign Keys - Inline Reference (Critical Rule)

Foreign key references must be declared **inline** on the column,
with the **constraint name and cascade behaviour** as a `//` comment
on the same line. The constraint is named `fk_<src-table>_<ref-table>`,
as in `sql-code-format`:

```dbml
region_code  char(3)  [not null, ref: > core.region_mw.region_code]  // fk_subregion_region · on update cascade · on delete restrict
```

  * `ref: >` means many-to-one (the current column → the referenced column).
  * Always include `· on update <action> · on delete <action>` in the comment,
    copied from the actual SQL constraint definition.
  * Nullable foreign keys omit `not null` but keep the `ref:` and comment.

## Composite Unique Constraints and Indexes

Use the `indexes` block inside the table for composite constraints:

```dbml
table core.state_mw {
  ...

  indexes {
    (country_code, state_name)  [unique, name: 'uq_state_name']
    (country_code, state_code)  [unique, name: 'uq_state_code']
  }
}
```

The `name:` must match the actual SQL constraint name.

## Table Note - Mandatory

Every table must have a `note:` block using triple single-quotes.
Structure the note with these sections, and use only the sections that apply:
**Composite Unique Constraints** only when the table has an `indexes` block,
**Check Constraints** only when check constraints exist, **Seeded Values** only
when the table ships seed data, and **Functions on This Table** only when UDFs
operate on it.

```dbml
table <schema>.<table_name> {
  ...

  note: '''
  ## <Table Title> (`<suffix meaning>`)

  <One-paragraph description of the table's purpose and scope.>

  ### Relationships

  - **Parents:** <parent tables and constraint names>
  - **Referenced by:** <child tables and constraint names>

  ### Composite Unique Constraints

  - `<constraint_name>`: (`col1`, `col2`) - reason for the composite scope.

  ### Check Constraints

  - `<ck_name>` - plain-English description of the rule.

  ### Seeded Values

  <Brief note on what values are pre-loaded and from which seed file.>

  ### Functions on This Table

  | Function | Purpose |
  | :---: | --- |
  | `schema.function_udf(...)` | Description |
  '''
}
```

### Publication Tables - Special Highlight

If a table is exposed via a PostgreSQL `CREATE PUBLICATION` statement,
the note **must** open with a blockquote callout naming the publication:

```dbml
  note: '''
  ## <Table Title> - Published

  > **Publication:** `<publication_name>`
  >
  > Exposed for logical replication to subscriber databases.
  > Subscribers should **omit foreign-key constraints** to avoid
  > load-order failures during apply.

  <Rest of the note...>
  '''
```

The publication name must match the PostgreSQL publication in
`database/publications/<publication-name>.sql`.

## Table Groups

Use `tablegroup` blocks to cluster related tables for layout in dbdiagram.io.
Group by functional domain, not by schema:

```dbml
tablegroup published_geography {
  core.country_mw
  core.state_mw
  core.city_mw
}

tablegroup reference_geography {
  core.continent_mw
  core.region_mw
  core.subregion_mw
  core.state_type_mw
}
```

Typical groups for this project:

  * `published_<domain>` - tables exposed via logical replication.
  * `reference_<domain>` - master/lookup tables that feed the published ones.
  * `transactional` - `*_tx` fact tables.

## Naming Convention (mirrors SQL skill)

<div align = "center">

| Suffix | Meaning | Example |
| :---: | --- | :---: |
| `*_mw` | master / world-scope reference | `country_mw`, `currency_mw` |
| `*_tx` | transactional / fact table | `forex_rate_tx` |

</div>

## Section Separators (Comments)

Use `//` section dividers to organize a large `.dbml` file:

```dbml
// ============================================================================
// core schema - geography hierarchy
// ============================================================================
```

## Free-Tier Compatibility

Only use the following constructs - all are available on the free tier:

  * `project { ... }` with `database_type` and `note`.
  * `table schema.name { ... }` with column definitions.
  * Column settings: `pk`, `not null`, `unique`, `default`, `increment`, `ref`, `note`.
  * `indexes { ... }` block with `unique` and `name`.
  * `tablegroup` blocks.
  * `//` single-line comments.
  * `'''` triple-quoted multi-line notes (table and project level).

Never use the following:

  * `enum` blocks (premium on dbdiagram.io).
  * `ref` blocks at the file level when inline refs suffice.
  * Sticky notes or colors (premium UI features).

## Quick Checklist Before Generating DBML

  - [ ] Does the file start with a `project` block with `database_type` and multi-line `note`?
  - [ ] Is indentation consistently 2 spaces (no tabs) at every level?
  - [ ] Are all keywords and settings in lowercase?
  - [ ] Do `note:` blocks use Title Case for headings and Sentence case for body text (not all-lowercase)?
  - [ ] Is every table prefixed with its schema (`schema.table_name`)?
  - [ ] Does every column carry its constraint name as a `//` comment?
  - [ ] Do all foreign-key columns use inline `ref: >` with cascade behaviour in the comment?
  - [ ] Do the constraint names follow `sql-code-format` (`pk_`, `cpk_`, `fk_<src-table>_<ref-table>`, `uq_`, `ck_`)?
  - [ ] Are composite uniques declared in an `indexes {}` block with the SQL constraint name?
  - [ ] Does every table have a `note: '''...'''` block?
  - [ ] Are publication tables highlighted with the blockquote callout in their note?
  - [ ] Are tables grouped by domain using `tablegroup` blocks?
  - [ ] Are only free-tier DBML features used?

</div>
