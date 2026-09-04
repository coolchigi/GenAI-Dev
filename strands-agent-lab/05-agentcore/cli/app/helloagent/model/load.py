from strands.models.bedrock import BedrockModel


def load_model() -> BedrockModel:
    """Get Bedrock model client using IAM credentials."""
    # Nova Lite in us-east-1 - the only model family enabled on this account.
    return BedrockModel(
        model_id="amazon.nova-lite-v1:0",
        region_name="us-east-1",
    )
