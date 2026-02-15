"""
Workflow loading utilities.

Loads workflows from JSON files and prepares them for indexing.
Does NOT create artificial tree structures - uses the unified Workflow model directly.
"""

import json
from typing import List, Dict, Any, Tuple

from models import Workflow, WorkflowNodeDoc


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
        # Handle both string and dict formats
        edge_summaries = []
        for edge in workflow.edge_cases[:3]:
            if isinstance(edge, dict):
                edge_summaries.append(edge.get('scenario', str(edge)))
            else:
                edge_summaries.append(str(edge))
        if edge_summaries:
            parts.append(f"Edge cases: {', '.join(edge_summaries)}")

    # Domain knowledge (for semantic relevance)
    if workflow.domain_knowledge:
        # Handle both string and dict formats
        domain_summaries = []
        for domain in workflow.domain_knowledge[:3]:
            if isinstance(domain, dict):
                domain_summaries.append(domain.get('concept', str(domain)))
            else:
                domain_summaries.append(str(domain))
        if domain_summaries:
            parts.append(f"Domain: {', '.join(domain_summaries)}")

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


def extract_nodes_from_workflow(workflow: Workflow) -> List[WorkflowNodeDoc]:
    """
    Extract indexable nodes (subtasks/steps) from a workflow.

    This enables tree-aware recursive search (Step 9 in algorithm).
    Each step becomes a searchable node with its own embedding.

    Args:
        workflow: Workflow object

    Returns:
        List of WorkflowNodeDoc objects ready for indexing
    """
    nodes = []

    # Extract steps as nodes
    if workflow.steps:
        for i, step in enumerate(workflow.steps):
            # Create text representation for this step
            step_text_parts = []

            if step.get("thought"):
                step_text_parts.append(f"Thought: {step['thought']}")

            if step.get("action"):
                step_text_parts.append(f"Action: {step['action']}")

            if step.get("context"):
                step_text_parts.append(f"Context: {step['context']}")

            step_text = " | ".join(step_text_parts)

            # Create node
            node = WorkflowNodeDoc(
                node_id=f"{workflow.workflow_id}_step_{step.get('step', i)}",
                workflow_id=workflow.workflow_id,
                node_type="step",
                title=step.get("thought", f"Step {step.get('step', i)}"),
                text=step_text,
                capability=None,  # Could be inferred from action
                parent_node_id=workflow.workflow_id,  # Direct parent is workflow
                ordinal=step.get("step", i),
                embedding=None  # Will be generated during indexing
            )

            nodes.append(node)

    return nodes


def prepare_nodes_for_indexing(
    nodes: List[WorkflowNodeDoc],
    embedding_service
) -> List[Dict[str, Any]]:
    """
    Prepare workflow nodes for Elasticsearch indexing.

    Generates embeddings for each node and converts to ES documents.

    Args:
        nodes: List of WorkflowNodeDoc objects
        embedding_service: EmbeddingService instance

    Returns:
        List of dictionaries ready for indexing
    """
    docs = []

    for node in nodes:
        # Generate embedding for node text
        embedding = embedding_service.embed(
            node.text,
            task="retrieval.passage"
        )
        node.embedding = embedding

        # Convert to ES document
        doc = node.to_es_document()
        doc["_id"] = node.node_id

        docs.append(doc)

    return docs


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
