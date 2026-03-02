"""
Audit log - tracks all API calls with cost, purpose, and result.

No API calls made. Purely local logging.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any
from threading import Lock


@dataclass
class AuditEntry:
    timestamp: float
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    purpose: str
    success: bool
    error: Optional[str] = None
    cache_hit: bool = False
    batched_with: Optional[int] = None


class AuditLog:
    """
    Log all API calls for analysis and optimization.

    Usage:
        audit = AuditLog(log_file="api_calls.log")
        audit.log_call(
            model="gpt-4",
            tokens_in=100,
            tokens_out=50,
            cost=0.01,
            purpose="user_query"
        )
    """

    def __init__(self, log_file: Optional[str] = None, max_entries: int = 10000):
        self.log_file = log_file or os.path.join(
            os.path.expanduser("~/.aeap_cache"),
            "audit_log.json"
        )
        self.max_entries = max_entries
        self._entries: List[AuditEntry] = []
        self._lock = Lock()

        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log_call(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost: float,
        purpose: str,
        success: bool = True,
        error: Optional[str] = None,
        cache_hit: bool = False,
        batched_with: Optional[int] = None,
    ) -> None:
        """Log an API call."""
        entry = AuditEntry(
            timestamp=datetime.now().timestamp(),
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            purpose=purpose,
            success=success,
            error=error,
            cache_hit=cache_hit,
            batched_with=batched_with,
        )

        with self._lock:
            self._entries.append(entry)

            # Trim to max_entries
            if len(self._entries) > self.max_entries:
                self._entries = self._entries[-self.max_entries:]

            # Write to file
            self._write_to_file()

    def get_entries(
        self,
        model: Optional[str] = None,
        purpose: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[AuditEntry]:
        """Get audit entries with optional filters."""
        with self._lock:
            entries = self._entries.copy()

            if model:
                entries = [e for e in entries if e.model == model]
            if purpose:
                entries = [e for e in entries if e.purpose == purpose]
            if limit:
                entries = entries[-limit:]

            return entries

    def get_stats(self) -> dict:
        """Get audit statistics."""
        with self._lock:
            total_calls = len(self._entries)
            total_cost = sum(e.cost for e in self._entries)
            total_tokens_in = sum(e.tokens_in for e in self._entries)
            total_tokens_out = sum(e.tokens_out for e in self._entries)
            success_rate = (
                sum(1 for e in self._entries if e.success) / total_calls
                if total_calls > 0
                else 0
            )
            cache_hit_rate = (
                sum(1 for e in self._entries if e.cache_hit) / total_calls
                if total_calls > 0
                else 0
            )

            # Group by purpose
            purpose_stats = {}
            for e in self._entries:
                purpose = e.purpose
                if purpose not in purpose_stats:
                    purpose_stats[purpose] = {
                        "count": 0,
                        "cost": 0.0,
                        "tokens_in": 0,
                        "tokens_out": 0,
                    }
                purpose_stats[purpose]["count"] += 1
                purpose_stats[purpose]["cost"] += e.cost
                purpose_stats[purpose]["tokens_in"] += e.tokens_in
                purpose_stats[purpose]["tokens_out"] += e.tokens_out

            return {
                "total_calls": total_calls,
                "total_cost": total_cost,
                "total_tokens_in": total_tokens_in,
                "total_tokens_out": total_tokens_out,
                "success_rate": success_rate,
                "cache_hit_rate": cache_hit_rate,
                "purpose_stats": purpose_stats,
            }

    def reset(self) -> None:
        """Clear all audit entries."""
        with self._lock:
            self._entries.clear()
            self._write_to_file()

    def _write_to_file(self) -> None:
        """Write entries to file."""
        try:
            with open(self.log_file, "w") as f:
                json.dump(
                    [e.__dict__ for e in self._entries],
                    f,
                    indent=2,
                    default=str,
                )
        except Exception:
            pass

    def export_csv(self, filepath: str) -> None:
        """Export audit log to CSV."""
        import csv

        with self._lock:
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "model", "tokens_in", "tokens_out",
                    "cost", "purpose", "success", "error", "cache_hit", "batched_with"
                ])

                for e in self._entries:
                    writer.writerow([
                        e.timestamp,
                        e.model,
                        e.tokens_in,
                        e.tokens_out,
                        e.cost,
                        e.purpose,
                        e.success,
                        e.error,
                        e.cache_hit,
                        e.batched_with,
                    ])
