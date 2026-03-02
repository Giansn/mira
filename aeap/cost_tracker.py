"""
Cost tracker - monitors and tracks API costs.

No API calls made. Purely local tracking.
"""

import time
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


@dataclass
class CostRecord:
    call_count: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_cost: float = 0.0
    errors: int = 0
    last_called: Optional[float] = None


class CostTracker:
    """
    Track API costs without making API calls.

    Usage:
        tracker = CostTracker()
        tracker.record_call(tokens_in=100, tokens_out=50, cost=0.01)
        print(tracker.get_total_cost())
    """

    def __init__(self, budget: Optional[float] = None, warn_threshold: float = 0.8):
        self.budget = budget
        self.warn_threshold = warn_threshold
        self._records: dict[str, CostRecord] = defaultdict(CostRecord)
        self._total: CostRecord = CostRecord()
        self._lock = __import__("threading").Lock()

    def record_call(
        self,
        model: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Record an API call's cost and token usage."""
        with self._lock:
            if model not in self._records:
                self._records[model] = CostRecord()

            record = self._records[model]
            record.call_count += 1
            record.total_tokens_in += tokens_in
            record.total_tokens_out += tokens_out
            record.total_cost += cost
            record.last_called = time.time()

            self._total.call_count += 1
            self._total.total_tokens_in += tokens_in
            self._total.total_tokens_out += tokens_out
            self._total.total_cost += cost

            # Warn if budget is exceeded
            if self.budget and self._total.total_cost > self.budget * self.warn_threshold:
                self._warn_budget(model, record)

    def get_record(self, model: str) -> CostRecord:
        """Get cost record for a specific model."""
        return self._records[model]

    def get_total(self) -> CostRecord:
        """Get total cost record across all models."""
        return self._total

    def get_stats(self) -> dict:
        """Get overall statistics."""
        with self._lock:
            total = self._total
            models = {
                model: {
                    "call_count": r.call_count,
                    "tokens_in": r.total_tokens_in,
                    "tokens_out": r.total_tokens_out,
                    "cost": r.total_cost,
                    "errors": r.errors,
                }
                for model, r in self._records.items()
            }

            return {
                "total_cost": total.total_cost,
                "total_calls": total.call_count,
                "total_tokens_in": total.total_tokens_in,
                "total_tokens_out": total.total_tokens_out,
                "models": models,
                "budget": self.budget,
                "budget_used": total.total_cost / self.budget if self.budget else None,
            }

    def reset(self, model: Optional[str] = None) -> None:
        """Reset cost tracking. If model is None, resets all models."""
        with self._lock:
            if model:
                self._records[model] = CostRecord()
            else:
                self._records.clear()
                self._total = CostRecord()

    def _warn_budget(self, model: str, record: CostRecord) -> None:
        """Warn when budget threshold is reached."""
        budget_pct = (self._total.total_cost / self.budget) * 100
        print(
            f"[AEAP] Budget warning: {budget_pct:.1f}% used "
            f"({self._total.total_cost:.4f}/{self.budget:.4f}) "
            f"on model '{model}'"
        )
