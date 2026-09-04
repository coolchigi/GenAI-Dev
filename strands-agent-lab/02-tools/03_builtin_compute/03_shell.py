# Built-in tool: shell — run shell commands
# ------------------------------------------
# `shell` lets the agent run arbitrary shell commands on the host machine.
# It uses a PTY (pseudo-terminal) so you see output in real time, just as
# you would in a terminal.
#
# Safety model:
#   - Non-trivial commands prompt for user confirmation before executing.
#   - The model must tell the user what it's about to run and why.
#   - BYPASS_TOOL_CONSENT=true skips confirmation (CI / deployed agents).
#   - STRANDS_NON_INTERACTIVE=true is an alias for the same bypass.
#
# Capabilities:
#   - Sequential commands  : list multiple commands and run them in order
#   - Parallel commands    : run independent commands concurrently
#   - Custom work_dir      : set the working directory per command
#   - Timeouts             : cap how long a command can run
#   - ignore_errors        : continue even if a command exits non-zero
#
# Security note: this gives the model the ability to run anything on your
# machine. Use it in trusted, local environments only. For production
# deployments, use sandboxed alternatives (agent_core_code_interpreter in
# 05-agentcore/cli/06_harness/).

from strands import Agent
from strands_tools import shell
from common import nova


agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a systems assistant. Use the shell tool to run commands "
        "when asked. Always explain what each command does before running it."
    ),
    tools=[shell],
)


if __name__ == "__main__":
    print("=== System info ===")
    agent("Run `uname -a` to show system information.")

    print("\n=== Directory listing ===")
    agent("Run `ls -la` in the current directory and summarise what you see.")

    print("\n=== Disk usage ===")
    agent("Show me how much disk space is available with `df -h`.")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required for the model.
#
# Interactive mode (default — prompts before each shell command):
#     aws-vault exec strands-lab -- uv run 02-tools/03_builtin_compute/03_shell.py
#
# Non-interactive mode (skip confirmation):
#     BYPASS_TOOL_CONSENT=true aws-vault exec strands-lab -- uv run 02-tools/03_builtin_compute/03_shell.py
#
# The commands above (uname, ls, df) are read-only and safe.
# Mutative commands (rm, mv, chmod, etc.) always prompt unless bypassed.
