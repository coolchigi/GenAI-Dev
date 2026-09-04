# AgentCore Memory agent — demonstrates all four memory strategies
# ----------------------------------------------------------------
# This agent uses AgentCore Memory to persist information across sessions.
# The four strategies (SEMANTIC, SUMMARIZATION, USER_PREFERENCE, EPISODIC)
# are configured in agentcore.json; the agent code just wires in the
# session manager and the rest happens automatically.
#
# How it works:
#   1. AgentCoreMemorySessionManager intercepts each agent turn.
#   2. After a turn completes, it extracts memory-worthy content based on
#      the active strategies and stores it in the AgentCore Memory service.
#   3. At the start of each turn, it retrieves relevant memories and injects
#      them into the agent's context.
#   4. The agent "remembers" across sessions without any extra application code.
#
# The MEMORY_MEMORYAGENTMEMORY_ID env var is injected automatically by
# AgentCore at runtime. Locally, set it in agentcore/.env.local.

from typing import Any
from strands import Agent, tool
from strands.agent.conversation_manager.null_conversation_manager import NullConversationManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model
from memory.session import get_memory_session_manager

app = BedrockAgentCoreApp()
log = app.logger


# ── Memory strategy notes (for the reader) ───────────────────────────────
#
# SEMANTIC:        The agent saying "Paris is the capital of France" stores
#                  that as a semantic fact. Later queries like "what city is
#                  the capital of France?" retrieve it via vector similarity.
#
# USER_PREFERENCE: "I prefer concise bullet points" gets stored as a
#                  preference. Future sessions see it injected as context so
#                  the agent already knows how the user likes responses.
#
# SUMMARIZATION:   Long conversations are summarised and the summary is stored.
#                  Prevents context windows from exploding across many turns.
#
# EPISODIC:        "User asked about X at 14:30, agent answered Y, user
#                  followed up with Z." Stores event sequences with timestamps
#                  for audit trails and session replay.


DEFAULT_SYSTEM_PROMPT = """
You are a helpful personal assistant with persistent memory.

You remember facts, preferences, and past conversations across sessions.
When the user shares information about themselves or their preferences,
acknowledge it — you will remember it in future sessions.

When asked "what do you remember about me?", recall everything you know.
"""


@tool
def recall_hint() -> str:
    """Remind yourself to check memory for context about the current user.

    Call this at the start of a conversation to ensure you have retrieved
    any stored memories about this user before responding.
    """
    return (
        "Memory check: review any injected context from previous sessions "
        "and use it to personalise your response."
    )


tools = [recall_hint]


def _make_conversation_manager():
    # NullConversationManager: the session manager handles history;
    # we don't want the default in-memory manager double-storing turns.
    return NullConversationManager()


def agent_factory():
    cache = {}

    def get_or_create_agent(session_id, user_id):
        key = f"{session_id}/{user_id}"
        if key not in cache:
            cache[key] = Agent(
                model=load_model(),
                session_manager=get_memory_session_manager(session_id, user_id),
                conversation_manager=_make_conversation_manager(),
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                tools=tools,
            )
            log.info(f"Created agent for session={session_id} user={user_id}")
        return cache[key]

    return get_or_create_agent


get_or_create_agent = agent_factory()


def _extract_prompt(payload: dict):
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")
    return prompt


@app.entrypoint
async def invoke(payload, context):
    log.info("Memory agent: invoking...")

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
# From 05-agentcore/cli/:
#
#     agentcore dev
#     agentcore invoke --dev "My name is Alex and I work on AI agents."
#     agentcore invoke --dev "What do you know about me?"
#
# ── How to deploy ─────────────────────────────────────────────────────────
#
#     agentcore deploy
#     agentcore invoke --session-id session-A "My name is Alex."
#     agentcore invoke --session-id session-B "Do you know who I am?"
