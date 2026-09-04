# Built-in tool: use_aws — universal boto3 wrapper
# -------------------------------------------------
# `use_aws` lets the agent call ANY AWS service operation via boto3.
# The model passes the service name, operation, and parameters; `use_aws`
# constructs the boto3 call and returns the result.
#
# This is the Swiss Army knife of AWS tools — you don't write a new @tool
# for each AWS API call; one tool covers all of them.
#
# Safety model:
#   - Read-only operations: run without confirmation (list, describe, get).
#   - Mutative operations (create, delete, put, update, run, stop):
#     prompt for user confirmation.
#   - SENSITIVE operations are ALWAYS redacted from the response, regardless
#     of BYPASS_TOOL_CONSENT:
#       • secretsmanager GetSecretValue
#       • sts AssumeRole / GetCallerIdentity
#       • ssm GetParameter / GetParameters (SecureString)
#     The model sees a "[REDACTED]" placeholder — it can confirm the call
#     worked but never reads the secret value.
#   - BYPASS_TOOL_CONSENT=true skips confirmation for non-redacted mutative ops.
#
# AWS credentials: standard boto3 credential chain (aws-vault injects them).

from strands import Agent
from strands_tools import use_aws
from common import nova


agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are an AWS assistant. Use the use_aws tool to query AWS services. "
        "For read-only queries you can run immediately. Always explain what you "
        "found after each AWS call."
    ),
    tools=[use_aws],
)


if __name__ == "__main__":
    print("=== EC2: list available regions ===")
    # Read-only: no confirmation prompt.
    agent("List all AWS regions where EC2 is available.")

    print("\n=== S3: list my buckets ===")
    # Read-only: safe to run without confirmation.
    agent("List all S3 buckets in my account and show their creation dates.")

    print("\n=== Bedrock: list available foundation models ===")
    # Another read-only call — shows the models available in your region.
    agent("List the foundation models available in Bedrock in us-east-1.")

    # ── Example of a mutative call (will prompt for confirmation) ────────
    # Uncomment to try — it will ask "Run this operation? [y/N]" before executing.
    # agent("Create an S3 bucket named 'strands-lab-test-12345' in us-east-1.")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required (strands-lab profile has ec2:DescribeRegions,
# s3:ListBuckets, and bedrock:ListFoundationModels at minimum).
#
#     aws-vault exec strands-lab -- uv run 02-tools/04_builtin_aws/01_use_aws.py
#
# Non-interactive (skip confirmation for mutative ops — use with care):
#     BYPASS_TOOL_CONSENT=true aws-vault exec strands-lab -- uv run 02-tools/04_builtin_aws/01_use_aws.py
