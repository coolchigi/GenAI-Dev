# Built-in tool: calculator — SymPy-powered math
# ------------------------------------------------
# The `calculator` tool uses SymPy under the hood, giving the model access to
# exact symbolic mathematics — not just floating-point arithmetic.
#
# What it can do:
#   - Basic arithmetic (including exact fractions, no float rounding)
#   - Algebra: solve equations, simplify expressions, expand/factor
#   - Calculus: differentiate, integrate, compute limits, Taylor series
#   - Trigonometry (exact values, e.g. sin(π/6) = 1/2)
#   - Complex numbers
#   - Matrix operations
#   - Statistics: mean, variance, standard deviation
#
# Security: The calculator uses an AST allowlist so only math operations are
# permitted — it cannot execute arbitrary Python code.
#
# No API key needed. AWS credentials required for the model.

from strands import Agent
from strands_tools import calculator
from common import nova


agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a precise math assistant. Always use the calculator tool "
        "to compute numerical results — never compute in your head. "
        "Show the expression you are computing and the result."
    ),
    tools=[calculator],
)


if __name__ == "__main__":
    print("=== Basic arithmetic ===")
    agent("What is 2 ** 32?")

    print("\n=== Algebra: solve an equation ===")
    agent("Solve the equation x**2 - 5*x + 6 = 0 for x.")

    print("\n=== Calculus: differentiation ===")
    agent("What is the derivative of x**3 + 2*x**2 - 5*x + 7 with respect to x?")

    print("\n=== Calculus: integration ===")
    agent("Compute the definite integral of x**2 from 0 to 3.")

    print("\n=== Trigonometry ===")
    agent("What is the exact value of sin(pi/6) + cos(pi/3)?")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required for the model. No other setup.
#
#     aws-vault exec strands-lab -- uv run 02-tools/03_builtin_compute/01_calculator.py
#
# The calculator tool is purely local — no cloud calls, no API keys.
# Dependency: SymPy (installed automatically with strands-agents-tools)
