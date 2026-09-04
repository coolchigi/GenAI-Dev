# Built-in tool: workflow — parallel tasks with dependency resolution
# -------------------------------------------------------------------
# `workflow` lets the agent define a set of named tasks with optional
# inter-task dependencies and run them in parallel (independent tasks)
# or sequentially (dependent tasks), with priority scheduling and retries.
#
# Key concepts:
#   - Each task has a name, description, and optional depends_on list.
#   - Tasks with no dependencies run concurrently in a thread pool.
#   - Tasks that depend on others wait for those to complete first.
#   - Each task can specify its own model provider, tool list, and retry count.
#   - State is persisted so interrupted workflows can resume.
#
# When to use vs Swarm:
#   - Swarm:    agents decide the path dynamically (emergent)
#   - Workflow: YOU define the tasks and dependencies upfront (planned)
#   - Workflow is better when you know exactly what work needs to happen
#     and which parts can run in parallel.

from strands import Agent
from strands_tools import workflow
from common import nova


agent = Agent(
    model=nova(0.3),
    system_prompt=(
        "You are a workflow orchestrator. Use the workflow tool to plan and "
        "execute multi-step tasks efficiently. Define tasks with clear names "
        "and descriptions, set up dependencies where needed, and run them."
    ),
    tools=[workflow],
)


if __name__ == "__main__":
    agent(
        "Create and run a workflow to produce a product brief for a "
        "'smart water bottle with hydration tracking'. "
        "The workflow should have these tasks:\n"
        "1. 'research'   — research the smart water bottle market (no dependencies)\n"
        "2. 'competitor' — identify top 3 competitors (no dependencies)\n"
        "3. 'brief'      — write a product brief using the research and competitor analysis "
        "                  (depends on both 'research' and 'competitor')\n"
        "Run 'research' and 'competitor' in parallel, then 'brief' when both are done."
    )


# ── How to run ────────────────────────────────────────────────────────────
# AWS credentials required.
#
#     aws-vault exec strands-lab -- uv run 02-tools/06_builtin_agents_orchestration/03_workflow.py
#
# Note: workflow state is persisted to a temp directory between retries.
# To see the parallel execution, watch the output — 'research' and 'competitor'
# will start at the same time; 'brief' will start only after both finish.
