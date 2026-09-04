# Built-in tool: speak — text-to-speech (macOS say + AWS Polly)
# --------------------------------------------------------------
# `speak` converts text to speech. Two modes:
#
#   fast   — uses macOS `say` command. Zero config, zero cost, instant.
#             Runs entirely locally. macOS only.
#
#   polly  — uses AWS Polly for high-quality, production-grade speech.
#             Many voices and languages. Costs ~$4 per 1M characters.
#             Requires AWS credentials with polly:SynthesizeSpeech permission.
#
# When to use:
#   - Voice output for accessibility
#   - Audio summaries (e.g. "read me today's news")
#   - Voice-enabled agent demos
#   - Notifications that need to be heard, not read
#
# Fast mode works on macOS with no setup. Try it first.

import os
from strands import Agent
from strands_tools import speak
from common import nova

# Default to fast mode (macOS say). Switch to polly for production quality.
SPEAK_MODE = os.environ.get("SPEAK_MODE", "fast")   # "fast" or "polly"

agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a voice assistant. Use the speak tool to read responses aloud. "
        f"Always use mode='{SPEAK_MODE}'. "
        "When the user asks you to say something, speak it out loud."
    ),
    tools=[speak],
)


if __name__ == "__main__":
    print(f"=== Speak in {SPEAK_MODE} mode ===")
    agent("Say out loud: 'Hello! I am a Strands AI agent running on Amazon Bedrock.'")

    print("\n=== Speak a summary ===")
    agent(
        "Summarise what Strands is in one sentence, then speak that summary aloud."
    )


# ── How to run ────────────────────────────────────────────────────────────
# Fast mode (macOS only, no AWS credentials needed for speak itself):
#     aws-vault exec strands-lab -- uv run 02-tools/08_builtin_comms_media/03_speak.py
#
# Polly mode (AWS credentials required, cross-platform):
#     SPEAK_MODE=polly aws-vault exec strands-lab -- uv run 02-tools/08_builtin_comms_media/03_speak.py
#
# Note: AWS credentials are ALWAYS required for the Bedrock model.
# Only the speak action itself is credential-free in fast mode.
#
# To change the macOS voice:
#     export SAY_VOICE=Samantha     # run `say -v ?` to list available voices
#
# To change the Polly voice:
#     export POLLY_VOICE_ID=Joanna  # see AWS docs for all voice IDs
