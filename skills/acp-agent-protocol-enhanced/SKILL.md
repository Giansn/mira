---
name: acp-agent-protocol-enhanced
description: "Enhanced ACP Agent Protocol with multi-agent orchestration patterns from Intent Agent Starter Kit"
---

# Enhanced ACP Agent Protocol Skill

## Overview

This enhanced ACP skill incorporates sophisticated multi-agent orchestration patterns from the Intent Agent Starter Kit, providing a comprehensive framework for coordinating multiple AI agents through OpenClaw's Agent Control Protocol (ACP).

## Key Enhancements from Intent Agent Starter Kit

### 1. **21-Agent Orchestration System**
- Coordinator agent with intelligent task routing
- Developer agent for implementation
- 19 specialist agents with domain expertise
- Universal agent protocol for consistent communication

### 2. **4-Gate Verification Pipeline**
- **Gate 1:** Risk Review (Devil's Advocate) - 10/10 confidence required
- **Gate 2:** Coverage Audit (Code Auditor + Security) - 100% spec coverage
- **Gate 3:** Test Suite (QA Engineer) - Zero failures, zero skipped tests
- **Gate 4:** Visual Validation (UI Validator) - 100% pass across viewports

### 3. **Structured Agent Communication**
- Coordinator assigns tasks to specialized agents
- Clear handoff protocols and shared context management
- Reference specific file paths and line numbers
- No cross-agent communication directly - all through Coordinator

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Enhanced ACP System                   │
├─────────────────────────────────────────────────────────┤
│  Coordinator (Master Agent)                             │
│  ├── Task Analysis & Decomposition                      │
│  ├── Specialist Routing                                 │
│  ├── Verification Gate Management                       │
│  └── Result Integration                                 │
│                                                         │
│  Specialist Agents (via ACP)                            │
│  ├── Lead Architect      ├── Security Specialist        │
│  ├── Product Owner       ├── Code Auditor               │
│  ├── QA Engineer         ├── Code Simplifier            │
│  ├── Research Analyst    ├── Performance Engineer       │
│  ├── Devil's Advocate    ├── Design Systems Specialist  │
│  └── [Domain Specialists]                               │
│                                                         │
│  ACP Runtime Layer                                      │
│  ├── Claude Code        ├── Codex                      │
│  ├── Pi                 ├── Gemini                     │
│  └── Custom Agents                                      │
└─────────────────────────────────────────────────────────┘
```

## Installation & Configuration

### 1. Install Required Components
```bash
# Install ACP runtime plugin
npm install -g @openclaw/acpx

# Configure ACP providers
openclaw config set acp.enabled true
openclaw config set acp.providers.claude-code.apiKey "${ANTHROPIC_API_KEY}"
openclaw config set acp.providers.claude-code.model "claude-3-5-sonnet-20241022"

# Configure multi-agent orchestration
openclaw config set agents.orchestration.enabled true
openclaw config set agents.orchestration.max_concurrent 3
```

### 2. Set Up Specialist Agent Templates
```bash
# Create agent templates directory
mkdir -p ~/.openclaw/agents/templates

# Copy specialist templates from Intent Agent Starter Kit patterns
# (Adapted for OpenClaw ACP)
```

## Usage

### Basic Multi-Agent Task
```python
from acp_enhanced import EnhancedACPOrchestrator

# Initialize enhanced orchestrator
orchestrator = EnhancedACPOrchestrator()

# Execute complex task with multi-agent orchestration
result = orchestrator.execute_complex_task(
    task="Develop a secure web application with user authentication",
    workflow_type="hierarchical",
    verification_gates=["risk", "security", "testing", "visual"],
    specialist_agents=["lead-architect", "security-specialist", "developer", "qa-engineer"]
)

print(f"Final result: {result.final_output}")
print(f"Gates passed: {result.gates_passed}")
print(f"Agents involved: {result.agents_used}")
```

### Coordinator-Driven Workflow
```python
# Coordinator analyzes task and delegates to specialists
coordinator = CoordinatorAgent()
task_analysis = coordinator.analyze_task(
    "Create a comprehensive API documentation system"
)

# Route to appropriate specialists
specialist_assignments = coordinator.route_to_specialists(task_analysis)

# Execute with verification gates
results = coordinator.orchestrate_execution(
    specialist_assignments,
    gates=["risk-review", "coverage-audit", "test-suite"]
)
```

### Verification Gate Pipeline
```python
# Run complete verification pipeline
verification = VerificationPipeline()

# Gate 1: Risk Review
risk_result = verification.gate_1_risk_review(
    task_spec=spec,
    agent="devils-advocate",
    confidence_threshold=10  # 10/10 required
)

# Gate 2: Coverage Audit
coverage_result = verification.gate_2_coverage_audit(
    implementation=code,
    spec=spec,
    agents=["code-auditor", "security-specialist"],
    coverage_threshold=1.0  # 100% coverage
)

# Gate 3: Test Suite
test_result = verification.gate_3_test_suite(
    code=code,
    tests=test_suite,
    agent="qa-engineer",
    failure_tolerance=0  # Zero failures allowed
)

# Gate 4: Visual Validation (if applicable)
if is_frontend_task:
    visual_result = verification.gate_4_visual_validation(
        ui_components=components,
        viewports=["desktop", "tablet", "mobile"],
        agent="ui-validator",
        pass_threshold=1.0  # 100% pass rate
    )
```

## Specialist Agent Routing Table

Adapted from Intent Agent Starter Kit for OpenClaw ACP:

| Domain | Specialist Agent | ACP Provider | When to Use |
|--------|------------------|--------------|-------------|
| **Architecture** | Lead Architect | Claude Code | System design, tech selection, ADRs |
| **Product** | Product Owner | Claude Code | PRDs, feature specs, user stories |
| **Testing** | QA Engineer | Claude Code | Test execution, coverage (Gate 3) |
| **Research** | Research Analyst | Claude Code + EXA | Technology research, competitive analysis |
| **Risk** | Devil's Advocate | Claude Code | Risk review, assumption testing (Gate 1) |
| **Security** | Security Specialist | Claude Code | Vulnerability audit, OWASP review (Gate 2) |
| **Code Audit** | Code Auditor | Claude Code | Spec vs implementation comparison (Gate 2) |
| **UX** | UX Strategist | Claude Code | User research, interaction design |
| **Docs** | Technical Writer | Claude Code | API docs, guides, documentation |
| **DevOps** | DevOps Engineer | Claude Code | CI/CD, deployment, infrastructure |
| **Performance** | Performance Engineer | Claude Code | Optimization, profiling, metrics |
| **Code Quality** | Code Simplifier | Claude Code | Complexity reduction, readability |
| **Design System** | Design Systems Specialist | Claude Code | Design tokens, component library |
| **Mobile** | Mobile Developer | Claude Code | React Native / Expo implementation |
| **iOS** | iOS Developer | Claude Code | Swift / SwiftUI implementation |
| **Visual QA** | UI Validator | Claude Code | Visual regression, viewport testing (Gate 4) |
| **Rust** | Rust Systems Developer | Claude Code | Systems programming, async runtime |
| **AI/Agents** | AI Agent Architect | Claude Code | LLM integration, agent design |
| **Content** | Content Strategist | Claude Code | Content planning, editorial |
| **Community** | Community Manager | Claude Code | Community engagement |
| **Business** | Venture Strategist | Claude Code | Market analysis, pricing |

## Enhanced Features

### 1. **Context-Aware Task Analysis**
```python
# Before planning ANY task, follow context acquisition sequence:
# 1. Use Augment Context Engine for codebase exploration
# 2. Map dependencies and import chains
# 3. Internal knowledge FIRST, external research SECOND
# 4. Reference specific file paths and line numbers
```

### 2. **MCP Tool Delegation Protocol**
```python
# When delegating tasks, include explicit MCP tool instructions:
# - Research tasks: "Use EXA for semantic search across the web"
# - PR/Review tasks: "Use Greptile to trigger code review"
# - Database tasks: "Use Supabase MCP to verify schema"
# - Complex reasoning: "Use Sequential Thinking MCP for multi-step analysis"
```

### 3. **Plan-Only Mode**
```python
# Trigger words: analyze, audit, assess, plan only, review architecture
# Behavior:
# 1. Classify as high complexity regardless of apparent simplicity
# 2. Run full enrichment pipeline
# 3. DO NOT delegate implementation — no code gets written
# 4. Output architecture diagrams, file references, effort estimates
# 5. Present findings and STOP — wait for explicit implementation request
```

### 4. **Quality Standards Enforcement**
```python
# Universal Agent Protocol rules:
# - Every output must be verifiable
# - Never use vague language: "simple", "easy", "obvious"
# - If unsure, say so explicitly rather than guessing
# - Self-review output before submitting
# - Check project-specific agent definitions in .claude/agents/
```

## Integration with OpenClaw

### Session Management
```python
# Spawn ACP sessions for specialist agents
sessions = []
for specialist in required_specialists:
    session = sessions_spawn(
        runtime="acp",
        agentId="claude-code",
        task=f"Act as {specialist}: {task_description}",
        mode="session",
        label=f"{specialist}-{task_id}"
    )
    sessions.append(session)

# Coordinate sessions through main orchestrator
orchestrator.coordinate_sessions(sessions)
```

### Memory Integration
```python
# Store orchestration results in memory
memory_search("multi-agent orchestration results")
memory_get("acp/orchestration/history.json")

# Update memory with lessons learned
memory_update(
    path="acp/patterns/successful_orchestrations.md",
    content=orchestration_insights
)
```

### Heartbeat Monitoring
```python
# Monitor ACP agent sessions during heartbeats
def check_acp_sessions():
    sessions = sessions_list(kinds=["acp"])
    for session in sessions:
        if session.status == "stuck":
            sessions_send(session.sessionKey, "Continue task or provide status update")
    
    # Log orchestration metrics
    log_orchestration_metrics()
```

## Configuration Examples

### Gateway Configuration
```json
{
  "acp": {
    "enabled": true,
    "providers": {
      "claude-code": {
        "type": "anthropic",
        "apiKey": "${ANTHROPIC_API_KEY}",
        "model": "claude-3-5-sonnet-20241022",
        "maxTokens": 4000,
        "temperature": 0.7
      }
    },
    "orchestration": {
      "enabled": true,
      "maxConcurrentAgents": 3,
      "defaultWorkflow": "hierarchical",
      "verificationGates": ["risk", "security", "testing"],
      "fallbackModel": "claude-code"
    }
  },
  "agents": {
    "specialists": {
      "lead-architect": {
        "provider": "claude-code",
        "systemPrompt": "templates/specialists/lead-architect.md",
        "capabilities": ["architecture", "design", "planning"]
      },
      "security-specialist": {
        "provider": "claude-code",
        "systemPrompt": "templates/specialists/security-specialist.md",
        "capabilities": ["security", "audit", "vulnerability"]
      }
    }
  }
}
```

### Environment Setup
```bash
# Required environment variables
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"

# Optional MCP tools
export EXA_API_KEY="your-exa-key"
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-key"
```

## Example Workflows

### 1. **Secure Application Development**
```python
workflow = {
    "task": "Develop secure user authentication system",
    "specialists": [
        {"role": "lead-architect", "task": "Design auth architecture"},
        {"role": "security-specialist", "task": "Security review and OWASP compliance"},
        {"role": "developer", "task": "Implement auth endpoints"},
        {"role": "qa-engineer", "task": "Test auth flows and security"}
    ],
    "gates": ["risk-review", "security-audit", "test-coverage"],
    "expected_output": "Production-ready auth system with security audit report"
}
```

### 2. **Research & Analysis Pipeline**
```python
workflow = {
    "task": "Comprehensive market analysis for AI coding tools",
    "specialists": [
        {"role": "research-analyst", "task": "Gather market data and trends"},
        {"role": "product-owner", "task": "Define feature requirements"},
        {"role": "venture-strategist", "task": "Business viability analysis"},
        {"role": "technical-writer", "task": "Create final report"}
    ],
    "gates": ["risk-review", "coverage-audit"],
    "expected_output": "Market analysis report with recommendations"
}
```

### 3. **Code Refactoring with Quality Gates**
```python
workflow = {
    "task": "Refactor legacy codebase with modern patterns",
    "specialists": [
        {"role": "code-auditor", "task": "Analyze current code quality"},
        {"role": "code-simplifier", "task": "Propose simplification strategies"},
        {"role": "developer", "task": "Implement refactoring"},
        {"role": "performance-engineer", "task": "Optimize critical paths"}
    ],
    "gates": ["risk-review", "coverage-audit", "test-suite"],
    "expected_output": "Refactored codebase with improved maintainability"
}
```

## Troubleshooting

### Common Issues & Solutions

**Issue:** "ACP runtime backend is not configured"
```bash
# Solution: Install acpx plugin
npm install -g @openclaw/acpx
openclaw config set acp.enabled true
openclaw gateway restart
```

**Issue:** "No suitable specialist agent found"
```python
# Solution: Check agent configuration and fallback to generalist
orchestrator.execute_with_fallback(
    task=task,
    primary_specialists=specialists,
    fallback_agent="claude-code",
    fallback_prompt="General implementation with risk awareness"
)
```

**Issue:** "Verification gate failed"
```python
# Solution: Implement gate recovery strategy
recovery = GateRecoveryStrategy()
recovery.handle_gate_failure(
    failed_gate=gate_name,
    failure_reason=reason,
    retry_attempts=2,
    alternative_specialists=backup_agents
)
```

**Issue:** "High token usage in multi-agent workflows"
```python
# Solution: Implement token optimization
optimizer = TokenOptimizer()
optimized_workflow = optimizer.optimize_multi_agent_workflow(
    workflow=original_workflow,
    token_budget=max_tokens,
    strategies=["context_pruning", "result_caching", "parallel_compression"]
)
```

## Performance Optimization

### 1. **Token Efficiency**
- Use smaller models for routing and classification tasks
- Cache repeated tool calls and LLM responses
- Implement context pruning between agent handoffs
- Set token budgets per agent per task

### 2. **Parallel Execution**
```python
# Execute independent tasks in parallel
async def execute_parallel_specialists(specialists):
    tasks = []
    for specialist in specialists:
        if not specialist.dependencies:
            task = execute_specialist(specialist)
            tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### 3. **Result Caching**
```python
# Cache specialist results for similar tasks
cache = SpecialistResultCache()
cached_result = cache.get(
    specialist_type=specialist,
    task_signature=task_hash
)

if cached_result and cache.is_valid(cached_result):
    return cached_result
else:
    result = await execute_specialist(specialist, task)
    cache.set(specialist, task_hash, result)
    return result
```

## Security Considerations

### 1. **API Key Management**
- Store keys in environment variables, not in code
- Use key rotation for production deployments
- Implement rate limiting per API key
- Monitor for unusual usage patterns

### 2. **Session Isolation**
- Each ACP session runs isolated from others
- Clear session state between tasks
- Implement session timeout policies
- Log session activities for audit trails

### 3. **Content Safety**
- Validate all agent outputs against safety guidelines
- Implement content filtering for user-facing outputs
- Monitor for prompt injection attempts
- Regular security reviews of agent prompts

## Monitoring & Metrics

### Key Metrics to Track
```python
metrics = {
    "agent_performance": {
        "success_rate": 0.95,
        "average_latency": 45.2,
        "token_efficiency": 0.78
    },
    "orchestration": {
        "gates_passed": 4,
        "agents_utilized": 3,
        "total_execution_time": 320.5
    },
    "cost_management": {
        "tokens_used": 12500,
        "estimated_cost": 0.85,
        "cost_per_task": 0.12
    }
}
```

### Logging Configuration
```python
logging_config = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s -