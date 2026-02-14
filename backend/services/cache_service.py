"""
Simple in-memory cache for storing temporary session data.

Stores solutions between /api/estimate and /api/buy endpoints.
Cache is needed because:
1. /api/estimate returns solution summaries (no full workflows)
2. Agent picks one solution
3. /api/buy retrieves cached solution and returns full workflows
"""

from typing import Dict, Any, Optional


class CacheService:
    """
    Simple in-memory cache for session data.

    Stores solutions from /api/estimate so /api/buy can retrieve them.
    """

    def __init__(self):
        """Initialize in-memory cache."""
        self._cache: Dict[str, Any] = {}
        print("Using in-memory cache")

    def cache_solution(
        self,
        session_id: str,
        solutions: list
    ):
        """
        Cache solutions from estimate endpoint.

        Args:
            session_id: Session ID
            solutions: List of solution dicts
        """
        self._cache[f"session:{session_id}"] = solutions

    def get_solution(self, session_id: str) -> Optional[list]:
        """
        Retrieve cached solutions.

        Args:
            session_id: Session ID

        Returns:
            List of solutions or None if not found
        """
        return self._cache.get(f"session:{session_id}")

    def delete_solution(self, session_id: str):
        """Delete cached solution after purchase."""
        key = f"session:{session_id}"
        if key in self._cache:
            del self._cache[key]


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get singleton cache service instance."""
    global _cache_service

    if _cache_service is None:
        _cache_service = CacheService()

    return _cache_service


if __name__ == "__main__":
    # Test cache service
    cache = CacheService()

    # Test set/get
    cache.cache_solution("test_session", [{"solution_id": "sol_1"}])
    result = cache.get_solution("test_session")
    print(f"Cached solution: {result}")

    # Test delete
    cache.delete_solution("test_session")
    result = cache.get_solution("test_session")
    print(f"After delete: {result}")
