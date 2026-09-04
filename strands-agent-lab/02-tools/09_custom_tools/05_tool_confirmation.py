# Custom tools: user confirmation before destructive actions
# -----------------------------------------------------------
# Some tools should ask the user for confirmation before doing something
# irreversible: deleting a file, sending an email, making a purchase.
#
# The built-in Strands tools (shell, file_write, use_aws mutative ops, etc.)
# do this automatically via the BYPASS_TOOL_CONSENT mechanism. Here we show
# how to implement the SAME pattern in your own custom tools.
#
# Two approaches shown:
#
# Approach A — Console confirmation (interactive terminals)
#   Ask the user via input() before running the destructive action.
#   Set BYPASS_TOOL_CONSENT=true to skip (for CI/deployed agents).
#
# Approach B — Dry-run mode
#   The tool accepts a dry_run parameter. When True, it describes what it
#   WOULD do without actually doing it. The model can first call with
#   dry_run=True, present the plan to the user, then call with dry_run=False.
#   This is the safer pattern for agentic pipelines.

import os
from pathlib import Path
from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")

# Read BYPASS_TOOL_CONSENT once at module level — same as the built-in tools.
BYPASS_CONSENT = os.environ.get("BYPASS_TOOL_CONSENT", "").lower() == "true"


# ── Approach A: console confirmation ─────────────────────────────────────
@tool
def delete_file(path: str) -> str:
    """Delete a file at the given path. DESTRUCTIVE — asks for confirmation first.

    Use this when the user explicitly asks to delete a file.
    `path` is the absolute or relative file path to delete.
    The action will ask for confirmation unless BYPASS_TOOL_CONSENT=true.
    """
    target = Path(path)
    if not target.exists():
        return f"File not found: {path}"

    if not BYPASS_CONSENT:
        # Present the action clearly before asking — same pattern as built-ins.
        print(f"\n⚠️  About to DELETE: {target.resolve()}")
        answer = input("Confirm? [y/N]: ").strip().lower()
        if answer != "y":
            return f"Deletion of '{path}' cancelled by user."

    target.unlink()
    return f"Deleted: {path}"


# ── Approach B: dry-run parameter ────────────────────────────────────────
@tool
def send_notification(
    recipient: str,
    subject: str,
    body: str,
    dry_run: bool = True,
) -> str:
    """Send an email notification to a recipient.

    IMPORTANT: By default this runs in dry_run=True mode and only describes
    what would be sent without actually sending anything. Set dry_run=False
    to send for real.

    Use the dry-run first: describe the notification to the user and ask them
    to confirm. Then call again with dry_run=False to send.

    `recipient` — email address of the recipient
    `subject`   — email subject line
    `body`      — plain-text body of the email
    `dry_run`   — if True (default), preview only; if False, send for real
    """
    preview = (
        f"To:      {recipient}\n"
        f"Subject: {subject}\n"
        f"Body:    {body[:200]}{'...' if len(body) > 200 else ''}"
    )

    if dry_run:
        return f"[DRY RUN — not sent]\n{preview}"

    # In a real implementation, call your email API here (SES, SendGrid, etc.)
    # For this demo, we just print to simulate.
    print(f"[SENDING EMAIL]\n{preview}")
    return f"Notification sent to {recipient}."


agent = Agent(
    model=model,
    system_prompt=(
        "You are a cautious assistant. Before taking any destructive action, "
        "describe what you're about to do and ask for confirmation. For the "
        "send_notification tool, always do a dry_run first, present the preview "
        "to the user, and only send for real when explicitly confirmed."
    ),
    tools=[delete_file, send_notification],
)


if __name__ == "__main__":
    # Create a test file to delete.
    test_file = Path("/tmp/strands_delete_test.txt")
    test_file.write_text("This file is safe to delete — it was created by the lab.")

    print("=== Approach A: console confirmation ===")
    agent(f"Please delete the file at {test_file}.")

    print("\n=== Approach B: dry-run pattern ===")
    agent(
        "Send a notification to alice@example.com with subject 'Lab complete' "
        "and body 'All Strands tools have been explored successfully!'"
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required.
#
# Interactive (default — prompts for confirmation on delete):
#     aws-vault exec strands-lab -- uv run 02-tools/09_custom_tools/05_tool_confirmation.py
#
# Non-interactive (skip confirmation — use in CI):
#     BYPASS_TOOL_CONSENT=true aws-vault exec strands-lab -- uv run 02-tools/09_custom_tools/05_tool_confirmation.py
