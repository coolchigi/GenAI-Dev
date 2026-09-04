# Built-in tool: generate_image — text-to-image via Bedrock Stable Diffusion
# ---------------------------------------------------------------------------
# `generate_image` calls Amazon Bedrock's image generation models to turn a
# text prompt into an image. The generated image is saved locally as a PNG.
#
# Available models (set via STABILITY_MODEL_ID env var or pass in prompt):
#   - stability.stable-diffusion-xl-v1       (default, SDXL)
#   - stability.sd3-5-large-v1:0             (SD 3.5 — highest quality)
#   - stability.stable-image-core-v1:1       (fast, lower cost)
#   - stability.stable-image-ultra-v1:1      (ultra quality, highest cost)
#
# Output: PNG file saved to ./generated_images/ by default.
# Customize with STABILITY_OUTPUT_DIR env var.
#
# Note: this uses Bedrock Stability models (AWS-hosted). For the
# Stability AI Platform API (direct, not Bedrock), see:
# 08_builtin_comms_media/04_generate_image_stability.py

from strands import Agent
from strands_tools import generate_image
from common import nova


agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a creative director. When asked to create an image, use the "
        "generate_image tool with a detailed, descriptive prompt. After generating, "
        "tell the user where the image was saved."
    ),
    tools=[generate_image],
)


if __name__ == "__main__":
    print("=== Generate a landscape image ===")
    agent(
        "Generate an image of a serene mountain lake at sunset with reflections "
        "in the water, photorealistic style."
    )

    print("\n=== Generate a technical diagram style ===")
    agent(
        "Generate an image of a futuristic cloud computing data center, "
        "digital art style, blue and white color scheme."
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required. The strands-lab user needs:
#   bedrock:InvokeModel on stability.* models
#
# Enable model access in the Bedrock console first:
#   https://console.aws.amazon.com/bedrock/ → Model access → Stability AI
#
#     aws-vault exec strands-lab -- uv run 02-tools/04_builtin_aws/02_generate_image.py
#
# Optional env vars:
#   STABILITY_MODEL_ID=stability.sd3-5-large-v1:0   # change model
#   STABILITY_OUTPUT_DIR=/tmp/images                 # change output dir
