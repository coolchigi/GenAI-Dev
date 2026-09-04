# Pattern 7 - Giving an agent real web search (no API key)
# --------------------------------------------------------
# A Strands agent can only reach the internet through a TOOL you give it. Here we
# write a `web_search` tool backed by DuckDuckGo via the `ddgs` package - no API
# key, no signup. The model calls it like any other tool; Strands feeds the
# results back and the model answers from them.
#
# Swapping in a "real" search API later (e.g. Tavily) is a one-function change -
# see the note at the bottom.

from ddgs import DDGS
from strands import Agent, tool
from common import nova


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return the top results (title, url, snippet).

    Use this when you need current facts, news, prices, or anything you might
    not already know. `query` is a normal search phrase.
    """
    with DDGS() as ddgs:
        hits = list(ddgs.text(query, max_results=max_results))

    if not hits:
        return "No results found."

    lines = []
    for i, h in enumerate(hits, 1):
        lines.append(f"{i}. {h.get('title','')}\n   {h.get('href','')}\n   {h.get('body','')}")
    return "\n".join(lines)


# An agent that knows it can search. Temperature 0 = stick to the facts found.
researcher = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a research assistant. When a question needs current or factual "
        "information, call web_search first, then answer using the results and "
        "cite the source URLs you used."
    ),
    tools=[web_search],
)


if __name__ == "__main__":
    researcher("What is the Amazon Bedrock AgentCore, and is it generally available? Cite sources.")


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 03-patterns/07_web_search.py
#
# ── Swap in Tavily (better, LLM-tuned results) later ─────────────────────────
#   1) uv add tavily-python   (or use the built-in `from strands_tools import tavily`)
#   2) export TAVILY_API_KEY=...        (free tier at tavily.com)
#   3) replace the body of web_search with a Tavily call, keep the @tool signature.
#      The agent code above does not change at all - that's the point of tools.
