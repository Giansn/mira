"""
Context manager - prunes irrelevant history to reduce token usage.

No API calls made. Purely local context manipulation.
"""

from typing import Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class ContextEntry:
    content: str
    timestamp: float
    relevance_score: float = 1.0
    metadata: dict = field(default_factory=dict)


class ContextManager:
    """
    Manages context window by pruning irrelevant entries.

    Usage:
        cm = ContextManager(max_tokens=10000, relevance_threshold=0.5)
        cm.add("User asked about X")
        cm.add("User asked about Y")
        pruned = cm.prune()  # Removes low-relevance entries
    """

    def __init__(
        self,
        max_tokens: int = 10000,
        relevance_threshold: float = 0.5,
        keep_recent: int = 10,
        keep_critical: int = 5,
    ):
        self.max_tokens = max_tokens
        self.relevance_threshold = relevance_threshold
        self.keep_recent = keep_recent
        self.keep_critical = keep_critical
        self._entries: List[ContextEntry] = []
        self._lock = __import__("threading").Lock()

    def add(self, content: str, relevance_score: Optional[float] = None) -> None:
        """Add content to context with optional relevance score."""
        with self._lock:
            entry = ContextEntry(
                content=content,
                timestamp=datetime.now().timestamp(),
                relevance_score=relevance_score or 1.0,
            )
            self._entries.append(entry)

    def get(self) -> List[str]:
        """Get all context entries as strings."""
        with self._lock:
            return [e.content for e in self._entries]

    def prune(self) -> List[str]:
        """
        Prune context to fit within max_tokens.

        Keeps:
        1. Most recent entries (last keep_recent)
        2. High-relevance entries (>= relevance_threshold)
        3. Critical entries (relevance_score >= 1.0)

        Returns the pruned content.
        """
        with self._lock:
            if not self._entries:
                return []

            # Categorize entries
            critical = [e for e in self._entries if e.relevance_score >= 1.0]
            high_relevance = [e for e in self._entries if self.relevance_threshold <= e.relevance_score < 1.0]
            low_relevance = [e for e in self._entries if e.relevance_score < self.relevance_threshold]

            # Sort by timestamp (most recent first)
            critical.sort(key=lambda e: e.timestamp, reverse=True)
            high_relevance.sort(key=lambda e: e.timestamp, reverse=True)
            low_relevance.sort(key=lambda e: e.timestamp, reverse=True)

            # Keep critical + high relevance + recent low-relevance
            selected = critical + high_relevance

            # Add low-relevance entries only if they're very recent
            selected.extend(low_relevance[:self.keep_recent])

            # Estimate token count (rough: 1 token ≈ 4 chars for English)
            total_chars = sum(len(e.content) for e in selected)
            estimated_tokens = total_chars // 4

            # Prune until we fit within max_tokens
            while selected and estimated_tokens > self.max_tokens:
                # Remove lowest relevance entry from the end
                if low_relevance and low_relevance[-1] in selected:
                    selected.remove(low_relevance[-1])
                    low_relevance.pop()
                else:
                    # Remove from high_relevance if no low_relevance left
                    selected.pop()

                total_chars = sum(len(e.content) for e in selected)
                estimated_tokens = total_chars // 4

            # Update internal entries
            self._entries = selected

            return [e.content for e in selected]

    def clear(self) -> None:
        """Clear all context entries."""
        with self._lock:
            self._entries.clear()

    def get_stats(self) -> dict:
        """Get context statistics."""
        with self._lock:
            return {
                "total_entries": len(self._entries),
                "estimated_tokens": sum(len(e.content) for e in self._entries) // 4,
                "max_tokens": self.max_tokens,
                "relevance_threshold": self.relevance_threshold,
            }

    def mark_critical(self, index: int) -> None:
        """Mark a specific entry as critical (relevance_score = 1.0)."""
        with self._lock:
            if 0 <= index < len(self._entries):
                self._entries[index].relevance_score = 1.0
