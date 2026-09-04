# Built-in tool: use_agent — delegate to a sub-agent (any model provider)
# ------------------------------------------------------------------------
# `use_agent` is like `use_llm` but allows the parent to switch to a
# DIFFERENT model provider for the sub-task. Supported providers:
#   bedrock, anthropic, openai, ollama, github, env (reads from env vars)
#
# This enables cross-provider delegation patterns:
#   - Parent uses Nova Lite (cost-efficient) for orchestration
#   - Sub-task that needs stronger reasoning uses Claude or GPT-4
#   - Sub-task that needs code generation uses a code-specialised model
#   - Local tasks use Ollama (no cloud, no cost)
#
# The provider and model settings are passed by the PARENT MODEL at call time —
# you configure allowed options in the tool, the model chooses per task.

from strands import Agent
from strands_tools import use_agent
from common import nova


agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a task router. You have access to multiple AI providers via "
        "use_agent. Route tasks to the appropriate provider:\n"
        "- Use 'bedrock' with 'amazon.nova-lite-v1:0' for general tasks\n"
        "- Use 'bedrock' with 'amazon.nova-pro-v1:0' for tasks needing deep reasoning\n"
        "Always explain which provider you chose and why."
    ),
    tools=[use_agent],
)


if __name__ == "__main__":
    print("=== Route to Nova Lite (general task) ===")
    agent(
        "Use the bedrock provider with amazon.nova-lite-v1:0 to "
        "write a one-sentence description of AWS Lambda."
    )

    print("\n=== Route to Nova Pro (reasoning task) ===")
    agent(
        "Use the bedrock provider with amazon.nova-pro-v1:0 to "
        "analyse the trade-offs between serverless and containerised "
        "deployment for a high-throughput API (>10k req/s)."
    )

    # ── To use Anthropic Claude (requires ANTHROPIC_API_KEY) ────────────
    # agent(
    #     "Use the anthropic provider with claude-3-5-haiku-20241022 to "
    #     "write a haiku about cloud computing."
    # )

    # ── To use a local Ollama model (requires Ollama running locally) ────
    # agent(
    #     "Use the ollama provider with llama3.2 to answer: "
    #     "What is the capital of France?"
    # )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required (for bedrock provider).
# Additional keys needed for other providers:
#   export ANTHROPIC_API_KEY=...   # for anthropic provider
#   export OPENAI_API_KEY=...      # for openai provider
#   (Ollama: run `ollama serve` locally, no key needed)
#
#     aws-vault exec strands-lab -- uv run 02-tools/06_builtin_agents_orchestration/02_use_agent.py
