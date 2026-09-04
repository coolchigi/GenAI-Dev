# Built-in tool: http_request
# ----------------------------
# `http_request` is a fully-featured HTTP client built into strands-agents-tools.
# It supports every HTTP method, authentication schemes, custom headers, cookies,
# retries, redirects, and even HTML-to-markdown conversion for web scraping.
#
# The model calls it like any tool — you just add it to the tools list.
# No API key required for basic GET/POST. Auth modes are configured via
# parameters the model passes when it calls the tool.
#
# Auth modes supported (comment reference — only unauthenticated runs here):
#   - none          : no auth (used below)
#   - bearer        : Authorization: Bearer <token>
#   - basic         : HTTP Basic (username + password)
#   - digest        : HTTP Digest auth
#   - jwt           : JWT in Authorization header
#   - aws_sigv4     : AWS Signature Version 4 (for AWS service APIs)
#   - api_key       : custom header name + key value
#
# IMPORTANT: Non-GET requests prompt for user confirmation by default.
# Set BYPASS_TOOL_CONSENT=true to skip the prompt in non-interactive environments.

from strands import Agent
from strands_tools import http_request   # built-in, no custom @tool needed
from common import nova


# Give the agent a system prompt that tells it when and how to use http_request.
# The model reads the tool's own docstring for parameter details — our prompt
# just sets the agent's behaviour around it.
agent = Agent(
    model=nova(0.0),   # temperature 0: we want deterministic, factual HTTP calls
    system_prompt=(
        "You are a helpful assistant that can make HTTP requests. "
        "When asked to fetch data from a URL, call http_request with the "
        "appropriate method, url, and headers. Always show the response body."
    ),
    tools=[http_request],
)


if __name__ == "__main__":
    print("=== Example 1: Simple GET ===")
    agent("Make a GET request to https://httpbin.org/get and show me the response.")

    print("\n=== Example 2: POST with JSON body ===")
    agent(
        'Make a POST request to https://httpbin.org/post with a JSON body: '
        '{"name": "strands", "version": "1.0"}. '
        "Use Content-Type: application/json header."
    )

    print("\n=== Example 3: Custom User-Agent header ===")
    agent(
        "Make a GET request to https://httpbin.org/headers and include a "
        "custom User-Agent header with value 'strands-agent-lab/1.0'."
    )


# ── How to run ────────────────────────────────────────────────────────────
# No API key needed. AWS credentials required for the Bedrock model.
#
#     aws-vault exec strands-lab -- uv run 02-tools/01_builtin_http_web/01_http_request.py
#
# To skip confirmation prompts on POST/PUT/DELETE:
#     BYPASS_TOOL_CONSENT=true aws-vault exec strands-lab -- uv run 02-tools/01_builtin_http_web/01_http_request.py
#
# Expected output: httpbin.org echoes back your request details as JSON.
# The agent will display the response body for each example.
