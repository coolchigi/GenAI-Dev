# Built-in tool: use_llm — delegate to a sub-agent (same model)
# --------------------------------------------------------------
# `use_llm` spawns a child agent using the SAME model as the parent and
# calls it with a task string. The child agent inherits the parent's model
# and, optionally, a filtered subset of the parent's tools.
#
# This is the tool-based way to do "agent as a tool" (compare to
# 03-patterns/01_agents_as_tools.py which uses the @tool decorator manually).
# The difference: use_llm is a built-in that the parent model can call itself
# at runtime, without the developer pre-defining which sub-agents exist.
#
# When to use:
#   - The parent needs to break a task into parts and parallelize or sequence
#     sub-tasks without the developer explicitly defining each specialist.
#   - You want flexible, ad-hoc delegation rather than fixed specialists.
#
# When NOT to use:
#   - You need the sub-agent to use a DIFFERENT model → use use_agent instead.
#   - You need named, reusable specialists → use agents-as-tools pattern.

from strands import Agent
from strands_tools import use_llm
from common import nova


# The parent agent has use_llm available — it can spin up sub-tasks on demand.
agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a project manager. When given a complex task, break it into "
        "sub-tasks and use use_llm to delegate each sub-task to a focused "
        "sub-agent. Synthesise the results into a final answer."
    ),
    tools=[use_llm],
)


if __name__ == "__main__":
    agent(
        "I need a market overview for electric vehicles. "
        "Please: (1) summarise the key market trends, "
        "(2) list the top 5 manufacturers by market share, "
        "(3) identify the biggest growth barriers. "
        "Delegate each part to a separate sub-agent and combine the results."
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required.
#
#     aws-vault exec strands-lab -- uv run 02-tools/06_builtin_agents_orchestration/01_use_llm.py
