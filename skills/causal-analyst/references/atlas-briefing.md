# Atlas Briefing — Professional AI Simulation Patterns for Phase 4

Source: "Designing Professional AI Simulation Environments" (Claude synthesis, 2025)
Context: Phase 4 of Causal Analyst MVP (Atlas) — seed-driven analysis engine for OpenClaw exec approvals with mirror layer.

---

## 1. Architecture: Five-Layer Blueprint

Production AI sim envs converge on five interacting layers. Each maps directly to an Atlas component.

### 1.1 Scenario Engine (Orchestration Layer)

What it does:
- Manages simulation flow, progression logic, scene transitions.
- A central orchestrator/director coordinates which agents interact, when scenes change, how the simulation advances.
- Replaces monolithic dialogue systems with modular, composable pipelines.

State of the art:
- HAMLET: hierarchical agents (director, actors, scene analyzer).
- Drama Engine: moderator for multi-agent chat orchestration.
- Adaptive-VP: five-stage VP Case Development Pipeline for scenario creation and progression.

Atlas mapping:
- **SimEnv Controller** is our orchestrator. It sequences phases (classify, decide, execute/block, mirror, log) per seed/command pair.
- Current design is single-threaded per run. Future: multi-agent orchestration where separate agents handle classification, policy evaluation, and mirror critique concurrently.
- Action item: add a `phase_hooks` interface to the controller so new phases (e.g., persona check, DDA adjustment) can be plugged in without rewriting the core loop.

### 1.2 Persona Module

What it does:
- Defines agent identity through structured profiles: demographics, personality traits, backstory, communication style, emotional state, domain knowledge.
- Multi-dimensional encoding prevents flat stereotypes and enables realistic variation.

State of the art:
- PatientSim (2025, NeurIPS): four axes — Big Five personality, language proficiency, medical history recall, cognitive confusion level. Produces 37 unique persona combinations. Clinician quality score: 3.89/4.
- CharacterBox: BDI (Belief-Desire-Intention) modeling for agent personas.
- Emotional modeling: Circumplex Model of Affect (valence + arousal), PAD framework (pleasure-arousal-dominance), Plutchik's wheel for categorical emotions.
- Critical limitation: RLHF training pushes LLMs toward overly cheerful personas, conflicting with accurate simulation of difficult/hostile/confused agents.

Atlas mapping:
- Currently Atlas has no explicit persona layer. The Mirror Layer implicitly "acts" as a persona (the cautious critic).
- Action item: define a `PersonaConfig` object that encodes the Mirror's behavioral axes:
  - `risk_sensitivity`: float 0.0–1.0 (how aggressive the critique is)
  - `verbosity`: low | medium | high
  - `domain_focus`: security | compliance | general
  - `confidence_bias`: optimistic | neutral | pessimistic
- This makes the Mirror's behavior tunable and reproducible across seeds.

### 1.3 Feedback and Assessment System

What it does:
- Operates as a separate agent or agent cluster.
- Evaluates performance across defined domains (e.g., Empathy, Explicitness, Empowerment in SOPHIE).
- Scores feed into adaptation modules for dynamic difficulty.
- Key pattern: **evaluator-generator separation** — distinct agents evaluate vs. generate.

State of the art:
- SOPHIE: measures communication across three domains.
- Adaptive-VP: multi-agent evaluation where multiple evaluator agents assess trainee communication.
- Roleplay-doh: converts expert feedback into natural language principles, then runs two-stage verification.

Atlas mapping:
- Our **Mirror Layer** is the evaluator. The **SimEnv Controller** is the generator (it produces Run objects).
- Currently tightly coupled: mirror runs inline after each run. Production pattern suggests decoupling:
  - Mirror becomes an independent agent that subscribes to Run events.
  - Enables parallel evaluation, batch critique, and pluggable evaluator models.
- Action item: define a `MirrorAgent` interface with `evaluate(run: Run) -> MirrorTrace` contract. Allow multiple evaluator implementations (heuristic, LLM-based, rule-based).

### 1.4 State Management

What it does:
- Short-term state: current conversation context.
- Long-term state: vector databases (semantic retrieval), knowledge graphs (structured relationships), traditional databases.
- Hybrid approach: in-context history + external stores for coherence and scalability.

State of the art:
- Mem0: universal memory layer with `memory.add()` and `memory.search()` APIs.
- Letta (formerly MemGPT): virtual memory hierarchy inspired by OS memory management — core memory, archival memory, recall memory.
- Zep/Graphiti: temporal knowledge graphs for time-aware retrieval.

Atlas mapping:
- Our **Audit Trail** = archival memory (append-only, immutable, hash-chained).
- Our **Memory Log** = core memory (redacted, shareable, derived from audit trail).
- Missing: **recall memory** — a retrieval layer that can surface relevant past runs based on semantic similarity (e.g., "show me all runs where curl was denied").
- Action item (P2): add a lightweight index over the audit trail that supports filtered queries by command, tier, decision, and risk_flags. JSON Lines + grep is MVP; vector embeddings are future.

### 1.5 Memory and Context System

What it does:
- Addresses finite context windows across extended sessions.
- Foundational pattern (Stanford Generative Agents, Park et al. 2023): memory stream stores all experiences in natural language, retrieved by recency + importance (scored 1–10) + relevance (embedding similarity).
- Reflection module periodically synthesizes higher-level inferences.
- Three-part architecture: **memory stream, reflection, planning**.

Atlas mapping:
- Memory stream = Audit Trail (raw Run objects).
- Reflection = Mirror Layer (single-pass critique per run). But we lack **periodic reflection** — a batch process that reviews N recent runs and synthesizes meta-insights (e.g., "tier classification is too aggressive for curl variants").
- Planning = not yet implemented. Would manifest as the Policy Engine adapting its rules based on reflection outputs.
- Action item (P1): add a `reflect(runs: Run[]) -> Insight[]` function that operates over a batch of recent runs. Insights are stored in a separate `insights.jsonl` file, referenced by run_ids. This enables the policy engine to evolve.

---

## 2. Persona Fidelity and Consistency

### The Problem
- Persona consistency degrades over long conversations without explicit enforcement.
- LLMs drift from assigned personas, contradict earlier statements, abandon role-appropriate behavior.
- Shanahan et al.'s "simulacra superposition" theory: LLM maintains a distribution over all possible characters; persona drift = distribution collapse toward unintended characters.

### Solutions (ranked by effectiveness)
1. **Multi-turn RL with consistency metrics** (2025): prompt-to-line, line-to-line, Q&A consistency as reward signals. Reduced inconsistency by 55%.
2. **Persona-Aware Contrastive Learning (PCL, 2025)**: "role chain" method where model self-questions based on role characteristics before responding.
3. **System prompt anchoring**: detailed, structured system prompts.
4. **Response prefilling**: start generation with character-consistent text.
5. **Scenario preparation**: pre-script expected in-character responses for common situations.
6. **Periodic re-anchoring**: restate persona in long conversations.
- Anthropic recommends combining all four practical techniques (3–6).

### Atlas mapping
- Mirror Layer currently has no persona drift protection. Over many runs, mirror reasoning could become formulaic or inconsistent.
- Action item: add `persona_anchor` field to Mirror config — a short, structured prompt that re-anchors the Mirror's behavioral profile before each critique pass. Cheap and effective.

---

## 3. Scenario Design: From Static Branching to Constrained Generation

### Key shift
- Traditional: branching decision trees (Twine, iSpring TalkMaster). Each choice leads to predetermined path.
- Modern: **constrained open-ended model** — AI generates dynamically within guardrails defined by objectives, parameters, and boundaries. Infinite conversational paths, pedagogical alignment maintained.
- Surprising finding (UCLA/JMIR 2025): a single detailed text prompt with only two states (setup + feedback) produced paths equivalent to complex scripted branching.

### Dynamic Difficulty Adjustment (DDA)
- Adaptive-VP (ACL 2025): LLM-based virtual patients adjust emotional intensity and resistance based on trainee communication quality.
- Personalized DDA (2024): imitation learning + RL to adapt to individual learner behavior in real-time; grounded in Csikszentmihalyi's flow state theory.

### Atlas mapping
- Our tier map (SAFE/SENSITIVE/BLOCKED) is a static branching model. Commands always map to the same tier.
- DDA equivalent: **adaptive tier thresholds** — if a seed consistently produces correct GRANTED/DENIED decisions, increase difficulty by introducing ambiguous commands (e.g., `curl https://internal-api` vs. bare `curl`).
- Action item (P2): define a `difficulty_level` field in policy_rules.json. At higher levels, inject edge-case commands with ambiguous tiering. Mirror confidence scores become the feedback signal for difficulty adjustment.

### Backward Design
- Start with desired outcomes (correct tier classification, appropriate decisions, accurate mirror critique).
- Design assessments (MVP test plan already does this).
- Shape scenarios around outcomes (seed/command selection should target known failure modes).
- Action item: add a `scenario_intent` field to each test case in mvp-test-plan.md — what specific behavior is this test designed to exercise?

---

## 4. Interaction Design

### Turn-taking
- Google Research DialogLab (UIST 2025): separates group dynamics (roles, relationships) from conversation dynamics (snippets, turn-taking rules).
- AI systems that end every response with a question feel artificial.

### Atlas mapping
- Our controller currently processes seed/command pairs sequentially. No "dialogue" between components.
- Future (P2): introduce a back-and-forth between Policy Engine and Mirror. Policy proposes a decision; Mirror critiques; Policy may revise. This creates a deliberative loop with turn-taking semantics.
- Guard: cap deliberation at 2 rounds to prevent infinite loops (already enforced for Mirror at 1 pass; extend to 2 for policy-mirror dialogue).

---

## 5. Evaluation Patterns

### LLM-as-Judge
- Dominant approach: use a separate LLM instance to evaluate simulation quality.
- Multi-agent evaluation: multiple evaluator agents assess different dimensions.
- Calibration is critical: evaluator models must be validated against human expert ratings.

### Atlas mapping
- Mirror Layer is our judge. Currently single-model, single-pass.
- Future: run multiple mirror instances with different persona configs (risk-sensitive vs. permissive) and aggregate. Disagreement = high-uncertainty run that should be flagged.
- Action item (P2): define a `multi_mirror` mode where N mirror instances evaluate the same run independently. Aggregate via majority vote on risk_flags; average confidence scores; flag runs where mirrors disagree.

---

## 6. Ethics, Safety, and Governance

### Key principles from the field
- Emotional safety boundaries: prevent simulation from causing psychological harm.
- Privacy and data governance: redact PII, enforce consent for data collection.
- Bias monitoring: track whether the system treats different inputs equitably.
- Transparency: make evaluation criteria visible; avoid opaque scoring.
- Human oversight: maintain human-in-the-loop for high-stakes decisions.

### Atlas mapping
- Redacted Memory Log already addresses privacy (no raw seeds/commands in shareable logs).
- Hash chain provides tamper detection (transparency).
- BLOCKED tier enforces hard safety boundaries (no execution of destructive commands).
- Missing: **bias monitoring** — do certain seeds consistently produce different outcomes? Is the tier map equitable across command families?
- Action item (P1): add a `bias_check` to the Metrics module. Compare decision distributions across seeds. Flag if any seed deviates >2 sigma from the mean.

---

## 7. Implementation Priorities (Atlas-specific)

### Immediate (Phase 4 MVP)
- [ ] Add `phase_hooks` interface to SimEnv Controller
- [ ] Define `PersonaConfig` for Mirror Layer
- [ ] Define `MirrorAgent` interface with pluggable evaluator contract
- [ ] Add `persona_anchor` to Mirror config
- [ ] Add `scenario_intent` to test cases
- [ ] Add `bias_check` stub to Metrics module

### Near-term (P1)
- [ ] Implement `reflect()` batch function over recent runs
- [ ] Create `insights.jsonl` store
- [ ] Wire reflection outputs to policy engine adaptation

### Future (P2)
- [ ] Adaptive tier thresholds with DDA
- [ ] Multi-mirror evaluation mode
- [ ] Recall memory with filtered queries over audit trail
- [ ] Policy-Mirror deliberative loop (2-round cap)
- [ ] Audit trail vector index for semantic retrieval

---

## 8. Key Takeaways

1. **Separation of concerns is everything.** Orchestrator, persona, evaluator, generator, memory — each should be independently replaceable.
2. **Persona consistency requires active enforcement.** Anchoring, re-anchoring, and RL-based consistency rewards.
3. **Evaluator-generator split is non-negotiable** for trustworthy systems. Our Mirror/Controller separation is correct; decouple further.
4. **Memory is three things, not one.** Stream (raw), reflection (synthesized), planning (actionable). We have stream and partial reflection; planning is the gap.
5. **Static tiering is a starting point, not an endpoint.** DDA and adaptive thresholds make the system more robust.
6. **Bias monitoring is a governance requirement**, not a nice-to-have.
7. **Simple prompts can be surprisingly powerful** — don't over-engineer scenarios when a well-crafted seed/command pair + good policy rules suffice.
