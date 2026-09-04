# AgentCore Gateway agent — calls tools via MCP Gateway
# -------------------------------------------------------
# This agent connects to the AgentCore MCP Gateway using the mcp_client tool.
# The gateway endpoint URL is injected via env var at runtime.
#
# Why a gateway instead of direct tool calls?
#   - The gateway handles authentication (SigV4, OAuth, API keys) for you
#   - You can add/remove tool targets without redeploying the agent
#   - The gateway enforces rate limits and Cedar policies (see 07_policy_guardrails/)
#   - The agent sees a standard MCP interface regardless of backend type
#     (Lambda, REST API, MCP server — all look the same to the agent)

import os
from typing import Any
from strands import Agent
from strands.agent.conversation_manager.null_conversation_manager import NullConversationManager
from strands_tools import mcp_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model

app = BedrockAgentCoreApp()
log = app.logger

# AgentCore injects the gateway endpoint URL automatically when the gateway
# resource is wired to this agent in agentcore.json.
# For local dev, set GATEWAY_MCP_ENDPOINT in agentcore/.env.local.
GATEWAY_ENDPOINT = os.environ.get("GATEWAY_MCP_ENDPOINT", "")

if GATEWAY_ENDPOINT:
    # Connect to the AgentCore MCP Gateway via Streamable HTTP transport.
    # The gateway handles auth — no API key needed in the agent.
    gateway_tool = mcp_client(
        transport="streamable-http",
        url=GATEWAY_ENDPOINT,
    )
    tools = [gateway_tool]
    log.info(f"Gateway connected: {GATEWAY_ENDPOINT}")
else:
    # No gateway configured — warn and run without tools.
    # Set GATEWAY_MCP_ENDPOINT in agentcore/.env.local for local dev.
    log.warning("GATEWAY_MCP_ENDPOINT not set — agent has no tools")
    tools = []


DEFAULT_SYSTEM_PROMPT = """
You are a helpful assistant with access to tools provided via a managed gateway.
Use the available tools to complete tasks. If a tool is not available, say so clearly.
"""


def agent_factory():
    cache = {}

    def get_or_create_agent(session_id, user_id):
        key = f"{session_id}/{user_id}"
        if key not in cache:
            cache[key] = Agent(
                model=load_model(),
                conversation_manager=NullConversationManager(),
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                tools=tools,
            )
        return cache[key]

    return get_or_create_agent


get_or_create_agent = agent_factory()


def _extract_prompt(payload: dict) -> str:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")
    return prompt


@app.entrypoint
async def invoke(payload, context):
    log.info("Gateway agent: invoking...")

    session_id = getattr(context, "session_id", "default-session")
    user_id    = getattr(context, "user_id",    "default-user")

    agent  = get_or_create_agent(session_id, user_id)
    prompt = _extract_prompt(payload)

    async for event in agent.stream_async(prompt):
        if not isinstance(event, dict) or "event" not in event:
            continue
        cbs = event["event"].get("contentBlockStart")
        if cbs is not None and not cbs.get("start"):
            continue
        yield event


if __name__ == "__main__":
    app.run()


# ── How to run locally ────────────────────────────────────────────────────
# Set the gateway endpoint in agentcore/.env.local:
#     GATEWAY_MCP_ENDPOINT=https://...agentcore.amazonaws.com/...
#
# Run:
#     agentcore dev
#     agentcore invoke --dev "Count the words in: hello world foo bar"
#
# ── How to deploy ─────────────────────────────────────────────────────────
# See 04_gateway_mcp/README.md for the full setup sequence.
#
#     agentcore deploy
#     agentcore invoke "Count the words in this sentence"
