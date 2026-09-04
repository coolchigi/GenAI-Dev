# Built-in tool: retrieve — semantic search against a Bedrock Knowledge Base
# ---------------------------------------------------------------------------
# `retrieve` performs semantic (vector) search against an Amazon Bedrock
# Knowledge Base. You give it a query string; it returns the most relevant
# passages from your documents along with their source location and a
# relevance score.
#
# When to use:
#   - Your agent needs to answer questions grounded in YOUR documents
#     (internal wikis, product docs, policy manuals, etc.)
#   - You want RAG (Retrieval-Augmented Generation) without building
#     the retrieval pipeline yourself
#   - You want source citations with every answer
#
# Prerequisites:
#   1. A Bedrock Knowledge Base must already exist in your AWS account.
#      Create one in the Bedrock console: https://console.aws.amazon.com/bedrock/
#      → Knowledge bases → Create knowledge base → point at an S3 bucket.
#   2. Set KB_ID to the knowledge base ID (format: e.g. "ABCDEF1234")
#   3. The strands-lab IAM user needs bedrock:Retrieve permission on the KB.

import os
from strands import Agent
from strands_tools import retrieve
from common import nova

# Read the knowledge base ID from the environment — never hardcode resource IDs.
KB_ID = os.environ.get("KB_ID")
if not KB_ID:
    raise EnvironmentError(
        "KB_ID environment variable is not set.\n"
        "Export your Bedrock Knowledge Base ID before running:\n"
        "    export KB_ID=<your-knowledge-base-id>"
    )


# Pass the KB ID as a tool configuration override so the agent always searches
# the right knowledge base without the model having to specify it.
agent = Agent(
    model=nova(0.0),   # low temperature = stick to retrieved facts, don't hallucinate
    system_prompt=(
        "You are a knowledgeable assistant. When asked a question, use the "
        "retrieve tool to search the knowledge base for relevant information, "
        "then answer based on what you find. Always cite the source documents "
        "returned by the retrieve tool."
    ),
    tools=[retrieve],
    # The tool reads BEDROCK_KNOWLEDGE_BASE_ID from env if not passed inline.
    # We set it in the environment below so the tool picks it up automatically.
)

# Make the KB ID available to the retrieve tool via env (it reads this key).
os.environ["BEDROCK_KNOWLEDGE_BASE_ID"] = KB_ID


if __name__ == "__main__":
    # Replace with a question relevant to YOUR knowledge base content.
    agent(
        "What are the main topics covered in the knowledge base? "
        "Search for 'overview' and summarise what you find."
    )

    # Example with a specific question:
    # agent("What is the refund policy?")
    # agent("How do I set up two-factor authentication?")


# ── How to run ────────────────────────────────────────────────────────────
# Requirements:
#   - AWS credentials with bedrock:Retrieve permission
#   - A Bedrock Knowledge Base with documents ingested
#
# Setup:
#   1. Create a Knowledge Base in the Bedrock console (10 min)
#      - Data source: an S3 bucket with a few .txt or .pdf files
#      - Embeddings model: Titan Text Embeddings v2
#      - Vector store: the console creates an OpenSearch Serverless collection
#   2. Note the Knowledge Base ID (shown in the console, format: XXXXXXXXXX)
#   3. Export it:
#         export KB_ID=XXXXXXXXXX
#
# Run:
#     aws-vault exec strands-lab -- uv run 02-tools/02_builtin_data_rss/02_retrieve_knowledge_base.py
#
# Tip: The retrieve tool also accepts numberOfResults, scoreThreshold, and
# metadata filters as parameters. The model can pass these when it calls
# the tool, or you can set defaults via env vars:
#   BEDROCK_KNOWLEDGE_BASE_NUMBER_OF_RESULTS (default: 5)
#   BEDROCK_KNOWLEDGE_BASE_SCORE_THRESHOLD   (default: 0.0)
