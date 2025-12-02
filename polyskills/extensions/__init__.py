# -*- encoding: utf-8 -*-

"""
An Extensionf for LLM Coding Tools for Fine-Grain Control
---------------------------------------------------------

Extensions are a set of distinct primitives for LLM Coding Tools
(like Claude Code, CodeX, Copilot CLI, etc.) which provides finer
control and may sometime alter the way a LLM model produces an output.
The solve different problem and are often confused.

# 🧠 SKILL.md

A bundled package of *domain knowledge + instructions* (plus, an
options scripts/assets) that the LLM loads on-demand when a task
matches its description. Typically a folder with a SKILL.md
(front matter: name, description, optional allowed-tools) plus
supporting files.

**✅ When to Use**

    * You have repeatable, procedural know-how ("how to write a
      :mod:`pandas` style transform", "how to fill a PDF form", "our
      company's API pagination convention").
    * The knowledge is too large to keep in system prompt for every
      turn (token cost) but should be available when needed.
    * You want portable, shareable capability packs (drop into
      any repo / share with team).
    * The trigger is content-based ("is this about PDFs?") rather
      than event-based.

**❌ When Not to Use**

    * The behavior must run on every request → use a system
      instruction / AGENTS.md / copilot-instructions.md instead.
    * You need to block or modify tool calls → use a hook.
    * It's a one-off task → just prompt directly.
    * The "skill" is really just a single function call → expose it
      as a tool/MCP server.

# 🤖 AGENTS.md

A separately-scoped LLM invocation with its own system prompt, tool
allow-list, model choice, and isolated context window. The parent
agent delegates a task and receives back only the final result.

**✅ When to Use**

    * The task is independently scoped and you only need the result,
      not the trail (e.g. "explore this large codebase and tell me
      where auth is handled").
    * You want parallelism - fan out several independent
      investigations at once.
    * You want context isolation - keep noisy intermediate output
      (test logs, search dumps) out of the main thread.
    * The sub-task benefits from a different model (cheap model for
      grep-heavy exploration, premium model for reasoning).
    * You want least-privilege tool access (e.g. a "code-review" agent
      that can read but not write).

**❌ When Not to Use**

    * The task is simple/single-step - overhead and latency aren't
      worth it; just do it inline.
    * The work needs tight back-and-forth with the user - sub-agents
      are batch, not interactive.
    * You need to share state continuously - sub-agents are stateless;
      everything must be passed in the prompt.
    * You're tempted to spawn them "just in case" - they cost tokens
      and rarely beat a direct grep.

# 🪝 HOOKS.md

Deterministic scripts that the runtime executes at lifecycle events -
*before* a tool runs, *after* it runs, on session start, on user
prompt submit, etc. They can inspect, block, modify, or augment the
action. Not an LLM call - plain code (shell/Python).

**✅ When to Use**

    * Safety / guardrails - block rm -rf, prevent edits to prod/ paths,
      deny shell commands containing secrets.
    * Policy enforcement - auto-run formatter/linter after every edit;
      reject commits without conventional-commit prefix.
    * Audit / logging - record every tool call to a file for compliance.
    * Deterministic injection - auto-add a header to every file the
      agent creates; inject env info on session start.
    * Cost / quota gates - block expensive operations outside
      business hours.

**❌ When Not to Use**

    * The decision requires judgment or context understanding → that's
      an LLM job (skill or agent).
    * The logic is task-specific rather than cross-cutting → put it
      in the prompt.
    * You'd need the hook to "ask the model" - hooks must be
      deterministic and fast.
    * A simpler instruction in AGENTS.md would suffice - hooks add
      operational complexity (failure modes, debugging, cross-platform
      scripts).

# Rule of Thumb

A simple rule of thumb to determine the correct extension can be - (I)
SKILL.md → Knowledge for an LLM, (II) AGENTS.md → Isolation of Logic,
and (III) HOOKS.md → Policy Rules.
"""

