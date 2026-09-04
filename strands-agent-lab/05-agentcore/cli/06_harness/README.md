# 06 — Declarative Harness

A **harness** is a declarative agent: you define its system prompt, tools
(sourced from a gateway), and memory in `agentcore.json` — no Python required.
AgentCore generates and manages the runtime for you.

When you need to customise beyond what the harness declaration allows, you
export it to a Strands Python agent:

```
agentcore.json harness definition
         │
         ▼  agentcore export harness
app/<agentName>/
  ├── main.py        ← standard Strands agent (editable)
  ├── EXPORT_NOTES.md ← READ THIS FIRST after every export
  └── ...
```

This is also where `agent_core_code_interpreter` fits naturally: add it as a
tool in the harness definition (via a gateway connector target) and it appears
as a sandboxed Python execution environment in the exported agent.

---

## When to use harness vs writing an agent directly

| | Harness | Write agent directly |
|---|---|---|
| Speed | Fast — JSON config only | Slower — write code |
| Customisation | Limited to declaration | Full Python |
| Memory + gateway wiring | Automatic | Manual plumbing |
| Best for | Standard agents, quick prototypes | Custom logic, complex tools |

Start with a harness. Export to code when you need to customise.

---

## Setup

### 1. Add the harness

From `05-agentcore/cli/`:

```bash
agentcore add harness --name researchHarness
```

Edit the resulting `agentcore.json` harness entry:

```json
{
  "name": "researchHarness",
  "systemPrompt": "You are a research assistant. Use your tools to find current information and remember what users tell you across sessions.",
  "tools": [
    {
      "gatewayName": "toolGateway",
      "targetNames": ["wordCountTool"]
    }
  ],
  "memoryName": "memoryAgentMemory"
}
```

To add `agent_core_code_interpreter` as a sandboxed compute tool, add a
`connector` target to the gateway (`04_gateway_mcp/agentcore.json`):

```json
{
  "name": "codeInterpreterTarget",
  "type": "connector",
  "connectorType": "codeInterpreter"
}
```

Then reference it in the harness tools list.

### 2. Validate

```bash
agentcore validate
```

### 3. Deploy (harness-only — no Python needed)

```bash
agentcore deploy
agentcore invoke "How many words are in: 'Hello world from AgentCore'?"
```

### 4. Export to a Strands Python agent (when you need customisation)

```bash
agentcore export harness --name researchHarness
```

**ALWAYS read the export notes first:**

```bash
cat app/researchHarness/EXPORT_NOTES.md
```

This file lists any manual follow-up steps (missing files, IAM additions,
config steps the exporter couldn't automate). A clean export produces
"No manual steps required."

### 5. Run the exported agent locally

```bash
agentcore dev --agent researchHarness
agentcore invoke --dev "Search for: latest AI agent frameworks 2026"
```

---

## agent_core_code_interpreter

`agent_core_code_interpreter` is the AgentCore-managed sandboxed code execution
environment. Unlike `python_repl` (which runs code on your machine), the
AgentCore code interpreter runs code in an isolated AWS-managed sandbox — safe
for production use.

It appears as a tool in the exported agent and supports:
- `execute_code` — run Python in a sandbox
- `execute_command` — run shell commands in a sandbox
- `read_files` / `write_files` / `list_files` — manage sandbox files

This is the production alternative to `02-tools/03_builtin_compute/02_python_repl.py`.
See the exported `app/researchHarness/main.py` after export to see it wired in.
