"""
Elasticsearch service for workflow indexing and search.
Handles all Elasticsearch operations including kNN vector search.
"""

import os
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticsearchService:
    """Service for Elasticsearch operations."""

    def __init__(
        self,
        index_name: str,
        embedding_dim: int = 1024,
        cloud_id: str = "",
        api_key: str = "",
        host: str = "",
        username: str = "",
        password: str = ""
    ):
        """
        Initialize Elasticsearch service.

        Supports two connection modes:
        1. Cloud ID + API Key (recommended for Elastic Cloud)
        2. Host + username/password (for self-hosted)

        Args:
            index_name: Name of the index (for assets)
            embedding_dim: Dimension of embedding vectors
            cloud_id: Elastic Cloud ID (preferred)
            api_key: Elastic API key (used with cloud_id)
            host: Elasticsearch host URL (fallback for self-hosted)
            username: Optional username for basic auth (legacy)
            password: Optional password for basic auth (legacy)
        """
        self.index_name = index_name  # Assets index
        self.nodes_index_name = f"{index_name}_nodes"  # Nodes index
        self.embedding_dim = embedding_dim

        # Build connection: prefer Cloud ID + API Key
        if cloud_id and api_key:
            self.es = Elasticsearch(
                cloud_id=cloud_id,
                api_key=api_key
            )
            connection_info = f"Elastic Cloud (ID: {cloud_id[:20]}...)"
        elif host:
            # Fallback to host-based connection
            if username and password:
                self.es = Elasticsearch(
                    hosts=[host],
                    basic_auth=(username, password)
                )
            else:
                self.es = Elasticsearch(hosts=[host])
            connection_info = host
        else:
            raise ValueError("Must provide either (cloud_id + api_key) or host")

        # Test connection (serverless-compatible)
        try:
            info = self.es.info()
            print(f"Connected to Elasticsearch: {connection_info}")
            print(f"  Version: {info.get('version', {}).get('number', 'unknown')}")
            print(f"Assets Index: {index_name}")
            print(f"Nodes Index: {self.nodes_index_name}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Elasticsearch at {connection_info}: {e}")

    def create_index(self, delete_existing: bool = False):
        """
        Create Elasticsearch index with proper mappings for workflows.

        Args:
            delete_existing: Whether to delete existing index first
        """
        # Delete if requested
        if delete_existing and self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            print(f"Deleted existing index: {self.index_name}")

        # Check if index already exists
        if self.es.indices.exists(index=self.index_name):
            print(f"Index '{self.index_name}' already exists")
            return

        # Define mappings
        mappings = {
            "mappings": {
                "properties": {
                    # Workflow metadata
                    "workflow_id": {"type": "keyword"},
                    "node_type": {"type": "keyword"},
                    "title": {"type": "text"},
                    "task_type": {"type": "keyword"},
                    "description": {"type": "text"},
                    "tags": {"type": "keyword"},

                    # Location/temporal fields
                    "state": {"type": "keyword"},
                    "location": {"type": "keyword"},
                    "year": {"type": "integer"},
                    "duration_days": {"type": "integer"},

                    # Metrics (both new and legacy field names for backward compatibility)
                    "download_cost": {"type": "integer"},
                    "execution_cost": {"type": "integer"},
                    "token_cost": {"type": "integer"},  # Legacy name for download_cost
                    "execution_tokens": {"type": "integer"},  # Legacy name for execution_cost
                    "rating": {"type": "float"},
                    "usage_count": {"type": "integer"},

                    # Workflow content (structured data, not searchable - use full_text for search)
                    "requirements": {"type": "text"},
                    "steps": {"type": "object", "enabled": False},  # Store but don't index
                    "edge_cases": {"type": "object", "enabled": False},  # Store but don't index
                    "domain_knowledge": {"type": "object", "enabled": False},  # Store but don't index
                    "examples": {"type": "object", "enabled": False},  # Store but don't index

                    # Token comparison
                    "token_comparison": {
                        "properties": {
                            "from_scratch": {"type": "integer"},
                            "with_workflow": {"type": "integer"},
                            "savings_percent": {"type": "integer"}
                        }
                    },

                    # Tree structure (for subtasks)
                    "parent_id": {"type": "keyword"},  # Parent workflow/step ID
                    "child_ids": {"type": "keyword"},  # Array of child IDs
                    "depth": {"type": "integer"},  # Tree depth level

                    # Vector embedding for semantic search (serverless-compatible)
                    "embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dim,
                        "index": True,  # Enable indexing for kNN
                        "similarity": "cosine"
                    },

                    # Full text representation
                    "full_text": {"type": "text"},
                }
            }
            # Note: No settings needed - serverless handles sharding/replicas automatically
        }

        # Create index
        self.es.indices.create(index=self.index_name, body=mappings)
        print(f"Created index: {self.index_name}")

    def create_nodes_index(self, delete_existing: bool = False):
        """
        Create Elasticsearch index for workflow nodes (subtasks/steps).

        This enables tree-aware recursive search (Step 9).

        Args:
            delete_existing: Whether to delete existing index first
        """
        # Delete if requested
        if delete_existing and self.es.indices.exists(index=self.nodes_index_name):
            self.es.indices.delete(index=self.nodes_index_name)
            print(f"Deleted existing nodes index: {self.nodes_index_name}")

        # Check if index already exists
        if self.es.indices.exists(index=self.nodes_index_name):
            print(f"Nodes index '{self.nodes_index_name}' already exists")
            return

        # Define mappings for nodes
        mappings = {
            "mappings": {
                "properties": {
                    # Identity
                    "node_id": {"type": "keyword"},
                    "workflow_id": {"type": "keyword"},  # Parent workflow
                    "node_type": {"type": "keyword"},  # "subtask", "step", "module"
                    "parent_node_id": {"type": "keyword"},  # Direct parent

                    # Content
                    "title": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "text": {"type": "text"},  # Full description
                    "capability": {"type": "keyword"},  # What this node does

                    # Structure
                    "ordinal": {"type": "integer"},  # Order within parent

                    # Vector embedding for semantic search (serverless-compatible)
                    "embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dim,
                        "index": True,  # Enable indexing for kNN
                        "similarity": "cosine"
                    }
                }
            }
            # Note: No settings needed - serverless handles sharding/replicas automatically
        }

        # Create nodes index
        self.es.indices.create(index=self.nodes_index_name, body=mappings)
        print(f"Created nodes index: {self.nodes_index_name}")

    def index_document(self, doc_id: str, document: Dict[str, Any]):
        """
        Index a single document.

        Args:
            doc_id: Document ID
            document: Document data
        """
        self.es.index(index=self.index_name, id=doc_id, body=document)

    def index_bulk(self, documents: List[Dict[str, Any]]):
        """
        Bulk index multiple documents.

        Args:
            documents: List of documents with '_id' field
        """
        def generate_actions():
            for doc in documents:
                doc_id = doc.pop("_id", doc.get("workflow_id"))
                yield {
                    "_index": self.index_name,
                    "_id": doc_id,
                    "_source": doc
                }

        try:
            success, failed = bulk(self.es, generate_actions(), raise_on_error=False)
            print(f"Indexed {success} documents, {len(failed)} failed")

            if failed:
                print("Failed documents:")
                for fail in failed[:3]:  # Show first 3 failures
                    print(f"  Error: {fail}")
        except Exception as e:
            print(f"Bulk index error: {e}")
            # Try to get more details
            if hasattr(e, 'errors'):
                for error in e.errors[:3]:
                    print(f"  Details: {error}")
            raise

    def vector_search(
        self,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search using kNN.

        Args:
            query_embedding: Query embedding vector
            filters: Optional filters (field: value)
            top_k: Number of results to return

        Returns:
            List of ES hits with standard structure: [{"_source": {...}, "_score": ...}, ...]
        """
        # Build kNN query
        knn_query = {
            "field": "embedding",
            "query_vector": query_embedding,
            "k": top_k,
            "num_candidates": max(top_k * 10, 100)  # Higher for better recall (recommended 10x)
        }

        # Add filters if provided
        if filters:
            filter_clauses = []
            for field, value in filters.items():
                if value is not None:
                    filter_clauses.append({"term": {field: value}})

            if filter_clauses:
                knn_query["filter"] = filter_clauses

        # Execute search
        response = self.es.search(
            index=self.index_name,
            knn=knn_query,
            size=top_k
        )

        # Return standard ES hit structure with _source and _score
        return response["hits"]["hits"]

    def hybrid_search(
        self,
        query_embedding: List[float],
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
        vector_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and text search.

        Args:
            query_embedding: Query embedding vector
            query_text: Query text for keyword search
            filters: Optional filters
            top_k: Number of results to return
            vector_weight: Weight for vector search (0-1), text weight = 1 - vector_weight

        Returns:
            List of ES hits with standard structure: [{"_source": {...}, "_score": ...}, ...]
        """
        # Build query
        query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        # Vector similarity (weighted)
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": f"{vector_weight} * (cosineSimilarity(params.query_vector, 'embedding') + 1.0)",
                                    "params": {"query_vector": query_embedding}
                                }
                            }
                        },
                        # Text search (weighted)
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["title^3", "description^2", "full_text", "tags^2"],
                                "type": "best_fields",
                                "boost": 1 - vector_weight
                            }
                        }
                    ],
                    "filter": []
                }
            }
        }

        # Add filters
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query["query"]["bool"]["filter"].append(
                        {"term": {field: value}}
                    )

        # Execute search
        response = self.es.search(index=self.index_name, body=query)

        # Return standard ES hit structure with _source and _score
        return response["hits"]["hits"]

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document or None if not found
        """
        try:
            result = self.es.get(index=self.index_name, id=doc_id)
            return result["_source"]
        except Exception:
            return None

    def get_children(
        self,
        parent_id: str,
        node_type: Optional[str] = None,
        sort_by: str = "depth"
    ) -> List[Dict[str, Any]]:
        """
        Get direct children of a node.

        Args:
            parent_id: ID of the parent node
            node_type: Optional filter by node type ("workflow", "subtask", "step")
            sort_by: Sort field (default: "depth")

        Returns:
            List of child nodes
        """
        must_clauses = [{"term": {"parent_id": parent_id}}]

        if node_type:
            must_clauses.append({"term": {"node_type": node_type}})

        query = {"bool": {"must": must_clauses}}

        response = self.es.search(
            index=self.index_name,
            query=query,
            size=1000,
            sort=[{sort_by: "asc"}]
        )

        return [hit["_source"] for hit in response["hits"]["hits"]]

    def index_node(self, node_id: str, node_doc: Dict[str, Any]):
        """
        Index a single workflow node (subtask/step).

        Args:
            node_id: Node ID
            node_doc: Node document data
        """
        self.es.index(index=self.nodes_index_name, id=node_id, body=node_doc)

    def search_nodes(
        self,
        workflow_id: str,
        query_text: str,
        query_embedding: List[float],
        node_type: Optional[str] = None,
        parent_node_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search workflow nodes using hybrid semantic + text search.

        This is the key method for Step 9 tree-aware recursion.

        Args:
            workflow_id: Workflow to search within
            query_text: Query text
            query_embedding: Query embedding vector
            node_type: Optional filter by node type ("subtask", "step", "module")
            parent_node_id: Optional filter by parent node
            top_k: Number of results

        Returns:
            List of ES hits with node documents
        """
        # Build filters
        must_clauses = [{"term": {"workflow_id": workflow_id}}]

        if node_type:
            must_clauses.append({"term": {"node_type": node_type}})

        if parent_node_id:
            must_clauses.append({"term": {"parent_node_id": parent_node_id}})

        # Use native kNN query (better than script_score)
        query = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": must_clauses,
                    "should": [
                        # Text search on title and text
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["title^3", "text^2", "capability^2"],
                                "type": "best_fields"
                            }
                        }
                    ]
                }
            },
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": top_k,
                "num_candidates": max(top_k * 10, 50),
                "filter": must_clauses
            }
        }

        response = self.es.search(index=self.nodes_index_name, body=query)
        return response["hits"]["hits"]

    def delete_index(self):
        """Delete the assets index."""
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            print(f"Deleted index: {self.index_name}")

    def delete_nodes_index(self):
        """Delete the nodes index."""
        if self.es.indices.exists(index=self.nodes_index_name):
            self.es.indices.delete(index=self.nodes_index_name)
            print(f"Deleted nodes index: {self.nodes_index_name}")


# Example usage
if __name__ == "__main__":
    import os
    from embedding_service import EmbeddingService

    # Initialize services (using cloud_id + api_key or host)
    cloud_id = os.getenv("ELASTIC_CLOUD_ID", "")
    api_key = os.getenv("ELASTIC_API_KEY", "")
    host = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")

    es_service = ElasticsearchService(
        index_name="test_workflows",
        embedding_dim=1024,
        cloud_id=cloud_id,
        api_key=api_key,
        host=host
    )

    # Create index
    es_service.create_index(delete_existing=True)

    # Test embedding service
    embedding_service = EmbeddingService(
        api_key=os.getenv("JINA_API_KEY"),
        model="jina-embeddings-v3"
    )

    # Index a test document (use retrieval.passage for indexing)
    test_doc = {
        "workflow_id": "test_1",
        "title": "Test Workflow",
        "task_type": "test",
        "description": "This is a test workflow",
        "tags": ["test"],
        "full_text": "Test Workflow: This is a test workflow for testing purposes",
        "embedding": embedding_service.embed(
            "Test Workflow: This is a test workflow",
            task="retrieval.passage"
        ),
        "rating": 4.5,
        "usage_count": 10
    }

    es_service.index_document("test_1", test_doc)
    print("Indexed test document")

    # Test search (use retrieval.query for search queries)
    query_text = "test workflow"
    query_embedding = embedding_service.embed(query_text, task="retrieval.query")
    results = es_service.hybrid_search(
        query_embedding=query_embedding,
        query_text=query_text,
        top_k=5
    )

    print(f"\nSearch results for '{query_text}':")
    for hit in results:
        print(f"  - {hit['_source']['title']} (score={hit['_score']:.2f})")
