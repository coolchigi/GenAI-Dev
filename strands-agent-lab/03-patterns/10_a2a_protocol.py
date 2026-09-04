# Pattern 10 - Agent-to-Agent (A2A) protocol
# -------------------------------------------
# A2A is Google's open Agent-to-Agent protocol. Unlike Strands' in-process
# patterns (agents-as-tools, swarm, graph), A2A works over HTTP — agents
# discover and call each other across the network, across frameworks, and
# potentially across organisations.
#
# How it works:
#   1. An A2A SERVER exposes an "agent card" at /.well-known/agent.json
#      describing its capabilities and endpoint URL.
#   2. An A2A CLIENT discovers the server via the agent card URL and calls it
#      using the A2A protocol's JSON message format.
#   3. Communication uses standard HTTP POST — no shared memory, no SDK version
#      coupling, no framework dependency.
#
# When to use A2A vs in-process patterns:
#   In-process (agents-as-tools, swarm, graph):
#     - Both agents in the same Python process
#     - Same deployment, same runtime, same framework
#     - Lower latency, simpler setup
#
#   A2A:
#     - Agents run on different machines / services
#     - Different frameworks (a Strands client calling a LangChain server)
#     - Different organisations (external partner agents)
#     - When you need an HTTP API boundary for security, versioning, or isolation
#
# This file runs BOTH the server and client. In production, they would be
# separate services.
#
# Requires: strands-agents-tools >= 0.8.6 (a2a_client tool)

import asyncio
import threading
import time
from strands import Agent, tool
from strands_tools.a2a_client import A2AClientToolProvider
from common import nova

# ── Server agent ──────────────────────────────────────────────────────────
# This agent will be exposed as an A2A server.
# In production, run this as a separate service (e.g. in Docker, Lambda, ECS).

@tool
def summarise_text(text: str) -> str:
    """Summarise a block of text into one sentence."""
    # A simple non-LLM summary for demo purposes.
    words = text.split()
    if len(words) <= 20:
        return text
    return " ".join(words[:20]) + "... [summarised]"


server_agent = Agent(
    name="summariser-server",
    model=nova(0.0),
    system_prompt=(
        "You are a summarisation specialist. When given any text or topic, "
        "produce a single, clear sentence that captures the key point. "
        "Be concise and precise."
    ),
    tools=[summarise_text],
)

# ── A2A server runner ─────────────────────────────────────────────────────
# BedrockAgentCoreApp wraps the agent as an HTTP server on port 8765.
# We run it in a background thread so the client can call it from the same script.

SERVER_PORT = 8765
SERVER_URL  = f"http://localhost:{SERVER_PORT}"

def start_server():
    """Start the A2A server in a background thread."""
    from bedrock_agentcore.runtime import BedrockAgentCoreApp

    app = BedrockAgentCoreApp()

    @app.entrypoint
    def invoke(payload):
        prompt = payload.get("prompt", "")
        result = server_agent(prompt)
        return {"result": str(result)}

    # Run on a non-standard port so it doesn't conflict with other services.
    app.run(host="0.0.0.0", port=SERVER_PORT)


# ── Client agent ──────────────────────────────────────────────────────────
# The client discovers the server via its agent card and calls it via A2A.

def build_client_agent():
    """Build the client agent with A2A tool pointing at the local server."""
    a2a_provider = A2AClientToolProvider(
        agent_card_url=f"{SERVER_URL}/.well-known/agent.json",
    )

    return Agent(
        name="client-orchestrator",
        model=nova(0.3),
        system_prompt=(
            "You are an orchestrator. You have access to a remote summarisation "
            "agent via the A2A protocol. When asked to summarise text, call the "
            "remote agent tool and return its response."
        ),
        tools=a2a_provider.tools,
    )


if __name__ == "__main__":
    print("Starting A2A server in background thread...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Give the server a moment to start up.
    time.sleep(2)
    print(f"Server running at {SERVER_URL}\n")

    print("Building client agent...")
    client = build_client_agent()

    print("\n=== Client calling remote server via A2A ===")
    client(
        "Summarise this for me using the remote summarisation agent: "
        "'Amazon Bedrock is a fully managed service that offers a choice of "
        "high-performing foundation models from leading AI companies via a "
        "single API, along with a broad set of capabilities you need to build "
        "generative AI applications with security, privacy, and responsible AI.'"
    )

    print("\n=== Second call — cross-agent via network ===")
    client(
        "Ask the remote agent: What is the Strands SDK in one sentence?"
    )

    print("\nDone. (Server thread will stop when script exits.)")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required. Both agents use the same Bedrock model.
#
# Single-process mode (server + client in one script — demo only):
#     aws-vault exec strands-lab -- uv run 03-patterns/10_a2a_protocol.py
#
# Production mode (two terminals):
#   Terminal 1 — run just the server:
#     aws-vault exec strands-lab -- python -c "
#     from 10_a2a_protocol import start_server; start_server()
#     "
#   Terminal 2 — run just the client:
#     aws-vault exec strands-lab -- python -c "
#     from 10_a2a_protocol import build_client_agent
#     client = build_client_agent()
#     client('Summarise: ...')
#     "
#
# Note: bedrock-agentcore must be installed (it's in pyproject.toml).
