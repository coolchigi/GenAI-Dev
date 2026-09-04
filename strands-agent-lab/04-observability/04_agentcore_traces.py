# Phase 4, file 4 - OTEL traces wired to AgentCore (CloudWatch)
# -------------------------------------------------------------
# When your agent is deployed on Bedrock AgentCore Runtime, you get a managed
# observability backend for free — no Jaeger to run, no collector to maintain.
# AgentCore automatically injects the OTEL endpoint via environment variable.
#
# This file is IDENTICAL to 03_otlp_jaeger.py except for one detail:
# instead of hardcoding the endpoint to localhost:4318, we READ it from the
# environment variable that AgentCore sets automatically at runtime.
#
# Locally (development):
#   OTEL_EXPORTER_OTLP_ENDPOINT is not set → we default to localhost:4318
#   (same as file 03, useful for local dev with a Jaeger container)
#
# Deployed on AgentCore:
#   OTEL_EXPORTER_OTLP_ENDPOINT is injected by the runtime automatically
#   → traces go to the AgentCore managed backend → visible in CloudWatch
#
# Your agent code does not change between local dev and production.
# The backend is determined by the environment, not the code.
# This is the full OTEL portability promise.

import os
from strands import Agent, tool
from strands.models import BedrockModel
from strands.telemetry import StrandsTelemetry

# AgentCore injects OTEL_EXPORTER_OTLP_ENDPOINT automatically when deployed.
# Locally, fall back to Jaeger on localhost so you can develop and test.
endpoint = os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "http://localhost:4318"   # local fallback (run Jaeger — see file 03)
)

# Set it back in the environment so StrandsTelemetry can read it.
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = endpoint

# Must be called BEFORE creating the Agent.
StrandsTelemetry().setup_otlp_exporter()

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


@tool
def add(a: int, b: int) -> int:
    """Add two integers and return their sum."""
    return a + b


agent = Agent(model=model, tools=[add])


if __name__ == "__main__":
    is_agentcore = "OTEL_EXPORTER_OTLP_ENDPOINT" in os.environ
    if is_agentcore:
        print(f"Running on AgentCore — traces go to: {endpoint}")
    else:
        print("Running locally — traces go to Jaeger at http://localhost:16686")
        print("(Start Jaeger first — see 04-observability/03_otlp_jaeger.py)")

    agent("What is 17 + 25? Use the add tool.")
    print("Done — check your trace backend for the new span.")


# ── How to run ────────────────────────────────────────────────────────────
#
# ── Local development (same as 03_otlp_jaeger.py) ────────────────────────
#   Start Jaeger:
#     docker run -d --name jaeger -p 4318:4318 -p 16686:16686 jaegertracing/all-in-one:latest
#
#   Run:
#     aws-vault exec strands-lab -- uv run 04-observability/04_agentcore_traces.py
#
#   View: http://localhost:16686
#
# ── Deployed on AgentCore ─────────────────────────────────────────────────
#   When this file is the entrypoint of an AgentCore runtime, the endpoint
#   env var is set automatically. No configuration needed on your part.
#
#   To view traces after deployment:
#     agentcore traces list                  # list recent trace sessions
#     agentcore traces get --id <trace-id>   # download a trace to JSON
#
#   Or in CloudWatch:
#     CloudWatch → X-Ray traces → Filter by service name "strands-agent"
#
# ── CloudWatch Logs Insights — token usage over time ──────────────────────
# Paste this query in CloudWatch Logs Insights to chart token consumption:
#
#   fields @timestamp, inputTokens, outputTokens
#   | filter ispresent(inputTokens)
#   | stats sum(inputTokens) as totalInput, sum(outputTokens) as totalOutput by bin(1h)
#   | sort @timestamp desc
#
# See 05-agentcore/cli/08_observability_agentcore/ for the full observability
# CLI reference (agentcore logs, agentcore traces, CloudWatch queries).
