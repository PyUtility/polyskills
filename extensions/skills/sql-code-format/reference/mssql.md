<div align = "center">

# MS-SQL Code Format

</div>

<div align = "justify">

Inherit the original skill and the general rules, and extend them with the rules below for Microsoft SQL Server (T-SQL)
and Azure SQL. The rules target SQL Server 2016 SP1 and later, which adds `CREATE OR ALTER`, and call out the features
that need a newer release. Every file keeps the block comment header, the 4-space indentation, and the leading-comma
style of `SKILL.md`.

## Getting Started

  1. Confirm the target is SQL Server or Azure SQL, and its version - `CREATE OR ALTER`, `DROP ... IF EXISTS`, `THROW`,
     and UTF-8 collations all depend on it. If the server is older than SQL Server 2016 SP1, always recommend an upgrade
     to a supported release and ask the user to confirm; only when the user declines, write for the older release.
  2. Write every script for `sqlcmd` mode, so the initialization file can include other files with `:r`.
  3. Never create application objects in the `dbo` schema on a production server - see **Schema Organization**.
  4. Start a new database from [`resources/initialize.sql.mssql.template`](../resources/initialize.sql.mssql.template).

## Schema Organization

SQL Server resolves a one-part name to the caller's default schema first and then to `dbo`, and every object in `dbo`
shares one owner, so an ownership chain can reach all of them. Create application objects only in named schemas (`core`,
`auth`, `events`, and `projects` - one schema per domain of usage) owned by a dedicated role, always write two-part
names (`core.currency_mw`), and keep `dbo` empty on a production server.

MS-SQL adds these directories to the general layout of `SKILL.md`:

<div align = "center">

| Directory Name | Usage and Details |
| :---: | --- |
| `database/schemas/<schema>/types/<name>.sql` | Alias types and table types. |
| `database/schemas/<schema>/procedures/<procedure-name>.sql` | Stored procedures, one procedure per file. |
| `database/replications/<publication-name>.sql` | One SQL Server Replication setup per publication (see **Replications**). |

</div>

A schema `initialize.sql` loads the MS-SQL objects in this order: types, tables, functions, procedures, views,
triggers, migrations, and the seeds last. Replication scripts are never loaded from it.

## Naming Convention

The following prefixes and suffixes are added for an MS-SQL database:

<div align = "center">

| Prefix or Suffix | Object | Example/Usage |
| :---: | :---: | :---: |
| `df_<column-name>` | Default constraint | `df_bill_type` |
| `<schema>.<name>_usp` | Stored procedure | `events.raise_bill_usp` |
| `pub_<description>` | Publication | `pub_core_master` |

</div>

Name every constraint, defaults included. An unnamed constraint gets a generated name (`DF__bill_tx__bill_ty__3A81B327`)
that differs from one database to the next and breaks a later `DROP CONSTRAINT` script. Identifiers may be up to 128
characters, but the 30-character limit of `SKILL.md` still applies. Quote a name with brackets only when it needs them.

## Batches and Scripts

  * `GO` is a batch separator of `sqlcmd` and SSMS, not T-SQL: never follow it with `;`, and remember that a variable
    ends at the next `GO`.
  * `CREATE SCHEMA`, `CREATE VIEW`, `CREATE FUNCTION`, `CREATE PROCEDURE`, and `CREATE TRIGGER` must be the first
    statement of a batch, so close the batch with `GO` before each of them (or wrap `CREATE SCHEMA` in `EXEC`).
  * In the trigger file of a table, each `CREATE OR ALTER TRIGGER` (with the trigger body inline) follows its block
    comment and ends with `GO`, as every trigger must start its own batch.
  * Start an initialization script with `:on error exit` and run it with `sqlcmd -b`, so the first error stops the run.
  * Include files with `:r <path>`. A relative path resolves from the directory `sqlcmd` starts in, so run the script
    from the `database/` directory.
  * End every statement with `;`.

## Guarded DDL

T-SQL has no `CREATE TABLE IF NOT EXISTS`, so guard each statement with a catalog check and a second run becomes a
no-op:

```sql
IF SCHEMA_ID(N'core') IS NULL
    EXEC (N'CREATE SCHEMA core AUTHORIZATION core_owner;');
GO

IF OBJECT_ID(N'core.currency_mw', N'U') IS NULL
CREATE TABLE core.currency_mw (
    currency_code
        CHAR(3) NOT NULL
        CONSTRAINT pk_currency_code PRIMARY KEY,

    currency_name
        NVARCHAR(64) NOT NULL
        CONSTRAINT uq_currency_name UNIQUE,

    n_decimals
        TINYINT NOT NULL
        CONSTRAINT df_n_decimals DEFAULT 2
);
GO
```

  * Use `CREATE OR ALTER` for views, functions, procedures, and triggers. It keeps the existing permissions, which a
    `DROP` and `CREATE` pair loses, but it does not cover tables or indexes.
  * Guard an index with a lookup in `sys.indexes` on its name and `OBJECT_ID` of the table.
  * Use `DROP ... IF EXISTS` (2016 and later) only in a migration that is meant to remove the object.

## Data Types

<div align = "center">

| Use | Instead Of | Reason |
| :---: | :---: | --- |
| `DATETIME2`, `DATE`, `TIME` | `DATETIME` | `DATETIME` rounds to .000, .003, or .007 seconds |
| `DATETIMEOFFSET` | `DATETIME` and a separate offset | Keeps the time zone offset, like `TIMESTAMPTZ` |
| `NVARCHAR(n)`, or `VARCHAR(n)` with a `_UTF8` collation | `VARCHAR(n)` in a non-UTF-8 collation | Unicode text; UTF-8 collations need 2019 or later |
| `NVARCHAR(MAX)`, `VARBINARY(MAX)` | `TEXT`, `NTEXT`, `IMAGE` | The old large-object types are deprecated |
| `DECIMAL(p, s)` | `MONEY` | `MONEY` can lose precision in calculations |
| `BIT` | `CHAR(1)` flags | Native boolean values |

</div>

`IDENTITY` generates a key at insert time, while a `SEQUENCE` is a separate object that tables can share. A sequence is
allocated outside the transaction, so both leave gaps - never rely on a gap-free number from either.

## Procedural Code

Stored procedures follow this layout, with the error handling every write needs:

```sql
CREATE OR ALTER PROCEDURE events.raise_bill_usp
    @client_syskey UNIQUEIDENTIFIER
    , @bill_date DATE
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        INSERT INTO events.bill_tx (client_syskey, bill_date)
        VALUES (@client_syskey, @bill_date);

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        THROW;
    END CATCH;
END;
GO
```

  * `SET XACT_ABORT ON` rolls the whole transaction back on a run-time error, and `SET NOCOUNT ON` removes the
    row-count messages.
  * Raise errors with `THROW` (2012 and later), never `RAISERROR`, and re-raise a caught error with a bare `THROW;`.
  * T-SQL has no named error conditions - an error is only a number. Keep a custom error number (50000 or above) in a
    variable whose name says what it is, and add a short comment wherever a number must still be written, such as a
    `CATCH` block that checks `ERROR_NUMBER()`:

```sql
DECLARE @bill_number_exhausted INT = 50001;

THROW @bill_number_exhausted
    , N'Fiscal Sequence:: 999 bills are exhausted.'
    , 1;

IF ERROR_NUMBER() = 2627 -- unique or primary key violation
    ...
```

  * Build dynamic SQL with `sp_executesql` and typed parameters, and quote identifiers with `QUOTENAME` - never
    concatenate input into a statement.
  * Document objects in the header block. `sp_addextendedproperty` (`MS_Description`) is optional, for tools that need
    it.

## Seed Data

Write a seed as an update of the rows that differ followed by an insert of the missing rows, so a second run changes
nothing. Avoid `MERGE` for seeds, as it has known concurrency and correctness pitfalls:

```sql
INSERT INTO core.data_source_mw (data_source_id, data_source_name)
SELECT
    src.data_source_id
    , src.data_source_name
FROM (VALUES
    ('ERAPI', N'Exchange Rates API'),
    ('XECCV', N'XE Currency Converter')
) AS src (data_source_id, data_source_name)
WHERE NOT EXISTS (
    SELECT 1
    FROM core.data_source_mw dsrc
    WHERE dsrc.data_source_id = src.data_source_id
);
```

Pair it with an `UPDATE ... FROM` over the same `VALUES` list that changes only the rows whose columns differ
(`IS DISTINCT FROM` needs SQL Server 2022 or later; use explicit comparisons before that).

## Domains and Extensions

SQL Server has neither, so the `domain/` and `extensions/` directories of `SKILL.md` are not used:

  * There is no `CREATE DOMAIN`. An alias type (`CREATE TYPE <schema>.<name> FROM <base-type> NOT NULL`) carries only
    `NULL` or `NOT NULL`, so write every check and default as a named constraint on the column. Never use the
    deprecated `CREATE RULE` with `sp_bindrule`, or `CREATE DEFAULT` with `sp_bindefault`.
  * There is no `CREATE EXTENSION`. Instance features come from SQL Server setup and `sp_configure`, which belong to the
    server configuration. CLR assemblies (`CREATE ASSEMBLY`) and external languages or libraries are database objects
    outside this layout - ask the user before adding one.

## Replications

SQL Server publishes data through SQL Server Replication (snapshot, transactional, and merge), with a Publisher, a
Distributor, and Subscribers. There is no `CREATE PUBLICATION` statement: replication is set up with system stored
procedures, and its agents run as SQL Server Agent jobs. The `publications/` and `subscriptions/` directories of
PostgreSQL are therefore replaced by one `database/replications/` directory, with one script per publication.

  * The distribution setup (`sp_adddistributor`, `sp_adddistributiondb`, `sp_adddistpublisher`) runs once per instance
    and belongs to the server configuration, not to `database/`.
  * A script `replications/<publication-name>.sql` enables the database (`sp_replicationdboption`), creates the
    publication (`sp_addpublication`, `sp_addpublication_snapshot`, and `sp_addlogreader_agent` for transactional
    replication), adds its articles (`sp_addarticle`), and adds its subscriptions (`sp_addsubscription`,
    `sp_addpushsubscription_agent`).
  * Check the publication or subscription first (for example with `sp_helppublication` or `sp_helpsubscription`), so a
    second run changes nothing.
  * Pass logins and passwords as `sqlcmd` variables (`$(Login)`, `$(Password)`) or use Windows authentication - never
    commit them.
  * SQL Server Express (which has no SQL Server Agent) can only be a Subscriber. Azure SQL Database can only be a push
    Subscriber of snapshot or transactional replication, and its replicated tables need a primary key; Azure SQL
    Managed Instance supports snapshot and transactional replication only.

</div>
