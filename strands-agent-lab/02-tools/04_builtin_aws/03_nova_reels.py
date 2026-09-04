# Built-in tool: nova_reels — text-to-video via Bedrock Nova Reel
# ----------------------------------------------------------------
# `nova_reels` generates short videos from a text prompt using Amazon Bedrock's
# Nova Reel model. Unlike image generation (which is synchronous), video
# generation is ASYNCHRONOUS — you submit a job, then poll for its status.
#
# The tool exposes three actions:
#   create  — start a new video generation job; returns a job ID
#   status  — check the status of a job (SUBMITTED, IN_PROGRESS, COMPLETED, FAILED)
#   list    — list all your video generation jobs
#
# Output: when COMPLETED, the video is written to the S3 bucket you specify.
#
# Prerequisites:
#   1. An S3 bucket to write the output video to.
#   2. The strands-lab IAM user needs:
#      - bedrock:StartAsyncInvoke + bedrock:GetAsyncInvoke
#      - s3:PutObject on your output bucket
#   3. Enable Nova Reel model access in the Bedrock console.

import os
from strands import Agent
from strands_tools import nova_reels
from common import nova

# Set your output S3 bucket. The video will be written here when complete.
OUTPUT_BUCKET = os.environ.get("NOVA_REELS_S3_BUCKET", "")
if not OUTPUT_BUCKET:
    raise EnvironmentError(
        "NOVA_REELS_S3_BUCKET environment variable is not set.\n"
        "Create an S3 bucket and export its name:\n"
        "    export NOVA_REELS_S3_BUCKET=my-video-output-bucket"
    )

agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a video production assistant. Use nova_reels to create short "
        "videos. When creating a video: first call create to start the job, "
        "tell the user the job ID, then call status to check if it's done. "
        f"Always use s3_uri=s3://{OUTPUT_BUCKET}/videos/ as the output location."
    ),
    tools=[nova_reels],
)


if __name__ == "__main__":
    print("=== Create a video (async) ===")
    # This starts the job and returns a job ID. The video takes 1-3 minutes.
    agent(
        "Create a 6-second video of a calm ocean wave rolling onto a sandy beach "
        "at golden hour. After creating, check the status once."
    )

    # To list all your jobs:
    # agent("List all my nova_reels video generation jobs.")

    # To check status of a specific job (paste your job ID):
    # agent("Check the status of nova_reels job <job-id>.")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required + S3 bucket.
#
# Setup:
#   1. Create an S3 bucket (or use an existing one):
#         aws s3 mb s3://my-strands-video-output --region us-east-1
#   2. Enable Nova Reel in Bedrock console → Model access
#   3. Export bucket name:
#         export NOVA_REELS_S3_BUCKET=my-strands-video-output
#
# Run:
#     aws-vault exec strands-lab -- uv run 02-tools/04_builtin_aws/03_nova_reels.py
#
# The job starts immediately. Poll status every ~30s until COMPLETED.
# Completed video appears in: s3://$NOVA_REELS_S3_BUCKET/videos/
