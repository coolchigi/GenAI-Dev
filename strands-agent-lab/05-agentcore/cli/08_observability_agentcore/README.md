# 08 — AgentCore Observability

When your agent is deployed on AgentCore Runtime, you get three observability
primitives with no extra infrastructure:

| Primitive | CLI command | What you see |
|---|---|---|
| **Logs** | `agentcore logs` | Runtime stdout/stderr, Python logs, errors |
| **Traces** | `agentcore traces list/get` | Full OTEL span tree per session |
| **Metrics** | CloudWatch (auto) | Token usage, latency, invocation count |

All three work immediately after `agentcore deploy`. No exporters to configure,
no collectors to run.

---

## Logs

Stream live runtime logs from a deployed agent:

```bash
# Tail all logs for the default agent
agentcore logs

# Tail logs for a specific agent
agentcore logs --agent helloagent

# Search / filter logs
agentcore logs --filter "ERROR"

# View logs for a specific time range
agentcore logs --since 30m
```

Logs include:
- Python `logging` output from your agent code
- BedrockAgentCoreApp request/response lifecycle events
- Tool call results and errors
- Memory session manager events

---

## Traces

AgentCore automatically collects OTEL traces from every invocation. The runtime
injects `OTEL_EXPORTER_OTLP_ENDPOINT` — your agent just needs the two-line
setup shown in `04-observability/04_agentcore_traces.py`:

```python
from strands.telemetry import StrandsTelemetry
StrandsTelemetry().setup_otlp_exporter()   # reads endpoint from env
```

### CLI trace commands

```bash
# List the 10 most recent trace sessions
agentcore traces list

# List more
agentcore traces list --limit 50

# Download a specific trace to JSON
agentcore traces get --id <trace-id>

# Pretty-print a downloaded trace
agentcore traces get --id <trace-id> | python -m json.tool
```

### What's in a trace

Each trace contains a tree of OTEL spans:

```
agent-turn (root span)
  ├── bedrock-converse       duration=1.2s  input_tokens=312  output_tokens=84
  ├── tool:word_count        duration=0.001s
  └── bedrock-converse       duration=0.9s  input_tokens=420  output_tokens=55
```

Attributes on each span:
- `gen_ai.input_tokens` / `gen_ai.output_tokens` — token counts per model call
- `gen_ai.usage.total_tokens` — total for the turn
- `duration` — wall-clock time for that span
- Tool name, tool input/output (if enabled)

---

## Metrics in CloudWatch

AgentCore automatically writes metrics to CloudWatch. No configuration needed.

### Console

CloudWatch → Metrics → Bedrock → AgentCore → <runtime-name>

Key metrics:
- `InvocationCount` — total invocations
- `Latency` — end-to-end response time (p50, p90, p99)
- `ErrorCount` — failed invocations
- `TokensConsumed` — total tokens (input + output)

### Logs Insights — token usage over time

Paste in CloudWatch Logs Insights (select your AgentCore log group):

```
fields @timestamp, inputTokens, outputTokens
| filter ispresent(inputTokens)
| stats sum(inputTokens)  as totalInputTokens,
        sum(outputTokens) as totalOutputTokens,
        count()           as invocations
  by bin(1h)
| sort @timestamp desc
```

### Logs Insights — error rate

```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() as errorCount by bin(1h)
| sort @timestamp desc
```

### Logs Insights — slowest tool calls

```
fields @timestamp, spanName, duration
| filter ispresent(spanName) and spanName like /tool:/
| sort duration desc
| limit 20
```

---

## OTEL backend: the full picture

```
Your agent code (main.py)
  │  StrandsTelemetry().setup_otlp_exporter()
  │
  ▼
OTEL SDK (Python)
  │  reads OTEL_EXPORTER_OTLP_ENDPOINT (injected by AgentCore)
  ▼
AgentCore OTEL endpoint
  │  managed, no infra to run
  ▼
CloudWatch (X-Ray traces + Logs)
```

Locally (dev), swap the endpoint for a Jaeger container and the agent code
stays identical — see `04-observability/03_otlp_jaeger.py`.

---

## Connecting observability dots across sections

| What you want | Where to look |
|---|---|
| Understand OTEL basics | `04-observability/02_tracing_console.py` |
| Local traces with Jaeger UI | `04-observability/03_otlp_jaeger.py` |
| AgentCore OTEL wiring | `04-observability/04_agentcore_traces.py` |
| CLI trace commands | This file (above) |
| Token usage in deployed agents | CloudWatch Logs Insights (above) |
| Eval scores over time | `05_evaluation/` + `agentcore evals history` |
