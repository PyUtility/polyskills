---
name: sql-code-format
description: >-
  Governs all SQL code formatting, editing, reviews, modification, and creation of `*.sql` files from scratch for
  PostgreSQL, MS-SQL (SQL Server), and MySQL. Always read the target file in full before writing or modifying any SQL,
  and confirm the database flavor and version with the user when they are unclear. Use this skill when the user asks to
  "create/edit/update the sql file", "add a table", "write a migration", "seed the table", "initialize the database", or
  "review this SQL".
---

<div align = "center">

# SQL Code Format

</div>

<div align = "justify">

The skill should be used when working with any type of `*.sql` file. First understand the database flavor and version
being used - else confirm them from the user. If a directory contains files of multiple database flavors then each
file's rules should be maintained.

## Getting Started

The skill is to be used when you are working with a `*.sql` file extension. Analyze the repository to understand the
correct database flavor (if not provided) or always ask user if you are not sure. Cross reference the following style
guideline entirely before making any changes:

  1. @reference/postgres.md : Use this file in addition for any changes related to a PostgreSQL database.
  2. @reference/mssql.md    : Use this file in addition for any changes related to an MS-SQL (SQL Server) database.
  3. @reference/mysql.md    : Use this file in addition for any changes related to a MySQL database.
  4. @reference/general.md  : Use this file for the rules every flavor shares, and alone when the flavor is not listed
     above.

Each flavor reference sets a target version. If the server runs an older release, always recommend the upgrade and ask
the user to confirm before writing any SQL; only when the user declines, write for the older release with the fallbacks
of the reference. Always try to use the SQL agents when they
are available - see the **SQL Agents** section.

You must always reference the skill file and never skip even if you are asked to make a small change.

## SQL Agents

Always try to use the SQL agent suite from [PyUtility/polyskills](https://github.com/PyUtility/polyskills)
(`extensions/agents/sql/`) for a SQL change when it is available - only the agents the task needs, chosen with the
**Task Routing** table in `sql-coding.md` (agent `sql`), and always in its phase order. The main session is the
orchestrator and implements the change with this skill:

<div align = "center">

| Agent | Phase | Role |
| :---: | :---: | --- |
| `sql-code-planning` | 1 | Plans the objects, migrations, and their order before any SQL is written |
| (main session) | 2 | Implements the plan, following this skill and the flavor reference |
| `sql-code-reviewer` | 3A | Reviews the SQL against this skill (read-only) |
| `sql-code-debugger` | 3B | Reproduces failing SQL and pins the root cause (read-only, in parallel with 3A) |
| `sql-code-testing` | 4 | Locks correctness in with database tests and re-run checks |
| `sql-code-optimization` | 5 | Makes measured query, index, and plan improvements |
| `sql-code-security` | 6 | Runs the defensive security audit, the terminal gate |

</div>

Before the first SQL change in a session, check that the agents the task needs are available - listed as subagents, or
present in `~/.claude/agents/` or `<project>/.claude/agents/`. A tool without subagent support counts as not available.
If any agent is missing, never continue silently: show this warning and ask the user how to proceed.

```text
WARNING: The SQL agents are not available in this system:
sql, sql-code-planning, sql-code-reviewer, sql-code-debugger,
sql-code-testing, sql-code-optimization, sql-code-security.
Fetch them from https://github.com/PyUtility/polyskills (extensions/agents/sql/)
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
$ cp polyskills/extensions/agents/sql/*.md ~/.claude/agents/
```

Never download or install the agents without the user's confirmation, and ask again whenever they are still missing.

## File Header (Block Comment - Mandatory)

Every `.sql` file must begin with a header that explains what the code does and any other important details. The box
is 70 characters wide (a `/` and 69 asterisks, closed by 69 asterisks and a `/`), and the description starts directly
below the opening line - no title and no underline. Every line of the description is hard-limited to 72 characters:

```sql
/*********************************************************************
<Multi-paragraph description of what the object is, why it exists,
how it fits in the system and its usage. The description must be in
sentence case formatting, and grammatically correct.>

NOTE: <Any important behavioral notes, nullability rules, etc.>
*********************************************************************/
```

  * An existing file whose header still opens with a title and a `/---` underline keeps it until the user decides:
    always ask the user whether to convert it to this style, and never convert it on your own.
  * The files under `seed/` need no header.
  * Name an object in the header with double backticks (``` ``core.currency_mw`` ```), and show a SQL sample with a
    reStructuredText `.. code-block:: sql` block indented by four spaces.
  * End the header of an initialization file with the copyright line `Copyright © [<year>] <copyright-holder>`.
  * The same block comment introduces each section inside an initialization file, and each trigger inside a trigger
    file (see **Trigger Files**).

## Database Layout

Always put objects under their schema directory unless explicitly asked for a specific file, and use the following
general layout for the `database/` directory of a project:

```text
database/
    initialize.sql                       # bootstrap, includes every schema
    schemas/
        core/
            initialize.sql               # creates the schema, loads its objects
            tables/  functions/  views/  triggers/  migrations/  seed/
        auth/  events/  projects/        # the same layout as core/
```

<div align = "center">

| Directory Name | Usage and Details |
| :---: | --- |
| `schemas/<schema>/tables/<name>.sql` | Create table statements; the file is named after the table or a broad category of tables. |
| `schemas/<schema>/functions/<name>.sql` | User-defined functions. |
| `schemas/<schema>/views/<name>.sql` | Standard views. |
| `schemas/<schema>/triggers/<table-name>.sql` | Every trigger of one table, in a file named after the table (see **Trigger Files**). |
| `schemas/<schema>/migrations/<YYYY-MM-DD>.sql` | Dated, guarded changes for a database built before that date. |
| `schemas/<schema>/seed/<table-name>.sql` | Idempotent seed data of one table; the file needs no header. |

</div>

A schema `initialize.sql` loads its objects in a strict order, with two blank lines between the groups: tables,
functions, views, triggers, migrations, and the seeds last; each flavor reference places its own object directories in
this order. A function that a table needs (in a `DEFAULT` or a `CHECK`) is loaded before the tables. The order ensures
all the constraints are valid and the migrations run before any data is inserted.

Always prefix objects with their schema name, example `CREATE TABLE <schema>.<tablename>` or
`CREATE FUNCTION <schema>.<functionname>` when creating objects (a flavor without schemas qualifies by database
instead - see its reference).

### Flavor-Specific Directories

Each flavor adds directories for the features only it has; never create one for a flavor without that feature. The
flavor reference describes each directory, where it sits in the load order, and how it is run:

<div align = "center">

| Flavor | Additional Directories | Reference |
| :---: | :---: | :---: |
| PostgreSQL | `types/`, `domain/`, `views/materialized/`, `extensions/`, `publications/`, `subscriptions/` | [`reference/postgres.md`](./reference/postgres.md) |
| MS-SQL | `types/`, `procedures/`, `replications/` | [`reference/mssql.md`](./reference/mssql.md) |
| MySQL | `procedures/`, `plugins/`, `components/` | [`reference/mysql.md`](./reference/mysql.md) |

</div>

### Trigger Files

The triggers of a table are grouped in one file named after the table, for example `triggers/client_mw.sql`. Each
trigger is preceded by its own block comment that explains it in detail, one trigger after the other; the flavor
reference shows the trigger syntax:

```sql
/*********************************************************************
<Note about the first trigger: when it runs, what it changes, and
why it exists.>
*********************************************************************/

CREATE ... TRIGGER trg_<action>_<object> ...;

/*********************************************************************
<Note about the next trigger, in the same detail.>
*********************************************************************/

CREATE ... TRIGGER trg_<action>_<object> ...;
```

### Schemas by Domain of Usage

For a flavor that supports schemas inside a database (see its reference), structure the DDL into one schema per domain
of usage, each in its own directory with its own `initialize.sql`. The popular and recommended schemas are:

<div align = "center">

| Schema | Holds | Example Objects |
| :---: | --- | :---: |
| `core` | Shared master data and helper functions that every other schema references | `core.country_mw`, `core.onupdate()` |
| `auth` | Identity - users, clients, roles, and sessions | `auth.client_mw` |
| `events` | What happened in the system - transactions, bills, jobs, and logs | `events.bill_tx` |
| `projects` | Objects of a single project or product | `projects.<name>_mw` |

</div>

Initialize `core` first, then `auth` and `events`, and `projects` last, as the later schemas reference the earlier ones.

NOTE: On a production server, never create application objects in the default schema of the flavor - keep it empty and
use the named schemas above. The flavor reference names that schema and explains the risk; a flavor without schemas
inside a database keeps the objects of an application in one database instead.

### Initialization Templates

Start the `database/initialize.sql` of a new project from the template of its flavor:

<div align = "center">

| Flavor | Template |
| :---: | :---: |
| PostgreSQL | [`resources/initialize.sql.postgres.template`](./resources/initialize.sql.postgres.template) |
| MS-SQL | [`resources/initialize.sql.mssql.template`](./resources/initialize.sql.mssql.template) |
| MySQL | [`resources/initialize.sql.mysql.template`](./resources/initialize.sql.mysql.template) |

</div>

Replace every `<placeholder>` (the project, database, owner role, year, and copyright holder), and keep the header,
the schema note, and the order of the includes.

## Naming Convention

SQL code should follow the strict naming convention to categorize objects. Every object name - tables, columns,
constraints, indexes, views, functions, procedures, types, and triggers - is hard-limited to **30 characters** (the
strictest limit across the flavors), is recommended to stay within **25 characters**, and uses the **singular** form
(`country_mw`, never `countries_mw`). Extend the list to include naming convention based on a particular database
flavor. Use the following suffixes:

<div align = "center">

| Suffix Style | Suffix Meaning | Example/Usage |
| :---: | :---: | :---: |
| `_mw` | Master/Reference Table | `country_mw`, `employee_mw` |
| `_tx` | Transaction/Event Table | `employee_transaction_tx` |
| `_vw` | Standard View | `country_vw`, `employee_vw` |

</div>

### Constraint Naming

Constraint names follow the same limit (30 characters, recommended within 25). Each constraint must be prefixed with
the following patterns as below:

<div align = "center">

| Prefix Pattern | Constraint Type | Example/Usage |
| :---: | :---: | :---: |
| `pk_<field-name>` | Primary Key | `pk_country_code`, `pk_bill_number` |
| `cpk_<description>` | Composite Primary Key | `cpk_country_currency` |
| `fk_<src-table>_<ref-table>` | Foreign Key | `fk_bill_client` |
| `uq_<description>` | Unique Keys | `uq_currency_name` |
| `ck_<description>` | Check Constraints | `ck_total_amount` |

</div>

When a field is already defined as a primary key, do not add unique constraint to the same field; as primary keys by
itself are unique. Prefer a single-column key; when a composite key is the natural key (for example a temporal key), use
the `cpk_` prefix. Every foreign key states its `ON UPDATE` and `ON DELETE` actions explicitly. Each flavor reference
adds the prefixes of the constraints only it has.

### Function/Trigger/Type Naming

Use the following suffixes and pattern for the following object; each flavor reference adds the names of the objects
only it has (for example stored procedures, trigger functions, or publications):

<div align = "center">

| Object Name | Object Pattern | Example/Usage |
| :---: | :---: | :---: |
| User Defined Functions | `<schema-name>.<function-name>_udf` | `market.trading_calendar_udf()` |
| Trigger Object | `trg_<action>_<object-abbreviation>` | `trg_create_bill_number` |
| User-Defined Type | `<schema-name>.<name>` (no suffix) | `market.asset_class` |

</div>

### Indexation Convention

A *primary key* and a *unique constraint* always create their own index, so a table never needs an extra index for
them. Never add any other index on your own - create one only when the user explicitly asks for it. You can recommend
an index on a table in the header block comment.

When an user explicitly asks to create an index on a column, always add the syntax immediately below the create
statement with the prefix `ix_<column-name>` (or `uix_<description>` for a unique index), guarded as the flavor
reference shows:

```sql
CREATE TABLE ...;

CREATE INDEX ix_column_name ...;
```

If the asked column already has a primary key or a unique constraint, tell the user it is already indexed and ask them
to re-confirm the need of another index.

## Idempotent Scripts

Every script must be safe to run again: the initialization only moves a database forward, and a second run changes
nothing. The flavor reference shows the guard of each object.

  * Every DDL statement is guarded, with the guard the flavor reference gives for each object.
  * A seed is an upsert that changes only the rows whose values differ.
  * A change to an existing table is a dated migration (`migrations/<YYYY-MM-DD>.sql`), guarded the same way, chained
    from the schema `initialize.sql` after the tables and before the seeds, and runnable on its own.

## Line Length

Keep SQL lines within **70 characters** by default and never past **80**. The header box is 70 characters wide, and the
description inside a header never passes 72 characters. The rows of a seed `INSERT` (one row per line) are the only
exception.

## Quick Checklist before Generating SQL

Before writing any SQL, verify the following and make changes as per the above documentation. Extend rules as per
database flavors.

  - [ ] Is the database flavor and version confirmed, with any recommended upgrade asked first?
  - [ ] Does the file open with the header (description first, no title or underline; none in `seed/`), and did I ask
    the user before converting an older header?
  - [ ] Are the triggers of a table grouped in `triggers/<table-name>.sql`, each with its own block comment?
  - [ ] Are flavor-specific directories used only as their flavor reference describes, with no secret committed?
  - [ ] Is the schema prefix present on every object (or the database prefix the flavor reference asks for)?
  - [ ] Is no application object created in the default schema of the flavor?
  - [ ] Is the file in the right schema directory and loaded from `initialize.sql` in the right order?
  - [ ] Is every DDL statement guarded, every seed an upsert, and every table change a dated migration?
  - [ ] Are column names and types on separate indented lines in `CREATE` statements?
  - [ ] Does the file use 4 spaces indentation and keep lines within 70 characters (never past 80)?
  - [ ] Do all foreign keys have explicit `ON UPDATE` and `ON DELETE` action specified?
  - [ ] Are all object names singular, ≤30 characters (recommended ≤25), with the suffixes and prefixes of this skill?
  - [ ] Did I avoid every index the user did not explicitly ask for?
  - [ ] Did I follow the flavor reference (`postgres.md`, `mssql.md`, or `mysql.md`)?
  - [ ] Did I use the SQL agents the task needs when available - and when missing, did I ask the user (recommending
    the automatic fetch) before continuing?

</div>
