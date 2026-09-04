# Built-in tool: graph — DAG execution via the tool interface
# ------------------------------------------------------------
# The `graph` tool from strands-agents-tools provides a DAG (directed acyclic
# graph) execution engine accessible as a tool the MODEL can call.
#
# Compare to 03-patterns/04_graph.py (SDK GraphBuilder):
#   SDK GraphBuilder  — you write the graph structure in Python code at
#                       development time; the graph is fixed when you deploy.
#   graph tool        — the MODEL defines the graph at runtime by calling the
#                       tool with a list of nodes and edges; the structure is
#                       dynamic and determined by the model.
#
# When to use the tool version:
#   - The graph structure varies based on the input (the model decides the
#     pipeline shape per request).
#   - You want the agent to be able to describe and execute its own pipeline.
#
# When to use the SDK version (03-patterns/04_graph.py):
#   - The pipeline structure is fixed and known at deploy time.
#   - You want maximum reproducibility and auditability.

from strands import Agent
from strands_tools import graph
from common import nova


agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a pipeline architect. Use the graph tool to design and execute "
        "directed acyclic graph (DAG) pipelines. Each node is an agent task; "
        "edges define the execution order. Define nodes with clear names and "
        "descriptions, then run the graph."
    ),
    tools=[graph],
)


if __name__ == "__main__":
    agent(
        "Build and execute a graph pipeline to create a blog post outline for "
        "'The Future of AI Agents'. The pipeline should have:\n"
        "- Node 'research': gather key themes and recent developments\n"
        "- Node 'outline': create a structured outline (depends on 'research')\n"
        "- Node 'hooks': write 3 compelling opening hooks (depends on 'research')\n"
        "- Node 'combine': merge outline and hooks into a final document "
        "  (depends on 'outline' and 'hooks')\n"
        "Run it and show the final combined output."
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required.
#
#     aws-vault exec strands-lab -- uv run 02-tools/06_builtin_agents_orchestration/04_graph_tool.py
