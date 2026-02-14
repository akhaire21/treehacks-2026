"""
Workflow matching engine using embedding-based similarity search.
Combines hard filters (exact match on task_type, state) with semantic similarity.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Any
import json


class WorkflowMatcher:
    """Matches user queries to workflows using hybrid search (filters + embeddings)."""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize with sentence transformer model."""
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.workflows = []
        self.workflow_embeddings = None

    def load_workflows(self, workflows_path: str):
        """Load workflows from JSON file and pre-compute embeddings."""
        with open(workflows_path, 'r') as f:
            data = json.load(f)
            self.workflows = data['workflows']

        print(f"Loaded {len(self.workflows)} workflows")

        # Pre-compute embeddings for all workflows
        workflow_texts = [self._workflow_to_text(wf) for wf in self.workflows]
        self.workflow_embeddings = self.model.encode(workflow_texts)
        print("Computed workflow embeddings")

    def search(self, query: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for matching workflows using hybrid approach:
        1. Hard filters (task_type, state, year)
        2. Embedding similarity ranking

        Args:
            query: User query dict with task_type, state, and other attributes
            top_k: Number of results to return

        Returns:
            List of matching workflows with similarity scores
        """
        # Step 1: Hard filter
        candidates = self._apply_hard_filters(query)

        if not candidates:
            return []

        # Step 2: Compute query embedding
        query_text = self._query_to_text(query)
        query_embedding = self.model.encode([query_text])[0]

        # Step 3: Compute similarities for candidates
        results = []
        for workflow, idx in candidates:
            workflow_emb = self.workflow_embeddings[idx]
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1),
                workflow_emb.reshape(1, -1)
            )[0][0]

            result = workflow.copy()
            result['similarity_score'] = float(similarity)
            result['match_percentage'] = int(similarity * 100)
            results.append(result)

        # Step 4: Sort by similarity and return top K
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]

    def _apply_hard_filters(self, query: Dict[str, Any]) -> List[tuple]:
        """Apply exact match filters on critical fields."""
        candidates = []

        required_fields = ['task_type']
        for field in required_fields:
            if field not in query:
                return []

        for idx, workflow in enumerate(self.workflows):
            # Must match task type
            if workflow.get('task_type') != query.get('task_type'):
                continue

            # If state specified, must match (if workflow has state)
            if 'state' in query and 'state' in workflow:
                if workflow['state'] != query['state']:
                    continue

            # If year specified, must match (if workflow has year)
            if 'year' in query and 'year' in workflow:
                if workflow['year'] != query['year']:
                    continue

            candidates.append((workflow, idx))

        return candidates

    def _workflow_to_text(self, workflow: Dict[str, Any]) -> str:
        """Convert workflow to text representation for embedding."""
        parts = [
            f"Task: {workflow.get('task_type', '')}",
            f"Description: {workflow.get('description', '')}",
            f"State: {workflow.get('state', '')}",
            f"Tags: {', '.join(workflow.get('tags', []))}",
        ]

        # Add key requirements
        if 'requirements' in workflow:
            parts.append(f"Requirements: {', '.join(workflow['requirements'])}")

        return " | ".join(parts)

    def _query_to_text(self, query: Dict[str, Any]) -> str:
        """Convert query to text representation for embedding."""
        parts = []

        # Core fields
        if 'task_type' in query:
            parts.append(f"Task: {query['task_type']}")
        if 'state' in query:
            parts.append(f"State: {query['state']}")
        if 'year' in query:
            parts.append(f"Year: {query['year']}")

        # Additional context
        for key, value in query.items():
            if key not in ['task_type', 'state', 'year']:
                parts.append(f"{key}: {value}")

        return " | ".join(parts)

    def get_workflow_by_id(self, workflow_id: str) -> Dict[str, Any]:
        """Retrieve specific workflow by ID."""
        for workflow in self.workflows:
            if workflow['workflow_id'] == workflow_id:
                return workflow
        return None


# Example usage for testing
if __name__ == "__main__":
    matcher = WorkflowMatcher()

    # For testing, we'll create this after workflows.json exists
    print("WorkflowMatcher module loaded successfully")
    print("Run with workflows.json to test: matcher.load_workflows('workflows.json')")
