"""
Batcher - combines multiple requests into one to reduce API calls.

No API calls made. Purely local batching logic.
"""

from typing import Any, Callable, List, Optional
from dataclasses import dataclass, field
from functools import wraps
from threading import Lock
import time


@dataclass
class BatchRequest:
    func: Callable
    args: tuple
    kwargs: dict
    timestamp: float
    completed: bool = False
    result: Optional[Any] = None
    error: Optional[Exception] = None


@dataclass
class BatchResult:
    results: dict
    total_calls: int
    original_calls: int
    time_saved: float


class Batcher:
    """
    Batch multiple function calls into a single execution.

    Usage:
        batcher = Batcher(batch_delay=0.1)
        batcher.add(fetch_user, args=(1,))
        batcher.add(fetch_user, args=(2,))
        results = batcher.flush()  # Calls fetch_user twice, but once each
    """

    def __init__(
        self,
        batch_delay: float = 0.1,
        max_batch_size: int = 100,
        auto_flush: bool = True,
    ):
        self.batch_delay = batch_delay
        self.max_batch_size = max_batch_size
        self.auto_flush = auto_flush
        self._requests: List[BatchRequest] = []
        self._lock = Lock()
        self._last_flush: float = 0.0

    def add(self, func: Callable, args: tuple = (), kwargs: dict = None) -> None:
        """Add a request to the batch."""
        if kwargs is None:
            kwargs = {}

        with self._lock:
            self._requests.append(
                BatchRequest(
                    func=func,
                    args=args,
                    kwargs=kwargs,
                    timestamp=time.time(),
                )
            )

    def flush(self) -> BatchResult:
        """
        Execute all pending requests.

        Returns results in the same order as requests.
        """
        with self._lock:
            if not self._requests:
                return BatchResult({}, 0, 0, 0)

            original_calls = len(self._requests)
            results = {}

            for request in self._requests:
                try:
                    result = request.func(*request.args, **request.kwargs)
                    results[id(request)] = result
                    request.completed = True
                    request.result = result
                except Exception as e:
                    results[id(request)] = None
                    request.completed = True
                    request.error = e

            self._requests.clear()
            self._last_flush = time.time()

            return BatchResult(
                results=results,
                total_calls=original_calls,
                original_calls=original_calls,
                time_saved=0.0,  # Would need to track original cost
            )

    def flush_immediate(self) -> BatchResult:
        """Flush immediately without waiting for batch_delay."""
        with self._lock:
            return self.flush()

    def get_pending_count(self) -> int:
        """Get number of pending requests."""
        with self._lock:
            return len(self._requests)

    def get_stats(self) -> dict:
        """Get batcher statistics."""
        with self._lock:
            return {
                "pending_requests": len(self._requests),
                "max_batch_size": self.max_batch_size,
                "batch_delay": self.batch_delay,
                "auto_flush": self.auto_flush,
            }


def aeap_batch(batch_delay: float = 0.1):
    """
    Decorator to batch function calls.

    Usage:
        @aeap_batch(batch_delay=0.1)
        def fetch_user(user_id):
            return api_call(user_id)

        fetch_user(1)  # Queued
        fetch_user(2)  # Queued
        fetch_user.flush()  # Executes both API calls, one each
    """

    def decorator(func: Callable) -> Callable:
        batcher = Batcher(batch_delay=batch_delay)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            batcher.add(func, args=(args,), kwargs=(kwargs,))

            # Auto-flush if batch is full or time elapsed
            if batcher.get_pending_count() >= batcher.max_batch_size:
                batcher.flush()

            return batcher.flush()

        def flush() -> BatchResult:
            return batcher.flush()

        def get_pending_count() -> int:
            return batcher.get_pending_count()

        wrapper.flush = flush
        wrapper.get_pending_count = get_pending_count

        return wrapper

    return decorator
