# Custom tools: validation — Pydantic parameters and error handling
# -----------------------------------------------------------------
# Two validation approaches and a critical design decision:
#
# 1. PYDANTIC MODELS as parameters
#    Pass a Pydantic model as a parameter type — Strands serialises the schema
#    automatically. The model receives a structured input and must fill all
#    required fields. Great for tools that take structured input.
#
# 2. ERROR HANDLING: ValueError vs returning an error string
#    This is a subtle but important design decision:
#
#    raise ValueError("bad input")
#      → Strands surfaces this as a TOOL ERROR in the model's context.
#        The model SEES the error and can RETRY with corrected input.
#        Use for: invalid arguments, precondition failures, validation errors.
#
#    return "Error: bad input"
#      → The model receives this as a SUCCESSFUL tool result.
#        It treats the error string as a normal answer — it may accept it
#        and move on rather than retrying. Use with care.
#
#    Rule of thumb: if the model should RETRY, raise. If the error IS the
#    answer (e.g. "no results found"), return a descriptive string.

from pydantic import BaseModel, Field
from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(model_id="amazon.nova-lite-v1:0", region_name="us-east-1")


# ── Pydantic model as a tool parameter ───────────────────────────────────
class ShippingAddress(BaseModel):
    """A postal address for shipping."""
    street:  str = Field(..., description="Street address including number")
    city:    str = Field(..., description="City name")
    country: str = Field(..., description="ISO 3166-1 alpha-2 country code (e.g. 'CA', 'US')")
    postal_code: str = Field(..., description="Postal or ZIP code")


@tool
def format_shipping_label(address: ShippingAddress, recipient_name: str) -> str:
    """Format a shipping label from a structured address and recipient name.

    Use this when you need to produce a formatted shipping label.
    `recipient_name` is the full name of the recipient.
    `address` must be a complete postal address with street, city, country, and postal_code.
    """
    return (
        f"{recipient_name}\n"
        f"{address.street}\n"
        f"{address.city}  {address.postal_code}\n"
        f"{address.country.upper()}"
    )


# ── ValueError vs return-error-string ────────────────────────────────────
@tool
def divide(numerator: float, denominator: float) -> float:
    """Divide numerator by denominator and return the result.

    Use this to perform division. Both values must be numbers.
    `denominator` must not be zero.

    Raises an error if denominator is zero so you can retry with a valid value.
    """
    if denominator == 0:
        # Raising ValueError tells the model "bad input — try again with a non-zero denominator".
        raise ValueError("denominator must not be zero — please provide a non-zero value")
    return numerator / denominator


@tool
def find_user(user_id: str) -> str:
    """Look up a user by their ID and return their display name.

    Use this to get a user's name from their user ID string.
    Returns the user's display name, or a 'not found' message if the ID doesn't exist.
    """
    # Fake user store for the demo
    users = {"u001": "Alice Chen", "u002": "Bob Kumar", "u003": "Carol Smith"}

    if user_id not in users:
        # Returning a string (not raising) — "not found" IS the answer here.
        # The model should accept this and tell the user, not retry.
        return f"User '{user_id}' not found."

    return users[user_id]


agent = Agent(
    model=model,
    tools=[format_shipping_label, divide, find_user],
)


if __name__ == "__main__":
    print("=== Pydantic structured input ===")
    agent(
        "Format a shipping label for Alice Chen at "
        "123 Maple Street, Ottawa, Canada, postal code K1A 0A9."
    )

    print("\n=== ValueError: model sees the error and retries ===")
    # The model will try to divide by zero, see the error, correct itself.
    agent("What is 10 divided by 0? Then try 10 divided by 2.")

    print("\n=== Return-error-string: model accepts the result ===")
    agent("What is the name of user u999?")


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required.
#
#     aws-vault exec strands-lab -- uv run 02-tools/09_custom_tools/02_tool_with_validation.py
