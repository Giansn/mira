"""
Lazy executor - defers API calls until value is needed.

No API calls made during setup. API call happens only when value is accessed.
"""

from typing import Any, Callable, Optional
from functools import wraps
from dataclasses import dataclass, field
from threading import Lock
import time


@dataclass
class LazyValue:
    _value: Optional[Any] = None
    _called: bool = False
    _error: Optional[Exception] = None
    _timestamp: float = 0.0
    _cache_key: Optional[str] = None


def aeap_lazy(cache_key: Optional[str] = None):
    """
    Decorator to defer execution until value is needed.

    Usage:
        @aeap_lazy(cache_key="user_profile")
        def fetch_user_profile(user_id):
            # This only runs when get() is called
            return expensive_api_call(user_id)

        profile = fetch_user_profile(123)  # API call happens here
    """

    def decorator(func: Callable) -> Callable:
        lazy_value = LazyValue(_cache_key=cache_key)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Return cached value if available
            if lazy_value._called and lazy_value._value is not None:
                return lazy_value._value

            # Return error if previously failed
            if lazy_value._error is not None:
                raise lazy_value._error

            # Execute function
            try:
                result = func(*args, **kwargs)
                lazy_value._value = result
                lazy_value._called = True
                lazy_value._timestamp = time.time()
                return result
            except Exception as e:
                lazy_value._error = e
                raise

        def invalidate() -> None:
            """Force re-execution on next access."""
            lazy_value._called = False
            lazy_value._value = None
            lazy_value._error = None

        def get_cached() -> Optional[Any]:
            """Get cached value without re-executing."""
            if lazy_value._called:
                return lazy_value._value
            return None

        def is_ready() -> bool:
            """Check if value has been cached."""
            return lazy_value._called and lazy_value._value is not None

        wrapper.invalidate = invalidate
        wrapper.get_cached = get_cached
        wrapper.is_ready = is_ready

        return wrapper

    return decorator


class LazyExecutor:
    """
    Manage lazy-executed values.

    Usage:
        executor = LazyExecutor()
        profile = executor.execute(fetch_user_profile, args=(123,), cache_key="user_profile")
        profile.get()  # API call happens here
    """

    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self._cache: dict[str, LazyValue] = {}
        self._lock = Lock()

    def execute(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        cache_key: Optional[str] = None,
    ) -> LazyValue:
        """
        Schedule execution of a function. Returns immediately without calling func.

        The function is only called when get() is invoked.
        """
        if kwargs is None:
            kwargs = {}

        if cache_key and self.cache_enabled:
            with self._lock:
                if cache_key in self._cache:
                    return self._cache[cache_key]

        lazy_value = LazyValue(_cache_key=cache_key)

        # Execute in background
        def run():
            try:
                result = func(*args, **kwargs)
                lazy_value._value = result
                lazy_value._called = True
                lazy_value._timestamp = time.time()

                if cache_key and self.cache_enabled:
                    with self._lock:
                        self._cache[cache_key] = lazy_value
            except Exception as e:
                lazy_value._error = e

        import threading
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        return lazy_value

    def get(self, lazy_value: LazyValue) -> Any:
        """Get value, executing if not already cached."""
        if lazy_value._called:
            return lazy_value._value
        raise lazy_value._error or RuntimeError("Value not yet available")

    def invalidate(self, cache_key: Optional[str] = None) -> None:
        """Invalidate cached value(s)."""
        if cache_key:
            with self._lock:
                if cache_key in self._cache:
                    del self._cache[cache_key]
        else:
            with self._lock:
                self._cache.clear()

    def get_stats(self) -> dict:
        """Get executor statistics."""
        with self._lock:
            cached_count = sum(1 for v in self._cache.values() if v._called)
            return {
                "cached_values": cached_count,
                "cache_enabled": self.cache_enabled,
            }
