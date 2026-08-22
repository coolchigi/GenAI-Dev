# Shared model factory for all Phase 2 examples.
# Every pattern needs a model; rather than repeat the BedrockModel config in
# each file, we define it once here and import it. (This is just DRY - nothing
# Strands-specific.)

from strands.models import BedrockModel


def nova(temperature: float = 0.3) -> BedrockModel:
    """Return a Nova Lite model provider pinned to us-east-1."""
    return BedrockModel(
        model_id="amazon.nova-lite-v1:0",
        region_name="us-east-1",
        temperature=temperature,
    )
