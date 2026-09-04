# Phase 4, file 3 - Distributed tracing with OTLP → Jaeger
# ----------------------------------------------------------
# File 02 (02_tracing_console.py) printed spans to the terminal. That's fine
# for a quick look, but hard to navigate in a multi-agent system with dozens
# of nested spans. A REAL trace backend gives you:
#   - A visual span tree (see the full call graph)
#   - Timeline view (see exactly which calls were slow)
#   - Search across trace sessions
#   - Persisted history (not just the current terminal)
#
# Jaeger is a free, open-source distributed tracing system. It receives OTEL
# spans over OTLP (gRPC or HTTP) and renders them in a browser UI.
#
# CRITICAL POINT: The agent code below is BYTE-FOR-BYTE identical to
# 04-observability/02_tracing_console.py. The only difference is the
# StrandsTelemetry setup line. This is the point — your observability backend
# is a ONE-LINE configuration change, not a code change.
#
# All backends supported by swapping setup_*_exporter():
#   setup_console_exporter()  → print to terminal (file 02)
#   setup_otlp_exporter()     → ship to any OTEL backend (this file)
#   Same code, different destination.

import os
from strands import Agent, tool
from strands.models import BedrockModel
from strands.telemetry import StrandsTelemetry

# 1) Configure the OTLP exporter BEFORE creating the Agent.
#    Strands auto-instruments all agents created after this call.
#
# Default OTLP endpoint is http://localhost:4318 (OTLP/HTTP).
# Override with the env var if you're using a different backend.
OTEL_ENDPOINT = os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "http://localhost:4318"  # Jaeger all-in-one default
)
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = OTEL_ENDPOINT

StrandsTelemetry().setup_otlp_exporter()  # ← the ONE line that differs from file 02

# 2) Build the agent — identical to file 02 from here on.
model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


@tool
def add(a: int, b: int) -> int:
    """Add two integers and return their sum."""
    return a + b


agent = Agent(model=model, tools=[add])


if __name__ == "__main__":
    print(f"Sending traces to: {OTEL_ENDPOINT}")
    print("Open http://localhost:16686 to view traces in Jaeger.\n")

    agent("What is 17 + 25? Use the add tool.")
    agent("What is 100 + 42? Use the add tool.")

    print("\nTraces sent. Refresh the Jaeger UI to see the new spans.")
    print("In Jaeger: search for Service = 'strands-agent' to find your traces.")


# ── How to run ────────────────────────────────────────────────────────────
# Step 1: Start Jaeger all-in-one (single Docker container, no compose needed)
#
#     docker run -d --name jaeger \
#       -p 4317:4317 \
#       -p 4318:4318 \
#       -p 16686:16686 \
#       jaegertracing/all-in-one:latest
#
#   Port 4317 = OTLP/gRPC receiver
#   Port 4318 = OTLP/HTTP receiver  ← Strands uses this by default
#   Port 16686 = Jaeger UI
#
# Step 2: Open Jaeger UI
#     open http://localhost:16686
#
# Step 3: Run the agent
#     aws-vault exec strands-lab -- uv run 04-observability/03_otlp_jaeger.py
#
# Step 4: In Jaeger UI, select Service = "strands-agent" and click "Find Traces".
#         You'll see two traces, each with:
#           - One span for the full agent turn
#           - One span for the Bedrock model call
#           - One span for the add tool execution
#
# To use a different OTEL backend (Langfuse, Grafana Tempo, CloudWatch):
#     export OTEL_EXPORTER_OTLP_ENDPOINT=https://your-backend-endpoint
#     aws-vault exec strands-lab -- uv run 04-observability/03_otlp_jaeger.py
#
# To stop Jaeger when done:
#     docker stop jaeger && docker rm jaeger
