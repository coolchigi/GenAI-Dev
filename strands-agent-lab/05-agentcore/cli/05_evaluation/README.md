# 05 — Evaluation and Online Eval

AgentCore provides two evaluation modes:

| Mode | Trigger | Use case |
|---|---|---|
| **On-demand eval** | You run it manually against a session | Spot-check a specific conversation |
| **Online eval** | Runs automatically on live traffic | Continuous quality monitoring |

Both use the same evaluator definition. The evaluator scores each agent response
and returns a 1–5 quality rating with a reasoning string.

---

## Setup

### 1. Add an LLM-as-judge evaluator

From `05-agentcore/cli/`:

```bash
agentcore add evaluator --name qualityJudge --type llm-as-judge
```

This appends to `agentcore.json`. The evaluator uses a foundation model to score
responses. Edit the entry to customise the judging criteria:

```json
{
  "name": "qualityJudge",
  "type": "LLMJudge",
  "modelId": "amazon.nova-lite-v1:0",
  "systemPrompt": "You are an expert evaluator. Score the assistant response on helpfulness, accuracy, and clarity. Return a JSON object: {\"score\": <1-5>, \"reasoning\": \"<why>\"}"
}
```

Or add a custom Python evaluator (see `evaluators/quality_judge.py`):

```bash
agentcore add evaluator --name qualityJudge --type custom
```

### 2. Add an online eval config (continuous monitoring)

Bind the evaluator to `helloagent` so it runs on every live invocation:

```bash
agentcore add online-eval \
  --name helloagentQuality \
  --agent helloagent \
  --evaluator qualityJudge \
  --sampling-rate 1.0   # evaluate 100% of traffic; use 0.1 for 10% in production
```

### 3. Deploy

```bash
agentcore deploy
agentcore status
```

### 4. Run an on-demand evaluation

After invoking `helloagent` at least once to generate a session:

```bash
# List recent sessions to find a session ID
agentcore traces list

# Run the evaluator against a specific session
agentcore run eval \
  --agent helloagent \
  --evaluator qualityJudge \
  --session-id <session-id>

# View results
agentcore evals history
```

### 5. View online eval results

Online evals run automatically. View the history:

```bash
agentcore evals history
agentcore logs evals   # stream live eval output
```

---

## On-demand vs online eval

**On-demand** — you pick the session, you trigger the run:
```bash
agentcore run eval --agent helloagent --evaluator qualityJudge --session-id <id>
```

**Online** — fires automatically on every invocation (or a sampled subset):
```bash
agentcore pause online-eval --name helloagentQuality    # pause without deleting
agentcore resume online-eval --name helloagentQuality   # resume
```

Use on-demand for targeted debugging. Use online for production dashboards.

---

## Custom evaluator

See `evaluators/quality_judge.py` for a Python-based evaluator that scores
response helpfulness. Custom evaluators give you full control over the scoring
logic — useful when the standard LLM-as-judge criteria don't match your domain.
