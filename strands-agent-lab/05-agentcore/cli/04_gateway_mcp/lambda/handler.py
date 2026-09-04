# Lambda tool handler — exposed via AgentCore MCP Gateway
# --------------------------------------------------------
# This is a minimal Lambda function that acts as a tool target for the
# AgentCore MCP Gateway. The gateway routes MCP tool calls here based on
# the tool name configured in agentcore.json.
#
# The gateway wraps this in the MCP protocol — your Lambda just implements
# the business logic and returns a structured result. No MCP SDK needed here.

def lambda_handler(event, context):
    """Handle a tool invocation routed by the AgentCore MCP Gateway.

    The gateway passes the tool input as the event body. We implement
    a simple word-count tool as a demo.
    """
    # The gateway forwards the tool input parameters as the event.
    text = event.get("text", "")

    if not text:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Parameter 'text' is required."}]
        }

    word_count = len(text.split())
    char_count = len(text)

    return {
        "isError": False,
        "content": [
            {
                "type": "text",
                "text": (
                    f"Word count: {word_count}\n"
                    f"Character count: {char_count}\n"
                    f"Text: '{text[:100]}{'...' if len(text) > 100 else ''}'"
                )
            }
        ]
    }
