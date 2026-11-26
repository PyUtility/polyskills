<div align = "center">

# DBML Paid-Tier Reference

</div>

<div align = "justify">

Syntax for the DBML constructs that [dbdiagram.io](https://dbml.dbdiagram.io/home) renders only on a paid plan (see
section 11 of [`general.md`](./general.md)): enums, colors and sticky notes. Use them only when the user asks for them.
Everything in `general.md` and every house rule of `SKILL.md` still applies: lowercase syntax, 2-space indentation,
constraint names in `//` comments, inline refs, and the table note template.

The `@dbml/core` parser reads table group notes and colors only in its `dbmlv2` mode:
`new Parser().parse(source, 'dbmlv2')`. Every example below parses there.

---

## 1. When To Use

  * The user asks for enums, colors, header colors or sticky notes, or for a styled diagram.
  * The user asks for a tool that reads the file and honors these settings, such as a schema browser that colors its
    containers.
  * Say in the `project` note that the file uses paid-tier features, so the next editor does not strip them as
    free-tier violations.

---

## 2. Enum Blocks

```dbml
enum auth.client_role {
  SUPER_ADMINISTRATOR  [note: 'At most one current grant in the whole database']
  ADMINISTRATOR
  USER
}

enum materials.cost_driver_category {
  "MATERIALS"
  "MACRO INDICATORS"
}
```

  * Prefix the schema, as for tables.
  * List the values in the order of the SQL `CREATE TYPE ... AS ENUM`, then the values appended later with `ALTER TYPE
    ... ADD VALUE`, so the DBML order is the database order.
  * A value keeps the exact case of its SQL label: the lowercase rule covers DBML syntax, not data.
  * Wrap a value in double quotes when it holds a space or any character other than a letter, digit or underscore.
  * A value note is short and single-quoted; escape an apostrophe as `\'`.
  * A column of the type names the enum as its type, schema included: `client_role  auth.client_role  [not null]`.

---

## 3. Table Header Color

```dbml
table core.country_mw [headercolor: #2563eb] {
  country_code  char(3)  [pk]  // pk_country_code
}
```

  * Write the color as a lowercase six-digit hex value.
  * Keep one palette per diagram. Master tables (`_mw`) take the color of their group, transaction tables (`_tx`) a
    darker shade of it, and views (`_vw`) a neutral slate.

---

## 4. Table Group Color And Note

```dbml
tablegroup core [color: #2563eb] {
  core.continent_mw
  core.country_mw

  note: '''
  ## Reference Data

  Multi-line Markdown note of the group.
  '''
}
```

  * The `color` setting tints the group; use the same hex as the header of its master tables.
  * A multi-line note goes inside the block, after the members. A one-line note may sit in the settings instead:
    `tablegroup auth [color: #7c3aed, note: 'One line']`.

---

## 5. Sticky Notes

```dbml
note core_routines [color: #fde68a] {
  '''
  ## Core Routines

  | Function | Purpose |
  | :---: | --- |
  | `core.onupdate()` | Sets `updated_on` on every update. |
  '''
}
```

  * A sticky note is a top-level block, not a setting. Name it in snake case and prefix the schema it describes
    (`<schema>_<topic>`), so a tool can place it next to that schema.
  * Its Markdown body follows the capitalisation rules of table notes: Title Case headings, Sentence case text.
  * Use sticky notes for what has no DBML block of its own: functions, triggers, domains, server extensions and
    planned modules.

---

## 6. Relationship Line Color

```dbml
ref fk_city_state_code: core.city_mw.(country_code, state_code) > core.state_mw.(country_code, state_code) [update: cascade, delete: restrict, color: #64748b]
```

  * `color` is a setting of a file-level ref only: inline refs take no settings.
  * Keep inline refs wherever they suffice; do not turn a ref into a file-level block just to color it.

---

## 7. Summary

<div align = "center">

| Construct | Syntax | Section |
| :---: | :---: | :---: |
| Enum | `enum schema.name { value [note: '...'] }` | 2 |
| Table header color | `table schema.name [headercolor: #hex]` | 3 |
| Group color | `tablegroup name [color: #hex]` | 4 |
| Group note | `note: '''...'''` inside the `tablegroup` block | 4 |
| Sticky note | `note name [color: #hex] { '''...''' }` | 5 |
| Relationship color | `ref name: a.b > c.d [color: #hex]` | 6 |

</div>

</div>
