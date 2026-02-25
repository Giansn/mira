#!/usr/bin/env python3
"""Bias Check — detect decision skew across seeds."""
from collections import Counter

def bias_check(runs):
    """Compare decision distributions across seeds.
    Flag if any seed deviates >2x from mean."""
    seed_decisions = {}
    for r in runs:
        s = r.get("seed")
        d = r.get("status", "unknown")
        seed_decisions.setdefault(s, []).append(d)

    seed_dist = {}
    for s, decisions in seed_decisions.items():
        seed_dist[s] = dict(Counter(decisions))

    total_counts = Counter(r.get("status", "unknown") for r in runs)
    n = len(runs) or 1
    mean_rates = {k: v / n for k, v in total_counts.items()}

    flagged = []
    for s, dist in seed_dist.items():
        seed_n = sum(dist.values()) or 1
        for status, count in dist.items():
            rate = count / seed_n
            mean = mean_rates.get(status, 0)
            if mean > 0 and rate > mean * 2:
                flagged.append({"seed": s, "status": status, "rate": round(rate, 3), "mean": round(mean, 3)})

    return {
        "total_runs": len(runs),
        "seed_distribution": seed_dist,
        "decision_skew": dict(total_counts),
        "flagged_seeds": flagged
    }
