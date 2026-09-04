# Deprecated Tools Reference

Seven tools in `strands-agents-tools` v0.8.6 are deprecated and will **raise an error
in v0.9.0**. If you find an old example using one of these, here is what to do instead.

---

## `rss`

**What it did:** Persistent RSS feed manager — subscribe/unsubscribe, fetch, search, and
categorise entries. Stored subscription state as JSON in a temp directory.

**Why deprecated:** Tight coupling to a specific storage format and no clear migration path
as the library evolves. The underlying `feedparser` library does the same job without the
abstraction overhead.

**Replacement — use `feedparser` directly:**

```python
import feedparser
from strands import tool

@tool
def fetch_rss(url: str, max_items: int = 10) -> str:
    """Fetch the latest entries from an RSS feed at `url`."""
    feed = feedparser.parse(url)
    lines = [f"Feed: {feed.feed.get('title', url)}", ""]
    for entry in feed.entries[:max_items]:
        lines.append(f"- {entry.get('title', '')} — {entry.get('link', '')}")
    return "\n".join(lines)
```

Full working example: `02-tools/02_builtin_data_rss/01_rss_feedparser.py`

---

## `batch`

**What it did:** Invoked multiple tools sequentially from a single request — a way to
"batch up" tool calls before the SDK supported concurrent execution natively.

**Why deprecated:** The Strands SDK now runs multiple tool calls concurrently by default
via `ConcurrentToolExecutor`. The `batch` tool is redundant.

**Replacement — nothing to do:**

The SDK handles concurrent tool calls automatically. If the model wants to call multiple
tools in one turn, it issues multiple `toolUse` blocks and Strands executes them in parallel.
No code change required on your part.

---

## `think`

**What it did:** Ran "recursive analytical thinking cycles" by spawning a sub-agent to
reason step by step before answering. Used to simulate extended thinking.

**Why deprecated:** Modern foundation models (Claude 3.5+, Nova Pro) support native
**extended thinking** (chain-of-thought reasoning) via the model provider's `reasoning`
configuration. This is more integrated, cheaper, and produces better results.

**Replacement — enable native reasoning on the model:**

```python
from strands.models import BedrockModel

# Enable extended thinking on Claude 3.7 Sonnet
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    additional_request_fields={
        "thinking": {"type": "enabled", "budget_tokens": 5000}
    },
)
```

For Nova Pro (Amazon's reasoning model):

```python
model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",
    additional_request_fields={
        "inferenceConfig": {"reasoningConfig": {"type": "ENABLED"}}
    },
)
```

---

## `current_time`

**What it did:** Returned the current time in a specified timezone as an ISO 8601 string.
The model called this tool whenever it needed the current date/time.

**Why deprecated:** Injecting context via a tool call adds an unnecessary model round-trip.
The `ContextInjector` plugin injects time (and other ambient context) into the system
prompt automatically, with no tool call needed.

**Replacement — use `ContextInjector`:**

```python
from strands import Agent
from strands.experimental.hooks import ContextInjector
from datetime import datetime, timezone

injector = ContextInjector(
    context_fn=lambda: f"Current UTC time: {datetime.now(timezone.utc).isoformat()}"
)

agent = Agent(model=model, hooks=[injector])
# The agent now always knows the current time without a tool call.
```

Or simply inject time into the system prompt directly:

```python
from datetime import datetime, timezone
system_prompt = f"Today is {datetime.now(timezone.utc).strftime('%Y-%m-%d')} UTC."
agent = Agent(model=model, system_prompt=system_prompt)
```

---

## `sleep`

**What it did:** Paused agent execution for N seconds. Used in polling loops or to add
delays between actions.

**Why deprecated:** Sleeping in a tool call ties up the Strands event loop. The SDK now
provides a vended sleep that is event-loop aware.

**Replacement — use the vended `sleep` tool:**

```python
from strands.vended_tools import sleep
agent = Agent(model=model, tools=[sleep])
```

Or pause in your own code: `await asyncio.sleep(n)` / `time.sleep(n)` outside the agent.

---

## `cron`

**What it did:** Managed the host machine's crontab — listed, added, and removed cron
jobs to schedule recurring tasks.

**Why deprecated:** Modifying the host crontab is fragile and non-portable. For scheduled
agent runs, a managed scheduler is the right tool.

**Replacement — use Amazon EventBridge Scheduler:**

```bash
# Create a recurring schedule that invokes your AgentCore runtime every hour
aws scheduler create-schedule \
  --name "my-agent-hourly" \
  --schedule-expression "rate(1 hour)" \
  --target '{"Arn": "<your-lambda-or-agentcore-arn>", "RoleArn": "<role-arn>"}' \
  --flexible-time-window '{"Mode": "OFF"}'
```

Or use the `shell` tool to run a one-off command instead of adding a cron job.

---

## `diagram`

**What it did:** Generated cloud architecture, network topology, sequence, and flowchart
diagrams using Graphviz, Matplotlib, NetworkX, and the `diagrams` Python package.

**Why deprecated:** The abstraction layer added complexity without benefit. Generating
diagram code directly and running it is simpler and more flexible.

**Replacement — generate and run diagram code directly:**

```python
from strands import tool
from strands_tools import python_repl  # or shell

# Let the model generate the diagram code and run it via python_repl or shell.
# Example: Mermaid diagram (renders in GitHub, Notion, many tools)

@tool
def render_mermaid(diagram_code: str, output_file: str = "/tmp/diagram.md") -> str:
    """Save a Mermaid diagram definition to a file.

    `diagram_code` is valid Mermaid syntax (flowchart, sequence, etc.).
    Paste the content into https://mermaid.live to render it.
    """
    with open(output_file, "w") as f:
        f.write(f"```mermaid\n{diagram_code}\n```")
    return f"Diagram saved to {output_file}. Open https://mermaid.live to render."
```

Or use the `diagrams` library directly in a `python_repl` tool call.

---

## Quick reference

| Tool | Deprecated | Replacement |
|---|---|---|
| `rss` | v0.8.6 | `feedparser` directly — see `02_builtin_data_rss/01_rss_feedparser.py` |
| `batch` | v0.8.6 | Built-in `ConcurrentToolExecutor` (automatic, no code change) |
| `think` | v0.8.6 | Native model reasoning (`thinking` / `reasoningConfig` in model config) |
| `current_time` | v0.8.6 | `ContextInjector` plugin or inject time into system prompt |
| `sleep` | v0.8.6 | `from strands.vended_tools import sleep` |
| `cron` | v0.8.6 | Amazon EventBridge Scheduler |
| `diagram` | v0.8.6 | Generate diagram code via `python_repl` or `render_mermaid` custom tool |
| `agent_graph` | v0.8.6 | `strands.multiagent.Swarm` or `strands.multiagent.GraphBuilder` |
