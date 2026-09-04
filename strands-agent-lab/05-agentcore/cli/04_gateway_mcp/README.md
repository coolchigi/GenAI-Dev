# 04 — MCP Gateway

An AgentCore Gateway sits between your agent and its tools. Instead of calling
a Lambda function or API directly, the agent calls the gateway over MCP
(Model Context Protocol). The gateway handles routing, authentication, and
access control — your agent code doesn't change when you add a new tool target.

---

## Architecture

```
Agent
  │  (MCP over HTTPS)
  ▼
AgentCore Gateway
  │  (routes by tool name)
  ├── Lambda target   → your_tool Lambda function
  ├── MCP server      → any MCP-compatible server
  └── OpenAPI target  → any REST API with an OpenAPI schema
```

---

## Gateway target types

| Type | Use case |
|---|---|
| `lambda` / `lambdaFunctionArn` | AWS Lambda function |
| `mcpServer` | Any MCP-compatible server (stdio, SSE, HTTP) |
| `openApiSchema` | REST API described by an OpenAPI 3.x spec |
| `smithyModel` | AWS Smithy service model |
| `apiGateway` | Amazon API Gateway endpoint |
| `connector` (web-search) | Built-in web search connector |
| `connector` (bedrock-knowledge-bases) | Built-in KB search connector |

---

## Note: agent_core_browser

`agent_core_browser` is an AgentCore-managed browser sandbox that can be wired
as a gateway target. Add it to the gateway's targets to give your agent a fully
managed, isolated browser without running Playwright locally:

```json
{
  "type": "connector",
  "connectorType": "browser"
}
```

This is the production alternative to `local_chromium_browser` shown in
`02-tools/07_builtin_browser_computer/01_browser_local.py`.

---

## Setup

### 1. Deploy the Lambda tool function

```bash
cd lambda/
# Package and deploy (adjust with your preferred method — SAM, CDK, or CLI):
zip function.zip handler.py
aws lambda create-function \
  --function-name strands-gateway-tool \
  --runtime python3.13 \
  --role arn:aws:iam::<ACCOUNT_ID>:role/lambda-basic-role \
  --handler handler.lambda_handler \
  --zip-file fileb://function.zip \
  --region us-east-1
```

Note the Lambda ARN — you'll need it in the next step.

### 2. Add the gateway and target

From `05-agentcore/cli/`:

```bash
agentcore add gateway --name toolGateway --protocol MCP
agentcore add gateway-target \
  --gateway toolGateway \
  --name wordCountTool \
  --type lambdaFunctionArn \
  --arn arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:strands-gateway-tool
```

### 3. Add the agent

```bash
agentcore add agent --name gatewayagent --framework strands --build CodeZip
```

Copy `app/gatewayagent/main.py` from this folder into `app/gatewayagent/`.

### 4. Deploy

```bash
agentcore deploy
agentcore status
```

### 5. Get the gateway endpoint

```bash
agentcore fetch access --gateway toolGateway
```

Copy the MCP endpoint URL and set it:

```bash
export GATEWAY_MCP_ENDPOINT=https://...agentcore.amazonaws.com/...
```

### 6. Invoke

```bash
agentcore invoke "Count the words in: 'The quick brown fox jumps over the lazy dog'"
```

---

## Local dev

Without the gateway deployed, you can test the agent against a local Lambda
stub. Adjust the `GATEWAY_MCP_ENDPOINT` to point at a local MCP server
(e.g. the filesystem MCP server from `02-tools/06_builtin_agents_orchestration/05_mcp_client.py`).

```bash
agentcore dev
agentcore invoke --dev "Count the words in this sentence"
```
