"""
Elasticsearch service for workflow indexing and search.
Handles all Elasticsearch operations including kNN vector search.
"""

from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticsearchService:
    """Service for Elasticsearch operations."""

    def __init__(
        self,
        host: str,
        index_name: str,
        embedding_dim: int = 1024,
        username: str = "",
        password: str = ""
    ):
        """
        Initialize Elasticsearch service.

        Args:
            host: Elasticsearch host URL
            index_name: Name of the index
            embedding_dim: Dimension of embedding vectors
            username: Optional username for authentication
            password: Optional password for authentication
        """
        # Build connection config
        es_config = {"hosts": [host]}

        if username and password:
            es_config["basic_auth"] = (username, password)

        self.es = Elasticsearch(**es_config)
        self.index_name = index_name
        self.embedding_dim = embedding_dim

        # Test connection
        if not self.es.ping():
            raise ConnectionError(f"Failed to connect to Elasticsearch at {host}")

        print(f"Connected to Elasticsearch at {host}")
        print(f"Index: {index_name}")

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

                    # Metrics
                    "token_cost": {"type": "integer"},
                    "execution_tokens": {"type": "integer"},
                    "rating": {"type": "float"},
                    "usage_count": {"type": "integer"},

                    # Workflow content
                    "requirements": {"type": "text"},
                    "steps": {
                        "type": "nested",
                        "properties": {
                            "step": {"type": "integer"},
                            "thought": {"type": "text"},
                            "action": {"type": "text"},
                            "context": {"type": "text"},
                            "dependencies": {"type": "integer"}
                        }
                    },
                    "edge_cases": {"type": "text"},
                    "domain_knowledge": {"type": "text"},

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

                    # Vector embedding for semantic search
                    "embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dim,
                        "index": True,
                        "similarity": "cosine"
                    },

                    # Full text representation
                    "full_text": {"type": "text"},
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "index": {
                    "knn": True  # Enable k-NN search
                }
            }
        }

        # Create index
        self.es.indices.create(index=self.index_name, body=mappings)
        print(f"Created index: {self.index_name}")

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

        success, failed = bulk(self.es, generate_actions())
        print(f"Indexed {success} documents, {len(failed)} failed")

        if failed:
            print("Failed documents:", failed)

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
            "num_candidates": top_k * 5  # Search more candidates for better results
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

    def delete_index(self):
        """Delete the index."""
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            print(f"Deleted index: {self.index_name}")


# Example usage
if __name__ == "__main__":
    import os
    from embedding_service import EmbeddingService

    # Initialize services
    es_service = ElasticsearchService(
        host=os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200"),
        index_name="test_workflows",
        embedding_dim=1024
    )

    # Create index
    es_service.create_index(delete_existing=True)

    # Test embedding service
    embedding_service = EmbeddingService(
        api_key=os.getenv("JINA_API_KEY"),
        model="jina-embeddings-v3"
    )

    # Index a test document
    test_doc = {
        "workflow_id": "test_1",
        "title": "Test Workflow",
        "task_type": "test",
        "description": "This is a test workflow",
        "tags": ["test"],
        "full_text": "Test Workflow: This is a test workflow for testing purposes",
        "embedding": embedding_service.embed("Test Workflow: This is a test workflow"),
        "rating": 4.5,
        "usage_count": 10
    }

    es_service.index_document("test_1", test_doc)
    print("Indexed test document")

    # Test search
    query_text = "test workflow"
    query_embedding = embedding_service.embed(query_text)
    results = es_service.hybrid_search(
        query_embedding=query_embedding,
        query_text=query_text,
        top_k=5
    )

    print(f"\nSearch results for '{query_text}':")
    for hit in results:
        print(f"  - {hit['_source']['title']} (score={hit['_score']:.2f})")
