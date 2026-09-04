# Built-in tool: slack — full Slack integration
# -----------------------------------------------
# The `slack` tool connects to Slack via Socket Mode (WebSocket, no public
# endpoint needed) and exposes all Slack API methods to the agent.
# The convenience `slack_send_message` function is also available for simple
# message sending without needing to know the full Slack API.
#
# Actions available to the model (examples):
#   chat_postMessage    — send a message to a channel
#   chat_update         — edit a message
#   conversations_list  — list channels
#   users_list          — list workspace members
#   reactions_add       — add an emoji reaction
#   files_upload        — upload a file
#   ... and the full Slack Web API surface
#
# Prerequisites:
#   1. Create a Slack app at https://api.slack.com/apps
#   2. Add these OAuth scopes (Bot Token Scopes):
#      chat:write, channels:read, users:read, reactions:write
#   3. Enable Socket Mode (under "Socket Mode" in your app settings)
#   4. Generate an App-Level Token with connections:write scope
#   5. Install the app to your workspace

import os
from strands import Agent
from strands_tools import slack
from common import nova

# Both tokens are required.
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")

if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
    raise EnvironmentError(
        "Slack tokens not set. Export both before running:\n"
        "    export SLACK_BOT_TOKEN=xoxb-...\n"
        "    export SLACK_APP_TOKEN=xapp-..."
    )

# The CHANNEL to post to — replace with a channel your bot has been invited to.
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#general")

agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a Slack assistant. Use the slack tool to interact with Slack. "
        "When asked to send messages, use chat_postMessage with the channel "
        f"'{SLACK_CHANNEL}' unless told otherwise."
    ),
    tools=[slack],
)


if __name__ == "__main__":
    print("=== Send a message ===")
    agent(
        f"Send a message to {SLACK_CHANNEL} saying: "
        "'Hello from Strands Agent Lab! 🤖 This message was sent by an AI agent.'"
    )

    print("\n=== List channels ===")
    agent("List the first 5 channels in this Slack workspace.")


# ── How to run ────────────────────────────────────────────────────────────
# Setup (one-time, ~10 minutes):
#
# 1. Go to https://api.slack.com/apps → Create New App → From scratch
# 2. App Name: "Strands Lab Bot", Workspace: your workspace
# 3. OAuth & Permissions → Bot Token Scopes: add chat:write, channels:read
# 4. Install App → Install to Workspace → copy the Bot User OAuth Token (xoxb-...)
# 5. Socket Mode → Enable Socket Mode
# 6. Basic Information → App-Level Tokens → Generate Token (connections:write)
#    → copy the App-Level Token (xapp-...)
# 7. Invite the bot to your channel: /invite @strands-lab-bot
#
# Export tokens and run:
#     export SLACK_BOT_TOKEN=xoxb-...
#     export SLACK_APP_TOKEN=xapp-...
#     export SLACK_CHANNEL=#general    # or any channel the bot is in
#
#     aws-vault exec strands-lab -- uv run 02-tools/08_builtin_comms_media/01_slack.py
