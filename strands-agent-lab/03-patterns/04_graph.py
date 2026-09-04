# Pattern 4 - Graph (deterministic pipeline / DAG)
# ------------------------------------------------
# You define the route yourself: nodes (agents) connected by edges. Strands runs
# them in dependency order and passes each node's output to the next. No model
# decides the routing - YOU do, by wiring the edges.
#
# When to use: you already know the exact steps and their order (a pipeline),
# and you want it reproducible and auditable. Least "agentic", most reliable.
# Edges can also be CONDITIONAL (run a node only if a check passes).

from strands import Agent
from strands.multiagent import GraphBuilder
from common import nova

# Two agents = two stages of a fixed pipeline.
research = Agent(name="research", model=nova(),
                 system_prompt="List 3 factual selling points for the product.")
write = Agent(name="write", model=nova(temperature=0.7),
              system_prompt="Turn the selling points into one short tagline.")

# Build the graph explicitly.
builder = GraphBuilder()
builder.add_node(research, "research")     # node id "research"
builder.add_node(write, "write")           # node id "write"
builder.add_edge("research", "write")      # research -> write (write waits for research)
builder.set_entry_point("research")        # start here

# Cap total node executions. Our graph is linear (no cycle), but setting this
# silences the "Graph without execution limits may run indefinitely" warning and
# is good hygiene once you add conditional/looping edges.
builder.set_max_node_executions(10)

# Optional conditional edge example (commented - shows the shape):
# def has_points(state):
#     return "point" in str(state.results.get("research").result).lower()
# builder.add_edge("research", "write", condition=has_points)

graph = builder.build()


if __name__ == "__main__":
    result = graph("Product: a noise cancelling headphone")
    print("\n--- graph trace ---")
    print("status:", result.status)


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 03-patterns/04_graph.py
