# 07 — Policy and Guardrails

AgentCore Policy gives you two layers of control over what your agent can do
and what content it can produce:

| Layer | Mechanism | What it controls |
|---|---|---|
| **Guardrails** | Bedrock content filters | What the model says (output) |
| **Cedar policies** | Attribute-based access control | Which gateway tools the agent can call |

Both can operate in `ACTIVE` mode (block) or `PASSIVE` mode (log only).
Use `PASSIVE` first to understand your traffic before enabling blocking.

---

## Enforcement modes

| Mode | Effect |
|---|---|
| `ACTIVE` | The policy engine blocks the request and returns an error |
| `PASSIVE` | The request proceeds; the policy engine logs the violation |

`PASSIVE` is your shadow-testing mode: deploy a policy, watch what it would
have blocked, tune it, then switch to `ACTIVE`.

---

## Setup

### 1. Add a policy engine

From `05-agentcore/cli/`:

```bash
agentcore add policy-engine --name mainPolicyEngine
```

Edit the entry in `agentcore.json` to set the enforcement mode:

```json
{
  "name": "mainPolicyEngine",
  "enforcementMode": "PASSIVE"
}
```

### 2. Add a content filter policy (guardrails)

```bash
agentcore add policy \
  --name contentFilter \
  --policy-engine mainPolicyEngine \
  --type guardrail
```

Edit the policy in `agentcore.json` to configure which content categories to filter:

```json
{
  "name": "contentFilter",
  "policyEngineName": "mainPolicyEngine",
  "type": "GUARDRAIL",
  "guardrailConfig": {
    "contentFilters": [
      {"type": "VIOLENCE",   "inputStrength": "HIGH",   "outputStrength": "HIGH"},
      {"type": "HATE",       "inputStrength": "HIGH",   "outputStrength": "HIGH"},
      {"type": "SEXUAL",     "inputStrength": "MEDIUM", "outputStrength": "HIGH"},
      {"type": "MISCONDUCT", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"}
    ],
    "promptAttack": true,
    "sensitiveInfoFilters": ["EMAIL", "PHONE", "CREDIT_DEBIT_CARD_NUMBER"]
  }
}
```

### 3. Add a Cedar tool-access policy

```bash
agentcore add policy \
  --name toolAccessPolicy \
  --policy-engine mainPolicyEngine \
  --type cedar
```

Copy `policies/allow_safe_tools.cedar` into the policy. This Cedar policy
allows only the `wordCountTool` gateway tool and blocks everything else:

```cedar
permit (
  principal,
  action == AgentCore::Action::"invoke",
  resource == AgentCore::GatewayTool::"wordCountTool"
);
```

### 4. Bind the policy engine to the gateway agent

Add `policyEngineName` to `gatewayagent` in `agentcore.json`:

```json
{
  "name": "gatewayagent",
  ...
  "policyEngineName": "mainPolicyEngine"
}
```

### 5. Deploy

```bash
agentcore deploy
agentcore status
```

### 6. Test

```bash
# Should succeed (wordCountTool is allowed):
agentcore invoke "Count the words in: hello world"

# Should be logged (PASSIVE) or blocked (ACTIVE) — not an allowed tool:
agentcore invoke "List all files in the filesystem"

# Switch to ACTIVE mode and retry:
# Edit agentcore.json: "enforcementMode": "ACTIVE"
# agentcore deploy
# The second invoke above should now return a policy violation error.
```

---

## Prompt attack protection

Setting `"promptAttack": true` in the guardrail config activates Bedrock's
built-in prompt injection detection. Attempts to override the system prompt
or jailbreak the agent are caught at the guardrail layer before they reach
the model.

---

## Sensitive information filtering

The `sensitiveInfoFilters` list masks PII in both directions:
- **Input**: strips detected PII from the user's prompt before the model sees it
- **Output**: masks PII in the model's response before it reaches the caller

Useful for compliance with GDPR, HIPAA, and PCI-DSS.
