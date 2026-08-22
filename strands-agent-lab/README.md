# Strands Agent Lab

Learning-by-doing with the [Strands Agents SDK](https://strandsagents.com) on
Amazon Bedrock (Nova), from a hello-world agent to multi-agent architectures,
observability, and deployment on Bedrock AgentCore.

## Setup

- **Model:** Amazon Nova Lite, `us-east-1`
- **Credentials:** [aws-vault](https://github.com/ByteNess/aws-vault) profile `strands-lab` (keys stay in Keychain)
- **Runner:** [uv](https://docs.astral.sh/uv/)

Run any file:

```bash
aws-vault exec strands-lab -- uv run 01-hello/hello.py
```

## Phases

| Folder | What |
|--------|------|
| `01-hello/` | Smallest agent + one custom tool |
| `02-patterns/` | 7 multi-agent patterns (orchestrator, swarm, graph, mesh, hierarchy, web search) |
| `03-observability/` | Metrics + OpenTelemetry tracing |
| `04-agentcore/` | Deploy to Bedrock AgentCore Runtime (AgentCore CLI, CodeZip) |

## Key ideas

- A model only knows its **pretraining** unless you give it a **tool** or context.
- Web access = a tool (`07_web_search.py`), never the model itself.
- On Bedrock, **no** model has web search built in — you always add it.
- Pick the least autonomy that solves the problem: Graph (you route) → Swarm (agents route).
