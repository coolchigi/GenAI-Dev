# Custom evaluator: response quality judge
# -----------------------------------------
# This is a custom Python evaluator for AgentCore. It scores an agent
# response on a 1–5 scale across three dimensions, then returns an overall
# score and reasoning string.
#
# When to use a custom evaluator over LLM-as-judge:
#   - You have domain-specific scoring criteria
#   - You want deterministic, rule-based scoring (not model-dependent)
#   - You want to combine heuristics (length, keywords) with model scoring
#   - You want the scoring logic in version control
#
# AgentCore calls this function with each (prompt, response) pair from a
# session. The function must return a dict with "score" and "reasoning".
#
# Deploy by registering this file as an evaluator in agentcore.json:
#   agentcore add evaluator --name qualityJudge --type custom

import re


def evaluate(prompt: str, response: str, context: dict | None = None) -> dict:
    """Score an agent response on helpfulness, length, and source citation.

    Args:
        prompt:   The user's input message.
        response: The agent's response to score.
        context:  Optional additional context (session metadata, etc.)

    Returns:
        A dict with:
          score     — integer 1–5 (5 = excellent)
          reasoning — plain-text explanation of the score
    """
    issues = []
    score  = 5   # start at full marks and deduct

    # ── Dimension 1: length (too short = not helpful) ────────────────────
    word_count = len(response.split())
    if word_count < 10:
        score  -= 2
        issues.append(f"Response too short ({word_count} words — minimum 10)")
    elif word_count < 25:
        score  -= 1
        issues.append(f"Response is brief ({word_count} words)")

    # ── Dimension 2: does it address the prompt? ─────────────────────────
    # Simple heuristic: look for at least one content word from the prompt.
    prompt_keywords = {
        w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", prompt)
    }
    response_words  = {
        w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", response)
    }
    overlap = prompt_keywords & response_words
    if not overlap:
        score  -= 1
        issues.append("Response shares no keywords with the prompt — may be off-topic")

    # ── Dimension 3: citations (for research/factual questions) ──────────
    is_factual_question = any(
        kw in prompt.lower()
        for kw in ["what is", "how does", "explain", "when", "where", "who"]
    )
    has_citation = "http" in response or "source:" in response.lower()
    if is_factual_question and not has_citation:
        score  -= 1
        issues.append("Factual question answered without source citation")

    # Floor at 1 — never give 0 (that would mean "no response", handled separately)
    score = max(1, score)

    reasoning = (
        f"Score: {score}/5. "
        + (("Issues: " + "; ".join(issues) + ".") if issues else "No issues found.")
    )

    return {"score": score, "reasoning": reasoning}


# ── Local test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        ("What is Amazon Bedrock?", "It's a thing."),
        ("What is Amazon Bedrock?",
         "Amazon Bedrock is a fully managed AWS service for foundation models. "
         "Source: https://aws.amazon.com/bedrock/"),
        ("How does AgentCore work?",
         "AgentCore is a runtime for deploying AI agents on AWS. It handles "
         "scaling, memory, and observability automatically. See the docs for details."),
    ]
    for prompt, response in samples:
        result = evaluate(prompt, response)
        print(f"Prompt: {prompt[:60]}")
        print(f"Result: {result}\n")
