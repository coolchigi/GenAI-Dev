# Pattern 2 - Orchestrator / Supervisor (agents-as-tools, scaled up)
# ------------------------------------------------------------------
# Same mechanism as file 01, but now the lead ("supervisor") has SEVERAL
# specialists and routes each request to the right one - and can combine them.
# This is what people usually mean by "orchestrator": one brain that plans and
# delegates, specialists that just do their one job.
#
# When to use: tasks that split cleanly into known specialties, and you want
# central control over routing and a single final answer. Predictable, easy to
# debug. The supervisor is the bottleneck (everything flows through it).

from strands import Agent, tool
from common import nova


@tool
def researcher(query: str) -> str:
    """Find and summarize factual background on a topic."""
    a = Agent(model=nova(), system_prompt="You are a concise research analyst. "
              "Give 2-3 bullet points of factual background.")
    return str(a(query))


@tool
def copywriter(brief: str) -> str:
    """Write short, punchy marketing copy from a brief."""
    a = Agent(model=nova(temperature=0.7),  # more creative
              system_prompt="You are a snappy marketing copywriter. "
              "Write one short tagline.")
    return str(a(brief))


# The supervisor sees both specialists and decides the order: research first,
# then hand the findings to the copywriter.
supervisor = Agent(
    model=nova(),
    system_prompt=(
        "You are a marketing supervisor. For a product request: first call "
        "researcher for background, then call copywriter to produce a tagline "
        "based on that background. Present the final tagline to the user."
    ),
    tools=[researcher, copywriter],
)


if __name__ == "__main__":
    supervisor("We're launching a durable backpack that competes with the Aer Travel Pack 4. Give me a tagline.")


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 02-patterns/02_orchestrator.py
