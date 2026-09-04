# Built-in tool: image_reader — read local images into the agent
# --------------------------------------------------------------
# `image_reader` reads PNG, JPEG, GIF, or WebP files from disk and formats
# them as Bedrock Converse API document blocks. This lets a multimodal model
# "see" a local image — it's passed directly in the conversation, not via URL.
#
# When to use:
#   - Ask the model to describe, analyse, or extract text from a local image
#   - Include a diagram or screenshot in an agent conversation
#   - Build vision-augmented pipelines (e.g. read a chart, then summarise it)
#
# Note: The model receiving the image must support vision (multimodal).
# Nova Lite supports images natively via Bedrock's Converse API.
#
# No extra API keys needed. AWS credentials required for the model.

import os
import urllib.request
from pathlib import Path
from strands import Agent
from strands_tools import image_reader
from common import nova

# We download a small public-domain test image to /tmp so the example is
# self-contained. In real usage, point image_reader at any local PNG/JPEG.
TEST_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
TEST_IMAGE_PATH = Path("/tmp/strands_test_image.png")

if not TEST_IMAGE_PATH.exists():
    print(f"Downloading test image to {TEST_IMAGE_PATH}...")
    urllib.request.urlretrieve(TEST_IMAGE_URL, TEST_IMAGE_PATH)
    print("Done.")

agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a visual analysis assistant. Use the image_reader tool to load "
        "images from disk, then describe and analyse what you see in detail."
    ),
    tools=[image_reader],
)


if __name__ == "__main__":
    print("=== Read and describe the test image ===")
    agent(
        f"Read the image at {TEST_IMAGE_PATH} and describe what you see. "
        "What shapes, colours, and patterns are visible?"
    )

    # To use your own image:
    # agent("Read the image at /path/to/your/image.png and tell me what's in it.")

    # To extract text from a screenshot (e.g. a terminal screenshot):
    # agent(
    #     "Read the image at /tmp/screenshot.png and extract all the text you can see."
    # )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required. Pillow required (installed with strands-agents-tools).
#
#     aws-vault exec strands-lab -- uv run 02-tools/08_builtin_comms_media/02_image_reader.py
#
# The test image is downloaded automatically on first run.
# To use your own image: export IMAGE_PATH=/path/to/image.png
# and adjust the agent prompt above.
