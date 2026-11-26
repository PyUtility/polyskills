<div align = "center">

# Linking Vendor Folders

</div>

<div align = "justify">

Claude Code reads skills only from `.claude/skills/` and agents only from `.claude/agents/`, and it never reads anything
under `.agents/`. Something has to connect the two. There are two ways, and the argument `links=` picks one.

<div align = "center">

| | `links=pointer` (Default) | `links=symlink` |
| :---: | --- | --- |
| What git holds | Small real files: frontmatter and one directive | Two symlinks, `.claude/skills` and `.claude/agents` |
| Works on | Every operating system, clone, archive, and container | Linux, macOS, WSL; Windows only with Developer Mode and `core.symlinks=true` |
| Vendor-only frontmatter | Lives in the pointer (`tools`, `model`, `argument-hint`) | Impossible: the shared file is the only file |
| Repeats | The name and description, which the check compares | Nothing |
| A new skill needs | Its pointer file | Nothing |

</div>

## Why Pointer Files Are The Default

Tested in November 2026 with Claude Code 2.1.278 and git 2.46 on Windows 10, and with git 2.43 on Linux:

<div align = "center">

| Situation | What Happened |
| --- | --- |
| A committed symlink, checked out with `core.symlinks=false` (the default of Git for Windows) | A 17-byte text file. Claude Code found no skill and no agent, and gave no error. |
| An editor adds a newline to that text file, and it is committed | git keeps it as a symlink whose target ends in a newline. It is broken on Linux and macOS. |
| `core.symlinks=true` without the right to create symlinks | Checkout fails and leaves the path missing, so `git commit -a` would delete the link. |
| A **junction over a tracked symlink** | `git reset --hard`, `checkout`, `restore`, `stash`, and a branch switch all **emptied `.agents/skills`**, untracked files included. `git add -A` would have replaced the link by copies. |
| A junction at an untracked path that git ignores | Safe, but it exists on one machine only: every other clone lacks it. |
| Pointer files, or real directories | Found everywhere. |
| A real symlink on Linux | Every git operation above was safe. |

</div>

Two more reasons hold even where symlinks work. Antigravity reads `.agents/agents/` directly, and its documentation says
that a tool name it does not know can hang the agent, so a shared agent cannot carry the `tools` list that Claude Code
needs to keep a reviewer read-only. A pointer keeps that limit in the one place that understands it. And the Edit and
Write tools of Claude Code refuse a path that is itself a symlink.

## Pointer Mode

For each shared skill, `<dir>/.agents/skills/<name>/SKILL.md`, write `<dir>/.claude/skills/<name>/SKILL.md` from
[`pointer-skill.md.template`](../resources/pointer-skill.md.template). For each shared agent,
`<dir>/.agents/agents/<role>.md`, write `<dir>/.claude/agents/<role>.md` from
[`pointer-agent.md.template`](../resources/pointer-agent.md.template). `<dir>` is the repository root, or the package
that owns the skill.

  * Copy the name and the description word for word. The check compares them, however the YAML is folded.
  * Name the shared file by its full path from the repository root, in backticks.
  * Put every key that only Claude Code reads into the pointer, and only there. Keep `Read` in a `tools` list, or the
    agent cannot open its own instructions. Add `readonly: true` to a read-only role, because Cursor reads the same file
    and knows no `tools` key.
  * Write nothing else. A pointer that explains the skill is a second copy of it.
  * A skill or agent that only Claude Code can use stays in `.claude/` as it is, without a pointer.

## Symlink Mode

Use it only when the user passed `links=symlink`, and only after both checks pass on this machine:

```shell
$ git config --get core.symlinks                                   # must not be false
$ ln -s target va-probe && test -L va-probe && echo ok; rm -f va-probe
```

On Windows, run the second line in Git Bash with `MSYS=winsymlinks:nativestrict` set, because Git Bash otherwise copies
instead of linking. When a check fails, stop and tell the user the one-time setup: turn on Developer Mode (Settings, For
developers), run `git config core.symlinks true` in the clone, and check `.claude` out again. Every Windows clone needs
it. Offer `links=pointer` as the other way.

Then, in a POSIX shell (never in PowerShell or cmd, where a pipe adds a line ending to the target):

```shell
$ for kind in skills agents; do
>   blob=$(printf '%s' "../.agents/$kind" | git hash-object -w --stdin)
>   git update-index --add --cacheinfo "120000,$blob,.claude/$kind"
>   git checkout-index --force -- ".claude/$kind"
> done
```

  * The targets must hold a tracked file, so both folders under `.agents/` need at least a `.gitkeep`. A link to an
    untracked folder is broken in every fresh clone.
  * Move a real `.claude/skills/` or `.claude/agents/` away first, with `git mv`, file by file.
  * Use relative targets only. Never link `.claude` itself, and never link outside the repository.
  * Every shared agent must stay free of vendor keys, and an agent that needs a tool limit cannot be linked. Keep
    `.claude/agents/` as a pointer folder in that case and link only the skills.

## Never Do This

  * Never put a junction (`mklink /J`) where git tracks a symlink. It loses files.
  * Never copy or sync `.agents/` into a vendor folder. Two copies drift.
  * Never commit a link as a regular file, and never edit the text file that a checkout left in its place.
  * Never remove a junction with a recursive delete. `cmd /c rmdir <link>` removes the link alone.

</div>
