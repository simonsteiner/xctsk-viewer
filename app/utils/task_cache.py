"""Simple in-memory cache for task data to avoid repeated downloads."""

import threading
import time
from typing import Any, Dict, Optional


class TaskCache:
    """Simple in-memory cache with time-based expiration."""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        """Initialize the cache.

        Args:
            default_ttl: Default time-to-live for cache entries in seconds
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get an item from cache if it exists and hasn't expired.

        Args:
            key: Cache key to look up

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            if time.time() > entry["expires_at"]:
                # Entry has expired, remove it
                del self._cache[key]
                return None

            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set an item in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl

        with self._lock:
            self._cache[key] = {"value": value, "expires_at": time.time() + ttl}

    def delete(self, key: str) -> bool:
        """Delete an item from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if item was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key
                for key, entry in self._cache.items()
                if current_time > entry["expires_at"]
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    def size(self) -> int:
        """Get the current number of cached items."""
        with self._lock:
            return len(self._cache)


# Global cache instance
_task_cache = TaskCache()


def get_task_cache() -> TaskCache:
    """Get the global task cache instance."""
    return _task_cache
