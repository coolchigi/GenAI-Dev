# Pattern 8 - Parallel fan-out (concurrent specialist agents)
# -----------------------------------------------------------
# Fan-out: the same input is sent to N specialist agents CONCURRENTLY.
# All agents run in parallel; a synthesis agent merges their outputs into
# one final answer.
#
# Compare to other patterns:
#   Orchestrator (02): supervisor calls specialists ONE AT A TIME (sequential)
#   Swarm       (03):  agents hand off to each other (emergent path)
#   Fan-out     (08):  ALL specialists run AT THE SAME TIME (parallel)
#
# When to use fan-out:
#   - You know the N perspectives/analyses you want upfront
#   - Each specialist is independent (no inter-agent communication)
#   - You care about wall-clock time (parallel is faster than sequential)
#   - You want a balanced final answer from multiple viewpoints
#
# Implementation: asyncio.gather() runs all agent calls concurrently.
# Total time ≈ slowest single agent call, not sum of all calls.

import asyncio
import time
from strands import Agent
from common import nova


# ── Specialist agents ─────────────────────────────────────────────────────
# Each one analyses the same input through a different lens.
# All three share the same model factory but have distinct system prompts.

optimist = Agent(
    name="optimist",
    model=nova(0.7),   # higher temp = more creative, expressive output
    system_prompt=(
        "You are an optimistic business analyst. In 2-3 sentences, identify "
        "the strongest opportunities and best-case outcomes for the given topic. "
        "Be enthusiastic but grounded in realistic possibilities."
    ),
)

pessimist = Agent(
    name="pessimist",
    model=nova(0.3),   # lower temp = more disciplined risk thinking
    system_prompt=(
        "You are a critical risk analyst. In 2-3 sentences, identify the "
        "biggest risks, failure modes, and worst-case scenarios for the given "
        "topic. Be rigorous and realistic, not alarmist."
    ),
)

realist = Agent(
    name="realist",
    model=nova(0.3),
    system_prompt=(
        "You are a pragmatic strategist. In 2-3 sentences, give a balanced, "
        "evidence-based assessment of the given topic — neither overly positive "
        "nor negative. Focus on what is most likely to happen."
    ),
)

synthesiser = Agent(
    name="synthesiser",
    model=nova(0.2),   # low temp = tight, coherent summary
    system_prompt=(
        "You are a strategic advisor. You will receive three analyses of the "
        "same topic: one optimistic, one pessimistic, and one realistic. "
        "Synthesise them into a single, balanced 3-4 sentence summary that "
        "captures the key opportunity, the key risk, and the most likely path."
    ),
)


async def fan_out(topic: str) -> str:
    """Send `topic` to all three specialists concurrently, then synthesise."""

    # asyncio.gather runs all three coroutines at the same time.
    # Total wait ≈ max(optimist, pessimist, realist), not their sum.
    optimist_result, pessimist_result, realist_result = await asyncio.gather(
        optimist.invoke_async(topic),
        pessimist.invoke_async(topic),
        realist.invoke_async(topic),
    )

    # Feed all three results to the synthesiser.
    synthesis_prompt = (
        f"Topic: {topic}\n\n"
        f"OPTIMIST:\n{optimist_result.message}\n\n"
        f"PESSIMIST:\n{pessimist_result.message}\n\n"
        f"REALIST:\n{realist_result.message}"
    )
    final = await synthesiser.invoke_async(synthesis_prompt)
    return final.message


if __name__ == "__main__":
    topic = "Launching an AI-powered personal finance app in 2026"

    print(f"Topic: {topic}\n")
    print("Running optimist, pessimist, and realist in PARALLEL...\n")

    start = time.monotonic()
    result = asyncio.run(fan_out(topic))
    elapsed = time.monotonic() - start

    print("── SYNTHESISED ANALYSIS ──────────────────────────────────────")
    print(result)
    print(f"\n[Completed in {elapsed:.1f}s for 4 agent calls]")


# ── How to run ────────────────────────────────────────────────────────────
#     aws-vault exec strands-lab -- uv run 03-patterns/08_parallel_fanout.py
#
# Watch the timing: 4 agent calls (3 parallel + 1 sequential synthesis)
# complete faster than 4 sequential calls would.
#
# To change the topic, edit the `topic` variable above or pass it as an arg:
#     aws-vault exec strands-lab -- uv run 03-patterns/08_parallel_fanout.py
