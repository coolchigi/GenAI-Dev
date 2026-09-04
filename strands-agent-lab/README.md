# Strands Agent Lab

Learning-by-doing with the [Strands Agents SDK](https://strandsagents.com) on
Amazon Bedrock (Nova Lite) — from a hello-world agent to exhaustive tool coverage,
multi-agent architecture patterns, observability, and deployment on Bedrock AgentCore.

## Setup

- **Model:** Amazon Nova Lite, `us-east-1`
- **Credentials:** [aws-vault](https://github.com/ByteNess/aws-vault) profile `strands-lab` (keys stay in Keychain)
- **Runner:** [uv](https://docs.astral.sh/uv/)

Run any file:

```bash
aws-vault exec strands-lab -- uv run 01-hello/hello.py
```

Files that need no AWS credentials say so in their `How to run` block:

```bash
uv run 02-tools/02_builtin_data_rss/01_rss_feedparser.py
```

---

## Learning path

Work through the sections in order. Each section builds on the previous:

```
01-hello/          ← start here — smallest possible agent
02-tools/          ← exhaustive tool coverage (built-in + custom)
03-patterns/       ← multi-agent architecture patterns
04-observability/  ← metrics, traces, OTEL backends
05-agentcore/      ← deploy to Bedrock AgentCore Runtime
```

---

## Phases

| Folder | What | Files |
|---|---|---|
| `01-hello/` | Smallest agent + one custom tool | 1 |
| `02-tools/` | All 50 built-in tools + custom tool patterns | 33 |
| `03-patterns/` | 10 multi-agent patterns | 10 |
| `04-observability/` | Metrics + OTEL traces (console, Jaeger, AgentCore) | 4 |
| `05-agentcore/` | Deploy to Bedrock AgentCore (by-hand + CLI) | — |

---

## `02-tools/` — tool categories

| Category | Folder | Key tools | Needs key? |
|---|---|---|---|
| HTTP & Web | `01_builtin_http_web/` | `http_request`, DuckDuckGo, Tavily, Exa | No / optional |
| Data & RSS | `02_builtin_data_rss/` | feedparser (RSS), `retrieve` (KB) | AWS creds |
| Compute | `03_builtin_compute/` | `calculator`, `python_repl`, `shell` | AWS creds |
| AWS | `04_builtin_aws/` | `use_aws`, `generate_image`, `nova_reels` | AWS creds |
| Memory | `05_builtin_memory/` | `journal` (local), `memory` (Bedrock KB) | No / AWS |
| Orchestration | `06_builtin_agents_orchestration/` | `use_llm`, `use_agent`, `workflow`, `graph`, `mcp_client` | AWS creds |
| Browser | `07_builtin_browser_computer/` | `local_chromium_browser`, `use_computer` | playwright |
| Comms / Media | `08_builtin_comms_media/` | `slack`, `image_reader`, `speak`, Stability AI | varies |
| Custom patterns | `09_custom_tools/` | @tool anatomy, Pydantic, state, async, confirmation, dynamic loading | AWS creds |
| Deprecated | `10_deprecated_reference/` | Reference: rss, batch, think, cron, diagram + replacements | — |

> **AgentCore-dependent tools** (`agent_core_memory`, `agent_core_code_interpreter`,
> `agent_core_browser`) are covered in `05-agentcore/cli/` where the required cloud
> resources are already configured.

---

## `03-patterns/` — when to use which

| File | Pattern | Who routes? |
|---|---|---|
| `01_agents_as_tools.py` | Agent wrapped as a tool | Lead agent (ad hoc) |
| `02_orchestrator.py` | Supervisor + specialists | One central agent (planned) |
| `03_swarm.py` | Peer hand-off | Agents themselves |
| `04_graph.py` | Fixed pipeline / DAG | You (hard-wired edges) |
| `05_swarm_mesh.py` | Collaborative mesh (shared context) | Agents themselves |
| `06_hierarchical.py` | Multi-level hierarchy | Each level delegates down |
| `07_web_search.py` | Agent with web search | — (tool demo) |
| `08_parallel_fanout.py` | N specialists run concurrently, results merged | `asyncio.gather` |
| `09_graph_conditional.py` | Graph with if/else branching | You (condition functions) |
| `10_a2a_protocol.py` | Agent-to-Agent over HTTP (A2A protocol) | Network / HTTP |

**Rule of thumb:** More control (Graph) = predictable, less adaptive.
More autonomy (Swarm) = adaptive, harder to debug. Start with the least autonomy
that solves the problem.

---

## `05-agentcore/` — two paths

| Path | When to use |
|---|---|
| `by-hand/` | Understand the raw AWS API calls; no CLI dependency |
| `cli/` | Production workflow; full feature surface via AgentCore CLI |

### `cli/` sections

| Folder | What |
|---|---|
| `00_setup.md` | Prerequisites, IAM policy, CLI install, aws-targets.json |
| `01_runtime_hello/` | Baseline hello-world agent (helloagent) |
| `02_memory/` | All four memory strategies (SEMANTIC, SUMMARIZATION, USER_PREFERENCE, EPISODIC) |
| `03_identity_credentials/` | API key + OAuth credential providers |
| `04_gateway_mcp/` | MCP gateway with Lambda target; agent_core_browser |
| `05_evaluation/` | LLM-as-judge + custom evaluator + online eval |
| `06_harness/` | Declarative agent; export to Strands code; agent_core_code_interpreter |
| `07_policy_guardrails/` | Cedar policies + Bedrock content filters |
| `08_observability_agentcore/` | CLI trace commands + CloudWatch Logs Insights queries |

---

## Key ideas

- A model only knows its **pretraining** unless you give it a **tool** or context.
- Web access = a tool (`03-patterns/07_web_search.py`), never the model itself.
- On Bedrock, **no** model has web search built in — you always add it.
- The `@tool` **docstring** is the model's entire description of the tool. Write it clearly.
- Deprecated built-in tools (`rss`, `batch`, `think`, `cron`, `diagram`, `current_time`, `sleep`)
  will raise errors in `strands-agents-tools` v0.9.0 — see `02-tools/10_deprecated_reference/`.
- Pick the least autonomy that solves the problem: Graph (you route) → Swarm (agents route).
- Observability backend = a one-line config change, not a code change.
