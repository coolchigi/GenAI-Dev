# Custom tools: dynamic tool loading at runtime
# -----------------------------------------------
# `load_tool` from strands-agents-tools loads a Python file at runtime and
# registers the @tool-decorated functions it finds. The agent can then call
# those tools as if they were built-in.
#
# This is the PLUGIN PATTERN: tools are separate files that can be added,
# removed, or updated without changing the agent code. Useful for:
#   - Agent frameworks where users contribute their own tools
#   - Large tool libraries loaded on-demand (not all in memory at startup)
#   - Testing new tools without restarting the agent
#   - Tenant-specific tools in multi-tenant systems
#
# The load_tool tool works as a meta-tool: the MODEL tells the agent to load
# a tool file, and from that point it can call the newly loaded tools.

import textwrap
from pathlib import Path
from strands import Agent
from strands_tools import load_tool
from strands.models import BedrockModel

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")

# Write a "plugin" tool file to /tmp that we'll load at runtime.
# In a real system this would be a file from a tools library or a user upload.
PLUGIN_FILE = Path("/tmp/strands_plugin_tools.py")
PLUGIN_FILE.write_text(textwrap.dedent("""\
    # This file is a Strands tool plugin — loaded dynamically at runtime.
    from strands import tool

    @tool
    def word_frequency(text: str, top_n: int = 5) -> str:
        \"\"\"Count word frequencies in a block of text and return the top N most common words.

        Use this to analyse text for the most frequently occurring words.
        `text` is any string of text to analyse.
        `top_n` is how many top words to return (default: 5).
        \"\"\"
        from collections import Counter
        import re
        words = re.findall(r\"\\b[a-z]+\\b\", text.lower())
        most_common = Counter(words).most_common(top_n)
        lines = [f\"{rank}. '{word}': {count} times\"
                 for rank, (word, count) in enumerate(most_common, 1)]
        return \"Top words:\\n\" + \"\\n\".join(lines)

    @tool
    def reverse_words(sentence: str) -> str:
        \"\"\"Reverse the order of words in a sentence.

        Use this when the user wants to flip the word order of a sentence.
        `sentence` is the input string.
        \"\"\"
        return \" \".join(sentence.split()[::-1])
"""))

print(f"Plugin file written to: {PLUGIN_FILE}")


agent = Agent(
    model=model,
    system_prompt=(
        "You are a text analysis assistant. You can load new tool plugins at "
        "runtime using load_tool, then use those tools immediately after loading."
    ),
    # The agent starts with only load_tool. It has no text tools yet.
    tools=[load_tool],
)


if __name__ == "__main__":
    print("=== Load the plugin file at runtime ===")
    # The model calls load_tool to register the plugin, then immediately uses it.
    agent(
        f"Load the tool file at {PLUGIN_FILE}. "
        "Then use word_frequency to analyse this text: "
        "'The quick brown fox jumps over the lazy dog. The dog did not move. "
        "The fox was very quick and very clever.' "
        "Show me the top 5 most frequent words."
    )

    print("\n=== Use the second tool from the same plugin ===")
    agent("Reverse the words in: 'Agents are the future of software'.")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required.
#
#     aws-vault exec strands-lab -- uv run 02-tools/09_custom_tools/06_dynamic_tool_loading.py
#
# The plugin file at /tmp/strands_plugin_tools.py is created automatically
# when the script runs. No extra setup needed.
#
# In a real system, the plugin files would come from:
#   - A user-provided directory (load each .py file on demand)
#   - A remote tools registry (download + load)
#   - A CI/CD pipeline that drops tool files into a known location
