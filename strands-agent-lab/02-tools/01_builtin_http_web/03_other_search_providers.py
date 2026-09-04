# Built-in tools: Tavily, Exa, Bright Data — production-grade search
# -------------------------------------------------------------------
# This file is a survey of the three commercial search providers available
# as built-in Strands tools. Each needs an API key, so only one section
# is active at a time. Uncomment the section for the provider you have a
# key for and comment the others out.
#
# Why use these over the free DuckDuckGo approach (02_web_search_ddgs.py)?
#   - Tavily: tuned for LLM consumption — results are pre-processed, ranked
#     by relevance to the query, not just keyword match
#   - Exa: neural (semantic) search — finds conceptually related results,
#     not just keyword matches; great for research tasks
#   - Bright Data: scraping-first — bypasses bot protection, gets full page
#     content, screenshots, and multiple search engines (Google/Bing/Yandex)
#
# The agent code is IDENTICAL for all three providers — only the imported
# tool changes. That's the point of the @tool abstraction.

from strands import Agent
from common import nova

# ── PROVIDER SELECTION ────────────────────────────────────────────────────
# Uncomment exactly ONE of the three import blocks below.

# --- Option A: Tavily ---------------------------------------------------
# Free tier available at https://tavily.com (1,000 API calls/month)
# export TAVILY_API_KEY=tvly-...
#
# from strands_tools import tavily as search_tool
# PROVIDER = "Tavily"

# --- Option B: Exa ------------------------------------------------------
# Free trial at https://exa.ai (pricing at exa.ai/pricing)
# export EXA_API_KEY=...
#
# from strands_tools import exa as search_tool
# PROVIDER = "Exa"

# --- Option C: Bright Data ----------------------------------------------
# Plans at https://brightdata.com (no permanent free tier)
# export BRIGHTDATA_API_KEY=...
# export BRIGHTDATA_ZONE=serp  # optional, defaults to 'serp'
#
# from strands_tools import bright_data as search_tool
# PROVIDER = "Bright Data"

# ── FALLBACK (no key) ────────────────────────────────────────────────────
# If you have no key yet, this dummy lets the file still import cleanly so
# you can read the code. The agent below won't run usefully.
try:
    search_tool  # type: ignore[name-defined]
except NameError:
    from strands_tools import http_request as search_tool  # type: ignore
    PROVIDER = "http_request (fallback — uncomment a provider above)"

# ── AGENT ────────────────────────────────────────────────────────────────
# Same agent definition regardless of which tool is active. Swap the tool,
# the agent behaviour doesn't change — that's the value of tool abstraction.
agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a research assistant. Use your search tool to find current, "
        "accurate information. Always cite the URLs from your search results."
    ),
    tools=[search_tool],
)


if __name__ == "__main__":
    print(f"Active provider: {PROVIDER}")   # type: ignore[name-defined]
    agent(
        "What is Amazon Bedrock AgentCore and when did it become generally available?"
    )

    # Tavily-specific: tavily_extract fetches and extracts full page content
    # from a URL — useful when you need more than a snippet.
    # agent("Extract the full content of https://aws.amazon.com/bedrock/agentcore/")

    # Exa-specific: exa_get_contents retrieves full page content + highlights.
    # Similar pattern to tavily_extract but via Exa's neural index.

    # Bright Data-specific: get_screenshot returns a visual snapshot of the page.
    # agent("Take a screenshot of https://aws.amazon.com/bedrock/")


# ── How to run ────────────────────────────────────────────────────────────
# 1. Sign up for one of the providers above and get an API key.
# 2. Export your key:
#       export TAVILY_API_KEY=tvly-...       # or
#       export EXA_API_KEY=...              # or
#       export BRIGHTDATA_API_KEY=...
# 3. Uncomment the matching import block above.
# 4. Run:
#       aws-vault exec strands-lab -- uv run 02-tools/01_builtin_http_web/03_other_search_providers.py
#
# To install a provider's package if not already present:
#       uv add tavily-python     # Tavily
#       uv add exa-py            # Exa (strands_tools uses aiohttp internally)
