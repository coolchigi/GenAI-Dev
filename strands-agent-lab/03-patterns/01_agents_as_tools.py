# Pattern 1 - Agents as Tools (the core mechanism)
# ------------------------------------------------
# Idea: an Agent can be wrapped inside a @tool function. To the OUTER agent it
# looks like any other tool, but calling it actually runs a whole INNER agent
# with its own system prompt. This is the building block for the "orchestrator"
# pattern in file 02.
#
# When to use: you want a "lead" agent that delegates a sub-task to a
# specialist, and YOU want the lead agent to decide when to do that.

from strands import Agent, tool
from common import nova


# A specialist agent, wrapped as a tool. The docstring is what the outer agent
# reads to decide when to call this - treat it as the tool's "advertisement".
@tool
def spanish_translator(text: str) -> str:
    """Translate the given English text into Spanish."""
    inner = Agent(
        model=nova(),
        system_prompt="You are a professional English-to-Spanish translator. "
        "Return only the translation, nothing else.",
    )
    return str(inner(text))


# The outer / lead agent. It has ONE tool available: the translator specialist.
lead = Agent(
    model=nova(),
    system_prompt="You are a helpful assistant. If the user wants a translation, "
    "use the spanish_translator tool.",
    tools=[spanish_translator],
)


if __name__ == "__main__":
    lead("Please translate to Spanish: 'Good morning, how are you?'")


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 03-patterns/01_agents_as_tools.py
