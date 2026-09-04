# Built-in tool: memory — CRUD + semantic search on a Bedrock Knowledge Base
# ---------------------------------------------------------------------------
# `memory` provides persistent, searchable memory backed by a Bedrock Knowledge
# Base with a CUSTOM data source. Unlike `retrieve` (read-only search), `memory`
# lets the agent both WRITE new memories and READ them back.
#
# Actions:
#   store    — save a piece of information to the knowledge base
#   retrieve — semantic search: find memories similar to a query
#   list     — list all stored memory records
#   get      — retrieve a specific memory record by ID
#   delete   — delete a memory record by ID
#
# The difference vs `retrieve` (02_builtin_data_rss/02_retrieve_knowledge_base.py):
#   retrieve  = read-only search on a KB you pre-populated (e.g. S3 documents)
#   memory    = read-write: the AGENT stores and retrieves its own memories
#
# Note: AgentCore Memory (a managed, session-aware version of this) is covered
# in 05-agentcore/cli/02_memory/ where the AgentCore resource already exists.
#
# Prerequisites:
#   - A Bedrock Knowledge Base with a CUSTOM data source (not S3).
#     Create in console: Bedrock → Knowledge bases → New → Data source: Custom
#   - KB_ID env var set to the knowledge base ID

import os
from strands import Agent
from strands_tools import memory
from common import nova

KB_ID = os.environ.get("KB_ID")
if not KB_ID:
    raise EnvironmentError(
        "KB_ID environment variable is not set.\n"
        "Create a Bedrock Knowledge Base with a CUSTOM data source and export:\n"
        "    export KB_ID=<your-knowledge-base-id>"
    )

# The memory tool reads BEDROCK_KNOWLEDGE_BASE_ID from env.
os.environ["BEDROCK_KNOWLEDGE_BASE_ID"] = KB_ID

agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are an assistant with persistent memory. Use the memory tool to "
        "store important facts the user shares, and retrieve them when relevant. "
        "When storing, be concise. When retrieving, surface the most relevant facts."
    ),
    tools=[memory],
)


if __name__ == "__main__":
    print("=== Store some facts ===")
    agent(
        "Remember these facts: "
        "The project name is 'Strands Agent Lab'. "
        "The primary model is Amazon Nova Lite. "
        "The AWS region is us-east-1."
    )

    print("\n=== Retrieve a fact ===")
    agent("What do you know about the AWS region being used?")

    print("\n=== List all memories ===")
    agent("List all the facts you have stored.")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required.
# A Bedrock Knowledge Base with CUSTOM data source required.
#
# Setup:
#   1. In the Bedrock console: Knowledge bases → Create
#      - Data source: Custom (not S3 — Custom allows programmatic writes)
#      - Embeddings: Titan Text Embeddings v2
#      - Vector store: OpenSearch Serverless (auto-created)
#   2. Note the KB ID from the console
#   3. Export it:
#         export KB_ID=XXXXXXXXXX
#
# Run:
#     aws-vault exec strands-lab -- uv run 02-tools/05_builtin_memory/02_memory_kb.py
