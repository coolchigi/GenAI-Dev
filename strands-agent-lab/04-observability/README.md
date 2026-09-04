# Phase 3 - Observability (o11y)

```bash
aws-vault exec strands-lab -- uv run 04-observability/01_builtin_metrics.py
aws-vault exec strands-lab -- uv run 04-observability/02_tracing_console.py
```

## The three primitives

| Primitive | Answers | In this lab |
|-----------|---------|-------------|
| **Metrics** | "How much?" tokens, latency, cycles | `01` — `result.metrics` (free) |
| **Traces** | "What happened, step by step?" | `02` — OTEL spans via `StrandsTelemetry` |
| **Logs** | "What did the code say?" | standard Python `logging` |

Metrics to spot a problem, traces to find where, logs for raw detail.

## Where to ship traces

| Backend | Setup | Notes |
|---------|-------|-------|
| Console | none | dev only |
| Jaeger (local) | container + OTLP `:4318` | free trace UI |
| Langfuse | OTLP endpoint + key | LLM-focused |
| AgentCore Observability | env var only (Phase 4) | AWS-managed, CloudWatch |

Your agent code doesn't change between backends — only the exporter config does.
Set up telemetry **before** creating the Agent, or spans won't attach.
