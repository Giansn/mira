#!/usr/bin/env python3
# telclaw_utils/metrics.py
import time
import threading
import statistics
from typing import Dict, Any, Optional

class APIUsageMetrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.requests = 0
            self.successful_requests = 0
            self.error_requests = 0
            self.response_times_ms = []  # list of latencies in ms
            self.token_usage_in = 0
            self.token_usage_out = 0
            self.start_time = time.time()

    def record_request(
        self,
        start_time: float,
        success: bool,
        error_code: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ):
        with self._lock:
            self.requests += 1
            duration_ms = (time.time() - start_time) * 1000
            self.response_times_ms.append(duration_ms)

            if success:
                self.successful_requests += 1
            else:
                self.error_requests += 1

            self.token_usage_in += int(input_tokens)
            self.token_usage_out += int(output_tokens)

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            total_time_sec = time.time() - self.start_time
            avg_rt = statistics.mean(self.response_times_ms) if self.response_times_ms else 0.0
            p95 = (
                sorted(self.response_times_ms)[int(len(self.response_times_ms) * 0.95)]
                if len(self.response_times_ms) > 0
                else avg_rt
            )
            success_rate = (self.successful_requests / self.requests * 100) if self.requests else 0.0
            error_rate = (self.error_requests / self.requests * 100) if self.requests else 0.0

            return {
                "total_requests": self.requests,
                "successful_requests": self.successful_requests,
                "error_requests": self.error_requests,
                "success_rate_percent": round(success_rate, 2),
                "error_rate_percent": round(error_rate, 2),
                "avg_response_time_ms": round(avg_rt, 2),
                "p95_response_time_ms": round(p95, 2),
                "total_tokens_in": self.token_usage_in,
                "total_tokens_out": self.token_usage_out,
                "total_session_time_sec": round(total_time_sec, 2),
            }

    def reset_to(self, other: 'APIUsageMetrics'):
        # Not used in MVP; provided for completeness
        with self._lock:
            self.requests = other.requests
            self.successful_requests = other.successful_requests
            self.error_requests = other.error_requests
            self.response_times_ms = list(other.response_times_ms)
            self.token_usage_in = other.token_usage_in
            self.token_usage_out = other.token_usage_out
            self.start_time = other.start_time
