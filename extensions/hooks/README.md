<div align = "center">

# AI Hooks Extensions

[![Better Comments](https://img.shields.io/badge/Better-%20Comments-007ACC?style=plastic&logo=visualstudiocode)](Better%20Comments%20%28VS%20Code%20Extension%29/README.md)

</div>

<div align = "justify">

Hooks are scripts that run around the code - before or after an event (a commit, a tool call, a save) or on demand - to
check, set up, or sync the tools that a project uses. Each hook lives in its own folder, named after the tool it serves,
with a `README.md` that documents when the hook runs, how to register or call it, its requirements, and its options.

## Available Hooks

<div align = "center">

| Hook | Tool | Runs | Purpose |
| :---: | :---: | :---: | --- |
| [Better Comments](Better%20Comments%20%28VS%20Code%20Extension%29/README.md) | VS Code extension | On demand | Syncs the comment tags of the `code-modification-rule` skill with the VS Code settings |

</div>

## Calling a Hook

A hook runs the way the `README.md` of its folder describes:

  * **Event hooks** run before or after an event (a `pre-*` or `post-*` hook) once they are registered with the tool
    that fires the event - for example a git hook in `.git/hooks/`, or a Claude Code hook in `settings.json`.
  * **On-demand hooks** run only when they are called, with the command that their `README.md` gives.

## Adding a Hook

  1. Create a folder named after the tool it serves, such as `<Tool> (<Kind of Tool>)/`.
  2. Add a `README.md` that states when the hook runs (the event it is registered for, or on demand), its requirements,
     how to register or call it, and its options.
  3. Add a badge and a table row for the hook to this file, and update the `HOOKS` count badge of the root `README.md`.

</div>
