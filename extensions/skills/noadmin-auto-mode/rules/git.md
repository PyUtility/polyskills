<div align = "center">

# Git

</div>

<div align = "justify">

The administrator commits. The session leaves its work in the working tree and writes the commit message.

## Rules

  1. Do not commit. Leave every change uncommitted in the working tree.
  2. Do not touch history, branches, the index, the stash, or a remote: no `add`, `push`, `pull`, `merge`, `rebase`,
     `cherry-pick`, `revert`, `reset`, `restore`, `checkout`, `switch`, `stash`, `clean`, `rm`, or `tag`. Reading is
     fine: `status`, `diff`, `log`, `show`, `blame`.
  3. Undo your own edit by editing the file back. `git restore` and `git checkout` would also wipe the administrator's
     uncommitted work in that file.
  4. When a task is complete, write its commit message and post it in the chat, in a `text` block, with the list of
     files that belong to it. Follow the `git-commiter` skill when it is installed, otherwise the style of `git log`.
     Copy the message into the plan, so that it survives a context compaction. The administrator creates the commit
     later.
  5. Write one message per task, or per logically independent change. When two tasks change the same file, say so,
     because their commits cannot be split by file.
  6. Protect the administrator's uncommitted work. When a task must change a file that the baseline lists as already
     changed, first copy it next to the plan file, then make only the edits the task needs, and list the file as mixed.
  7. Never change the git configuration, a remote, a credential, or a hook, and never pass `--no-verify`. This holds for
     an authorized commit as well.
  8. An authorized git action covers what the administrator named and nothing more. "Commit" does not include "push".

</div>
