<div align = "center">

# MySQL Code Format

</div>

<div align = "justify">

Inherit the original skill and the general rules, and extend them with the rules below for MySQL. The rules target
MySQL 8.0 and the 8.4 LTS release, and call out the features that need a specific minor version. Every file keeps the
block comment header, the 4-space indentation, and the leading-comma style of `SKILL.md`.

## Getting Started

  1. Confirm the MySQL version - enforced `CHECK` constraints need 8.0.16, `EXPLAIN ANALYZE` 8.0.18, and the row alias
     of `ON DUPLICATE KEY UPDATE` 8.0.19. If the server is older than 8.0.19, always recommend an upgrade to the 8.4 LTS
     release and ask the user to confirm; only when the user declines, write for the older release.
  2. Remember that DDL commits implicitly: a script cannot be rolled back as one transaction, so every statement must be
     guarded and safe to run again.
  3. Run scripts with the `mysql` client in batch mode, which stops at the first error - never pass `--force`.
  4. Start a new database from [`resources/initialize.sql.mysql.template`](../resources/initialize.sql.mysql.template).

## Databases Instead of Schemas

In MySQL, `SCHEMA` is a synonym of `DATABASE`: there is no schema namespace inside a database. The schema-per-domain
layout of `SKILL.md` therefore does not apply. Keep the objects of an application in one database, group them by
directory (`database/schemas/<database>/tables/`, and so on), and create a separate database only for a part of the
application that is deployed on its own. Objects are created in the current database (`USE <database>;`), so qualify a
name with the database (`db.table`) only for a cross-database reference - this replaces the schema prefix rule of
`SKILL.md`.

MySQL adds a `procedures/` directory (`database/schemas/<database>/procedures/<procedure-name>.sql`, named
`<name>_usp`) and the server-level `plugins/` and `components/` (see **Plugins and Components**). A database
`initialize.sql` loads tables, functions, procedures, views, triggers, migrations, and the seeds last. The counterpart
of the default schema rule of `SKILL.md`: never create application objects in the system databases (`mysql`, `sys`,
`performance_schema`, `information_schema`).

## Naming and Identifiers

  * Identifiers may be up to 64 characters, but the 30-character limit of `SKILL.md` still applies.
  * Whether a table name is case-sensitive depends on the operating system (`lower_case_table_names`), so keep every
    name in lowercase `snake_case`.
  * Quote a name with backticks only when it needs them.
  * The primary key is always named `PRIMARY`, so MySQL ignores a `CONSTRAINT pk_...` name on it; keep the name in the
    DDL for the other flavors and for readability. Every other constraint name must be unique in the database.

## Table Options and Data Types

Create every table with InnoDB and `utf8mb4`, never `utf8` or `utf8mb3`, which cannot store four-byte characters:

```sql
CREATE TABLE IF NOT EXISTS currency_mw (
    currency_code
        CHAR(3) NOT NULL
        CONSTRAINT pk_currency_code PRIMARY KEY,

    currency_name
        VARCHAR(64) NOT NULL
        CONSTRAINT uq_currency_name UNIQUE,

    n_decimals
        TINYINT UNSIGNED NOT NULL DEFAULT 2
        CONSTRAINT ck_n_decimals CHECK (n_decimals <= 8)
)
    ENGINE = InnoDB
    DEFAULT CHARSET = utf8mb4
    COLLATE = utf8mb4_0900_ai_ci;
```

<div align = "center">

| Use | Instead Of | Reason |
| :---: | :---: | --- |
| `DATETIME` | `TIMESTAMP` for business dates | `TIMESTAMP` ends at 2038-01-19 and converts with the session time zone |
| `JSON` | `TEXT` holding JSON | Validated on write; index it through a generated column or a functional index |
| `DECIMAL(p, s)` | `FLOAT`, `DOUBLE` for money | Exact arithmetic |
| `AUTO_INCREMENT` | A sequence object | MySQL has no sequences; the counter leaves gaps on rollback |

</div>

  * `CHECK` constraints are enforced from 8.0.16; earlier releases parse and ignore them.
  * A `JSON`, `TEXT`, or `BLOB` column takes a default only as an expression, for example `DEFAULT ('[]')` (8.0.13).

## Guarded DDL

  * Tables use `CREATE TABLE IF NOT EXISTS`, which does not compare the structure of an existing table, so a change to
    a table belongs in a dated migration.
  * Views use `CREATE OR REPLACE VIEW`; MySQL offers `OR REPLACE` for views only.
  * Procedures, functions, and triggers are dropped with `DROP ... IF EXISTS` and created again (`CREATE ... IF NOT
    EXISTS` needs 8.0.29).
  * `CREATE INDEX` and `ADD COLUMN` have no `IF NOT EXISTS` in MySQL, so a migration checks `information_schema` before
    it adds either one.

Routine and trigger bodies contain `;`, so wrap them in a `DELIMITER` block of the `mysql` client:

```sql
DELIMITER $$

DROP PROCEDURE IF EXISTS raise_bill_usp $$

CREATE PROCEDURE raise_bill_usp (
    IN p_client_syskey CHAR(36)
    , IN p_bill_date DATE
)
SQL SECURITY INVOKER
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    INSERT INTO bill_tx (client_syskey, bill_date)
    VALUES (p_client_syskey, p_bill_date);

    COMMIT;
END $$

DELIMITER ;
```

## Stored Routines

  * Declare `SQL SECURITY INVOKER`. The default, `DEFINER`, runs the routine with the privileges of its creator, and the
    routine breaks when that account is dropped.
  * With binary logging on, a function must declare `DETERMINISTIC`, `NO SQL`, or `READS SQL DATA`.
  * Name every error condition once with `DECLARE <name> CONDITION FOR ...`, with a short comment on its code, and use
    the name in `SIGNAL`, `RESIGNAL`, and every handler - never a bare SQLSTATE or error number. A condition used with
    `SIGNAL` or `RESIGNAL` must be declared with an SQLSTATE (`'45000'` is the generic user-defined error), and the
    built-in classes `SQLEXCEPTION`, `SQLWARNING`, and `NOT FOUND` need no declaration.
  * Raise errors with `SIGNAL <condition-name> SET MESSAGE_TEXT = '<Context>:: <message>'`, and re-raise inside a
    handler with `RESIGNAL`:

```sql
DECLARE bill_number_exhausted CONDITION
    FOR SQLSTATE '45000'; -- unhandled user-defined error
DECLARE duplicate_entry CONDITION
    FOR 1062; -- ER_DUP_ENTRY, a duplicate key value

SIGNAL bill_number_exhausted
    SET MESSAGE_TEXT = 'Fiscal Sequence:: 999 bills are exhausted.';
```

  * Build dynamic SQL in a procedure with `PREPARE` and `EXECUTE ... USING`. Identifiers cannot be bound as parameters,
    so check them against an allow-list before they are concatenated in.

## Seed Data

Write a seed as an upsert with the row alias of 8.0.19, which only changes the rows whose values differ; the
`VALUES()` function is deprecated:

```sql
INSERT INTO data_source_mw (data_source_id, data_source_name) VALUES
    ('ERAPI', 'Exchange Rates API'),
    ('XECCV', 'XE Currency Converter')
AS src
ON DUPLICATE KEY UPDATE
    data_source_name = src.data_source_name;
```

## Plugins and Components

MySQL has no per-database extensions, so the `extensions/` directory of PostgreSQL is replaced by two directories for
the server-level features:

<div align = "center">

| Directory | Holds | Installed With |
| :---: | --- | :---: |
| `database/components/` | A `README.md` and one script per component | `INSTALL COMPONENT` |
| `database/plugins/` | A `README.md` and one script per plugin | `INSTALL PLUGIN` |

</div>

  * Both register in the `mysql` system schema (`mysql.component`, `mysql.plugin`), apply to the whole server, and are
    loaded again at every restart - run each script once per server, by an administrator, never from `initialize.sql`.
  * Check whether a plugin or component is already installed (`INFORMATION_SCHEMA.PLUGINS`, `mysql.component`) before
    installing it, so a second run changes nothing.
  * Prefer a component when MySQL offers one - 8.4 replaced the keyring and `openssl_udf` plugins with components - and
    keep a plugin only for features that exist only as plugins, such as Group Replication.

## Domains and Types

MySQL has no domains or user-defined data types (`ENUM` and `SET` are column types), so the `types/` and `domain/`
directories are not used: write every rule as a named `CHECK` constraint on the column or the table (enforced from
8.0.16).

## Replication Instead of Publications

MySQL has no publication or subscription objects, so the `publications/` and `subscriptions/` directories are not used.
Replication is server-level: a replica reads the binary log of its source, configured on the replica with
`CHANGE REPLICATION SOURCE TO` (8.0.23) and `START REPLICA` (8.0.22); 8.4 removed `CHANGE MASTER TO` and `START SLAVE`.
Keep that setup in the server configuration and its runbook, not in `database/`:

  * Replicate selected databases or tables with replication filters - `CHANGE REPLICATION FILTER` (lost on a restart)
    or the `--replicate-do-db` and `--replicate-do-table` options in the option file.
  * Keep credentials out of the stored settings: leave `SOURCE_USER` empty and pass `USER` and `PASSWORD` to
    `START REPLICA` from the secret store.

</div>
