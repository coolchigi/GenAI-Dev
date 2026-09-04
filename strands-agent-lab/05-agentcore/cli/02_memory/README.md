# 02 — Memory Strategies

Demonstrates all four AgentCore Memory strategies on a single agent.
The agent remembers things across sessions — invoke it twice with different
session IDs and the second session recalls facts from the first.

---

## The four strategies

| Strategy | What it stores | When it fires |
|---|---|---|
| `SEMANTIC` | Verbatim facts for vector similarity recall | When the agent asserts something as a fact |
| `SUMMARIZATION` | A rolling summary of long conversations | At conversation end / on overflow |
| `USER_PREFERENCE` | Persistent preferences ("I prefer X") | When the user states a preference |
| `EPISODIC` | Event sequences with timestamps | When a sequence of actions occurs |

Use `SEMANTIC` for factual grounding, `USER_PREFERENCE` for personalisation,
`SUMMARIZATION` to keep context windows bounded, and `EPISODIC` for audit trails.

---

## Setup

### 1. Add the memory resource

From `05-agentcore/cli/`:

```bash
agentcore add memory --name memoryAgentMemory
```

This appends to `agentcore.json`. Edit the entry to add all four strategies:

```json
{
  "name": "memoryAgentMemory",
  "eventExpiryDuration": 30,
  "strategies": [
    { "type": "SEMANTIC" },
    { "type": "SUMMARIZATION" },
    { "type": "USER_PREFERENCE" },
    { "type": "EPISODIC" }
  ]
}
```

### 2. Add the agent

```bash
agentcore add agent --name memoryagent --framework strands --build CodeZip
```

Copy `app/memoryagent/main.py` from this folder into `app/memoryagent/`.

### 3. Deploy

```bash
agentcore deploy
agentcore status
```

### 4. Invoke — two sessions to demo cross-session recall

```bash
# Session A: introduce yourself and state a preference
agentcore invoke --session-id session-A "My name is Alex. I prefer concise answers."

# Session A continued: add a fact
agentcore invoke --session-id session-A "I'm working on an AI agent for financial analysis."

# Session B: new session — does it remember Alex?
agentcore invoke --session-id session-B "Do you know anything about me or my project?"
```

Expected: session B recalls the name, preference, and project from session A
via SEMANTIC and USER_PREFERENCE memory strategies.

---

## Local dev

```bash
cd app/memoryagent
agentcore dev   # starts server on :8080
# in another terminal:
agentcore invoke --dev "My name is Alex."
agentcore invoke --dev "What do you know about me?"
```

Note: `LOCAL_DEV=1` skips AgentCore Identity — the session manager falls back
to a synthesised session ID when no memory ID is set (no cross-session recall
locally without a deployed memory resource).
