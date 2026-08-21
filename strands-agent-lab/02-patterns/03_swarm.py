# Pattern 3 - Swarm (autonomous peer hand-off)
# --------------------------------------------
# No supervisor. Agents are PEERS that hand off to each other by calling an
# auto-injected `handoff_to_agent` tool. Strands shares context between them and
# stops when an agent produces a final answer (or limits are hit).
#
# When to use: the path isn't known up front and you want the agents themselves
# to decide who works next. More flexible than an orchestrator, but less
# predictable - you don't control the exact route.

from strands import Agent
from strands.multiagent import Swarm
from common import nova

# Give each agent a NAME (peers refer to each other by name) and a clear job.
researcher = Agent(
    name="researcher",
    model=nova(),
    system_prompt="You research product ideas. Once you have 2-3 key facts, "
    "hand off to 'writer' to draft copy.",
)

writer = Agent(
    name="writer",
    model=nova(temperature=0.7),
    system_prompt="You write a short marketing tagline from the researcher's "
    "facts. When the tagline is done, hand off to 'genz' to draft a Gen-Z copy.",
)

genz = Agent(
    name="genz",
    model=nova(temperature=0.7),
    system_prompt="You write a Gen-Z funny marketing tagline from the writer's "
    "facts. When the tagline is done, give the final answer (do not hand off).",
)

# Assemble the swarm. entry_point = who receives the task first.
# max_handoffs / max_iterations are safety caps so it can't loop forever.
swarm = Swarm(
    [researcher, writer, genz],
    entry_point=researcher,
    max_handoffs=6,
    max_iterations=6,
)


if __name__ == "__main__":
    result = swarm("Create a tagline for a reusable steel water bottle.")
    print("\n--- swarm trace ---")
    print("status:", result.status)
    print("agents involved:", [n.node_id for n in result.node_history])


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 02-patterns/03_swarm.py
