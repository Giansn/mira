"""
AEAP - Efficient API Economy Protocol

A local optimization layer that reduces API usage through:
- Caching
- Lazy evaluation
- Batching
- Context pruning
- Offline fallbacks
- Cost tracking

AEAP is designed to REDUCE API calls, not increase them.
"""

from .cache import Cache
from .cost_tracker import CostTracker
from .context_manager import ContextManager
from .lazy_executor import LazyExecutor
from .batcher import Batcher
from .offline_fallback import OfflineFallback
from .audit_log import AuditLog

__version__ = "0.1.0"
__all__ = [
    "Cache",
    "CostTracker",
    "ContextManager",
    "LazyExecutor",
    "Batcher",
    "OfflineFallback",
    "AuditLog",
]
