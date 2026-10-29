<div align = "center">

# DBML General Reference (Free-Tier)

</div>

<div align = "justify">

Complete syntax reference for DBML (Database Markup Language) as supported by
[dbdiagram.io](https://dbml.dbdiagram.io/home) on the free tier.
All keywords must be written in **lowercase** per the house style in `SKILL.md`.

---

## 1. Project Block

Declares database-level metadata. One per file, at the top.

```dbml
project project_name {
  database_type: 'postgresql'
  note: '''
  Multi-line Markdown note.
  '''
}
```

Supported `database_type` values: `'postgresql'`, `'mysql'`, `'mssql'`,
`'sqlite'`, `'mariadb'`.

---

## 2. Table Block

```dbml
table schema.table_name {
  column_name  data_type  [settings]  // constraint_comment

  indexes {
    (col1, col2)  [unique, name: 'constraint_name']
  }

  note: '''
  Table-level Markdown note.
  '''
}
```

  * Schema prefix is mandatory: `table core.country_mw { ... }`.
  * Columns, `indexes`, and `note` are the only valid inner blocks.
  * The `note` block must come **last** inside the table, after `indexes`.

---

## 3. Column Settings

Settings are placed inside `[...]` after the data type.
Multiple settings are comma-separated: `[not null, unique]`.

<div align = "center">

| setting | meaning |
| :---: | --- |
| `pk` | primary key |
| `primary key` | alias for `pk` |
| `not null` | column is `not null` |
| `null` | column is nullable (explicit) |
| `unique` | column has a unique constraint |
| `increment` | auto-increment / identity column |
| `default: value` | column default value |
| `default: 'string'` | string default - wrap in single quotes |
| `default: now()` | function default |
| `note: 'short text'` | short inline column annotation |
| `ref: > t.col` | inline many-to-one foreign key |
| `ref: < t.col` | inline one-to-many foreign key |
| `ref: - t.col` | inline one-to-one foreign key |

</div>

---

## 4. Data Types

Use standard SQL type names. dbdiagram.io renders them as-is:

<div align = "center">

| postgresql type | dbml representation |
| :---: | :---: |
| `char(n)` | `char(n)` |
| `varchar(n)` | `varchar(n)` |
| `text` | `text` |
| `integer` / `int` | `integer` |
| `bigint` | `bigint` |
| `smallint` | `smallint` |
| `numeric(p, s)` | `numeric(p, s)` |
| `boolean` | `boolean` |
| `date` | `date` |
| `timestamp` | `timestamp` |
| `timestamptz` | `timestamptz` |
| `uuid` | `uuid` |
| `json` / `jsonb` | `json` / `jsonb` |

</div>

---

## 5. Foreign Key References (Inline - Preferred)

Inline refs are declared as part of the column settings.
Direction is from the perspective of the current column:

```text
ref: >   many-to-one  (current table's many → referenced table's one)
ref: <   one-to-many  (current table's one ← child table's many)
ref: -   one-to-one
```

Always use `ref: >` (many-to-one) on the FK-owning column.

```dbml
table core.state_mw {
  country_code  char(3)  [not null, ref: > core.country_mw.country_code]  // fk_state_country · on update cascade · on delete restrict
}
```

### Standalone Ref Blocks (Alternative)

Use only when inline is not possible (e.g. cross-file reference documentation):

```dbml
ref: core.state_mw.country_code > core.country_mw.country_code
```

or with a label:

```dbml
ref fk_label {
  core.state_mw.country_code > core.country_mw.country_code
}
```

---

## 6. Indexes Block

Defines single-column or composite indexes and unique constraints.

```dbml
indexes {
  column_name                         [name: 'idx_col']
  column_name                         [unique, name: 'uq_col']
  (col1, col2)                        [unique, name: 'uq_composite']
  (col1, col2)                        [name: 'idx_composite']
  (col1, col2)                        [pk, name: 'cpk_composite']
}
```

  * Use `unique` to express a unique constraint.
  * `name:` value must match the actual SQL constraint or index name.
  * Composite primary keys are declared here via `[pk]` on a multi-column tuple, named `cpk_<description>`.

---

## 7. Table Note

Two syntax forms - both produce the same output:

**Short (single line):**
```dbml
note: 'Short description'
```

**Multi-line (triple single-quotes):**
```dbml
note: '''
## Section Heading

Paragraph text with **Markdown** support.

- Bullet one
- Bullet two
'''
```

Markdown is rendered by dbdiagram.io.
Always use triple single-quotes for notes longer than one line.

---

## 8. Table Groups

Clusters tables for layout purposes in dbdiagram.io.

```dbml
tablegroup group_name {
  schema.table_one
  schema.table_two
}
```

  * Table names inside the group must include the schema prefix.
  * Groups have no semantic meaning - layout only.
  * One table can appear in at most one group.

---

## 9. Comments

```dbml
// single-line comment

/* multi-line
   comment */
```

Use `//` for inline constraint annotation (house style).
Use `/* */` sparingly, only for large section banners where `//` is insufficient.

---

## 10. Project-Level Note (multi-line reference)

The `project` block's `note` supports full markdown and typically includes:

  1. **Database name & purpose** - what the database is for.
  2. **Schema layout table** - a markdown table mapping schema → purpose.
  3. **Naming convention** - `*_mw` vs `*_tx` suffixes.
  4. **Logical replication / publications** - list of publication names and tables.
  5. **CI/CD** - links to relevant pipelines or workflow files.

---

## 11. What Is NOT Supported on the Free Tier

<div align = "center">

| feature | tier |
| :---: | :---: |
| `enum` blocks | premium |
| sticky notes / diagram colors | premium UI |
| access control / sharing permissions | premium |
| versioned schema history | premium |
| multi-diagram projects | premium |

</div>

Do not generate any of the above constructs.

---

## 12. Constraint Comment Convention (house style)

Every constraint name appearing in the SQL DDL must be echoed in `schema.dbml`
as a `//` comment on the same line as the column or index it governs:

```dbml
// format for primary keys
record_id  integer  [pk, increment]  // pk_record_id

// format for unique constraints
name  varchar(64)  [not null, unique]  // uq_name

// format for foreign keys (include cascade behaviour)
region_code  char(3)  [not null, ref: > core.region_mw.region_code]  // fk_subregion_region · on update cascade · on delete restrict

// format for composite indexes (in indexes block - comment goes on the index line)
indexes {
  (country_code, state_name)  [unique, name: 'uq_state_name']  // composite: state name unique per country
}
```

The `·` (middle dot, U+00B7) is used as a visual separator within the comment.

</div>
