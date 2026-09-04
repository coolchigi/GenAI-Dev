# Shared model factory for all Phase 2 (tools) examples.
# Every tool example needs a model; rather than repeat the BedrockModel config
# in each file, we define it once here and import it. Same pattern as
# 03-patterns/common.py — nothing Strands-specific, just DRY.

from strands.models import BedrockModel


def nova(temperature: float = 0.3) -> BedrockModel:
    """Return a Nova Lite model provider pinned to us-east-1."""
    return BedrockModel(
        model_id="amazon.nova-lite-v1:0",
        region_name="us-east-1",
        temperature=temperature,
    )
