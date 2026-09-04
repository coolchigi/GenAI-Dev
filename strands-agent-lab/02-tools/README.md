# Phase 2 — Strands Tools

This section is an exhaustive reference for every tool available to a Strands agent — both the
**built-in tools** shipped in `strands-agents-tools` and the **custom tool patterns** you write
yourself.

Run any file from the `strands-agent-lab/` root:

```bash
aws-vault exec strands-lab -- uv run 02-tools/03_builtin_compute/01_calculator.py
```

Files that need no AWS credentials say so in their `How to run` block and can be run as:

```bash
uv run 02-tools/02_builtin_data_rss/01_rss_feedparser.py
```

---

## Built-in tool map

All tools are from `strands-agents-tools` v0.8.6.

| Category | Tool | File in this section | Needs API key / resource | Status |
|---|---|---|---|---|
| **HTTP & Web** | `http_request` | `01_builtin_http_web/01_http_request.py` | No | ✅ current |
| | DuckDuckGo (custom) | `01_builtin_http_web/02_web_search_ddgs.py` | No | ✅ current |
| | `tavily` / `exa` / `bright_data` | `01_builtin_http_web/03_other_search_providers.py` | Yes (per provider) | ✅ current |
| **Data / RSS** | feedparser (custom) | `02_builtin_data_rss/01_rss_feedparser.py` | No | ✅ current |
| | `retrieve` | `02_builtin_data_rss/02_retrieve_knowledge_base.py` | AWS creds + KB_ID | ✅ current |
| **Compute** | `calculator` | `03_builtin_compute/01_calculator.py` | No | ✅ current |
| | `python_repl` | `03_builtin_compute/02_python_repl.py` | AWS creds | ✅ current |
| | `shell` | `03_builtin_compute/03_shell.py` | AWS creds | ✅ current |
| | `agent_core_code_interpreter` | see `05-agentcore/cli/06_harness/` | AWS creds + AgentCore | ✅ current |
| **AWS** | `use_aws` | `04_builtin_aws/01_use_aws.py` | AWS creds | ✅ current |
| | `generate_image` | `04_builtin_aws/02_generate_image.py` | AWS creds | ✅ current |
| | `nova_reels` | `04_builtin_aws/03_nova_reels.py` | AWS creds + S3 | ✅ current |
| | `retrieve` | `02_builtin_data_rss/02_retrieve_knowledge_base.py` | AWS creds + KB_ID | ✅ current |
| **Memory** | `journal` | `05_builtin_memory/01_journal.py` | No | ✅ current |
| | `memory` (Bedrock KB) | `05_builtin_memory/02_memory_kb.py` | AWS creds + KB_ID | ✅ current |
| | `agent_core_memory` | see `05-agentcore/cli/02_memory/` | AWS creds + AgentCore | ✅ current |
| | `mem0_memory` | — | Mem0 creds | ✅ current |
| | `mongodb_memory` | — | MongoDB Atlas + AWS | ✅ current |
| | `elasticsearch_memory` | — | Elasticsearch + AWS | ✅ current |
| **Agent orchestration** | `use_llm` | `06_builtin_agents_orchestration/01_use_llm.py` | AWS creds | ✅ current |
| | `use_agent` | `06_builtin_agents_orchestration/02_use_agent.py` | AWS creds | ✅ current |
| | `workflow` | `06_builtin_agents_orchestration/03_workflow.py` | AWS creds | ✅ current |
| | `graph` (tool) | `06_builtin_agents_orchestration/04_graph_tool.py` | AWS creds | ✅ current |
| | `mcp_client` | `06_builtin_agents_orchestration/05_mcp_client.py` | AWS creds | ✅ current |
| | `a2a_client` | see `03-patterns/10_a2a_protocol.py` | AWS creds | ✅ current |
| | `swarm` (tool) | — (see `03-patterns/03_swarm.py` for SDK version) | AWS creds | ✅ current |
| | `agent_graph` | — | — | ⚠️ deprecated v0.8.6 |
| | `load_tool` | `09_custom_tools/06_dynamic_tool_loading.py` | AWS creds | ✅ current |
| **Browser / Desktop** | `local_chromium_browser` | `07_builtin_browser_computer/01_browser_local.py` | playwright | ✅ current |
| | `agent_core_browser` | see `05-agentcore/cli/04_gateway_mcp/` | AWS creds + AgentCore | ✅ current |
| | `use_computer` | `07_builtin_browser_computer/02_use_computer.py` | macOS | ✅ current |
| **Comms / Media** | `slack` | `08_builtin_comms_media/01_slack.py` | Slack tokens | ✅ current |
| | `image_reader` | `08_builtin_comms_media/02_image_reader.py` | AWS creds | ✅ current |
| | `speak` | `08_builtin_comms_media/03_speak.py` | macOS (fast) / AWS (Polly) | ✅ current |
| | `generate_image_stability` | `08_builtin_comms_media/04_generate_image_stability.py` | STABILITY_API_KEY | ✅ current |
| | `chat_video` / `search_video` | — | TWELVELABS_API_KEY | ✅ current |
| | `generate_image` | `04_builtin_aws/02_generate_image.py` | AWS creds | ✅ current |
| | `nova_reels` | `04_builtin_aws/03_nova_reels.py` | AWS creds | ✅ current |
| **System / Control** | `environment` | — | AWS creds | ✅ current |
| | `stop` | — | AWS creds | ✅ current |
| | `handoff_to_user` | — | AWS creds | ✅ current |
| | `cron` | see `10_deprecated_reference/` | — | ⚠️ deprecated v0.8.6 |
| | `current_time` | see `10_deprecated_reference/` | — | ⚠️ deprecated v0.8.6 |
| | `sleep` | see `10_deprecated_reference/` | — | ⚠️ deprecated v0.8.6 |
| **Other** | `rss` | see `10_deprecated_reference/` | — | ⚠️ deprecated v0.8.6 |
| | `diagram` | see `10_deprecated_reference/` | — | ⚠️ deprecated v0.8.6 |
| | `batch` | see `10_deprecated_reference/` | — | ⚠️ deprecated v0.8.6 |
| | `think` | see `10_deprecated_reference/` | — | ⚠️ deprecated v0.8.6 |
| **Custom patterns** | — | `09_custom_tools/` (6 files) | AWS creds | ✅ |

---

## AgentCore-dependent tools

Three tools require a deployed AgentCore resource to function. They are covered in the
`05-agentcore/` section where that resource already exists:

| Tool | Covered in |
|---|---|
| `agent_core_memory` | `05-agentcore/cli/02_memory/` |
| `agent_core_code_interpreter` | `05-agentcore/cli/06_harness/` |
| `agent_core_browser` | `05-agentcore/cli/04_gateway_mcp/` |

---

## Key ideas

- The `@tool` decorator is the only thing Strands needs to turn a Python function into a
  tool. The **function name**, **type hints**, and **docstring** are the model's entire
  description of that tool — write them clearly.
- Built-in tools from `strands_tools` are imported exactly like custom ones: pass them in
  the `tools=[]` list.
- Tools that perform destructive actions (file writes, shell commands, AWS mutations) prompt
  for user confirmation by default. Set `BYPASS_TOOL_CONSENT=true` to skip in non-interactive
  environments (CI, deployed agents).
- Deprecated tools print a warning in v0.8.6 and will raise an error in v0.9.0. See
  `10_deprecated_reference/README.md` for the full list and their replacements.
