# 03 — Identity and Credential Providers

AgentCore Identity manages API keys and OAuth credentials on your behalf.
Instead of hardcoding secrets in agent code or `.env` files, you store them
in AgentCore as named credential resources. At runtime, AgentCore injects
them as environment variables — your agent code reads `os.getenv(...)` and
never sees the raw secret value in source control.

---

## Credential types

| Type | Use case | How it's injected |
|---|---|---|
| `API_KEY` | Third-party API keys (Tavily, Slack, etc.) | `CREDENTIAL_<NAME>` env var |
| `OAUTH2_CLIENT_CREDENTIALS` | OAuth 2.0 client credentials flow | `CREDENTIAL_<NAME>_TOKEN` env var (auto-refreshed) |
| `OAUTH2_AUTHORIZATION_CODE` | OAuth 2.0 user-consent flow | `CREDENTIAL_<NAME>_TOKEN` env var |

The agent code is identical regardless of credential type — it just reads the
env var. AgentCore handles storage, encryption, rotation (OAuth), and injection.

---

## How this differs from `by-hand/`

The `05-agentcore/by-hand/` folder shows the underlying IAM trust and execution
policies that grant the runtime access to AWS services. AgentCore Identity extends
that pattern to third-party credentials: instead of hardcoding a key in an env
file, the runtime fetches it from a secure store and injects it.

---

## Setup

### 1. Add a credential resource

From `05-agentcore/cli/`:

```bash
agentcore add credential --name tavilyKey --type API_KEY
```

When prompted, enter your Tavily API key (or any API key for the demo).
This stores the key encrypted in AgentCore and appends to `agentcore.json`:

```json
{
  "name": "tavilyKey",
  "credentialType": "API_KEY"
}
```

Store the actual key value in `agentcore/.env.local` for local dev:

```
CREDENTIAL_TAVILYKEY=tvly-...
```

### 2. Add the agent

```bash
agentcore add agent --name identityagent --framework strands --build CodeZip
```

Copy `app/identityagent/main.py` from this folder into `app/identityagent/`.

### 3. Deploy

```bash
agentcore deploy
agentcore status
```

### 4. Invoke

```bash
# The agent will call an authenticated endpoint using the injected credential.
agentcore invoke "Search the web for: latest Amazon Bedrock announcements"
```

---

## What the agent does

The identity agent reads `CREDENTIAL_TAVILYKEY` from the environment (injected
by AgentCore) and uses it to call the Tavily search API via `http_request`.
The API key is never in source code, never in git, and never visible in logs
(AgentCore redacts it from any output it controls).

---

## Local dev

```bash
# Set local credentials in agentcore/.env.local:
echo "CREDENTIAL_TAVILYKEY=tvly-..." >> agentcore/.env.local

agentcore dev
agentcore invoke --dev "Search for: Strands agent framework"
```

The `LOCAL_DEV=1` env var (set automatically by `agentcore dev`) tells the agent
to read from `.env.local` rather than the AgentCore Identity service.
