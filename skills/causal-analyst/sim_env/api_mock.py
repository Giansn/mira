#!/usr/bin/env python3
"""Mock API layer for offline AEAP runs.
Provides deterministic, local responses to simulate LLM/API calls.
"""
import time
import hashlib

def mock_llm_call(model: str, prompt: str, max_tokens: int = 256, temperature: float = 0.0, seed: int = 0) -> dict:
    # deterministic pseudo-response based on prompt digest
    h = hashlib.sha256((prompt + str(seed)).encode()).hexdigest()[:8]
    content = f"Mock response ({model}) for prompt digest {h}."
    time.sleep(0.05)  # simulate tiny latency
    return {
        "choices": [ {"message": {"role": "assistant", "content": content}, "finish_reason": "stop"} ],
        "usage": {"prompt_tokens": 50, "completion_tokens": 120, "total_tokens": 170}
    }
