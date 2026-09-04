# Phase 3, file 1 - Built-in metrics (zero setup, no external tools)
# ------------------------------------------------------------------
# EVERY agent call already returns metrics. Calling an agent returns an
# `AgentResult`, and `result.metrics` (an EventLoopMetrics object) records:
# model round-trips ("cycles"), duration, tokens, and which tools ran.
#
# Why you care: tokens = cost, cycles/duration = latency, tool_usage = whether
# the model actually used your tools. Cheapest observability there is.

from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


@tool
def word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())


agent = Agent(model=model, tools=[word_count])

# Capture the result instead of ignoring it.
result = agent("How many words are in 'the quick brown fox jumps'? Use the tool.")

m = result.metrics                      # EventLoopMetrics
summary = m.get_summary()               # dict overview

print("\n================ METRICS ================")
print("model round-trips (cycles):", summary["total_cycles"])
print("total duration (s):        ", round(summary["total_duration"], 3))
print("token usage:               ", m.accumulated_usage)   # input/output/total
print("tool usage:                ", summary["tool_usage"])
print("=========================================")


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 04-observability/01_builtin_metrics.py
