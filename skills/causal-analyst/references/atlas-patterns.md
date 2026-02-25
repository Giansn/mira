# Atlas Patterns — Mapped to Phase 4 MVP

## Pattern → Component Mapping

| Pattern | Atlas Component | Status | Priority |
|---|---|---|---|
| Orchestrator/Director | SimEnv Controller + phase_hooks | Scaffold | P0 |
| Persona Module | PersonaConfig for Mirror | New | P1 |
| Evaluator-Generator Split | MirrorAgent interface | New | P0 |
| Memory Stream | Audit Trail (append-only JSONL) | Done | P0 |
| Reflection | reflect(runs[]) -> Insight[] | New | P1 |
| Planning | Policy Engine adaptation from insights | New | P2 |
| Constrained Generation | Tier map + policy_rules.json | Done | P0 |
| DDA | Adaptive tier thresholds + difficulty_level | New | P2 |
| Backward Design | scenario_intent per test case | New | P1 |
| Persona Fidelity | persona_anchor in Mirror config | New | P1 |
| Bias Monitoring | bias_check in Metrics | New | P1 |
| Multi-Mirror Eval | N mirror instances, majority vote | New | P2 |
| Recall Memory | Filtered queries over audit trail | New | P2 |
| Deliberative Loop | Policy-Mirror 2-round dialogue | New | P2 |

## Interface Contracts

### phase_hooks (Orchestrator)
```
hook(phase_name: str, run: Run, context: dict) -> Run
```
Phases: classify, decide, execute, mirror, log. Hooks can modify the Run or inject signals.

### PersonaConfig (Persona)
```json
{
  "risk_sensitivity": 0.7,
  "verbosity": "medium",
  "domain_focus": "security",
  "confidence_bias": "neutral",
  "persona_anchor": "You are a cautious security reviewer..."
}
```

### MirrorAgent (Evaluator)
```
evaluate(run: Run, persona: PersonaConfig) -> MirrorTrace
```
Pluggable. Implementations: heuristic, LLM-based, rule-based.

### reflect (Reflection)
```
reflect(runs: Run[], window: int = 50) -> Insight[]
```
Insight: { insight_id, run_ids[], summary, recommendation, confidence }

### bias_check (Metrics)
```
bias_check(audit_trail: Run[]) -> BiasReport
```
BiasReport: { seed_distribution, decision_skew, flagged_seeds[] }
