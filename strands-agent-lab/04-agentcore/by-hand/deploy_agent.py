# Create the AgentCore Runtime, pointing it at the image you pushed to ECR.
# This is the "control plane" call the CLI/CDK makes for you.
#
# Run (after ECR push + role creation):
#     aws-vault exec strands-lab -- uv run 04-agentcore/by-hand/deploy_agent.py
#
# Fill the two placeholders below (printed by the ECR + IAM steps in README.md).

import boto3

REGION = "us-east-1"
CONTAINER_URI = "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/strands-byhand:latest"
ROLE_ARN = "arn:aws:iam::ACCOUNT_ID:role/AgentRuntimeRole"

# NOTE the client name: bedrock-agentcore-CONTROL is the control plane
# (create/manage resources). The data plane (invoke) is a different client.
control = boto3.client("bedrock-agentcore-control", region_name=REGION)

resp = control.create_agent_runtime(
    agentRuntimeName="strands_byhand",
    agentRuntimeArtifact={
        "containerConfiguration": {"containerUri": CONTAINER_URI}
    },
    networkConfiguration={"networkMode": "PUBLIC"},
    roleArn=ROLE_ARN,
    lifecycleConfiguration={
        "idleRuntimeSessionTimeout": 300,   # stop idle sessions after 5 min
        "maxLifetime": 1800,                # hard cap 30 min (cost guardrail)
    },
)

print("ARN:   ", resp["agentRuntimeArn"])
print("Status:", resp["status"])
