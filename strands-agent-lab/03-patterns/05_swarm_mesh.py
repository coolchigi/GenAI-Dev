# Pattern 5 - Collaborative mesh (research + creative + critic)
# -------------------------------------------------------------
# This is the blog's "swarm of agents in a mesh / blackboard" idea, done with
# the SUPPORTED api. (The blog uses the built-in `agent_graph` tool, but that
# tool is now DEPRECATED - it prints a removal warning and points you at the
# `Swarm` / graph primitives. So we use `Swarm` here.)
#
# Why Swarm counts as a "mesh": Swarm keeps ONE shared working context that every
# agent reads and writes (that's the blackboard), and ANY agent can hand off to
# ANY other agent (that's the mesh - not a fixed line).
#
# Roles (collaborative swarm - they build on each other toward consensus):
#   researcher -> gathers facts, hands to creative
#   creative   -> proposes a tagline, hands to critic
#   critic     -> TERMINAL: always finalizes (never hands back)

from strands import Agent
from strands.multiagent import Swarm
from common import nova

researcher = Agent(
    name="researcher",
    model=nova(),
    system_prompt="You gather 2-3 factual selling points, then hand off to "
    "'creative'. Do not write marketing copy yourself.",
)

creative = Agent(
    name="creative",
    model=nova(temperature=0.8),  # high temp = more idea variety
    system_prompt="You turn the researcher's facts into ONE punchy tagline, then "
    "hand off to 'critic' for review. Do not hand off to anyone else.",
)

# The critic is TERMINAL: it always produces the final answer and never hands
# back. This guarantees the swarm ends. (An earlier version let the critic bounce
# work back to creative - realistic, but it ping-ponged past the iteration cap
# and the swarm returned FAILED. A terminal judge is the simplest fix.)
critic = Agent(
    name="critic",
    model=nova(temperature=0.2),  # low temp = strict, consistent judgement
    system_prompt="You are the final reviewer. Take the creative's tagline and "
    "give the FINAL answer: if it's already strong keep it, otherwise improve it "
    "yourself in one line. Never hand off - you always finish the task.",
)

swarm = Swarm(
    [researcher, creative, critic],
    entry_point=researcher,
    max_handoffs=8,
    max_iterations=8,
)


if __name__ == "__main__":
    result = swarm("Create a tagline for a reusable steel water bottle.")
    print("\n--- mesh trace ---")
    print("status:", result.status)
    print("path:", [n.node_id for n in result.node_history])


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 03-patterns/05_swarm_mesh.py
