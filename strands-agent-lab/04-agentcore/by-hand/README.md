# By-hand AgentCore deploy (no CLI, no CDK)

The minimal path: package your wrapped agent as an ARM64 image, push to ECR,
create a runtime, invoke it. Every step here is something the `agentcore` CLI
does for you behind `deploy`.

## The pieces (and what the CLI hides)

| File | What it is | CLI equivalent |
|------|-----------|----------------|
| `agent.py` | The whole app — `/invocations` + `/ping` via `BedrockAgentCoreApp` | `app/.../main.py` + harness |
| `Dockerfile` | ARM64 container (required by AgentCore) | generated |
| `trust-policy.json` | lets `bedrock-agentcore` assume the role | auto-created role |
| `execution-policy.json` | role perms: invoke Bedrock, pull ECR, write logs | auto-created |
| `deploy_agent.py` | `create_agent_runtime` (control plane) | the CDK stack |
| `invoke_agent.py` | `invoke_agent_runtime` (data plane) | `agentcore invoke` |

## Requirements (the "you set it up yourself" part)

- **ARM64** image, port **8080**, `/invocations` POST + `/ping` GET
- Image lives in **ECR**
- An **execution IAM role** the runtime assumes

## Runbook

**0. Prereqs**
- Docker daemon running (buildx cross-builds ARM64 on an x86 Mac via QEMU)
- IAM permissions to create ECR repos, an IAM role, and AgentCore runtimes
  (the `strands-lab` user needs these added — same gate as the CLI path)

```bash
ACCOUNT=ACCOUNT_ID   # your account id
REGION=us-east-1
cd 04-agentcore/by-hand
```

**1. Test locally (no cloud) — already verified, see below**
```bash
aws-vault exec strands-lab -- python agent.py    # serves :8080
curl -s localhost:8080/ping
curl -s -X POST localhost:8080/invocations -H 'content-type: application/json' \
     -d '{"prompt":"How many words in \"a b c d\"? Use the tool."}'
```

**2. Build + push ARM64 image to ECR**
```bash
aws-vault exec strands-lab -- aws ecr create-repository --repository-name strands-byhand --region $REGION
aws-vault exec strands-lab -- bash -c "aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.$REGION.amazonaws.com"
docker buildx create --use    # once
aws-vault exec strands-lab -- docker buildx build --platform linux/arm64 \
  -t $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/strands-byhand:latest --push .
```

**3. Create the execution role**
```bash
aws-vault exec strands-lab -- aws iam create-role --role-name AgentRuntimeRole \
  --assume-role-policy-document file://trust-policy.json
aws-vault exec strands-lab -- aws iam put-role-policy --role-name AgentRuntimeRole \
  --policy-name agentcore-exec --policy-document file://execution-policy.json
```

**4. Create the runtime** (fill CONTAINER_URI + ROLE_ARN in `deploy_agent.py`)
```bash
aws-vault exec strands-lab -- uv run deploy_agent.py    # prints the runtime ARN
```

**5. Invoke** (paste the ARN into `invoke_agent.py`)
```bash
aws-vault exec strands-lab -- uv run invoke_agent.py
```

## Control plane vs data plane (worth remembering)

- `bedrock-agentcore-control` → **manage** runtimes (create/update/delete)
- `bedrock-agentcore` → **use** a runtime (invoke, stop session)

## Cost note

`lifecycleConfiguration` in `deploy_agent.py` caps idle + max session time so a
forgotten runtime can't rack up charges. Delete the runtime when done:
`control.delete_agent_runtime(agentRuntimeId=...)`.

## Status in this lab

Steps 2–5 need Docker running **and** the IAM permissions added to `strands-lab`
(the console step). Step 1 (local server) is verified working.
