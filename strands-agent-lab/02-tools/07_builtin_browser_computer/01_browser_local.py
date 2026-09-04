# Built-in tool: local_chromium_browser — Playwright browser automation
# -----------------------------------------------------------------------
# `local_chromium_browser` gives the agent a full browser it can control
# programmatically. Built on Playwright, it supports navigation, clicking,
# typing, JavaScript evaluation, screenshots, tab management, and network
# interception.
#
# Available actions:
#   navigate        — go to a URL
#   get_text        — extract visible text from the current page
#   get_html        — get the raw HTML source
#   screenshot      — take a screenshot (returns base64 PNG)
#   click           — click an element by CSS selector or coordinates
#   type            — type text into a focused input
#   press_key       — press a keyboard shortcut
#   evaluate        — run JavaScript in the page context
#   new_tab         — open a new browser tab
#   switch_tab      — switch between tabs
#   back / forward  — browser history navigation
#   refresh         — reload the current page
#   get_cookies     — read cookies
#   network_intercept — intercept and inspect network requests
#
# Variants:
#   local_chromium_browser — runs Chromium locally (this file)
#   agent_core_browser     — AgentCore-managed browser sandbox (05-agentcore/)
#
# Prerequisite: `playwright install chromium` (see How to run).

from strands import Agent
from strands_tools.browser import local_chromium_browser
from common import nova

# Instantiate the browser tool. This creates a Playwright browser session.
browser = local_chromium_browser()

agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a web browsing assistant. Use the browser tool to navigate "
        "websites, extract information, and take screenshots. Always describe "
        "what you see on the page."
    ),
    tools=[browser],
)


if __name__ == "__main__":
    print("=== Navigate and extract text ===")
    agent(
        "Navigate to https://example.com and tell me what the page says. "
        "Then take a screenshot."
    )

    print("\n=== Extract the page title ===")
    agent(
        "Navigate to https://aws.amazon.com/bedrock/ and tell me the page title "
        "and the first paragraph of content you can see."
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required for the model.
# Playwright + Chromium required for the browser tool.
#
# One-time setup (install Playwright and Chromium):
#     uv add playwright
#     uv run playwright install chromium
#
# Run:
#     aws-vault exec strands-lab -- uv run 02-tools/07_builtin_browser_computer/01_browser_local.py
#
# Note: A Chromium window may open during execution depending on your system.
# For headless mode, set the PLAYWRIGHT_HEADLESS env var or configure it in
# the browser constructor. The browser session closes automatically when the
# script ends.
