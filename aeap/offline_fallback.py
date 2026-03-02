"""
Offline fallback - use local execution when possible, API only when necessary.

No API calls made during fallback checks. Purely local logic.
"""

from typing import Any, Callable, Optional
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os


@dataclass
class FallbackRule:
    name: str
    local_func: Callable
    api_func: Callable
    conditions: Optional[callable] = None
    ttl: Optional[float] = None
    enabled: bool = True


class OfflineFallback:
    """
    Execute local function first, fall back to API if needed.

    Usage:
        fallback = OfflineFallback()
        result = fallback.execute(
            local_func=my_local_logic,
            api_func=expensive_api_call,
            conditions=lambda: should_use_api()
        )
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or os.path.join(
            os.path.expanduser("~/.aeap_cache"),
            "fallbacks"
        )
        os.makedirs(self.cache_dir, exist_ok=True)

        self._rules: dict[str, FallbackRule] = {}
        self._lock = __import__("threading").Lock()

    def register(
        self,
        name: str,
        local_func: Callable,
        api_func: Callable,
        conditions: Optional[callable] = None,
        ttl: Optional[float] = None,
    ) -> None:
        """Register a fallback rule."""
        with self._lock:
            self._rules[name] = FallbackRule(
                name=name,
                local_func=local_func,
                api_func=api_func,
                conditions=conditions,
                ttl=ttl,
            )

    def execute(
        self,
        name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute fallback rule.

        Returns local result if available and conditions met.
        Otherwise returns API result.
        """
        with self._lock:
            rule = self._rules.get(name)
            if not rule:
                raise ValueError(f"Rule '{name}' not found")

            if not rule.enabled:
                return rule.api_func(*args, **kwargs)

            # Try local function first
            try:
                result = rule.local_func(*args, **kwargs)

                # Check conditions
                if rule.conditions and not rule.conditions(result):
                    return rule.api_func(*args, **kwargs)

                # Cache result if TTL is set
                if rule.ttl:
                    self._cache_result(name, result, rule.ttl)

                return result

            except Exception as e:
                # Local failed, try API
                try:
                    return rule.api_func(*args, **kwargs)
                except Exception as api_error:
                    raise api_error

    def get_stats(self) -> dict:
        """Get fallback statistics."""
        with self._lock:
            return {
                "total_rules": len(self._rules),
                "enabled_rules": sum(1 for r in self._rules.values() if r.enabled),
                "cache_dir": self.cache_dir,
            }

    def _cache_result(self, name: str, result: Any, ttl: float) -> None:
        """Cache result locally."""
        cache_file = os.path.join(self.cache_dir, f"{name}.json")
        cache_data = {
            "result": result,
            "timestamp": datetime.now().timestamp(),
            "ttl": ttl,
        }

        try:
            with open(cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception:
            pass

    def _get_cached_result(self, name: str) -> Optional[Any]:
        """Get cached result if valid."""
        cache_file = os.path.join(self.cache_dir, f"{name}.json")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)

            # Check TTL
            if cache_data["ttl"]:
                age = datetime.now().timestamp() - cache_data["timestamp"]
                if age > cache_data["ttl"]:
                    return None

            return cache_data["result"]

        except Exception:
            return None

    def disable(self, name: str) -> None:
        """Disable a specific rule."""
        with self._lock:
            if name in self._rules:
                self._rules[name].enabled = False

    def enable(self, name: str) -> None:
        """Enable a specific rule."""
        with self._lock:
            if name in self._rules:
                self._rules[name].enabled = True

    def clear_cache(self, name: Optional[str] = None) -> None:
        """Clear cache for a specific rule or all rules."""
        if name:
            cache_file = os.path.join(self.cache_dir, f"{name}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
        else:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
