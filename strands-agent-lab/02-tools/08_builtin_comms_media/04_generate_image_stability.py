# Built-in tool: generate_image_stability — Stability AI Platform API
# --------------------------------------------------------------------
# `generate_image_stability` calls the Stability AI Platform API directly
# (NOT via Bedrock). It supports text-to-image and image-to-image generation
# using Stability AI's hosted models.
#
# Compare to generate_image (04_builtin_aws/02_generate_image.py):
#   generate_image            — Bedrock-hosted Stability models (AWS billing)
#   generate_image_stability  — Stability AI Platform API (Stability billing)
#
# When to use the platform API:
#   - You want access to the latest Stability models before they reach Bedrock
#   - You have an existing Stability AI subscription
#   - You need image-to-image transformations (not available on Bedrock)
#
# Free credits: Stability AI provides free credits on signup at stability.ai
#
# Requires: STABILITY_API_KEY environment variable

import os
from strands import Agent
from strands_tools import generate_image_stability
from common import nova

STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY", "")
if not STABILITY_API_KEY:
    raise EnvironmentError(
        "STABILITY_API_KEY environment variable is not set.\n"
        "Sign up at https://platform.stability.ai/ to get a free API key:\n"
        "    export STABILITY_API_KEY=sk-..."
    )

agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a creative image generation assistant. Use generate_image_stability "
        "to create images from text descriptions. After generating, tell the user "
        "where the image was saved."
    ),
    tools=[generate_image_stability],
)


if __name__ == "__main__":
    print("=== Text-to-image ===")
    agent(
        "Generate an image of a minimalist workspace with a laptop, coffee cup, "
        "and succulent plant on a white desk. Clean, modern aesthetic, soft lighting."
    )

    # ── Image-to-image (requires an existing image file) ─────────────────
    # agent(
    #     "Transform /tmp/strands_test_image.png into a watercolor painting style. "
    #     "Keep the same composition but apply a soft watercolor texture."
    # )


# ── How to run ────────────────────────────────────────────────────────────
# Requires: STABILITY_API_KEY and AWS credentials (for Bedrock model).
#
# Get a free API key:
#   1. Go to https://platform.stability.ai/
#   2. Sign up and go to Account → API Keys
#   3. Create a new key
#
# Export and run:
#     export STABILITY_API_KEY=sk-...
#     aws-vault exec strands-lab -- uv run 02-tools/08_builtin_comms_media/04_generate_image_stability.py
#
# Output: PNG file saved to ./generated_images/ by default.
# Change output directory: export STABILITY_OUTPUT_DIR=/tmp/images
#
# Available models: the tool defaults to stable-diffusion-xl-1024-v1-0.
# Set STABILITY_MODEL_ID to use a different model.
