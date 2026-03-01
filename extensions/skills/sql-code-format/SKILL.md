---
name: sql-code-format
description:
  The skill governs all SQL code formatting, editing, reviews, modification and create a new file from scratch. Always, read
  the file in full before writing or modifying and SQL codes. The code is only applicable for file with *.sql extensions and
  should prompt user (if not already provided or understood) to understand which database flavor to use which are -
  (I) PostgreSQL DB. Use this skill when an use ask questions like "create/edit/update the sql file ..." in the prompt.
---

<div align = "center">

# SQL Code Format

</div>

<div align = "justify">

The skill should be used when working with any type of `*.sql` file. First understand the database flavor being used - else
confirm the database flavor from user. If a directory contains file of multiple database flavor then each file's rule should
be maintained.

## Getting Started

The skill is to be used when you are working with a `*.sql` file extension. Analyze the repository to understand the correct
database flavor (if not provided) or always ask user if you are not sure. Cross reference the following style guideline entirely
before making any changes:

  1. @reference/postgres.md : Use this file in addition for any changes related to PostgreSQL database.
  2. @reference/general.md  : Use this file when the database flavor in use is not defined above.

You must always reference the skill file and never skip even if you are asked to make a small change.

### File Header (Block Comment - Mandatory)

Every `.sql` file must begin with a header that explains what the code does and any other important details with this header
template:

```sql
/********************************************************************
<Short Title in Title Case of the Object & Usage>

< Multi-paragraph description of what the object is, why it exists,
how it fits in the system and its usage. The description must be in
scentence case formatting, and gramatically correct. >

NOTE: < Any important behavioral notes, nullability rules, etc. >
********************************************************************/
```

### Modification Rule

Use the below annotations using reStructuredText docstring style inline within the comment block (header) using the below
template for the use cases:

  * `-- ..refactor:: <YYYY-MM-DD> <short-description>` - use this when there was a refactor of the code,
  * `-- ..versionadded:: <YYYY-MM-DD> <short-description>` - use this when a new field is added during modification, and
  * `-- ..versionchanged:: <YYYY-MM-DD> <short-description>` - use this when a field is changed.

## Schema Organization

Always put objects under its schema directory unless explictly asked for a specific file. Use the following directory structure
to organize code:

| Directory Name | Usage and Details |
| :---: | --- |
| database/schema/<schema>/<filename>.sql | Use this to place create table statements, file name should be the table name or broad category name. |
| database/schema/<schema>/views/<viewname>.sql | Use this directory to keep standard views. |
| database/schema/<schema>/functions/<functioname>.sql | Use this directory to keep functions. |

Always prefix objects with its schema name, example `CREATE TABLE <schema>.<tablename>` or `CREATE FUNCTION <schema>.<functionname>`
when creating objects.

## Naming Convention

SQL code should follow the strict naming convention to categorize objects. All the object names is limited to 30 characters.
Extend the list to include naming convention based on a particular database flavor. Use the following suffixes:

| Suffix Style | Suffix Meaning | Example/Usage |
| :---: | :---: | --- |
| `_mw` | Master/Reference Table | `country_mw`, `employee_mw` |
| `_tx` | Transaction/Event Table | `employee_transaction_tx` |
| `_vw` | Standard View | `country_vw`, `employee_vw` |

### Constraint Naming

All constraint name is of maximum 30 characters. Each constraint must be prefixed with the following patterns as below:

| Prefix Pattern | Constraint Type | Example/Usage |
| :---: | :---: | --- |
| `pk_<field-name>` | Primary Key | `pk_country_code`, `pk_employuee_code` |
| `fk_<src-table>_<ref-table>` | Foreign Key | |
| `uq_<description>` | Unique Keys | |
| `ck_<description>` | Check Constraints | |

When a field is alredy defined as a primary key, do not add unique constraint to the same field; as primary keys by itself are
unique. Try to avoide composite primary key, but you can create composite unique key.

### Function/Trigger/Type Naming

Use the following suffixes and pattern for the following object:

| Object Name | Object Pattern | Example/Usage |
| :---: | :---: | --- |
| User Defined Functions | `<schema-name>.<function-name>_udf` | `public.get_employee_udf()` |
| Trigger Function | `<schema-name>.<trigger-name>` | `public.onupdate()` |
| Trigger Object | `trg_<trigger-name-abbreviation>_<action>` | |
| ENUM Type | `<schema-name>.<name>` (no suffix) | `public.employee_role` |

### Indexation Convention

Do not automatically create indexation in a table - unless specifically asked. You can recommended indexation on a table
in the header block comment.

When an user specifically asks to create indexation on a column, always follow add the syntax immediately below the create
statement with the prefix `ix_<column-name>` as below:

```sql
CREATE TABLE ...;

CREATE INDEX ix_column_name ...;
```

Always check if the asked column already has a *primary key* or *unique constraint* defined, if defined then always ask user to
re-confirm the need of index.

## Quick Checklist before Generating SQL

Before writing any SQL, verify the following and make changes as per the above documentation. Extend rules as per database
flavors.

  - [ ] Does the file have mandatory block comment header?
  - [ ] Is the schema prefix present on every object?
  - [ ] Are column names and types on seperate indented lines in `CREATE` statements?
  - [ ] Does the file uses 4 spaces indentation?
  - [ ] Do all foreign keys have explicit `ON UPDATE` and `ON DELETE` action specified?
  - [ ] Are all object names ≤30 characters?

</div>
