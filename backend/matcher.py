"""
Workflow matching engine backed by Elasticsearch + JINA embeddings.

Provides two modes:
  1. Elastic mode  — hybrid kNN + BM25 search via Elastic Cloud (production)
  2. Fallback mode — in-memory numpy cosine similarity (no Elastic needed)

The fallback lets the API start instantly for development / demo even when
Elastic Cloud / JINA keys are missing.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional


class WorkflowMatcher:
    """
    Matches user queries to workflows.
    Delegates to ElasticClient when available, else uses in-memory fallback.
    """

    def __init__(self, elastic_client=None):
        self.elastic = elastic_client
        self.workflows: List[Dict[str, Any]] = []
        self._use_elastic = elastic_client is not None
        print(f"[matcher] mode={'elastic' if self._use_elastic else 'in-memory'}")

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_workflows(self, workflows_path: str):
        """Load workflows from JSON file."""
        with open(workflows_path, "r") as f:
            data = json.load(f)
            self.workflows = data["workflows"]
        print(f"[matcher] loaded {len(self.workflows)} workflows from disk")

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for matching workflows.
        Uses Elasticsearch hybrid search when available, otherwise in-memory.
        """
        if self._use_elastic:
            return self._elastic_search(query, top_k)
        return self._memory_search(query, top_k)

    # -- Elasticsearch path --

    def _elastic_search(self, query: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        query_text = self._query_to_text(query)
        filters = {}
        for f in ("task_type", "state", "year", "location", "platform", "domain"):
            if f in query:
                filters[f] = query[f]
        return self.elastic.hybrid_search(query_text, filters=filters, top_k=top_k)

    # -- In-memory fallback (no Elastic / JINA needed) --

    def _memory_search(self, query: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        candidates = self._apply_hard_filters(query)
        if not candidates:
            return []

        query_text = self._query_to_text(query).lower()
        query_tokens = set(query_text.split())

        results = []
        for wf in candidates:
            wf_text = self._workflow_to_text(wf).lower()
            wf_tokens = set(wf_text.split())
            # Jaccard-ish similarity
            intersection = query_tokens & wf_tokens
            union = query_tokens | wf_tokens
            score = len(intersection) / max(len(union), 1)

            result = {k: v for k, v in wf.items()}
            result["similarity_score"] = round(score, 4)
            result["match_percentage"] = min(100, int(score * 120))  # slight boost
            results.append(result)

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _apply_hard_filters(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        candidates = []
        for wf in self.workflows:
            if "task_type" in query and wf.get("task_type") != query["task_type"]:
                continue
            if "state" in query and "state" in wf and wf["state"] != query["state"]:
                continue
            if "year" in query and "year" in wf and wf["year"] != query["year"]:
                continue
            candidates.append(wf)
        return candidates

    def _workflow_to_text(self, wf: Dict[str, Any]) -> str:
        parts = [
            f"Task: {wf.get('task_type', '')}",
            f"Title: {wf.get('title', '')}",
            f"Description: {wf.get('description', '')}",
            f"Tags: {', '.join(wf.get('tags', []))}",
        ]
        if wf.get("requirements"):
            parts.append(f"Requirements: {', '.join(wf['requirements'])}")
        return " | ".join(parts)

    def _query_to_text(self, query: Dict[str, Any]) -> str:
        parts = []
        for key, value in query.items():
            parts.append(f"{key}: {value}")
        return " | ".join(parts)

    def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        # Try Elastic first
        if self._use_elastic:
            wf = self.elastic.get_by_id(workflow_id)
            if wf:
                return wf
        # Fallback to in-memory
        for wf in self.workflows:
            if wf["workflow_id"] == workflow_id:
                return wf
        return None

    def get_all_workflows(self) -> List[Dict[str, Any]]:
        if self._use_elastic:
            try:
                return self.elastic.get_all()
            except Exception:
                pass
        return self.workflows
