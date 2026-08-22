# Phase 2 - Multi-agent architecture patterns

Run any file from the `strands-agent-lab/` folder:

```bash
aws-vault exec strands-lab -- uv run 02-patterns/01_agents_as_tools.py
```

## The files

| File | Pattern | Who decides the route? |
|------|---------|------------------------|
| `01_agents_as_tools.py` | Agent wrapped as a tool | The lead agent (ad hoc) |
| `02_orchestrator.py` | Supervisor + specialists (1 level) | One central agent (planned) |
| `03_swarm.py` | Peer hand-off (3 agents) | The agents themselves |
| `04_graph.py` | Fixed pipeline / DAG | You (hard-wired edges) |
| `05_swarm_mesh.py` | Collaborative mesh (shared context) | The agents themselves |
| `06_hierarchical.py` | Multi-level hierarchy (boss → leads → workers) | Each level delegates down |
| `07_web_search.py` | Agent with a real web-search tool (no key) | — (shows tool use) |

## When to use which

- **Agents-as-tools** — building block. A lead agent occasionally needs a specialist.
- **Orchestrator** — known specialties, central control, one final answer. Predictable.
- **Swarm** — path unknown up front; agents decide who works next. Use the caps.
- **Graph** — you know the exact steps and order. Most reliable, least "agentic".
- **Collaborative mesh** (`05`) — 3+ agents share one context (blackboard). Keep one node terminal so it can't loop.
- **Multi-level hierarchy** (`06`) — nest agents-as-tools; costs more calls.

## Rule of thumb

More control (Graph) = predictable, less adaptive. More autonomy (Swarm) = adaptive, harder to debug. Start with the least autonomy that solves the problem.

### Note on the blog's `agent_graph` tool

The AWS blog builds mesh networks with the built-in `agent_graph` tool. As of
strands-agents-tools 0.8.6 that tool is **deprecated** (prints a removal warning,
points to `Swarm` / graph). So `05` uses `Swarm` for the same shared-context mesh.
