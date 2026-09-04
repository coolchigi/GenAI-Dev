# Built-in tool: mcp_client — connect to an MCP server at runtime
# ----------------------------------------------------------------
# `mcp_client` connects to a Model Context Protocol (MCP) server and loads
# all of the server's tools into the agent dynamically. The agent can then
# call those tools as if they were regular Strands tools.
#
# Transport options:
#   stdio            — spawns a local process as the MCP server (simplest for local dev)
#   sse              — connects to a Server-Sent Events HTTP endpoint
#   streamable-http  — connects to a Streamable HTTP endpoint (AgentCore standard)
#
# Security note: this dynamically loads tools from an external server. Only
# connect to MCP servers you trust — a malicious server could expose harmful tools.
#
# This example uses STDIO transport to connect to the built-in `mcp` filesystem
# server, which is part of the official MCP reference servers. It exposes tools
# for reading, writing, and searching files.
#
# Prerequisites: Node.js 18+ (for npx to download the MCP server on first run)

from strands import Agent
from strands_tools import mcp_client
from common import nova


# Configure the MCP client to connect via stdio to the filesystem MCP server.
# npx will download @modelcontextprotocol/server-filesystem on first run.
# The last argument is the root directory the server is allowed to access.
mcp = mcp_client(
    transport="stdio",
    command="npx",
    args=[
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/tmp",          # allow the server to access /tmp only (safe for demo)
    ],
)

agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a file assistant. Use the MCP filesystem tools to read, list, "
        "and manage files in /tmp. Always explain what you are doing."
    ),
    tools=[mcp],
)


if __name__ == "__main__":
    print("=== List /tmp directory ===")
    agent("List the files in /tmp.")

    print("\n=== Write and read a file ===")
    agent(
        "Create a file called /tmp/strands_mcp_test.txt with the content: "
        "'Hello from Strands MCP client!'. Then read it back to confirm."
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required. Node.js 18+ required (for npx).
#
# Check Node.js:
#     node --version   # must be 18+
#
# Run:
#     aws-vault exec strands-lab -- uv run 02-tools/06_builtin_agents_orchestration/05_mcp_client.py
#
# On first run, npx downloads @modelcontextprotocol/server-filesystem (~2MB).
# Subsequent runs use the cached package.
#
# To connect to an HTTP MCP server instead (e.g. AgentCore gateway):
#   mcp = mcp_client(
#       transport="streamable-http",
#       url="https://your-agentcore-gateway-endpoint/mcp",
#   )
# See 05-agentcore/cli/04_gateway_mcp/ for the AgentCore gateway pattern.
