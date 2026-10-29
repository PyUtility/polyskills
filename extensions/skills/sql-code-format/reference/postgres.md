<div align = "center">

# PostgreSQL Code Format

</div>

<div align = "justify">

Inherit the original skill, general rules and extend to include section wise additional rules only for PostgreSQL
database. The additional contents are only added below.

## Getting Started

Extended from the original `SKILL.md` file, the following new updates are only applicable for a PostgreSQL database when
modifying SQL codes. **PostgreSQL 18 and later is the default target**: some rules and formats below changed with it
(see **Version 18 Defaults**), so a script written to these rules may not run on an older server.

  1. Confirm the PostgreSQL version. If the project runs a release older than 18, always recommend upgrading to
     PostgreSQL 18 and ask the user to confirm before writing any SQL. Only when the user declines the upgrade, write
     for the older release and use the fallback of every 18-only feature listed below.
  2. Write every script for `psql`, so an initialization file can include other files with `\ir`.
  3. Never create application objects in the `public` schema on a production server - see **Schema Organization**.
  4. Start a new database from
     [`resources/initialize.sql.postgres.template`](../resources/initialize.sql.postgres.template).

### Version 18 Defaults

The rules assume these PostgreSQL 18 features. Use the fallback only when the user has declined the recommended upgrade
of an older release:

<div align = "center">

| Feature | Rule on PostgreSQL 18 | Fallback Before 18 |
| :---: | --- | --- |
| Temporal key | `PRIMARY KEY (..., valid_period WITHOUT OVERLAPS)` | An `EXCLUDE USING GIST` constraint (`btree_gist`) |
| `NOT NULL` on a large table | `ADD CONSTRAINT ... NOT NULL ... NOT VALID`, then validate | `CHECK (column IS NOT NULL) NOT VALID`, validate, then `SET NOT NULL` |
| Time-ordered UUID key | `DEFAULT UUIDV7()` | `DEFAULT GEN_RANDOM_UUID()` (random v4) |
| Generated column | `GENERATED ALWAYS AS (...)` is virtual by default; add `STORED` to keep it on disk | Always write `STORED` |
| Query plan | `EXPLAIN ANALYZE` reports buffers by default | `EXPLAIN (ANALYZE, BUFFERS)` |
| Password hashing | `scram-sha-256` only; MD5 passwords are deprecated | `scram-sha-256` (the default since 14) |

</div>

### Schema Organization

Additional objects specific for a PostgreSQL database are to be organized in the following directory structure unless an
user explicitly asked for a different location:

<div align = "center">

| Directory Name | Usage and Details |
| :---: | --- |
| `database/schemas/<schema>/types/<name>.sql` | Enumerated and composite types. |
| `database/schemas/<schema>/domain/<name>.sql` | Domains with their validation checks. |
| `database/schemas/<schema>/views/materialized/<viewname>.sql` | Use this directory to keep materialized views. |
| `database/extensions/` | The `README.md` and one-off setup scripts of the installed extensions (see **Extensions**). |
| `database/publications/<publication-name>.sql` | One publication per file (see **Publications and Subscriptions**). |
| `database/subscriptions/<subscription-name>.sql` | One subscription per file (see **Publications and Subscriptions**). |

</div>

A schema `initialize.sql` loads the PostgreSQL objects in this order: types, domains, tables, functions, views,
materialized views, triggers, migrations, and the seeds last. Extensions, publications, and subscriptions are never
loaded from it.

The `public` schema is on the default `search_path` of every role, and before PostgreSQL 15 every role could create
objects in it, which is the attack path of CVE-2018-1058. Keep it empty on a production server, create each schema with
an owner (`CREATE SCHEMA IF NOT EXISTS <schema> AUTHORIZATION <owner>`), and schema-qualify every name. A database
upgraded from PostgreSQL 14 or earlier still needs `REVOKE CREATE ON SCHEMA public FROM PUBLIC`.

### Naming Convention

The following new string strict naming convention to categorize objects for a PostgreSQL database is added as below:

<div align = "center">

| Pattern | Meaning | Example/Usage |
| :---: | :---: | :---: |
| `_mvw` | Materialized View | `country_mvw`, `employee_mvw` |
| `ex_<description>` | Exclusion Constraint | `ex_country_primary_currency` |
| `<schema>.<verb>_<object>` (no suffix) | Trigger Function | `events.gen_bill_number()`, `core.onupdate()` |
| `<schema>.<name>` (no suffix) | Domain | `auth.email_address` |
| `pub_<description>` | Publication | `pub_core_master` |
| `sub_<description>` | Subscription | `sub_core_master` |

</div>

### Letter Case

Every keyword, data type, and function is written in uppercase, as `general.md` requires - including the functions an
extension adds and the keyword literals:

  * Built-in and extension functions: `NOW()`, `COALESCE()`, `GEN_RANDOM_UUID()`, `UUIDV7()`, `CREATE_HYPERTABLE()`,
    and `BY_RANGE()`.
  * Keywords and literals: `INTERVAL '3 months'`, `TRUE`, `FALSE`, `NULL`, and `CURRENT_TIMESTAMP`.
  * User-defined objects stay in lowercase `snake_case` - schemas, tables, columns, user-defined functions
    (`events.gen_bill_number()`), and the names of named arguments (`if_not_exists => TRUE`).
  * The only exception is the condition name of `RAISE ... USING ERRCODE = '<condition-name>'`, which must be lowercase
    (`'not_null_violation'`): PL/pgSQL does not accept it in uppercase.

Always name an error by its condition name - in `ERRCODE` and in `EXCEPTION WHEN <condition-name> THEN` - as it is
human readable. Write a five-character SQLSTATE only when nothing else is available (for example a test function that
accepts codes only), and then add a short comment that says what it is:

```sql
SELECT THROWS_OK(
    'INSERT INTO auth.client_mw (client_name) VALUES (NULL)'
    , '23502' -- not_null_violation
);
```

```sql
SELECT CREATE_HYPERTABLE(
    'core.forex_rate_tx'
    , BY_RANGE('effective_date', INTERVAL '3 months')
    , if_not_exists => TRUE
);
```

### Scripts and Meta-Commands

Initialization files are `psql` scripts and follow this frame:

  * `\set ON_ERROR_STOP ON` first, so the first error stops the run.
  * A start timestamp with `SELECT TO_CHAR(CLOCK_TIMESTAMP(), ...) AS ts \gset`, then `\echo` lines that report each
    step.
  * `BEGIN;` and `COMMIT;` around the whole run, with `\encoding UTF8` so seed values keep their accents.
  * `\ir <path>` to include each object file in order; the path is relative to the including file.

A migration runs alone in one transaction from its schema directory: `psql -1 -v ON_ERROR_STOP=1 -d <database> -f
migrations/<YYYY-MM-DD>.sql`.

### Guarded DDL

<div align = "center">

| Object | Guard |
| :---: | --- |
| Schema, table, index | `CREATE ... IF NOT EXISTS` |
| Function, view, trigger | `CREATE OR REPLACE` (`OR REPLACE TRIGGER` needs PostgreSQL 14) |
| Type, domain | A `DO $$` block that checks `TO_REGTYPE('<schema>.<name>') IS NULL` first |
| Column, constraint change | A `DO $$` block in a dated migration that checks `pg_attribute` or `pg_constraint` first |

</div>

```sql
DO $$
BEGIN
    IF TO_REGTYPE('market.asset_class') IS NULL THEN
        CREATE TYPE market.asset_class AS ENUM (
            'EQ', 'FI', 'FX', 'CMD', 'DER'
        );
    END IF;
END $$;
```

### Functions

A function lists one parameter per line with leading commas, documents its parameters in an inner block comment, and
raises errors with a context prefix and a named condition:

```sql
CREATE OR REPLACE FUNCTION market.exchange_listing_udf (
    exchange_code CHAR(4)
    , symbol_code VARCHAR(64) DEFAULT NULL
) RETURNS TABLE (
    security_symbol_id INTEGER
    , security_symbol VARCHAR(64)
)
LANGUAGE PLPGSQL STABLE AS
$$

    /****************************************************************
    Return every listing on an exchange, or the one listing a symbol
    names on it.

        exchange_code (Market Identifier Code): The exchange, for
            example ``XNSE``; an unknown code raises an error.

    Return Value: One row per listing.
    *****************************************************************/

    BEGIN

        IF NOT EXISTS (
            SELECT 1
            FROM market.stock_exchange_mw exc
            WHERE exc.market_identifier_code = exchange_code
        ) THEN
            RAISE EXCEPTION
                'Unknown Exchange:: % is not a market identifier code.'
                , exchange_code
            USING ERRCODE = 'invalid_parameter_value';
        END IF;

        RETURN QUERY
        SELECT
            sym.security_symbol_id
            , sym.security_symbol
        FROM market.security_symbol_mw sym
        WHERE sym.market_identifier_code = exchange_code;

    END;

$$;
```

  * Use a transaction-level advisory lock (`PG_ADVISORY_XACT_LOCK`) when a trigger reads the last value of a key to
    compute the next one, so two concurrent inserts cannot read the same value.
  * A `SECURITY DEFINER` function must set `search_path` (`SET search_path = <schema>, pg_temp`), and its `EXECUTE`
    must be revoked from `PUBLIC` in the same transaction.
  * Build dynamic SQL with `FORMAT()` (`%I` for identifiers, `%L` for literals) and `EXECUTE ... USING`.

### Trigger Files

A PostgreSQL trigger runs a trigger function, kept in `functions/` (see **Functions**), so the trigger file of a table
holds only its `CREATE OR REPLACE TRIGGER` statements, each after its own block comment:

```sql
/*********************************************************************
Sets ``updated_on`` of ``auth.client_mw`` before every update, so the
column always holds the time of the last change.
*********************************************************************/

CREATE OR REPLACE TRIGGER trg_update_client
    BEFORE UPDATE ON auth.client_mw
    FOR EACH ROW
        EXECUTE FUNCTION core.onupdate();

/*********************************************************************
Generates ``client_bizkey`` of ``auth.client_mw`` before every
insert, and overwrites any value sent by the caller.
*********************************************************************/

CREATE OR REPLACE TRIGGER trg_create_client_bizkey
    BEFORE INSERT ON auth.client_mw
    FOR EACH ROW
        EXECUTE FUNCTION auth.gen_client_bizkey();
```

### Seed Data

Write a seed as an upsert that only changes the rows whose values differ, so a second run changes nothing:

```sql
INSERT INTO core.data_source_mw (data_source_id, data_source_name) VALUES
    ('ERAPI', 'Exchange Rates API'),
    ('XECCV', 'XE Currency Converter')
ON CONFLICT (data_source_id) DO UPDATE SET
    data_source_name = EXCLUDED.data_source_name
    WHERE (
        core.data_source_mw.data_source_name
    ) IS DISTINCT FROM (
        EXCLUDED.data_source_name
    );
```

### Migrations

  * Name a migration `migrations/<YYYY-MM-DD>.sql`, describe every change in its header, and chain it from the schema
    `initialize.sql` after the tables and before the seeds.
  * Guard every block against the catalog, so a second run changes nothing.
  * Set `lock_timeout` before an `ALTER TABLE` on a busy table, add a foreign key or check as `NOT VALID` and validate
    it in a separate step, and remember that a volatile default or a new identity column rewrites the whole table.
  * `CREATE INDEX CONCURRENTLY`, `VACUUM`, and `CREATE DATABASE` cannot run inside a transaction, so they never belong
    in an `initialize.sql` chain.

### Extensions

Extensions exist only in PostgreSQL. Keep `database/extensions/README.md` with the installed extensions and their setup,
and the one-off configuration scripts in `database/extensions/scripts/<schema>.<table>.sql`, run by hand - never from
`initialize.sql`.

  * Create an extension with `CREATE EXTENSION IF NOT EXISTS <name> WITH SCHEMA <schema>`, in a schema that untrusted
    roles cannot create objects in.
  * An extension with a background worker (for example `pg_cron` or `timescaledb`) must also be listed in
    `shared_preload_libraries`, which needs a restart of the server.

### Publications and Subscriptions

PostgreSQL publishes tables through logical replication. Run the publication and subscription scripts separately, after
`initialize.sql`, as the published tables must exist first. The publisher needs `wal_level = logical` (with enough
`max_replication_slots` and `max_wal_senders`), and the subscriber enough `max_active_replication_origins` (new in 18)
and `max_logical_replication_workers`.

`CREATE PUBLICATION` has no `IF NOT EXISTS`, so guard it in a `DO` block against `pg_publication`. Listing the tables
needs their ownership, while `FOR TABLES IN SCHEMA` and `FOR ALL TABLES` need a superuser:

```sql
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_catalog.pg_publication pub
        WHERE pub.pubname = 'pub_core_master'
    ) THEN
        CREATE PUBLICATION pub_core_master
            FOR TABLE core.country_mw, core.currency_mw;
    END IF;
END $$;
```

`CREATE SUBSCRIPTION` creates a replication slot by default, and then cannot run inside a transaction block or a `DO`
block. Guard it with a `psql` `\if` instead, and filter `pg_subscription` on the current database, as that catalog is
shared by the whole cluster:

```sql
SELECT NOT EXISTS (
    SELECT 1
    FROM pg_catalog.pg_subscription sub
    JOIN pg_catalog.pg_database dbs ON
        dbs.oid = sub.subdbid
    WHERE
        sub.subname = 'sub_core_master'
        AND dbs.datname = CURRENT_DATABASE()
) AS is_missing \gset

\if :is_missing
    CREATE SUBSCRIPTION sub_core_master
        CONNECTION :'publisher_conninfo'
        PUBLICATION pub_core_master;
\endif
```

  * A subscription owned by a non-superuser must carry `password=` in its connection string; a password file or a
    `service=` entry helps only a superuser-owned subscription, or one with `password_required = false`. Never commit
    it - pass the connection string as a `psql` variable from the pipeline's secret store (`psql -v
    publisher_conninfo=...`).
  * Creating a subscription needs the `pg_create_subscription` role (16 and later) and `CREATE` on the database; the
    replication login of the publisher needs `REPLICATION`, a `pg_hba.conf` entry, and `SELECT` on the published
    tables.
  * The schema, sequences, and large objects are not replicated: build the tables on the subscriber first, and apply
    every later schema change to the subscriber before the publisher.

</div>
