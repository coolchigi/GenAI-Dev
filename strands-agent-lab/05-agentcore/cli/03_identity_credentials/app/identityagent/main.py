# AgentCore Identity agent — reads injected credentials at runtime
# ----------------------------------------------------------------
# This agent demonstrates AgentCore Identity credential injection.
# The Tavily API key is stored in AgentCore as a credential resource named
# "tavilyKey". At runtime, AgentCore injects it as CREDENTIAL_TAVILYKEY.
#
# The agent reads it via os.getenv() — the key is never in source code.
#
# For local dev, set CREDENTIAL_TAVILYKEY in agentcore/.env.local.
# agentcore dev sets LOCAL_DEV=1 automatically so the agent reads from there
# instead of the AgentCore Identity service.

import os
from typing import Any
from strands import Agent, tool
from strands.agent.conversation_manager.null_conversation_manager import NullConversationManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model

app = BedrockAgentCoreApp()
log = app.logger

# AgentCore injects this at runtime. Locally: set in agentcore/.env.local.
# Format: CREDENTIAL_<RESOURCE_NAME_UPPERCASE>
TAVILY_API_KEY = os.environ.get("CREDENTIAL_TAVILYKEY", "")


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for current information using Tavily.

    Use this to find up-to-date facts, news, and answers to questions.
    `query` is a plain search phrase. `max_results` controls how many
    results to return (default 5).
    Returns titles, URLs, and snippets for the top results.
    """
    if not TAVILY_API_KEY:
        return (
            "CREDENTIAL_TAVILYKEY is not set. "
            "Add it in agentcore/.env.local for local dev, or deploy and "
            "configure the credential resource in AgentCore."
        )

    # Use Tavily's REST API directly via requests to keep dependencies simple.
    # In production, you could also use `from strands_tools import tavily`.
    import requests
    resp = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": TAVILY_API_KEY, "query": query, "max_results": max_results},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(
            f"{i}. {r.get('title', '')}\n"
            f"   {r.get('url', '')}\n"
            f"   {r.get('content', '')[:200]}"
        )
    return "\n\n".join(lines)


DEFAULT_SYSTEM_PROMPT = """
You are a research assistant that can search the web for current information.
When asked a question that requires current facts, use web_search.
Always cite the source URLs from your search results.
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
                tools=[web_search],
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
    log.info("Identity agent: invoking...")

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
# 1. Add your Tavily key to agentcore/.env.local:
#        echo "CREDENTIAL_TAVILYKEY=tvly-..." >> 05-agentcore/cli/agentcore/.env.local
#
# 2. From 05-agentcore/cli/:
#        agentcore dev
#        agentcore invoke --dev "Search for: Amazon Bedrock AgentCore features"
#
# ── How to deploy ─────────────────────────────────────────────────────────
# 1. Add the credential resource:
#        agentcore add credential --name tavilyKey --type API_KEY
#    (enter your Tavily key when prompted)
#
# 2. Deploy:
#        agentcore deploy
#        agentcore invoke "What's new in Amazon Bedrock this month?"
