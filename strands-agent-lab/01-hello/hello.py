# Phase 1 - Strands "hello world" on Amazon Nova (Bedrock)
# ---------------------------------------------------------
# Goal: the smallest possible agent that (1) talks to a model and
# (2) can call a tool you wrote. Everything else in this lab builds on this.

# `Agent` is the core runtime loop: it sends your prompt to the model, and if
# the model decides to call a tool, Strands runs the tool and feeds the result
# back to the model automatically. `tool` turns a plain function into something
# the model is allowed to call.
from strands import Agent, tool

# `BedrockModel` is the "model provider" - it tells the agent WHICH model to
# use and HOW to reach it (which AWS region, what temperature, etc).
from strands.models import BedrockModel


# The @tool decorator exposes this function to the model.
# IMPORTANT: the model reads the function name, the type hints, AND the
# docstring to decide when/how to call it. So the docstring is not just for
# humans here - it's part of the prompt. Write it clearly.
@tool
def letter_counter(word: str, letter: str) -> int:
    """Count how many times `letter` appears in `word`."""
    if len(letter) != 1:
        raise ValueError("letter must be a single character")
    return word.lower().count(letter.lower())


# Point the agent at Nova Lite in us-east-1.
# temperature=0.3 keeps answers fairly deterministic (lower = more predictable).
model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",
    region_name="us-east-1",
    temperature=0.3,
)

# Build the agent: give it the model + the list of tools it may use.
agent = Agent(model=model, tools=[letter_counter])


if __name__ == "__main__":
    # Calling the agent like a function runs one full turn:
    # prompt -> model -> (maybe tool call) -> model -> final answer.
    agent('How many times does the letter "r" appear in "strawberry"? Use the tool.')


# ── How to run ────────────────────────────────────────────────────────────
# From the strands-agent-lab/ folder (aws-vault injects your AWS creds):
#
#     aws-vault exec strands-lab -- uv run 01-hello/hello.py
#
# Expected: the model calls letter_counter and answers "3".
