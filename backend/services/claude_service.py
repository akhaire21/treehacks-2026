"""
Claude AI service for LLM operations.
Handles query decomposition, reasoning, and other LLM tasks.
"""

import anthropic
from typing import List, Dict, Any, Optional


class ClaudeService:
    """Service for Claude AI API calls."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4096
    ):
        """
        Initialize Claude service.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Max tokens for generation
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

        print(f"Initialized ClaudeService with model: {model}")

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using Claude.

        Args:
            prompt: User prompt
            system: Optional system prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)

        return response.content[0].text

    def decompose_task(
        self,
        task_description: str,
        min_subtasks: int = 2,
        max_subtasks: int = 8,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Decompose a task into subtasks using Claude.

        Args:
            task_description: Natural language task description
            min_subtasks: Minimum number of subtasks
            max_subtasks: Maximum number of subtasks
            context: Optional context (previous search results, parent task, etc.)

        Returns:
            List of subtask dictionaries with:
                - text: Subtask description
                - task_type: Type of subtask
                - weight: Importance weight (0-1)
                - rationale: Why this subtask is needed
        """
        system_prompt = f"""You are a task decomposition expert for an AI agent workflow marketplace.

Your job is to break down user tasks into {min_subtasks}-{max_subtasks} searchable subtasks that can be used to find relevant workflow templates.

Guidelines:
- Each subtask should be atomic and searchable
- Subtasks should cover different aspects: location, time, requirements, constraints
- Assign weights (0-1) based on importance (1.0 = critical, 0.5 = helpful, 0.3 = optional)
- Provide task_type: tax_filing, travel_planning, data_parsing, real_estate_search, outreach, or general
- Explain rationale for each subtask

Output ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "subtasks": [
    {{
      "text": "subtask description",
      "task_type": "tax_filing",
      "weight": 0.9,
      "rationale": "why this subtask is important"
    }}
  ]
}}"""

        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{context}"

        prompt = f"""Task to decompose: "{task_description}"{context_str}

Decompose this into {min_subtasks}-{max_subtasks} searchable subtasks. Output JSON only."""

        try:
            response = self.generate(
                prompt=prompt,
                system=system_prompt,
                temperature=0.3  # Lower temperature for structured output
            )

            # Parse JSON response
            import json
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            result = json.loads(response)
            subtasks = result.get("subtasks", [])

            print(f"Decomposed into {len(subtasks)} subtasks")
            return subtasks

        except Exception as e:
            print(f"Error decomposing task: {e}")
            # Fallback: return single task
            return [{
                "text": task_description,
                "task_type": "general",
                "weight": 1.0,
                "rationale": "Failed to decompose, using original task"
            }]

    def score_plan_quality(
        self,
        task_description: str,
        workflow: Dict[str, Any]
    ) -> float:
        """
        Score how well a workflow matches a task (0-1).

        Args:
            task_description: Original task description
            workflow: Workflow candidate

        Returns:
            Quality score (0-1, where 1 = perfect match)
        """
        system_prompt = """You are a workflow quality scorer for an AI agent marketplace.

Your job is to evaluate how well a workflow template matches a user's task.

Consider:
- Task type match (exact match = higher score)
- Requirement coverage (does workflow handle all user needs?)
- Specificity match (too specific/general = lower score)
- Domain knowledge overlap

Output ONLY a JSON object with:
{
  "score": 0.85,
  "reasoning": "brief explanation"
}"""

        workflow_summary = f"""
Title: {workflow.title}
Task Type: {workflow.task_type}
Description: {workflow.description}
Tags: {', '.join(workflow.tags)}
Requirements: {workflow.requirements}
"""

        prompt = f"""Task: "{task_description}"

Workflow to evaluate:
{workflow_summary}

How well does this workflow match the task? Output JSON only."""

        try:
            response = self.generate(
                prompt=prompt,
                system=system_prompt,
                temperature=0.2
            )

            # Parse JSON
            import json
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            result = json.loads(response)
            score = result.get("score", 0.0)

            return max(0.0, min(1.0, score))  # Clamp to [0, 1]

        except Exception as e:
            print(f"Error scoring plan: {e}")
            # Fallback: use workflow rating as proxy
            return workflow.rating / 5.0 if workflow.rating else 0.0


# Example usage
if __name__ == "__main__":
    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        exit(1)

    # Initialize service
    service = ClaudeService(api_key=api_key)

    # Test task decomposition
    task = "I need to file my Ohio 2024 taxes with W2 income and itemized deductions"
    print(f"Task: {task}\n")

    subtasks = service.decompose_task(task, min_subtasks=2, max_subtasks=5)

    print("Subtasks:")
    for i, st in enumerate(subtasks):
        print(f"\n{i+1}. {st['text']}")
        print(f"   Type: {st['task_type']}")
        print(f"   Weight: {st['weight']}")
        print(f"   Rationale: {st['rationale']}")

    # Test plan scoring
    print("\n" + "="*60)
    print("Testing plan scoring...\n")

    mock_workflow = {
        "title": "Ohio 2024 IT-1040 (W2, Itemized, Married)",
        "task_type": "tax_filing",
        "description": "Complete Ohio state income tax filing for W2 employees with itemized deductions",
        "tags": ["tax", "ohio", "w2", "itemized"],
        "requirements": ["W2 forms", "itemized deduction records"],
        "rating": 4.8
    }

    score = service.score_plan_quality(task, mock_workflow)
    print(f"Plan quality score: {score:.2f}")
