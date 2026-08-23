# By-hand AgentCore Runtime agent - the whole app, ~30 lines.
# --------------------------------------------------------------
# AgentCore Runtime's contract is just an HTTP server with two endpoints:
#   POST /invocations  -> run the agent
#   GET  /ping         -> health check
# BedrockAgentCoreApp gives you both for free, so this IS the plumbing the CLI
# scaffold hides. Same file runs locally on :8080 and inside the deployed
# container.

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


@tool
def word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())


agent = Agent(model=model, tools=[word_count])


@app.entrypoint
def invoke(payload):
    """POST /invocations body arrives here as a dict; return a dict."""
    result = agent(payload.get("prompt", "Hello"))
    return {"result": result.message}


if __name__ == "__main__":
    app.run()  # serves /invocations + /ping on 0.0.0.0:8080
