# Phase 3, file 2 - Distributed tracing with OpenTelemetry (console)
# ------------------------------------------------------------------
# Metrics tell you totals. TRACES tell you the STORY: a tree of spans showing
# each step (model call, each tool call, nested agents) with timing and token
# counts per span. This is what makes a swarm or hierarchy legible.
#
# Strands emits OpenTelemetry (OTEL). You choose an EXPORTER:
#   - console  -> prints spans to your terminal (here, no infra)
#   - OTLP     -> ships to a backend (Jaeger, Langfuse, CloudWatch, AgentCore)
#
# CRITICAL: set up telemetry BEFORE you create the Agent, or spans won't attach.

from strands import Agent, tool
from strands.models import BedrockModel
from strands.telemetry import StrandsTelemetry

# 1) Turn on tracing FIRST.
StrandsTelemetry().setup_console_exporter()

# 2) Now build the agent - it's auto-instrumented from here on.
model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


agent = Agent(model=model, tools=[add])

if __name__ == "__main__":
    # After the answer you'll see OTEL spans printed as JSON - one per model call
    # and tool call, with duration and token attributes.
    agent("What is 17 + 25? Use the add tool.")


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 04-observability/02_tracing_console.py
#
# ── Ship to a REAL backend instead of console ────────────────────────────────
#       import os
#       os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
#       StrandsTelemetry().setup_otlp_exporter()   # instead of console
#
#   In Phase 4, AgentCore gives you a managed OTEL endpoint + CloudWatch, so you
#   set the env var and get traces with no collector to run yourself.
