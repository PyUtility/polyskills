<div align = "center">

# General SQL Format

</div>

<div align = "justify">

Inherit the original skill, and extend to include section wise additional rules for general purpose formatting of the SQL
codes. These formats are applicable for all type of database flavors.

## DDL Command Structure

Use the below sample template to generate DDL commands when user asks for any modification, or create from scratch.

### CREATE TABLE Statements

During create or modification of a table, each column layout follow the below mandatory formatting as below:

```sql
CREATE TABLE <schema-name>.<table-name> (
    column_name
        DATA_TYPE [NOT NULL] [DEFAULT value]
        [CONSTRAINT <name> <constraint-type>
            [REFERENCES <schema-name>.<table-name> (<column-name>)
              ON UPDATE <action>
              ON DELETE <action>]],

    next_column_name
        ...
);
```

  * Column name on its own line,
  * Data type and modifiers in the next line, below the column name,
  * Inline constraints start on a new line,
  * `REFERENCES` clause: each `ON UPDATE`/`ON DELETE` on its own line,
  * A blank line between logically grouped columns.

### CREATE VIEW Statements

During create or modification of a standard view, the following mandatory rule must be followed:

```sql
CREATE VIEW <schema-name>.<view-name>_vw AS
    SELECT
        t1.column_name
        , t1.next_column_name
        ...

    FROM <schema-name>.<table-name> t1

    LEFT JOIN <schema-name>.<table-name> t2 ON
        t1.fk_col = t2.fk_col
        [AND ...]

    WHERE
        t1.column_name ...
        [AND ...]

    ORDER BY
        t1.column_name
        , t1.next_column_name
        ...
```

  * Join condition `ON` stays on the same line,
  * Each joined column condition on its own line,
  * Column list uses leading comma style: `, column_name` (comma before column, aligned),
  * `CASE` blocks: `WHEN`/`ELSE`/`END AS alias` always on seperate indented lines,
  * `WHERE` clause: each condition on its own line with `AND` or `OR` prefix.
  * Use abbreviated names as alias when refering to, for example `employee_mw` can be refered as `emp`,
    `country_mw` can be aliased as `cntry` etc.

## DML Command Structure

Use the below sample template to generate DML commands when user asks for any modification, or create from scratch.

### INSERT Statements

Use the following insert statement template to generate when asked for modification or create from scratch. If the field names
are limited and all the field name can be managed into one line of maximum 120 length then use the below template.

```sql
INSERT INTO <schema-name>.<table-name> (<field>, <field>, ...) VALUES
    (<value>, <value>, ...),
    (<value>, <value>, ...),
    ...;
```

If there are too many field names, and cannot be fit to a line of less than 120 characters then break the line like below:

```sql
INSERT INTO <schema-name>.<table-name> (
    <field>
    , <field>
    , ...
) VALUES
    (<value>, <value>, ...),
    (<value>, <value>, ...),
    ...;
```

Any insert statement should be treated as a seed value to the database, and should be added into the following mandatory
directory like `database/schema/<schema>/seed/<filename>.sql` where `<filename>` is the name of the table.

## Rule Sets

The following rules are applicable across all types of database flavors and must be maintained. If the file under modification
does not follow the rules, modify the content along with the requested changes.

  * All SQL reserved words and built-in functions must be written in `UPPERCASE`. This applies to clauses, operators, data
    types, and functions. User-defined object names (tables, columns, aliases, schemas) must be in `snake_case`.
  * Limit all SQL lines to a maximum of **80 characters**, break long expressions across multiple lines using the
    leading-comma style (`, expression`) consistent with the column list style in `SKILL.md`. Long `WHERE` conditions,
    `JOIN` predicates, and function argument lists should each go on their own indented line.
  * Always place a single space on both sides of comparison and assignment operators (`=`, `<>`, `!=`, `<`, `>`, `<=`, `>=`)
    and arithmetic operators (`+`, `-`, `*`, `/`).
  * Always use `IS NULL` or `IS NOT NULL` to test for `NULL` values. Never use `= NULL` or `<> NULL` as these comparisons
    always evaluate to `UNKNOWN` in SQL.
  * All SQL file must have a consistent 4 spaces indentation style.
  * Do not add inline comments unless there is a new field added or removed or functionality is changed.

</div>
