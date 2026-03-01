<div align = "center">

# PostgreSQL Code Format

</div>

<div align = "justify">

Inherit the original skill, general rules and extend to include section wise additional rules only for PostgreSQL database. The
additional contents are only added below.

## Getting Started

Extended from the original `SKILL.md` file, the following new updates are only applicable for a PostgreSQL database when
modifing SQL codes.

### Schema Organization

Additional objects specific for a PostgreSQL database are to be organized in the following directory structure unless an
user explictly asked for a different location:

| Directory Name | Usage and Details |
| :---: | --- |
| database/schema/<schema>/views/materialized/<viewname>.sql | Use this directory to keep materialized views. |

### Naming Convention

The following new string strict naming convention to categorize objects for a PostgreSQL database is added as below:

| Suffix Style | Suffix Meaning | Example/Usage |
| :---: | :---: | --- |
| `_mvw` | Materialized View | `country_mvw`, `employee_mvw` |

</div>
