# Pattern 6 - Multi-level hierarchy (true "hierarchical agents")
# --------------------------------------------------------------
# File 02 was a ONE-level hierarchy: a supervisor over specialists. A real
# hierarchy has MORE THAN ONE level: a top boss delegates to team leads, and
# each team lead delegates to its own workers. You build this by nesting the
# agents-as-tools pattern - a tool can itself be an agent that has its own tools.
#
#   CEO (top supervisor)
#   ├── content_team  (team lead)   -> writer, editor  (workers)
#   └── data_team     (team lead)   -> analyst        (worker)
#
# When to use: the problem decomposes into departments, each with its own
# sub-tasks. Keeps each level's prompt small. Trade-off: more levels = more
# model calls = more latency and cost.

from strands import Agent, tool
from common import nova


# ---- Workers (leaf level) -------------------------------------------------
@tool
def writer(brief: str) -> str:
    """Write a short product blurb from a brief."""
    a = Agent(model=nova(0.7), system_prompt="Write a 2-sentence product blurb.")
    return str(a(brief))


@tool
def editor(text: str) -> str:
    """Tighten and proofread a blurb."""
    a = Agent(model=nova(0.2), system_prompt="Tighten this copy to one sentence.")
    return str(a(text))


@tool
def analyst(topic: str) -> str:
    """Give 3 factual data points about a product."""
    a = Agent(model=nova(), system_prompt="List 3 factual data points.")
    return str(a(topic))


# ---- Team leads (middle level) - each is an agent with its own workers -----
@tool
def content_team(task: str) -> str:
    """Produce polished marketing copy (writing + editing)."""
    lead = Agent(
        model=nova(),
        system_prompt="You lead the content team. Use writer to draft, then "
        "editor to polish. Return the final copy.",
        tools=[writer, editor],
    )
    return str(lead(task))


@tool
def data_team(task: str) -> str:
    """Produce factual data points about a product."""
    lead = Agent(
        model=nova(),
        system_prompt="You lead the data team. Use analyst to get facts.",
        tools=[analyst],
    )
    return str(lead(task))


# ---- Top supervisor (root) -------------------------------------------------
ceo = Agent(
    model=nova(),
    system_prompt=(
        "You are the CEO. Delegate: call data_team for facts, then content_team "
        "to turn those facts into final copy. Present the final copy."
    ),
    tools=[content_team, data_team],
)


if __name__ == "__main__":
    ceo("Produce a one-sentence marketing blurb for a reusable steel water bottle.")


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 02-patterns/06_hierarchical.py
