# Built-in tool: journal — local markdown journal
# ------------------------------------------------
# `journal` is the simplest memory tool in strands-agents-tools: a plain
# markdown file stored locally, organised by date. No cloud, no database,
# no API keys — just files in a `journal/` folder inside your working directory.
#
# Actions:
#   write      — append a free-form entry to today's journal file
#   add_task   — append a task/to-do item with a checkbox
#   read       — read the journal for a specific date (default: today)
#   list       — list all journal dates that have entries
#
# When to use:
#   - Giving an agent a simple, persistent scratch pad
#   - Logging what the agent did during a session
#   - Lightweight to-do tracking
#   - Demos / local dev where you don't want cloud dependencies
#
# No API key, no AWS credentials needed for the journal itself.
# AWS credentials ARE required for the Bedrock model.

from strands import Agent
from strands_tools import journal
from common import nova


agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a personal assistant that keeps a journal. Use the journal tool "
        "to record notes, tasks, and summaries. When asked to remember something, "
        "write it to the journal. When asked what's on the agenda, read today's journal."
    ),
    tools=[journal],
)


if __name__ == "__main__":
    print("=== Write a journal entry ===")
    agent(
        "Write a journal entry noting that we explored Strands tools today and "
        "learned about the http_request, calculator, and journal tools."
    )

    print("\n=== Add some tasks ===")
    agent(
        "Add three tasks to today's journal: "
        "1) Try the web search tool, "
        "2) Set up a Bedrock Knowledge Base, "
        "3) Deploy an agent to AgentCore."
    )

    print("\n=== Read today's journal ===")
    agent("Read today's journal and tell me what's in it.")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required for the model. No other dependencies.
#
#     aws-vault exec strands-lab -- uv run 02-tools/05_builtin_memory/01_journal.py
#
# The journal files are written to: ./journal/YYYY-MM-DD.md
# relative to wherever you run the command from.
#
# To see the generated file:
#     cat journal/$(date +%Y-%m-%d).md
