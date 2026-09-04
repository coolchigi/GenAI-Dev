# 00 — AgentCore CLI Setup

This section walks through everything you need before running any of the numbered
agent folders in `05-agentcore/cli/`. The existing `01_runtime_hello/` (helloagent)
was scaffolded with the AgentCore CLI and is already deployed. This doc explains
what was done and what you need to do to run the rest.

---

## Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Node.js | 20 or later | `node --version` |
| AgentCore CLI | latest | `agentcore --version` |
| Python | 3.10 or later | `python --version` |
| uv | any | `uv --version` |
| Docker | any | `docker --version` (Container build agents only) |
| AWS credentials | — | `aws sts get-caller-identity` |

### Install the AgentCore CLI

```bash
npm install -g @aws/agentcore-cli
agentcore update   # ensure you have the latest version
```

### Verify

```bash
agentcore --version
agentcore --help
```

---

## IAM permissions

The `strands-lab` IAM user needs additional permissions beyond the Bedrock model
invocation rights used in `01-hello/` and `02-tools/`.

Add the following to the user's IAM policy (or a separate managed policy):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AgentCoreControlPlane",
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:*",
        "bedrock-agentcore-control:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECRForContainerBuilds",
      "Effect": "Allow",
      "Action": [
        "ecr:CreateRepository",
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CodeBuildForContainerBuilds",
      "Effect": "Allow",
      "Action": [
        "codebuild:CreateProject",
        "codebuild:StartBuild",
        "codebuild:BatchGetBuilds"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudFormationForCDK",
      "Effect": "Allow",
      "Action": [
        "cloudformation:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMForExecutionRoles",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:PutRolePolicy",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "iam:GetRole",
        "iam:DeleteRole",
        "iam:DetachRolePolicy",
        "iam:DeleteRolePolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

See `05-agentcore/by-hand/execution-policy.json` and `trust-policy.json` for
what AgentCore creates on your behalf when you use the CLI.

---

## `aws-targets.json` — set your account and region

Open `05-agentcore/cli/agentcore/aws-targets.json` and confirm your account ID
and region are correct:

```json
[
  {
    "accountId": "337305803512",
    "region": "us-east-1"
  }
]
```

Replace `337305803512` with your actual AWS account ID if different.

---

## Validate the configuration

From inside any agent folder (e.g. `05-agentcore/cli/`):

```bash
agentcore validate
```

This checks `agentcore.json` against the schema and reports any issues before
you attempt a deploy.

---

## Project structure recap

```
05-agentcore/cli/
├── 00_setup.md                   ← you are here
├── agentcore/
│   ├── agentcore.json            ← declarative config (all resources)
│   ├── aws-targets.json          ← account + region
│   ├── .env.local                ← secrets (gitignored)
│   └── cdk/                      ← CDK infrastructure (generated)
├── app/
│   ├── helloagent/               ← 01_runtime_hello — existing agent
│   ├── memoryagent/              ← 02_memory
│   ├── identityagent/            ← 03_identity_credentials
│   ├── gatewayagent/             ← 04_gateway_mcp
│   └── ...
└── evaluators/                   ← 05_evaluation custom evaluators
```

The `agentcore.json` file is the single source of truth. All `agentcore add *`
commands append to it; `agentcore deploy` synthesises CDK and deploys to AWS.

---

## Key commands reference

```bash
agentcore dev                   # run any agent locally with hot-reload
agentcore invoke --dev "hello"  # invoke the locally running agent
agentcore deploy                # deploy to AWS via CDK
agentcore invoke "hello"        # invoke the deployed agent
agentcore status                # show deployment status of all resources
agentcore logs                  # stream runtime logs
agentcore traces list           # list recent trace sessions
agentcore validate              # validate agentcore.json against schema
```

---

## How each agent folder was created

All agent folders under `05-agentcore/cli/app/` were created with:

```bash
agentcore add agent --name <agentName> --framework strands --build CodeZip
```

This scaffolds:
- `app/<agentName>/main.py` — the agent entrypoint
- `app/<agentName>/pyproject.toml` — Python dependencies
- Adds an entry to `agentcore/agentcore.json`

The `02_memory/`, `03_identity_credentials/`, etc. folders then build on the
scaffolded agent by adding resources:

```bash
agentcore add memory --name <memoryName>
agentcore add credential --name <credentialName>
agentcore add gateway --name <gatewayName>
# etc.
```

---

## Cross-reference: by-hand vs CLI

The `05-agentcore/by-hand/` folder shows every step the CLI does under the hood:
- ECR image build and push
- IAM role creation (trust policy + execution policy)
- `bedrock-agentcore-control` API call to create the runtime
- `bedrock-agentcore` API call to invoke it

If you want to understand what `agentcore deploy` actually does in AWS,
start with `05-agentcore/by-hand/README.md`.
