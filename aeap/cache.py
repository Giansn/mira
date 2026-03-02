"""
Cache module - reduces API calls by reusing results.

Uses local memory cache with TTL and automatic cleanup.
"""

import time
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: float
    hits: int = 0


class Cache:
    """
    Simple in-memory cache with TTL.

    Usage:
        cache = Cache(default_ttl=3600)
        cache.set("key", value)
        value = cache.get("key")  # returns None if expired or not found
    """

    def __init__(self, default_ttl: float = 3600, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._store: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Store value in cache with optional TTL."""
        with self._lock:
            if len(self._store) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self._store.keys(), key=lambda k: self._store[k].timestamp)
                del self._store[oldest_key]

            self._store[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl,
            )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if valid. Returns None if expired or not found."""
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None

            # Check TTL
            if time.time() - entry.timestamp > entry.ttl:
                del self._store[key]
                return None

            entry.hits += 1
            return entry.value

    def delete(self, key: str) -> None:
        """Remove key from cache."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._store.clear()

    def get_stats(self) -> dict:
        """Return cache statistics."""
        with self._lock:
            total_hits = sum(e.hits for e in self._store.values())
            total_entries = len(self._store)
            return {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "total_misses": max(0, total_entries - total_hits),
            }

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns number of removed entries."""
        with self._lock:
            now = time.time()
            expired_keys = [
                k for k, e in self._store.items() if now - e.timestamp > e.ttl
            ]
            for key in expired_keys:
                del self._store[key]
            return len(expired_keys)
