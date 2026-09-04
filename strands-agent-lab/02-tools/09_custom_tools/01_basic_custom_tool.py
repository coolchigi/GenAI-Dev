# Custom tools: anatomy of @tool — from zero to typed parameters
# ---------------------------------------------------------------
# The @tool decorator is the ONLY thing Strands needs to turn a plain Python
# function into something a model can call. But the way you write the function
# determines how well the model uses it.
#
# Three things the model reads to understand a tool:
#   1. Function name   — must be descriptive (this IS the tool name)
#   2. Type hints      — define the parameter schema the model must follow
#   3. Docstring       — the model's ENTIRE description of what this tool does
#                        and how to call it. Write it as if explaining to a
#                        smart junior dev who has never seen your code.
#
# This file shows three tools of escalating complexity:
#   - Zero parameters (a tool that just returns something)
#   - Typed parameters (the normal case)
#   - Optional parameters with defaults (for flexible tools)

from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


# ── Tool 1: Zero parameters ──────────────────────────────────────────────
# Simplest possible tool. The model calls it with no arguments.
# Use case: "get the current state of something" — no input needed.
@tool
def get_lab_info() -> str:
    """Return information about this Strands Agent Lab setup.

    Returns the lab name, the model being used, and the AWS region.
    Call this when the user asks about the lab configuration or setup.
    """
    return (
        "Lab: Strands Agent Lab\n"
        "Model: Amazon Nova Lite (amazon.nova-lite-v1:0)\n"
        "Region: us-east-1\n"
        "SDK: strands-agents"
    )


# ── Tool 2: Typed parameters ─────────────────────────────────────────────
# The normal case. Type hints become the JSON schema the model must fill.
# str, int, float, bool are directly supported. Use | None for optionals.
@tool
def celsius_to_fahrenheit(celsius: float) -> str:
    """Convert a temperature from Celsius to Fahrenheit.

    Use this whenever the user provides a temperature in Celsius and wants
    to know the equivalent in Fahrenheit.

    `celsius` is the temperature value in degrees Celsius (e.g. 100.0 for
    boiling water, 0.0 for freezing, -40.0 for the crossover point).

    Returns a formatted string with both values.
    """
    fahrenheit = (celsius * 9 / 5) + 32
    return f"{celsius}°C = {fahrenheit}°F"


# ── Tool 3: Optional parameters with defaults ────────────────────────────
# Use Python default values for optional parameters. The model can omit
# them and the function will use the default.
@tool
def generate_slug(text: str, separator: str = "-", max_length: int = 60) -> str:
    """Convert a title or phrase into a URL-safe slug.

    Use this when the user needs a URL slug from a title or label.

    `text`       — the input string to slugify (e.g. "Hello World!")
    `separator`  — character to use between words (default: "-")
    `max_length` — truncate the slug to this many characters (default: 60)

    Returns the slugified string in lowercase.
    """
    import re
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)   # remove non-alphanumeric
    slug = re.sub(r"\s+", separator, slug.strip())
    return slug[:max_length]


agent = Agent(
    model=model,
    tools=[get_lab_info, celsius_to_fahrenheit, generate_slug],
)


if __name__ == "__main__":
    print("=== Zero-param tool ===")
    agent("What is this lab using?")

    print("\n=== Typed-param tool ===")
    agent("What is 37 degrees Celsius in Fahrenheit? That's normal body temperature.")

    print("\n=== Optional params tool ===")
    agent("Create a URL slug for 'The Complete Guide to Amazon Bedrock AgentCore 2026'.")

    # Force the model to use non-default params:
    agent(
        "Create a URL slug for 'AWS re:Invent 2026 Keynote' "
        "using underscores as the separator."
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required for the model.
#
#     aws-vault exec strands-lab -- uv run 02-tools/09_custom_tools/01_basic_custom_tool.py
