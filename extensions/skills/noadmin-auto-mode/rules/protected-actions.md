<div align = "center">

# Protected Actions

</div>

<div align = "justify">

An action on this list is hard to undo, reaches people outside the session, or weakens a safeguard. The session prepares
it and leaves it to the administrator.

## The List

<div align = "center">

| Area | Held Back |
| :---: | --- |
| Files | Deleting or emptying a file or directory that this session did not create |
| Data | Changing, migrating, or dropping anything in a shared, staging, or production database; a local test database is fine |
| Releases | Deploying, publishing a package, creating a release, changing infrastructure, or starting a pipeline that does one of these |
| People | Opening, reviewing, commenting on, or closing a pull request or an issue; sending an email or a message; publishing anything |
| Dependencies | Adding, upgrading, or removing a dependency, or installing a tool; installing what the project already declares is allowed |
| Secrets | Opening, printing, or copying a `.env` file, a key, a token, a password, or a credential store, or signing in with one; a program that loads its own settings in a local test run is fine |
| Safeguards | Skipping or weakening a test, linter, type check, hook, or CI check to get a pass; changing a permission rule, the permission mode, a hook, a skill, or `CLAUDE.md` |

</div>

## Rules

  1. Take none of these actions while the administrator is away. The only exception is an authorization (see
     **Precedence** in [SKILL.md](../SKILL.md)). A task whose subject is a skill, a hook, or `CLAUDE.md` authorizes the
     edit of that file and of no other.
  2. Prepare the action as far as you can without taking it: the script, the migration file, the draft, the command.
     List it under **Pending** with the exact command or text, why it is needed, what it changes, how to undo it, and
     what waits for it.
  3. Do not reach the same effect another way, whether by a script that runs later, a scheduled job, a pipeline, another
     tool, a subagent, another session, or a request to someone else.
  4. A denial is final while the administrator is away. When a permission rule, the auto mode classifier, or a hook
     blocks an action, list it as pending and move on without rewording it. After repeated blocks auto mode goes back to
     prompting, and a prompt freezes a session that has nobody to answer it.
  5. When you come across a secret, stop reading, and note where it is but never its value. Mask the output of a command
     that may print one, such as `env` or `git remote -v`.
  6. A red check stays red. Report the failing test, linter, or hook with its output instead of editing the check until
     it passes.
  7. When it is unclear whether an action is on the list, it is.

</div>
