# -*- encoding: utf-8 -*-

"""
LLM Application Management Tools & Prompt Parsers
-------------------------------------------------

Manager for LLM tools - for example if a tool accepts the extensions
in an Agent Skills format then directly write, or use the parser to
convert the skills to an prompt type format.
"""

from enum import Enum

class SupportedTools(Enum):
    CLAUDE_CODE = "https://claude.com/product/claude-code"
    GITHUB_COPILOT = "https://github.com/features/copilot"
