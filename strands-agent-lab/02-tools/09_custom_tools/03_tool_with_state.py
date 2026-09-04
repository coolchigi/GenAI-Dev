# Custom tools: class-based tools with shared state
# --------------------------------------------------
# Sometimes a tool needs to hold state between calls — a cache, a connection,
# a counter, a session. The way to do this in Strands is with a class-based tool.
#
# Pattern:
#   1. Create a class whose __init__ sets up the shared state.
#   2. Decorate a method (or __call__) with @tool.
#   3. Create an instance and pass it in the tools=[] list.
#
# The instance is long-lived — it persists for the entire agent session.
# State accumulates across tool calls in the same session.
#
# Example use cases:
#   - Cache expensive external lookups (avoid redundant API calls)
#   - Maintain a session-scoped counter or ledger
#   - Hold a database connection open across calls
#   - Accumulate agent observations into a shared structure

from strands import Agent, tool
from strands.models import BedrockModel
from typing import Optional

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


class ProductCatalog:
    """A tool that caches product lookups to avoid redundant calls.

    In a real implementation, _fetch_from_db would call a database or API.
    Here we use a static dict as a stand-in.
    """

    def __init__(self):
        # This cache persists for the entire agent session.
        # First lookup hits the "database"; subsequent lookups are instant.
        self._cache: dict[str, dict] = {}
        self._lookup_count = 0
        self._cache_hits = 0

    def _fetch_from_db(self, product_id: str) -> Optional[dict]:
        """Simulate a slow database lookup."""
        import time
        time.sleep(0.1)   # simulate latency
        db = {
            "P001": {"name": "Strands Backpack",   "price": 129.99, "stock": 42},
            "P002": {"name": "AgentCore Notebook",  "price": 24.99,  "stock": 7},
            "P003": {"name": "Nova Lite Water Bottle", "price": 34.99, "stock": 0},
        }
        return db.get(product_id)

    @tool
    def lookup_product(self, product_id: str) -> str:
        """Look up a product by its ID and return its name, price, and stock level.

        Returns product details or a 'not found' message. Results are cached —
        repeat lookups for the same product ID are served from cache instantly.

        `product_id` format: 'P' followed by three digits (e.g. 'P001', 'P002').
        """
        self._lookup_count += 1

        if product_id in self._cache:
            self._cache_hits += 1
            p = self._cache[product_id]
            return (
                f"[CACHED] {p['name']} — ${p['price']:.2f} — "
                f"{'In stock (' + str(p['stock']) + ')' if p['stock'] > 0 else 'Out of stock'}"
            )

        p = self._fetch_from_db(product_id)
        if not p:
            return f"Product '{product_id}' not found in catalog."

        self._cache[product_id] = p
        return (
            f"{p['name']} — ${p['price']:.2f} — "
            f"{'In stock (' + str(p['stock']) + ')' if p['stock'] > 0 else 'Out of stock'}"
        )

    @tool
    def catalog_stats(self) -> str:
        """Return stats about how many product lookups have been made this session.

        Call this at the end of a session to see cache performance.
        Returns total lookups, cache hits, and the cache hit rate.
        """
        hit_rate = (self._cache_hits / self._lookup_count * 100) if self._lookup_count else 0
        return (
            f"Lookups this session: {self._lookup_count}\n"
            f"Cache hits: {self._cache_hits}\n"
            f"Cache hit rate: {hit_rate:.1f}%"
        )


# Create ONE instance — this is the stateful object passed to the agent.
catalog = ProductCatalog()

agent = Agent(
    model=model,
    system_prompt=(
        "You are a product assistant. Use lookup_product to check product details. "
        "If asked for the same product more than once, note that it's served from cache."
    ),
    # Pass the BOUND METHODS (they carry the instance state with them).
    tools=[catalog.lookup_product, catalog.catalog_stats],
)


if __name__ == "__main__":
    agent("What's the price and stock status for P001, P002, and P003?")
    # Second lookup for P001 — should be served from cache.
    agent("Check P001 again. Is it still in stock?")
    agent("Show me the catalog stats for this session.")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required.
#
#     aws-vault exec strands-lab -- uv run 02-tools/09_custom_tools/03_tool_with_state.py
