# Custom tool: web_search via DuckDuckGo (no API key)
# -----------------------------------------------------
# A Strands agent can only reach the internet through a tool you give it.
# This file shows the simplest possible web search tool: a custom @tool backed
# by the `ddgs` package (DuckDuckGo search). No API key, no account, no signup.
#
# This is the standalone version of the pattern shown in
# 03-patterns/07_web_search.py — same tool, same idea, extracted here so the
# tools section is self-contained.
#
# When to use: quick demos, development, any situation where you don't want
# to manage an API key. For production or LLM-optimised results, see
# 01_builtin_http_web/03_other_search_providers.py (Tavily, Exa).

from ddgs import DDGS
from strands import Agent, tool
from common import nova


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for current information and return the top results.

    Use this when you need up-to-date facts, news, prices, or anything you
    might not already know. `query` is a plain search phrase. `max_results`
    controls how many results to return (default 5, max 10).

    Returns a numbered list of results with title, URL, and snippet.
    """
    with DDGS() as ddgs:
        hits = list(ddgs.text(query, max_results=max_results))

    if not hits:
        return "No results found."

    lines = []
    for i, h in enumerate(hits, 1):
        lines.append(
            f"{i}. {h.get('title', '')}\n"
            f"   {h.get('href', '')}\n"
            f"   {h.get('body', '')}"
        )
    return "\n\n".join(lines)


# temperature=0.0 keeps the agent close to what the search results actually say.
researcher = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a research assistant. When a question needs current or factual "
        "information, call web_search first, then answer using the results. "
        "Always cite the source URLs you used."
    ),
    tools=[web_search],
)


if __name__ == "__main__":
    researcher(
        "What are the latest features added to Amazon Bedrock? Cite your sources."
    )


# ── How to run ────────────────────────────────────────────────────────────
# No API key needed. AWS credentials required for the Bedrock model.
#
#     aws-vault exec strands-lab -- uv run 02-tools/01_builtin_http_web/02_web_search_ddgs.py
#
# Dependency: `ddgs` is already in pyproject.toml.
# If you need to add it: uv add ddgs
