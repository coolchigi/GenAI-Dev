# Custom tools: async @tool — non-blocking I/O-bound tools
# ---------------------------------------------------------
# By default, Strands tools are synchronous. If your tool does I/O-bound work
# (HTTP calls, database queries, file reads), you can make it `async` to avoid
# blocking the event loop.
#
# When to use async tools:
#   - The tool makes network calls (HTTP, gRPC, WebSocket)
#   - The tool queries a database
#   - You have MULTIPLE tools that can run concurrently within one agent turn
#     (Strands runs concurrent tool calls in the same event loop iteration)
#
# When NOT to use async:
#   - The tool does CPU-bound work (use a thread pool instead)
#   - Simplicity matters more than performance (sync is easier to debug)
#
# Usage: async tools work with both `agent(...)` (sync) and
# `await agent.stream_async(...)`. Strands handles the bridging automatically.

import asyncio
import time
import aiohttp
from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


# ── Async tool: non-blocking HTTP call ───────────────────────────────────
@tool
async def fetch_url_async(url: str) -> str:
    """Fetch the content of a URL asynchronously.

    Use this to retrieve data from a web URL. Unlike a synchronous HTTP call,
    this does not block while waiting for the response, allowing other work
    to proceed concurrently.

    `url` must be a valid HTTP or HTTPS URL.
    Returns the first 500 characters of the response body.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            text = await resp.text()
            # Truncate to avoid flooding the model context
            return f"Status: {resp.status}\nContent (first 500 chars):\n{text[:500]}"


# ── Async tool: simulated concurrent data fetch ──────────────────────────
@tool
async def fetch_multiple_async(urls: str) -> str:
    """Fetch multiple URLs concurrently and return a summary of all responses.

    `urls` is a comma-separated list of URLs to fetch simultaneously.
    All requests run in parallel — total time ≈ slowest single request.
    Returns status codes and content previews for each URL.
    """
    url_list = [u.strip() for u in urls.split(",") if u.strip()]
    if not url_list:
        return "No URLs provided."

    async def _fetch_one(session: aiohttp.ClientSession, url: str) -> str:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                text = await resp.text()
                return f"[{resp.status}] {url}: {text[:200]}"
        except Exception as e:
            return f"[ERROR] {url}: {e}"

    async with aiohttp.ClientSession() as session:
        start = time.monotonic()
        results = await asyncio.gather(*[_fetch_one(session, url) for url in url_list])
        elapsed = time.monotonic() - start

    output = "\n\n".join(results)
    return f"Fetched {len(url_list)} URLs in {elapsed:.2f}s (concurrent):\n\n{output}"


agent = Agent(
    model=model,
    system_prompt=(
        "You are a web assistant. Use fetch_url_async to retrieve a single URL "
        "or fetch_multiple_async to fetch several URLs concurrently. "
        "Report the status code and key content for each URL."
    ),
    tools=[fetch_url_async, fetch_multiple_async],
)


if __name__ == "__main__":
    print("=== Single async fetch ===")
    agent("Fetch https://httpbin.org/get and tell me what it returns.")

    print("\n=== Concurrent fetch (all at once) ===")
    agent(
        "Fetch these three URLs concurrently and report the status of each: "
        "https://httpbin.org/get, https://httpbin.org/ip, https://httpbin.org/uuid"
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required for the model.
# aiohttp required for the async HTTP calls:
#     uv add aiohttp
#
#     aws-vault exec strands-lab -- uv run 02-tools/09_custom_tools/04_async_tool.py
#
# Note: the concurrent fetch example shows the key benefit of async tools —
# three HTTP calls complete in the time of one.
