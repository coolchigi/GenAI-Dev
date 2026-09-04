# Custom tool: RSS feed reader via feedparser
# --------------------------------------------
# The built-in `rss` tool from strands-agents-tools is DEPRECATED in v0.8.6
# and will raise an error in v0.9.0. The recommended replacement is to use
# `feedparser` directly, wrapped in a custom @tool.
#
# This is the correct pattern going forward. It's also simpler — feedparser
# is a single-purpose, well-maintained library with no hidden state files or
# env-var configuration.
#
# No AWS credentials required. No API key. Just a public RSS URL and feedparser.

import feedparser
from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


@tool
def fetch_rss(url: str, max_items: int = 10) -> str:
    """Fetch and return the latest entries from an RSS or Atom feed.

    Use this to get current news, blog posts, or announcements from a feed URL.
    Returns up to `max_items` entries, each with title, link, and a short summary.
    `url` must be a valid RSS/Atom feed URL (e.g. https://aws.amazon.com/about-aws/whats-new/recent/feed/).
    """
    feed = feedparser.parse(url)

    if feed.bozo and not feed.entries:
        # bozo=True means the feed had parse errors; entries=[] means nothing came back
        return f"Failed to parse feed at {url}: {feed.bozo_exception}"

    if not feed.entries:
        return f"No entries found in feed at {url}."

    lines = [f"Feed: {feed.feed.get('title', url)}", ""]
    for i, entry in enumerate(feed.entries[:max_items], 1):
        title   = entry.get("title", "(no title)")
        link    = entry.get("link", "")
        # Use the plain-text summary if available; strip HTML tags roughly
        summary = entry.get("summary", entry.get("description", ""))
        # Trim long summaries so the model gets the gist without token overload
        if len(summary) > 300:
            summary = summary[:297] + "..."

        lines.append(f"{i}. {title}")
        lines.append(f"   Link: {link}")
        if summary:
            lines.append(f"   {summary}")
        lines.append("")

    return "\n".join(lines)


agent = Agent(
    model=model,
    system_prompt=(
        "You are a news analyst assistant. When asked about a topic, use "
        "fetch_rss to pull the latest items from a relevant feed, then "
        "summarise the key themes and highlight the most interesting items."
    ),
    tools=[fetch_rss],
)


if __name__ == "__main__":
    print("=== AWS What's New ===")
    agent(
        "Fetch the AWS What's New feed at "
        "https://aws.amazon.com/about-aws/whats-new/recent/feed/ "
        "and summarise the 5 most recent announcements."
    )

    print("\n=== Hacker News Top Stories ===")
    agent(
        "Fetch the Hacker News top stories feed at "
        "https://news.ycombinator.com/rss "
        "and tell me what topics are trending today."
    )


# ── How to run ────────────────────────────────────────────────────────────
# No AWS credentials needed! feedparser makes direct HTTP calls.
# AWS credentials ARE needed for the Bedrock model call.
#
#     aws-vault exec strands-lab -- uv run 02-tools/02_builtin_data_rss/01_rss_feedparser.py
#
# To run WITHOUT any AWS credentials (just test the tool function itself):
#     uv run -c "import feedparser; from 02_builtin_data_rss.01_rss_feedparser import fetch_rss; print(fetch_rss('https://news.ycombinator.com/rss', 3))"
#
# Dependency: feedparser is a standard package
#     uv add feedparser
