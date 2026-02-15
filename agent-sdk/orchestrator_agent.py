"""
orchestrator_agent.py — Multi-Task Orchestrator Agent

Demonstrates:
  ✅ Claude Agent SDK (Anthropic tool_use loop)
  ✅ Multi-step task chaining across domains
  ✅ Agent reasoning about WHEN to use the marketplace
  ✅ Token budget management

This is the most sophisticated demo — the agent chains multiple
marketplace queries to solve a complex multi-domain task.

Prize targets:
  - Greylock: Best Multi-Turn Agent
  - Anthropic: Best Use of Claude Agent SDK
"""

from agent_runner import MarkAgent


ORCHESTRATOR_SYSTEM_PROMPT = """You are an advanced orchestrator agent powered by the Mark AI marketplace.

You handle COMPLEX tasks that span multiple domains. Your strength is
breaking down big problems and finding the right marketplace workflow
for each subtask.

Process:
1. Decompose the user's request into subtasks
2. For EACH subtask, call mark_estimate to check marketplace coverage
3. Buy solutions for subtasks where the marketplace adds value
4. Skip the marketplace for simple subtasks you can handle directly
5. Synthesize all results into a comprehensive plan
6. Rate each workflow you purchased

Key principles:
- Not everything needs the marketplace — use judgment
- Chain workflows: output of one feeds input of another
- Track your token budget across all purchases
- Explain your decomposition strategy to the user
- This is multi-turn reasoning at its best"""


def run_orchestrator_agent():
    """Run the orchestrator demo."""
    agent = MarkAgent(
        name="orchestrator-agent",
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        max_turns=15,
        verbose=True,
    )

    task = (
        "I'm relocating from California to Ohio for a new job. I need help with: "
        "1) Filing my 2024 California taxes (partial year) "
        "2) Setting up Ohio state tax withholding for 2025 "
        "3) Finding the best neighborhoods in Columbus for a family of 4 "
        "Can you find marketplace workflows for each of these?"
    )

    trace = agent.run(task)
    return trace


if __name__ == "__main__":
    run_orchestrator_agent()
