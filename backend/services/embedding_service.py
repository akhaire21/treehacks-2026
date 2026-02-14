"""
Embedding service using Jina AI API.
Handles text-to-vector conversion for semantic search.
"""

import requests
from typing import List, Union
import numpy as np


class EmbeddingService:
    """Service for generating embeddings using Jina AI."""

    def __init__(
        self,
        api_key: str,
        model: str = "jina-embeddings-v3",
        embedding_dim: int = 1024
    ):
        """
        Initialize Jina embedding service.

        Args:
            api_key: Jina AI API key
            model: Jina model name
            embedding_dim: Dimension of embedding vectors
        """
        self.api_key = api_key
        self.model = model
        self.embedding_dim = embedding_dim
        self.api_url = "https://api.jina.ai/v1/embeddings"

        print(f"Initialized EmbeddingService with model: {model}")

    def embed(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text input(s).

        Args:
            text: Single text string or list of text strings

        Returns:
            Single embedding vector or list of embedding vectors
        """
        # Ensure text is a list
        is_single = isinstance(text, str)
        texts = [text] if is_single else text

        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": texts,
            "encoding_type": "float"
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            embeddings = [item["embedding"] for item in result["data"]]

            # Return single vector or list of vectors based on input
            return embeddings[0] if is_single else embeddings

        except requests.exceptions.RequestException as e:
            print(f"Error generating embeddings: {e}")
            raise

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for large batches of text with batching.

        Args:
            texts: List of text strings
            batch_size: Number of texts to process per batch

        Returns:
            List of embedding vectors
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.embed(batch)
            all_embeddings.extend(embeddings)

            print(f"Processed batch {i // batch_size + 1}/{(len(texts) - 1) // batch_size + 1}")

        return all_embeddings

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Cosine similarity score (0 to 1)
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))


# Example usage
if __name__ == "__main__":
    import os

    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        print("Error: JINA_API_KEY not set")
        exit(1)

    # Initialize service
    service = EmbeddingService(api_key=api_key)

    # Test single embedding
    text = "File Ohio 2024 taxes with W2 and itemized deductions"
    embedding = service.embed(text)
    print(f"Generated embedding with {len(embedding)} dimensions")

    # Test batch embedding
    texts = [
        "File Ohio 2024 taxes",
        "Plan Tokyo family trip",
        "Parse Stripe invoice"
    ]
    embeddings = service.embed_batch(texts, batch_size=2)
    print(f"Generated {len(embeddings)} embeddings")

    # Test similarity
    similarity = service.cosine_similarity(embeddings[0], embeddings[1])
    print(f"Similarity between Ohio taxes and Tokyo trip: {similarity:.3f}")
