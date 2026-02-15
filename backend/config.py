"""
Configuration module for initializing all services.
Loads environment variables and provides singleton service instances.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for all service settings."""

    # Anthropic Claude Settings
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
    CLAUDE_MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))

    # Jina AI Settings
    JINA_API_KEY: str = os.getenv("JINA_API_KEY", "")
    JINA_MODEL: str = os.getenv("JINA_MODEL", "jina-embeddings-v3")
    JINA_EMBEDDING_DIM: int = int(os.getenv("JINA_EMBEDDING_DIM", "1024"))

    # Elasticsearch Settings (Cloud ID + API Key recommended for Elastic Cloud)
    ELASTIC_CLOUD_ID: str = os.getenv("ELASTIC_CLOUD_ID", "")
    ELASTIC_API_KEY: str = os.getenv("ELASTIC_API_KEY", "")
    ELASTIC_INDEX_NAME: str = os.getenv("ELASTIC_INDEX_NAME", "workflow_marketplace")

    # Legacy settings (for local/self-hosted ES)
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    ELASTICSEARCH_INDEX: str = os.getenv("ELASTIC_INDEX_NAME", os.getenv("ELASTICSEARCH_INDEX", "workflow_marketplace"))
    ELASTICSEARCH_USERNAME: str = os.getenv("ELASTICSEARCH_USERNAME", "")
    ELASTICSEARCH_PASSWORD: str = os.getenv("ELASTICSEARCH_PASSWORD", "")

    # Cache Settings (use Redis in production)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour

    # Flask Settings
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True") == "True"

    # Search Algorithm Parameters
    SCORE_THRESHOLD_GOOD: float = float(os.getenv("SCORE_THRESHOLD_GOOD", "0.85"))
    SCORE_IMPROVEMENT_EPSILON: float = float(os.getenv("SCORE_IMPROVEMENT_EPSILON", "0.1"))
    MAX_RECURSION_DEPTH: int = int(os.getenv("MAX_RECURSION_DEPTH", "2"))
    SUBTASKS_MIN: int = int(os.getenv("SUBTASKS_MIN", "2"))
    SUBTASKS_MAX: int = int(os.getenv("SUBTASKS_MAX", "8"))

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        errors = []

        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is not set")

        if not cls.JINA_API_KEY:
            errors.append("JINA_API_KEY is not set")

        # Check that either Cloud ID or Host is set for Elasticsearch
        if not cls.ELASTIC_CLOUD_ID and not cls.ELASTICSEARCH_HOST:
            errors.append("Neither ELASTIC_CLOUD_ID nor ELASTICSEARCH_HOST is set")

        # If Cloud ID is used, API key is required
        if cls.ELASTIC_CLOUD_ID and not cls.ELASTIC_API_KEY:
            errors.append("ELASTIC_CLOUD_ID is set but ELASTIC_API_KEY is missing")

        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True


# Singleton instances (lazy loaded)
_claude_service: Optional['ClaudeService'] = None
_embedding_service: Optional['EmbeddingService'] = None
_elasticsearch_service: Optional['ElasticsearchService'] = None


def get_claude_service():
    """Get singleton instance of ClaudeService."""
    global _claude_service

    if _claude_service is None:
        from services.claude_service import ClaudeService
        _claude_service = ClaudeService(
            api_key=Config.ANTHROPIC_API_KEY,
            model=Config.CLAUDE_MODEL,
            max_tokens=Config.CLAUDE_MAX_TOKENS
        )

    return _claude_service


def get_embedding_service():
    """Get singleton instance of EmbeddingService."""
    global _embedding_service

    if _embedding_service is None:
        from services.embedding_service import EmbeddingService
        _embedding_service = EmbeddingService(
            api_key=Config.JINA_API_KEY,
            model=Config.JINA_MODEL,
            embedding_dim=Config.JINA_EMBEDDING_DIM
        )

    return _embedding_service


def get_elasticsearch_service():
    """Get singleton instance of ElasticsearchService."""
    global _elasticsearch_service

    if _elasticsearch_service is None:
        from services.elasticsearch_service import ElasticsearchService

        # Prefer ELASTIC_CLOUD_ID if set, otherwise fall back to ELASTICSEARCH_HOST
        index_name = Config.ELASTIC_INDEX_NAME or Config.ELASTICSEARCH_INDEX

        _elasticsearch_service = ElasticsearchService(
            index_name=index_name,
            embedding_dim=Config.JINA_EMBEDDING_DIM,
            cloud_id=Config.ELASTIC_CLOUD_ID,
            api_key=Config.ELASTIC_API_KEY,
            host=Config.ELASTICSEARCH_HOST,
            username=Config.ELASTICSEARCH_USERNAME,
            password=Config.ELASTICSEARCH_PASSWORD
        )

    return _elasticsearch_service


def initialize_services():
    """
    Initialize all services and validate configuration.
    Call this at application startup.
    """
    print("Initializing services...")

    # Validate configuration
    if not Config.validate():
        raise ValueError("Configuration validation failed. Check .env file.")

    # Initialize services
    claude_service = get_claude_service()
    embedding_service = get_embedding_service()
    es_service = get_elasticsearch_service()

    print("✓ Claude service initialized")
    print("✓ Embedding service initialized")
    print("✓ Elasticsearch service initialized")

    return {
        "claude_service": claude_service,
        "embedding_service": embedding_service,
        "elasticsearch_service": es_service
    }


if __name__ == "__main__":
    # Test configuration
    Config.validate()
    print("\nConfiguration:")
    print(f"  Claude Model: {Config.CLAUDE_MODEL}")
    print(f"  Jina Model: {Config.JINA_MODEL}")
    print(f"  Jina Embedding Dim: {Config.JINA_EMBEDDING_DIM}")

    # Show Elasticsearch config (cloud or self-hosted)
    if Config.ELASTIC_CLOUD_ID:
        print(f"  Elasticsearch: Cloud (ID: {Config.ELASTIC_CLOUD_ID[:20]}...)")
        print(f"  Elasticsearch Index: {Config.ELASTIC_INDEX_NAME}")
    else:
        print(f"  Elasticsearch Host: {Config.ELASTICSEARCH_HOST}")
        print(f"  Elasticsearch Index: {Config.ELASTICSEARCH_INDEX}")

    print(f"\nAlgorithm Parameters:")
    print(f"  Score Threshold: {Config.SCORE_THRESHOLD_GOOD}")
    print(f"  Improvement Epsilon: {Config.SCORE_IMPROVEMENT_EPSILON}")
    print(f"  Max Recursion Depth: {Config.MAX_RECURSION_DEPTH}")
    print(f"  Subtasks Range: {Config.SUBTASKS_MIN}-{Config.SUBTASKS_MAX}")
