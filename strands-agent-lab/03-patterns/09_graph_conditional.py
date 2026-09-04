# Pattern 9 - Graph with conditional branching (if/else in a DAG)
# ----------------------------------------------------------------
# This extends the linear graph from pattern 04 (04_graph.py) with REAL
# conditional edges. The pipeline branches based on content — different
# nodes run depending on what the classifier decides.
#
# Pipeline shape:
#
#   classify
#      ├── [if technical] ──► expand   (adds depth, examples, detail)
#      └── [if broad]     ──► simplify (reduces to 3 bullet points)
#
# Key Strands concept: `add_edge(src, dst, condition=fn)`
#   `condition` is a Python function that receives the graph state and returns
#   True (run this edge) or False (skip it). Only ONE branch fires per run.
#
# When to use conditional graphs:
#   - You know the possible paths upfront but which one applies depends on input
#   - You want a DETERMINISTIC pipeline (you control routing, not the model)
#   - You need different processing for different content types

from strands import Agent
from strands.multiagent import GraphBuilder
from common import nova


# ── Node agents ───────────────────────────────────────────────────────────
classify = Agent(
    name="classify",
    model=nova(0.0),   # low temp: we want a consistent, deterministic label
    system_prompt=(
        "Classify the given topic as either 'technical' or 'broad'. "
        "A topic is 'technical' if it involves specific technology, code, "
        "algorithms, or engineering concepts. It is 'broad' if it is a "
        "general concept, business topic, or non-technical subject. "
        "Reply with EXACTLY one word: either 'technical' or 'broad'."
    ),
)

expand = Agent(
    name="expand",
    model=nova(0.3),
    system_prompt=(
        "You received a technical topic. Expand it with: "
        "(1) a precise definition, "
        "(2) two concrete code or engineering examples, "
        "(3) one common pitfall to avoid."
    ),
)

simplify = Agent(
    name="simplify",
    model=nova(0.3),
    system_prompt=(
        "You received a broad/general topic. Distil it into exactly 3 bullet "
        "points that a non-specialist can understand in under 30 seconds."
    ),
)


# ── Condition functions ───────────────────────────────────────────────────
# Each condition reads the 'classify' node's output from the graph state.
# state.results is a dict: {node_id: AgentResult}.

def is_technical(state) -> bool:
    """True if the classifier said 'technical'."""
    result = state.results.get("classify")
    if not result:
        return False
    return "technical" in str(result.result).lower()


def is_broad(state) -> bool:
    """True if the classifier said 'broad'."""
    result = state.results.get("classify")
    if not result:
        return False
    return "broad" in str(result.result).lower()


# ── Build the graph ───────────────────────────────────────────────────────
builder = GraphBuilder()
builder.add_node(classify, "classify")
builder.add_node(expand,   "expand")
builder.add_node(simplify, "simplify")

# Conditional edges: only ONE will fire per run.
builder.add_edge("classify", "expand",   condition=is_technical)
builder.add_edge("classify", "simplify", condition=is_broad)

builder.set_entry_point("classify")
builder.set_max_node_executions(5)   # safety cap

graph = builder.build()


if __name__ == "__main__":
    print("=== Topic 1: technical → should route to 'expand' ===")
    result = graph("Explain Python's asyncio event loop")
    print("Path taken:", [n.node_id for n in result.node_history])

    print("\n=== Topic 2: broad → should route to 'simplify' ===")
    result = graph("Explain technology")
    print("Path taken:", [n.node_id for n in result.node_history])

    print("\n=== Topic 3: technical → should route to 'expand' ===")
    result = graph("How does AWS Lambda cold start work?")
    print("Path taken:", [n.node_id for n in result.node_history])


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 03-patterns/09_graph_conditional.py
#
# Watch the "Path taken" output — each run shows which branch fired.
# Technical topics go through classify → expand.
# Broad topics go through classify → simplify.
