# Built-in tool: python_repl — persistent Python REPL
# -----------------------------------------------------
# `python_repl` gives the agent access to a Python interpreter that persists
# state across calls within a single agent session. A variable defined in one
# tool call is still available in the next.
#
# This is more powerful than `calculator` (arbitrary Python, not just math) but
# less safe — it can do anything Python can. For most use cases, the built-in
# confirmation prompt (see below) is your guardrail.
#
# Key behaviours:
#   - State persists: `x = 10` in call 1, `print(x)` in call 2 — works.
#   - reset_state=True clears all variables between calls.
#   - Uses PTY for real-time output (you see print() as it runs).
#   - User confirmation prompt before each execution (interactive mode).
#     Set BYPASS_TOOL_CONSENT=true to skip (needed for CI / deployed agents).
#
# AWS credentials required for the model. No other setup.

from strands import Agent
from strands_tools import python_repl
from common import nova


agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a Python programming assistant. Use python_repl to run Python "
        "code when you need to compute results, process data, or demonstrate "
        "code behaviour. Always show the code before running it."
    ),
    tools=[python_repl],
)


if __name__ == "__main__":
    # The two turns below demonstrate persistent state.
    # Turn 1: define a list in the REPL.
    print("=== Turn 1: define a variable ===")
    agent("Using python_repl, create a list called `data` containing [3, 1, 4, 1, 5, 9, 2, 6].")

    # Turn 2: the same agent reuses the REPL state — `data` is still in scope.
    print("\n=== Turn 2: use the variable from Turn 1 ===")
    agent(
        "Now, still using python_repl, compute the mean and standard deviation "
        "of `data` using only the Python standard library (no numpy)."
    )

    # Turn 3: show that regular Python code works
    print("\n=== Turn 3: list comprehension ===")
    agent(
        "Using python_repl, create a list of the first 10 Fibonacci numbers "
        "and print them."
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required for the model.
#
# Interactive mode (default — prompts for confirmation before each code run):
#     aws-vault exec strands-lab -- uv run 02-tools/03_builtin_compute/02_python_repl.py
#
# Non-interactive mode (skip confirmation — use in CI or deployed agents):
#     BYPASS_TOOL_CONSENT=true aws-vault exec strands-lab -- uv run 02-tools/03_builtin_compute/02_python_repl.py
#
# Security note: python_repl executes arbitrary Python code. In production,
# prefer agent_core_code_interpreter (05-agentcore/cli/06_harness/) which
# runs code in an isolated sandbox. Use python_repl only in trusted,
# controlled environments.
