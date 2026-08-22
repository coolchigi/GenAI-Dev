# Project 03 - Bedrock Agents

## Overview
This project builds an **Amazon Bedrock Agent** — an orchestrated AI system that can reason, plan, and take actions by combining a foundation model with tool use (Action Groups) and a Knowledge Base. This represents the next step beyond basic RAG, enabling the agent to not only retrieve information but also call APIs and execute multi-step tasks autonomously.

## Architecture

```
User Query
    │
    ▼
Amazon Bedrock Agent
    ├── Reasoning & Orchestration (ReAct loop)
    ├── Knowledge Base (RAG — retrieves relevant context from S3 documents)
    └── Action Groups (invokes AWS Lambda functions to take real-world actions)
            │
            └── Lambda Functions
                    ├── Lookup / Query external systems
                    └── Perform write operations (create, update, etc.)
```

## Goals
- Understand how Amazon Bedrock Agents orchestrate multi-step reasoning with a foundation model
- Configure **Action Groups** backed by AWS Lambda to give the agent real-world capabilities
- Integrate a **Knowledge Base** (from Project 02) so the agent can answer questions from documents
- Learn how the agent uses the **ReAct (Reason + Act)** loop to decide which tool to call
- Explore agent **traces** and observability to debug and improve agent behavior

## AWS Services Used
- Amazon Bedrock (Agent + Foundation Model — Claude)
- Amazon Bedrock Knowledge Bases (document Q&A)
- AWS Lambda (Action Group tool implementations)
- Amazon S3 (source documents for Knowledge Base)
- Amazon OpenSearch Serverless (vector store for Knowledge Base)
- AWS IAM (roles and permissions for agent, Lambda, and Knowledge Base)
- Amazon CloudWatch (logs and traces for agent execution)

## Key Concepts
- **Bedrock Agents** — orchestrated AI agents powered by a foundation model
- **Action Groups** — groups of API operations (backed by Lambda + OpenAPI schema) the agent can invoke
- **ReAct loop** — the agent's iterative reason-then-act decision-making cycle
- **Agent Traces** — step-by-step visibility into how the agent thought through a task
- **Session management** — maintaining conversation context across multiple turns
- **Guardrails** — applying safety filters and topic restrictions to agent responses
- **Prompt Engineering for Agents** — writing effective system prompts and instructions

## Project Flow
1. User sends a natural language request to the agent
2. The agent analyzes the request and decides whether to:
   - Query the Knowledge Base for relevant document context
   - Invoke an Action Group Lambda function to take an action
   - Respond directly with its own knowledge
3. The agent iterates (ReAct loop) until it has enough information to respond
4. The final answer is returned to the user, with optional trace output

## Getting Started

### Prerequisites
- AWS account with Amazon Bedrock model access enabled (Claude)
- Python 3.11+ or AWS CDK/CloudFormation for infrastructure
- AWS CLI configured with appropriate credentials

### Setup (Coming Soon)
> Detailed setup instructions, CloudFormation/CDK templates, and Lambda function code will be added as the project develops.

### Folder Structure (Planned)
```
project-03-bedrock-agents/
├── README.md
├── agent/
│   ├── agent_config.json       # Agent name, model, instructions
│   └── system_prompt.txt       # Agent instructions / system prompt
├── action_groups/
│   ├── openapi_schema.json     # OpenAPI spec describing available actions
│   └── lambda_handler.py       # Lambda function implementing the actions
├── knowledge_base/
│   └── (reuses project-02 Knowledge Base config)
└── infra/
    └── template.yaml           # CloudFormation or CDK stack
```

## Resources
- [Amazon Bedrock Agents Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Bedrock Agents Action Groups](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-add.html)
- [Bedrock Agents Knowledge Base Integration](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-kb-add.html)
- [AWS Certified Generative AI Developer - Professional Exam Guide](https://aws.amazon.com/certification/certified-generative-ai-developer-professional/)
- [AWS Bedrock Agents Workshop](https://catalog.workshops.aws/amazon-bedrock-agents)
