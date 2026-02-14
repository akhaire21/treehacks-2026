"""
Workflow loading utilities.

Loads workflows from JSON files and prepares them for indexing.
Does NOT create artificial tree structures - uses the unified Workflow model directly.
"""

import json
from typing import List, Dict, Any

from models import Workflow


def load_workflows_from_json(workflows_path: str) -> List[Workflow]:
    """
    Load workflows from JSON file.

    Returns workflows as-is without creating artificial tree structures.
    Each workflow's steps are preserved in the steps array, not converted to child nodes.

    Args:
        workflows_path: Path to workflows.json

    Returns:
        List of Workflow objects
    """
    with open(workflows_path, 'r') as f:
        data = json.load(f)
        workflows_data = data.get("workflows", [])

    workflows = []
    for workflow_data in workflows_data:
        # Convert to Workflow model
        # Workflow.from_dict() already sets node_type="workflow" and depth=0 by default
        workflow = Workflow.from_dict(workflow_data)
        workflows.append(workflow)

    print(f"Loaded {len(workflows)} workflows from {workflows_path}")

    return workflows


def workflow_to_text(workflow: Workflow) -> str:
    """
    Convert workflow to text representation for embedding.

    This creates a rich text representation that captures all searchable aspects
    of the workflow for semantic search.

    Args:
        workflow: Workflow object

    Returns:
        Text representation for embedding
    """
    parts = []

    # Core identity
    parts.append(f"Title: {workflow.title}")
    parts.append(f"Task: {workflow.task_type}")
    parts.append(f"Description: {workflow.description}")

    # Location/temporal filters
    if workflow.state:
        parts.append(f"State: {workflow.state}")

    if workflow.location:
        parts.append(f"Location: {workflow.location}")

    if workflow.year:
        parts.append(f"Year: {workflow.year}")

    # Tags for categorization
    if workflow.tags:
        parts.append(f"Tags: {', '.join(workflow.tags)}")

    # Requirements (what's needed to use this workflow)
    if workflow.requirements:
        parts.append(f"Requirements: {', '.join(workflow.requirements)}")

    # Steps summary (for understanding workflow coverage)
    # Steps are stored as List[Dict[str, Any]], not objects
    if workflow.steps:
        step_summaries = []
        for step in workflow.steps[:5]:  # First 5 steps to avoid too long text
            # Access dict fields, not attributes
            step_num = step.get("step", "")
            thought = step.get("thought", "")
            if thought:
                step_summaries.append(f"{step_num}. {thought}")
        if step_summaries:
            parts.append(f"Steps: {'; '.join(step_summaries)}")

    # Edge cases (important for matching complex scenarios)
    if workflow.edge_cases:
        parts.append(f"Edge cases: {', '.join(workflow.edge_cases[:3])}")  # First 3

    # Domain knowledge (for semantic relevance)
    if workflow.domain_knowledge:
        parts.append(f"Domain: {', '.join(workflow.domain_knowledge[:3])}")  # First 3

    return " | ".join(parts)


def prepare_for_indexing(workflow: Workflow, full_text: str, embedding: List[float]) -> Dict[str, Any]:
    """
    Prepare workflow document for Elasticsearch indexing.

    Args:
        workflow: Workflow object
        full_text: Text representation for search
        embedding: Dense vector embedding

    Returns:
        Dictionary ready for indexing with _id field for Elasticsearch
    """
    # Set embedding and full_text on workflow
    workflow.embedding = embedding
    workflow.full_text = full_text

    # Convert to Elasticsearch document
    doc = workflow.to_es_document()

    # Add _id field for Elasticsearch bulk indexing
    doc["_id"] = workflow.workflow_id

    return doc


def validate_workflow_consistency(workflow: Workflow) -> List[str]:
    """
    Validate that workflow follows consistency rules.

    Checks:
    1. Workflows should have node_type="workflow", not "step"
    2. Steps should be in the steps array, not as child_ids
    3. Parent/child relationships should only be for sub-workflows, not steps
    4. Required fields are present

    Args:
        workflow: Workflow to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check node_type is valid
    if workflow.node_type not in ["workflow", "step"]:
        errors.append(f"Invalid node_type: {workflow.node_type}. Must be 'workflow' or 'step'.")

    # Check that steps are not represented as child workflows
    if workflow.child_ids:
        for child_id in workflow.child_ids:
            if "_step_" in child_id:
                errors.append(
                    f"Child ID '{child_id}' looks like a step. "
                    f"Steps should be in the 'steps' array, not child_ids."
                )

    # Check required fields
    if not workflow.workflow_id:
        errors.append("Missing required field: workflow_id")

    if not workflow.title:
        errors.append("Missing required field: title")

    if not workflow.task_type:
        errors.append("Missing required field: task_type")

    # Validate step structure if steps exist
    if workflow.steps:
        for i, step in enumerate(workflow.steps):
            if not isinstance(step, dict):
                errors.append(f"Step {i} is not a dictionary: {type(step)}")
            elif "step" not in step:
                errors.append(f"Step {i} is missing 'step' field (step number)")
            elif "thought" not in step:
                errors.append(f"Step {i} is missing 'thought' field")

    return errors


# Example usage
if __name__ == "__main__":
    # Load workflows
    workflows = load_workflows_from_json("workflows.json")

    # Validate
    for workflow in workflows:
        errors = validate_workflow_consistency(workflow)
        if errors:
            print(f"Validation errors for {workflow.workflow_id}:")
            for error in errors:
                print(f"  - {error}")

    # Convert to text
    if workflows:
        first_workflow = workflows[0]
        text = workflow_to_text(first_workflow)
        print(f"\nText representation of first workflow:")
        print(text)
