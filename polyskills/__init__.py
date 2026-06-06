# -*- encoding: utf-8 -*-

"""
Python Framework to Manage AI Customization Rules across LLM Tools
==================================================================

The :mod:`polyskills` is a Python open-source framework to manage AI
skills, agents, hooks, etc. from version controlled remote URL across
different LLM providers by fetching self-contained files written in
Agent Skills' native ``SKILL.md`` format that can work natively with
Claude Code and can also be loaded as a system prompt for other LLM
tools like CodeX, Cursor AI, etc. The library can fetch, install,
and update portable LLM "skills", "agents" from remote URL thus
providing one source of truth across different system and projects.
"""

__version__ = "v1.0.0"

# init-time options registrations, use api/ for public functions

# ? bootstrap the local tracking database on first import; the call
# ? is wrapped in a broad try/except so any unexpected failure (read
# ? only home dir, exotic filesystem) cannot ever break ``import``.
# ? the bootstrap honours the internal POLYSKILLS_DISABLE_BOOTSTRAP
# ? hook so test harnesses can suppress on-disk artefacts entirely.
import os as _os

if _os.environ.get("POLYSKILLS_DISABLE_BOOTSTRAP", "").lower() not in (
    "1", "true", "yes"
):
    try:
        from polyskills.db import get_tracker as _get_tracker
        _get_tracker()
    except Exception:
        pass
