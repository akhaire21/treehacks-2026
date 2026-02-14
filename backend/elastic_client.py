"""
Elasticsearch + JINA embeddings client for the Agent Workflow Marketplace.

Uses:
- JINA Embeddings v3 API for dense vector generation
- Elasticsearch kNN + BM25 hybrid search
- Elastic Cloud for hosted deployment

Prize targets: Elastic (full stack), JINA embeddings, Elastic Cloud
"""

import os
import json
import requests
import numpy as np
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch


# ---------------------------------------------------------------------------
# JINA Embeddings
# ---------------------------------------------------------------------------

class JinaEmbedder:
    """Generate embeddings via JINA Embeddings API."""

    API_URL = "https://api.jina.ai/v1/embeddings"

    def __init__(self, api_key: Optional[str] = None, model: str = "jina-embeddings-v3"):
        self.api_key = api_key or os.getenv("JINA_API_KEY", "")
        self.model = model
        self.dimension = 1024  # jina-embeddings-v3 output dim

    def embed(self, texts: List[str], task: str = "retrieval.passage") -> List[List[float]]:
        """
        Embed a list of texts using JINA API.
        task: 'retrieval.passage' for documents, 'retrieval.query' for queries.
        """
        if not self.api_key:
            raise ValueError("JINA_API_KEY is not set")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": texts,
            "task": task,
        }
        resp = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]

    def embed_query(self, text: str) -> List[float]:
        """Embed a single search query."""
        return self.embed([text], task="retrieval.query")[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of documents / workflow descriptions."""
        return self.embed(texts, task="retrieval.passage")


# ---------------------------------------------------------------------------
# Elasticsearch Client
# ---------------------------------------------------------------------------

INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            # ---- core fields ----
            "workflow_id":    {"type": "keyword"},
            "title":          {"type": "text", "analyzer": "standard"},
            "task_type":      {"type": "keyword"},
            "description":    {"type": "text", "analyzer": "standard"},
            "state":          {"type": "keyword"},
            "year":           {"type": "integer"},
            "location":       {"type": "keyword"},
            "platform":       {"type": "keyword"},
            "domain":         {"type": "keyword"},

            # ---- marketplace fields ----
            "token_cost":     {"type": "integer"},
            "execution_tokens": {"type": "integer"},
            "rating":         {"type": "float"},
            "usage_count":    {"type": "integer"},
            "tags":           {"type": "keyword"},

            # ---- dense vector (JINA) ----
            "embedding": {
                "type": "dense_vector",
                "dims": 1024,
                "index": True,
                "similarity": "cosine",
            },

            # ---- full workflow payload ----
            "steps":            {"type": "object", "enabled": False},
            "edge_cases":       {"type": "object", "enabled": False},
            "domain_knowledge": {"type": "text"},
            "requirements":     {"type": "text"},
            "token_comparison": {"type": "object", "enabled": False},
        }
    },
}


class ElasticClient:
    """
    Wraps Elasticsearch for the Workflow Marketplace.
    Provides hybrid search (kNN vector + BM25 text) using JINA embeddings.
    """

    def __init__(
        self,
        cloud_id: Optional[str] = None,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        jina_embedder: Optional[JinaEmbedder] = None,
    ):
        self.cloud_id = cloud_id or os.getenv("ELASTIC_CLOUD_ID", "")
        self.api_key = api_key or os.getenv("ELASTIC_API_KEY", "")
        self.index_name = index_name or os.getenv("ELASTIC_INDEX", "workflows")
        self.embedder = jina_embedder or JinaEmbedder()

        # Support both Cloud ID format and direct URL
        if self.cloud_id and self.api_key:
            if self.cloud_id.startswith("http"):
                # Direct Elasticsearch endpoint URL
                self.es = Elasticsearch(
                    self.cloud_id,
                    api_key=self._parse_api_key(self.api_key),
                    verify_certs=True,
                )
            else:
                # Standard Cloud ID (deployment-name:base64)
                self.es = Elasticsearch(
                    cloud_id=self.cloud_id,
                    api_key=self._parse_api_key(self.api_key),
                )
        else:
            # Fallback to localhost for dev
            self.es = Elasticsearch("http://localhost:9200")

        print(f"[elastic] connected — index={self.index_name}")

    @staticmethod
    def _parse_api_key(raw_key: str):
        """
        Parse API key — handles both raw base64 and id:key tuple formats.
        Elastic Python client accepts either a string or a tuple (id, key).
        """
        import base64
        try:
            decoded = base64.b64decode(raw_key).decode("utf-8")
            if ":" in decoded:
                parts = decoded.split(":", 1)
                return (parts[0], parts[1])
        except Exception:
            pass
        return raw_key

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def create_index(self):
        """Create the workflows index with dense_vector mapping."""
        if self.es.indices.exists(index=self.index_name):
            print(f"[elastic] index '{self.index_name}' already exists — deleting")
            self.es.indices.delete(index=self.index_name)
        self.es.indices.create(index=self.index_name, body=INDEX_SETTINGS)
        print(f"[elastic] created index '{self.index_name}'")

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def _workflow_to_text(self, wf: Dict[str, Any]) -> str:
        """Build a rich text representation for embedding."""
        parts = [
            f"Task: {wf.get('task_type', '')}",
            f"Title: {wf.get('title', '')}",
            f"Description: {wf.get('description', '')}",
        ]
        if wf.get("state"):
            parts.append(f"State: {wf['state']}")
        if wf.get("location"):
            parts.append(f"Location: {wf['location']}")
        if wf.get("platform"):
            parts.append(f"Platform: {wf['platform']}")
        if wf.get("tags"):
            parts.append(f"Tags: {', '.join(wf['tags'])}")
        if wf.get("requirements"):
            parts.append(f"Requirements: {', '.join(wf['requirements'])}")
        if wf.get("domain_knowledge"):
            parts.append(f"Domain knowledge: {' '.join(wf['domain_knowledge'][:3])}")
        return " | ".join(parts)

    def ingest_workflows(self, workflows: List[Dict[str, Any]]):
        """Embed workflows with JINA and bulk-index into Elasticsearch."""
        texts = [self._workflow_to_text(wf) for wf in workflows]
        print(f"[elastic] embedding {len(texts)} workflows via JINA …")
        embeddings = self.embedder.embed_documents(texts)

        for wf, emb in zip(workflows, embeddings):
            doc = {**wf, "embedding": emb}
            self.es.index(index=self.index_name, id=wf["workflow_id"], document=doc)

        self.es.indices.refresh(index=self.index_name)
        print(f"[elastic] indexed {len(workflows)} workflows")

    # ------------------------------------------------------------------
    # Hybrid search  (kNN + BM25)
    # ------------------------------------------------------------------

    def hybrid_search(
        self,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
        knn_boost: float = 0.7,
        bm25_boost: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining:
          1. kNN vector similarity (JINA embedding)
          2. BM25 text match on title + description + domain_knowledge

        Returns ranked list of workflow hits.
        """
        # Build query embedding
        query_embedding = self.embedder.embed_query(query_text)

        # Build filter clause
        filter_clauses = []
        if filters:
            for field in ("task_type", "state", "year", "location", "platform", "domain"):
                if field in filters and filters[field] is not None:
                    filter_clauses.append({"term": {field: filters[field]}})

        # kNN clause
        knn = {
            "field": "embedding",
            "query_vector": query_embedding,
            "k": top_k,
            "num_candidates": max(top_k * 5, 50),
            "boost": knn_boost,
        }
        if filter_clauses:
            knn["filter"] = {"bool": {"must": filter_clauses}}

        # BM25 clause
        bm25_query: Dict[str, Any] = {
            "bool": {
                "should": [
                    {"multi_match": {
                        "query": query_text,
                        "fields": ["title^3", "description^2", "domain_knowledge", "tags^2"],
                        "boost": bm25_boost,
                    }},
                ],
            },
        }
        if filter_clauses:
            bm25_query["bool"]["filter"] = filter_clauses

        body = {
            "size": top_k,
            "knn": knn,
            "query": bm25_query,
            "_source": {"excludes": ["embedding"]},
        }

        resp = self.es.search(index=self.index_name, body=body)

        results = []
        for hit in resp["hits"]["hits"]:
            doc = hit["_source"]
            doc["_score"] = hit["_score"]
            doc["match_percentage"] = min(100, int(hit["_score"] * 50))  # normalise
            results.append(doc)

        return results

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single workflow by ID."""
        try:
            resp = self.es.get(index=self.index_name, id=workflow_id)
            doc = resp["_source"]
            doc.pop("embedding", None)
            return doc
        except Exception:
            return None

    def update_field(self, workflow_id: str, field: str, value: Any):
        """Partial update of a single field."""
        self.es.update(
            index=self.index_name,
            id=workflow_id,
            body={"doc": {field: value}},
        )

    def get_all(self, size: int = 100) -> List[Dict[str, Any]]:
        """Return all workflows (for listing page)."""
        resp = self.es.search(
            index=self.index_name,
            body={"size": size, "query": {"match_all": {}}, "_source": {"excludes": ["embedding"]}},
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    def count(self) -> int:
        return self.es.count(index=self.index_name)["count"]
