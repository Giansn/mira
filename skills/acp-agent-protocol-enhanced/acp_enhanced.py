"""
Enhanced ACP Agent Protocol with Intent Agent Starter Kit Patterns

This module implements sophisticated multi-agent orchestration patterns
adapted from the Intent Agent Starter Kit for OpenClaw's ACP system.
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class AgentCapability(Enum):
    """Capabilities of specialist agents."""
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    TESTING = "testing"
    RESEARCH = "research"
    RISK_ASSESSMENT = "risk_assessment"
    CODE_AUDIT = "code_audit"
    UX_DESIGN = "ux_design"
    DOCUMENTATION = "documentation"
    DEVOPS = "devops"
    PERFORMANCE = "performance"
    CODE_SIMPLIFICATION = "code_simplification"
    DESIGN_SYSTEMS = "design_systems"
    MOBILE_DEVELOPMENT = "mobile_development"
    IOS_DEVELOPMENT = "ios_development"
    VISUAL_VALIDATION = "visual_validation"
    RUST_DEVELOPMENT = "rust_development"
    AI_AGENT_DESIGN = "ai_agent_design"
    CONTENT_STRATEGY = "content_strategy"
    COMMUNITY_MANAGEMENT = "community_management"
    BUSINESS_STRATEGY = "business_strategy"


class VerificationGate(Enum):
    """Verification gates from Intent Agent Starter Kit."""
    RISK_REVIEW = "risk_review"          # Gate 1: Devil's Advocate
    COVERAGE_AUDIT = "coverage_audit"    # Gate 2: Code Auditor + Security
    TEST_SUITE = "test_suite"            # Gate 3: QA Engineer
    VISUAL_VALIDATION = "visual_validation"  # Gate 4: UI Validator


class WorkflowType(Enum):
    """Types of multi-agent workflows."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    GATED = "gated"  # With verification gates


@dataclass
class SpecialistAgent:
    """Definition of a specialist agent."""
    name: str
    description: str
    capabilities: List[AgentCapability]
    acp_provider: str = "claude-code"
    system_prompt: Optional[str] = None
    confidence_threshold: float = 0.8
    max_tokens: int = 4000
    timeout_seconds: int = 120
    
    def can_handle(self, required_capabilities: List[AgentCapability]) -> bool:
        """Check if agent has all required capabilities."""
        return all(cap in self.capabilities for cap in required_capabilities)


@dataclass
class TaskAnalysis:
    """Analysis of a task for multi-agent orchestration."""
    original_task: str
    task_hash: str
    complexity_score: float
    required_capabilities: List[AgentCapability]
    suggested_specialists: List[str]
    estimated_effort: str  # "small", "medium", "large", "xlarge"
    dependencies: List[str] = field(default_factory=list)
    risk_level: str = "medium"  # "low", "medium", "high", "critical"


@dataclass
class SpecialistAssignment:
    """Assignment of a task to a specialist agent."""
    task_id: str
    specialist_name: str
    subtask_description: str
    acceptance_criteria: List[str]
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[str] = None
    confidence_score: float = 0.0
    execution_time: float = 0.0


@dataclass
class GateResult:
    """Result of a verification gate."""
    gate: VerificationGate
    passed: bool
    confidence_score: float
    feedback: str
    specialist_used: str
    execution_time: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """Final result from multi-agent orchestration."""
    task_id: str
    original_task: str
    final_output: str
    specialists_used: List[str]
    gates_passed: List[VerificationGate]
    total_execution_time: float
    confidence_score: float
    task_analysis: TaskAnalysis
    specialist_results: Dict[str, SpecialistAssignment]
    gate_results: Dict[VerificationGate, GateResult]
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedACPOrchestrator:
    """
    Enhanced orchestrator that implements Intent Agent Starter Kit patterns
    for multi-agent coordination through OpenClaw ACP.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.specialist_registry: Dict[str, SpecialistAgent] = {}
        self.task_history: List[OrchestrationResult] = []
        self.gate_history: List[GateResult] = []
        self._initialize_default_specialists()
        self._load_config(config_path)
    
    def _initialize_default_specialists(self):
        """Initialize with specialist agents from Intent Agent Starter Kit."""
        
        # Core specialists (always available)
        self.specialist_registry["lead-architect"] = SpecialistAgent(
            name="lead-architect",
            description="System design, tech selection, architecture decision records",
            capabilities=[
                AgentCapability.ARCHITECTURE,
                AgentCapability.PERFORMANCE,
                AgentCapability.DESIGN_SYSTEMS
            ],
            confidence_threshold=0.9
        )
        
        self.specialist_registry["security-specialist"] = SpecialistAgent(
            name="security-specialist",
            description="Vulnerability audit, OWASP review, security compliance",
            capabilities=[AgentCapability.SECURITY],
            confidence_threshold=0.95  # High threshold for security
        )
        
        self.specialist_registry["qa-engineer"] = SpecialistAgent(
            name="qa-engineer",
            description="Test execution, coverage analysis, quality assurance",
            capabilities=[AgentCapability.TESTING],
            confidence_threshold=0.85
        )
        
        self.specialist_registry["research-analyst"] = SpecialistAgent(
            name="research-analyst",
            description="Technology research, competitive analysis, information synthesis",
            capabilities=[AgentCapability.RESEARCH],
            confidence_threshold=0.8
        )
        
        self.specialist_registry["devils-advocate"] = SpecialistAgent(
            name="devils-advocate",
            description="Risk review, assumption testing, critical analysis",
            capabilities=[AgentCapability.RISK_ASSESSMENT],
            confidence_threshold=1.0  # 10/10 required per Intent Agent Starter Kit
        )
        
        self.specialist_registry["code-auditor"] = SpecialistAgent(
            name="code-auditor",
            description="Spec vs implementation comparison, code quality audit",
            capabilities=[AgentCapability.CODE_AUDIT],
            confidence_threshold=0.9
        )
        
        self.specialist_registry["code-simplifier"] = SpecialistAgent(
            name="code-simplifier",
            description="Complexity reduction, readability improvement, refactoring",
            capabilities=[AgentCapability.CODE_SIMPLIFICATION],
            confidence_threshold=0.85
        )
        
        self.specialist_registry["performance-engineer"] = SpecialistAgent(
            name="performance-engineer",
            description="Optimization, profiling, metrics analysis, latency reduction",
            capabilities=[AgentCapability.PERFORMANCE],
            confidence_threshold=0.85
        )
        
        self.specialist_registry["design-systems-specialist"] = SpecialistAgent(
            name="design-systems-specialist",
            description="Design tokens, component library, visual consistency",
            capabilities=[AgentCapability.DESIGN_SYSTEMS],
            confidence_threshold=0.85
        )
        
        # Domain-specific specialists
        self.specialist_registry["ai-agent-architect"] = SpecialistAgent(
            name="ai-agent-architect",
            description="LLM integration, agent design, multi-agent orchestration",
            capabilities=[AgentCapability.AI_AGENT_DESIGN],
            confidence_threshold=0.9
        )
        
        self.specialist_registry["technical-writer"] = SpecialistAgent(
            name="technical-writer",
            description="API docs, guides, documentation, technical content",
            capabilities=[AgentCapability.DOCUMENTATION],
            confidence_threshold=0.9
        )
        
        self.specialist_registry["devops-engineer"] = SpecialistAgent(
            name="devops-engineer",
            description="CI/CD, deployment, infrastructure, monitoring",
            capabilities=[AgentCapability.DEVOPS],
            confidence_threshold=0.85
        )
    
    def _load_config(self, config_path: Optional[str]):
        """Load configuration from file."""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                # Apply configuration
                if 'specialists' in config:
                    for spec_name, spec_config in config['specialists'].items():
                        if spec_name in self.specialist_registry:
                            # Update existing specialist
                            pass  # Implementation for config updates
            except FileNotFoundError:
                print(f"Config file not found: {config_path}")
    
    def analyze_task(self, task: str) -> TaskAnalysis:
        """
        Analyze a task to determine required capabilities and specialists.
        
        Implements Context Engine Protocol from Intent Agent Starter Kit:
        1. Analyze task requirements
        2. Determine required capabilities
        3. Map to specialist agents
        4. Assess complexity and risk
        """
        task_lower = task.lower()
        task_hash = hashlib.md5(task.encode()).hexdigest()[:8]
        
        # Determine required capabilities based on task content
        required_capabilities = set()
        
        # Pattern matching for capability detection
        capability_patterns = {
            AgentCapability.ARCHITECTURE: ["architecture", "design", "system", "tech stack", "framework"],
            AgentCapability.SECURITY: ["security", "secure", "vulnerability", "authentication", "encryption"],
            AgentCapability.TESTING: ["test", "qa", "quality", "coverage", "debug"],
            AgentCapability.RESEARCH: ["research", "analyze", "compare", "market", "competitive"],
            AgentCapability.RISK_ASSESSMENT: ["risk", "assumption", "critical", "review"],
            AgentCapability.CODE_AUDIT: ["audit", "review", "inspect", "examine"],
            AgentCapability.PERFORMANCE: ["performance", "optimize", "fast", "efficient", "latency"],
            AgentCapability.DOCUMENTATION: ["document", "doc", "guide", "manual", "api"],
            AgentCapability.DEVOPS: ["deploy", "ci/cd", "infrastructure", "docker", "kubernetes"],
            AgentCapability.AI_AGENT_DESIGN: ["ai", "agent", "llm", "model", "orchestration"],
            AgentCapability.DESIGN_SYSTEMS: ["design system", "ui", "ux", "component", "visual"],
            AgentCapability.CODE_SIMPLIFICATION: ["refactor", "simplify", "clean", "readability"]
        }
        
        for capability, patterns in capability_patterns.items():
            if any(pattern in task_lower for pattern in patterns):
                required_capabilities.add(capability)
        
        # If no specific capabilities detected, use general capabilities
        if not required_capabilities:
            required_capabilities = {
                AgentCapability.ARCHITECTURE,
                AgentCapability.CODE_AUDIT
            }
        
        # Map capabilities to specialists
        suggested_specialists = []
        for spec_name, specialist in self.specialist_registry.items():
            if any(cap in specialist.capabilities for cap in required_capabilities):
                suggested_specialists.append(spec_name)
        
        # Remove duplicates and limit to top matches
        suggested_specialists = list(dict.fromkeys(suggested_specialists))[:5]
        
        # Calculate complexity score
        word_count = len(task_lower.split())
        complexity_score = min(word_count / 50, 1.0)  # Normalize to 0-1
        
        # Determine effort level
        if complexity_score < 0.3:
            effort = "small"
        elif complexity_score < 0.6:
            effort = "medium"
        elif complexity_score < 0.9:
            effort = "large"
        else:
            effort = "xlarge"
        
        # Assess risk level
        risk_keywords = ["security", "critical", "production", "user data", "compliance"]
        risk_count = sum(1 for keyword in risk_keywords if keyword in task_lower)
        
        if risk_count >= 3:
            risk_level = "critical"
        elif risk_count >= 2:
            risk_level = "high"
        elif risk_count >= 1:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return TaskAnalysis(
            original_task=task,
            task_hash=task_hash,
            complexity_score=complexity_score,
            required_capabilities=list(required_capabilities),
            suggested_specialists=suggested_specialists,
            estimated_effort=effort,
            risk_level=risk_level
        )
    
    def create_specialist_assignments(self, task_analysis: TaskAnalysis) -> List[SpecialistAssignment]:
        """
        Create assignments for specialist agents based on task analysis.
        
        Implements Specialist Routing Table from Intent Agent Starter Kit.
        """
        assignments = []
        
        # Create assignments based on required capabilities
        capability_to_specialist = {
            AgentCapability.ARCHITECTURE: "lead-architect",
            AgentCapability.SECURITY: "security-specialist",
            AgentCapability.TESTING: "qa-engineer",
            AgentCapability.RESEARCH: "research-analyst",
            AgentCapability.RISK_ASSESSMENT: "devils-advocate",
            AgentCapability.CODE_AUDIT: "code-auditor",
            AgentCapability.PERFORMANCE: "performance-engineer",
            AgentCapability.DOCUMENTATION: "technical-writer",
            AgentCapability.DEVOPS: "devops-engineer",
            AgentCapability.AI_AGENT_DESIGN: "ai-agent-architect",
            AgentCapability.DESIGN_SYSTEMS: "design-systems-specialist",
            AgentCapability.CODE_SIMPLIFICATION: "code-simplifier"
        }
        
        task_id = f"task-{task_analysis.task_hash}"
        
        for capability in task_analysis.required_capabilities:
            if capability in capability_to_specialist:
                specialist_name = capability_to_specialist[capability]
                
                # Create subtask description based on capability
                subtask_descriptions = {
                    AgentCapability.ARCHITECTURE: f"Design architecture for: {task_analysis.original_task}",
                    AgentCapability.SECURITY: f"Security review for: {task_analysis.original_task}",
                    AgentCapability.TESTING: f"Create test plan for: {task_analysis.original_task}",
                    AgentCapability.RESEARCH: f"Research aspects of: {task_analysis.original_task}",
                    AgentCapability.RISK_ASSESSMENT: f"Risk assessment for: {task_analysis.original_task}",
                    AgentCapability.CODE_AUDIT: f"Code audit for implementation of: {task_analysis.original_task}",
                    AgentCapability.PERFORMANCE: f"Performance considerations for: {task_analysis.original_task}",
                    AgentCapability.DOCUMENTATION: f"Documentation for: {task_analysis.original_task}",
                    AgentCapability.DEVOPS: f"DevOps/infrastructure for: {task_analysis.original_task}",
                    AgentCapability.AI_AGENT_DESIGN: f"AI agent design for: {task_analysis.original_task}",
                    AgentCapability.DESIGN_SYSTEMS: f"Design system for: {task_analysis.original_task}",
                    AgentCapability.CODE_SIMPLIFICATION: f"Code simplification for: {task_analysis.original_task}"
                }
                
                subtask_desc = subtask_descriptions.get(
                    capability,
                    f"Handle {capability.value} aspect of: {task_analysis.original_task}"
                )
                
                # Create acceptance criteria
                acceptance_criteria = [
                    f"Complete analysis of {capability.value} requirements",
                    f"Provide specific recommendations",
                    f"Reference existing patterns where applicable",
                    f"Meet confidence threshold of {self.specialist_registry[specialist_name].confidence_threshold}"
                ]
                
                assignment = SpecialistAssignment(
                    task_id=task_id,
                    specialist_name=specialist_name,
                    subtask_description=subtask_desc,
                    acceptance_criteria=acceptance_criteria
                )
                
                assignments.append(assignment)
        
        # Add dependencies between assignments
        # Architecture typically comes first, security/testing come after implementation
        for i, assignment in enumerate(assignments):
            if "architect" in assignment.specialist_name:
                # Architecture should be done first
                pass
            elif "security" in assignment.specialist_name or "testing" in assignment.specialist_name:
                # Security/testing depend on implementation
                impl_assignments = [a for a in assignments if "architect" in a.specialist_name or "developer" in a.specialist_name]
                if impl_assignments:
                    assignment.dependencies = [a.task_id for a in impl_assignments]
        
        return assignments
    
    async def execute_specialist_assignment(self, assignment: SpecialistAssignment) -> SpecialistAssignment:
        """
        Execute a specialist assignment using ACP.
        
        In a real implementation, this would spawn an ACP session with the specialist.
        This is a mock implementation.
        """
        assignment.status = "running"
        start_time = time.time()
        
        # Simulate ACP session execution
        await asyncio.sleep(0.5)  # Simulate API call
        
        # Get specialist info
        specialist = self.specialist_registry.get(assignment.specialist_name)
        
        # Mock response based on specialist type
        if specialist:
            if "architect" in assignment.specialist_name:
                content = f"""# Architecture Design
**Specialist:** {assignment.specialist_name}
**Task:** {assignment.subtask_description}

## Architecture Overview
Designed scalable architecture with clear separation of concerns.

## Components
1. API Layer - RESTful endpoints
2. Business Logic - Domain services
3. Data Layer - Repository pattern
4. Security - Authentication & authorization

## Technology Recommendations
- Backend: Python/FastAPI
- Database: PostgreSQL
- Cache: Redis
- Deployment: Docker/Kubernetes

## Key Decisions
- Microservices architecture for scalability
- Event-driven communication between services
- Comprehensive monitoring and logging

Confidence: 0.92"""
                
            elif "security" in assignment.specialist_name:
                content = f"""# Security Review
**Specialist:** {assignment.specialist_name}
**Task:** {assignment.subtask_description}

## Security Assessment
Comprehensive security review completed.

## Findings
1. **Authentication**: Implement OAuth 2.0 with PKCE
2. **Authorization**: Role-based access control (RBAC)
3. **Data Protection**: AES-256 encryption at rest
4. **Network Security**: TLS 1.3, WAF protection

## OWASP Top 10 Compliance
- ✅ Injection prevention
- ✅ Broken authentication protection
- ✅ Sensitive data exposure mitigation
- ✅ XXE protection
- ✅ Broken access control prevention
- ✅ Security misconfiguration checks
- ✅ XSS protection
- ✅ Insecure deserialization prevention
- ✅ Using components with known vulnerabilities
- ✅ Insufficient logging & monitoring

## Recommendations
1. Implement security headers (CSP, HSTS)
2. Regular vulnerability scanning
3. Security training for developers

Confidence: 0.96"""
                
            elif "testing" in assignment.specialist_name:
                content = f"""# Test Plan
**Specialist:** {assignment.specialist_name}
**Task:** {assignment.subtask_description}

## Test Strategy
Comprehensive testing approach covering all quality dimensions.

## Test Levels
1. **Unit Tests**: 90% code coverage target
2. **Integration Tests**: API and service integration
3. **System Tests**: End-to-end workflow validation
4. **Performance Tests**: Load and stress testing
5. **Security Tests**: Vulnerability scanning

## Test Automation
- CI/CD pipeline integration
- Automated regression suite
- Performance monitoring
- Security scanning automation

## Acceptance Criteria Met
- [x] Complete test coverage analysis
- [x] Specific testing recommendations
- [x] Reference to existing patterns
- [x] Confidence threshold met (0.85+)

## Metrics
- Target code coverage: 90%
- Test execution time: < 10 minutes
- False positive rate: < 5%

Confidence: 0.88"""
                
            else:
                content = f"""# Specialist Analysis
**Specialist:** {assignment.specialist_name}
**Task:** {assignment.subtask_description}

## Analysis Complete
Comprehensive analysis completed by specialist agent.

## Key Findings
1. Requirement analysis complete
2. Pattern matching against existing solutions
3. Risk assessment performed
4. Recommendations provided

## Recommendations
- Follow established architectural patterns
- Implement with scalability in mind
- Include comprehensive monitoring
- Plan for future extensibility

## Confidence Assessment
Based on analysis of requirements and existing patterns, confidence score: 0.85

## Next Steps
1. Review recommendations
2. Plan implementation
3. Schedule follow-up review

Confidence: 0.85"""
        else:
            content = f"Error: Specialist {assignment.specialist_name} not found in registry"
        
        execution_time = time.time() - start_time
        
        assignment.status = "completed"
        assignment.result = content
        assignment.execution_time = execution_time
        assignment.confidence_score = 0.85  # Mock confidence
        
        return assignment
    
    async def run_verification_gate(self, gate: VerificationGate, 
                                  context: Dict[str, Any]) -> GateResult:
        """
        Run a verification gate from Intent Agent Starter Kit.
        
        Gates:
        1. Risk Review (Devil's Advocate) - 10/10 confidence required
        2. Coverage Audit (Code Auditor + Security) - 100% coverage
        3. Test Suite (QA Engineer) - Zero failures, zero skipped
        4. Visual Validation (UI Validator) - 100% pass across viewports
        """
        start_time = time.time()
        
        # Determine which specialist to use for this gate
        gate_specialists = {
            VerificationGate.RISK_REVIEW: "devils-advocate",
            VerificationGate.COVERAGE_AUDIT: "code-auditor",  # + security-specialist in real implementation
            VerificationGate.TEST_SUITE: "qa-engineer",
            VerificationGate.VISUAL_VALIDATION: "design-systems-specialist"  # Simplified
        }
        
        specialist_name = gate_specialists.get(gate, "code-auditor")
        specialist = self.specialist_registry.get(specialist_name)
        
        # Mock gate execution
        await asyncio.sleep(0.3)
        
        gate_descriptions = {
            VerificationGate.RISK_REVIEW: "Risk assessment and critical analysis",
            VerificationGate.COVERAGE_AUDIT: "Code coverage and security audit",
            VerificationGate.TEST_SUITE: "Test execution and validation",
            VerificationGate.VISUAL_VALIDATION: "Visual consistency and UI validation"
        }
        
        gate_thresholds = {
            VerificationGate.RISK_REVIEW: 1.0,  # 10/10 required
            VerificationGate.COVERAGE_AUDIT: 0.9,
            VerificationGate.TEST_SUITE: 0.95,
            VerificationGate.VISUAL_VALIDATION: 0.9
        }
        
        # Simulate gate result
        confidence = 0.95  # Mock confidence, would be calculated in real implementation
        passed = confidence >= gate_thresholds[gate]
        
        feedback = f"Gate '{gate.value}' {'PASSED' if passed else 'FAILED'} with confidence {confidence:.2f}"
        
        if passed:
            feedback += f"\n\nGate requirements met:\n"
            if gate == VerificationGate.RISK_REVIEW:
                feedback += "- All risks identified and mitigated\n- Confidence score: 10/10\n- No critical issues found"
            elif gate == VerificationGate.COVERAGE_AUDIT:
                feedback += "- 100% spec coverage achieved\n- Security audit passed\n- Code quality standards met"
            elif gate == VerificationGate.TEST_SUITE:
                feedback += "- Zero test failures\n- Zero skipped tests\n- All acceptance criteria validated"
            elif gate == VerificationGate.VISUAL_VALIDATION:
                feedback += "- 100% visual pass rate\n- All viewports validated\n- Design consistency maintained"
        else:
            feedback += f"\n\nGate requirements not met:\n"
            feedback += f"- Required confidence: {gate_thresholds[gate]:.2f}\n"
            feedback += f"- Actual confidence: {confidence:.2f}\n"
            feedback += "- Additional review needed"
        
        execution_time = time.time() - start_time
        
        return GateResult(
            gate=gate,
            passed=passed,
            confidence_score=confidence,
            feedback=feedback,
            specialist_used=specialist_name,
            execution_time=execution_time,
            details={
                "threshold": gate_thresholds[gate],
                "actual_confidence": confidence,
                "requirements_checked": ["completeness", "accuracy", "consistency"]
            }
        )
    
    def integrate_specialist_results(self, assignments: List[SpecialistAssignment],
                                   task_analysis: TaskAnalysis) -> str:
        """
        Integrate results from multiple specialist agents.
        
        Follows Universal Agent Protocol from Intent Agent Starter Kit:
        - Address Coordinator directly
        - Reference specific findings
        - Be verifiable and specific
        """
        integration = [f"# Multi-Agent Orchestration Results\n"]
        integration.append(f"## Task: {task_analysis.original_task}\n")
        integration.append(f"**Task ID:** {task_analysis.task_hash}\n")
        integration.append(f"**Complexity:** {task_analysis.complexity_score:.2f}\n")
        integration.append(f"**Risk Level:** {task_analysis.risk_level}\n")
        integration.append(f"**Estimated Effort:** {task_analysis.estimated_effort}\n\n")
        
        integration.append("## Specialist Contributions\n")
        
        for assignment in assignments:
            if assignment.status == "completed" and assignment.result:
                integration.append(f"### {assignment.specialist_name}\n")
                integration.append(f"**Subtask:** {assignment.subtask_description}\n")
                integration.append(f"**Confidence:** {assignment.confidence_score:.2f}\n")
                integration.append(f"**Time:** {assignment.execution_time:.2f}s\n")
                
                # Extract key points from result
                result_lines = assignment.result.split('\n')
                key_points = [line for line in result_lines if line.strip() and 
                             (line.startswith('- ') or line.startswith('✅ ') or 
                              line.startswith('## ') or ':' in line[:50])]
                
                if key_points:
                    integration.append("\n**Key Findings:**\n")
                    for point in key_points[:5]:  # Limit to top 5 points
                        integration.append(f"- {point}\n")
                
                integration.append("\n")
        
        integration.append("## Integrated Analysis\n")
        integration.append("The above specialist analyses have been integrated into a coherent plan.\n\n")
        
        integration.append("### Overall Assessment\n")
        integration.append("Based on multi-specialist analysis, the task is feasible with the following approach:\n")
        
        # Generate integrated recommendations
        recommendations = []
        
        # Check for architecture recommendations
        arch_assignments = [a for a in assignments if "architect" in a.specialist_name]
        if arch_assignments:
            recommendations.append("**Architecture**: Follow the designed architecture with clear separation of concerns")
        
        # Check for security recommendations
        sec_assignments = [a for a in assignments if "security" in a.specialist_name]
        if sec_assignments:
            recommendations.append("**Security**: Implement comprehensive security measures as outlined")
        
        # Check for testing recommendations
        test_assignments = [a for a in assignments if "testing" in a.specialist_name or "qa" in a.specialist_name]
        if test_assignments:
            recommendations.append("**Testing**: Follow the test strategy with automated validation")
        
        for rec in recommendations:
            integration.append(f"- {rec}\n")
        
        integration.append("\n### Next Steps\n")
        integration.append("1. Review specialist recommendations\n")
        integration.append("2. Plan implementation sequence\n")
        integration.append("3. Schedule verification gates\n")
        integration.append("4. Execute with quality assurance\n")
        
        integration.append("\n### Confidence Score\n")
        avg_confidence = sum(a.confidence_score for a in assignments if a.confidence_score > 0) / len(assignments)
        integration.append(f"**Overall Confidence:** {avg_confidence:.2f}/1.0\n")
        
        if avg_confidence >= 0.8:
            integration.append("✅ **High confidence** - Proceed with implementation\n")
        elif avg_confidence >= 0.6:
            integration.append("⚠️ **Moderate confidence** - Review recommendations before proceeding\n")
        else:
            integration.append("❌ **Low confidence** - Require additional analysis\n")
        
        return "\n".join(integration)
    
    async def execute_with_gated_workflow(self, task: str, 
                                        gates: List[VerificationGate] = None) -> OrchestrationResult:
        """
        Execute task with verification gates (Intent Agent Starter Kit pattern).
        
        Args:
            task: The task to execute
            gates: Which verification gates to run (default: all applicable)
        
        Returns:
            OrchestrationResult with gate results
        """
        start_time = time.time()
        
        # Analyze task
        task_analysis = self.analyze_task(task)
        task_id = f"task-{task_analysis.task_hash}"
        
        # Create specialist assignments
        assignments = self.create_specialist_assignments(task_analysis)
        
        # Determine which gates to run
        if gates is None:
            # Default gates based on task type
            gates = [VerificationGate.RISK_REVIEW, VerificationGate.COVERAGE_AUDIT]
            
            # Add test suite for implementation tasks
            if any("implement" in word or "develop" in word for word in task.lower().split()):
                gates.append(VerificationGate.TEST_SUITE)
            
            # Add visual validation for UI tasks
            if any("ui" in word or "design" in word or "frontend" in word for word in task.lower().split()):
                gates.append(VerificationGate.VISUAL_VALIDATION)
        
        # Execute specialist assignments
        specialist_results = {}
        for assignment in assignments:
            result = await self.execute_specialist_assignment(assignment)
            specialist_results[assignment.specialist_name] = result
        
        # Run verification gates
        gate_results = {}
        for gate in gates:
            gate_result = await self.run_verification_gate(gate, {
                "task": task,
                "task_analysis": task_analysis,
                "specialist_results": specialist_results
            })
            gate_results[gate] = gate_result
        
        # Integrate results
        completed_assignments = [a for a in assignments if a.status == "completed"]
        final_output = self.integrate_specialist_results(completed_assignments, task_analysis)
        
        # Add gate results to final output
        gate_section = ["\n## Verification Gates\n"]
        all_gates_passed = all(gate_result.passed for gate_result in gate_results.values())
        
        for gate, gate_result in gate_results.items():
            status = "✅ PASS" if gate_result.passed else "❌ FAIL"
            gate_section.append(f"### {gate.value.replace('_', ' ').title()}: {status}\n")
            gate_section.append(f"Confidence: {gate_result.confidence_score:.2f}\n")
            gate_section.append(f"Specialist: {gate_result.specialist_used}\n")
            gate_section.append(f"Time: {gate_result.execution_time:.2f}s\n")
            gate_section.append(f"Details: {gate_result.feedback}\n\n")
        
        if all_gates_passed:
            gate_section.append("🎉 **ALL GATES PASSED** - Task meets quality standards\n")
        else:
            gate_section.append("⚠️ **SOME GATES FAILED** - Review required before proceeding\n")
        
        final_output += "\n".join(gate_section)
        
        total_execution_time = time.time() - start_time
        
        # Calculate overall confidence
        specialist_confidences = [a.confidence_score for a in completed_assignments]
        gate_confidences = [gr.confidence_score for gr in gate_results.values()]
        all_confidences = specialist_confidences + gate_confidences
        
        if all_confidences:
            overall_confidence = sum(all_confidences) / len(all_confidences)
        else:
            overall_confidence = 0.5
        
        # Create result
        result = OrchestrationResult(
            task_id=task_id,
            original_task=task,
            final_output=final_output,
            specialists_used=[a.specialist_name for a in completed_assignments],
            gates_passed=[gate for gate, gr in gate_results.items() if gr.passed],
            total_execution_time=total_execution_time,
            confidence_score=overall_confidence,
            task_analysis=task_analysis,
            specialist_results={a.specialist_name: a for a in completed_assignments},
            gate_results=gate_results,
            metadata={
                "workflow_type": "gated",
                "gates_run": [g.value for g in gates],
                "all_gates_passed": all_gates_passed,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Store in history
        self.task_history.append(result)
        self.gate_history.extend(gate_results.values())
        
        return result
    
    async def execute_complex_task(self, task: str,
                                 workflow_type: WorkflowType = WorkflowType.GATED,
                                 gates: Optional[List[VerificationGate]] = None,
                                 specialist_agents: Optional[List[str]] = None) -> OrchestrationResult:
        """
        Main method to execute a complex task with multi-agent orchestration.
        
        Args:
            task: The complex task to execute
            workflow_type: Workflow type (default: gated with verification)
            gates: Which verification gates to run
            specialist_agents: Specific specialists to use (optional)
        
        Returns:
            OrchestrationResult with final output and metadata
        """
        print(f"Executing complex task: {task[:100]}...")
        print(f"Workflow type: {workflow_type.value}")
        
        if workflow_type == WorkflowType.GATED:
            return await self.execute_with_gated_workflow(task, gates)
        else:
            # For other workflow types, use simplified execution
            return await self.execute_simplified_workflow(task, workflow_type, specialist_agents)
    
    async def execute_simplified_workflow(self, task: str,
                                        workflow_type: WorkflowType,
                                        specialist_agents: Optional[List[str]] = None) -> OrchestrationResult:
        """
        Execute task with simplified workflow (without full gate system).
        """
        start_time = time.time()
        
        # Analyze task
        task_analysis = self.analyze_task(task)
        task_id = f"task-{task_analysis.task_hash}"
        
        # Filter specialists if specified
        if specialist_agents:
            assignments = []
            for spec_name in specialist_agents:
                if spec_name in self.specialist_registry:
                    assignment = SpecialistAssignment(
                        task_id=task_id,
                        specialist_name=spec_name,
                        subtask_description=f"Handle {spec_name} aspect of: {task}",
                        acceptance_criteria=["Complete analysis", "Provide recommendations"]
                    )
                    assignments.append(assignment)
        else:
            assignments = self.create_specialist_assignments(task_analysis)
        
        # Execute based on workflow type
        if workflow_type == WorkflowType.SEQUENTIAL:
            # Execute sequentially
            completed_assignments = []
            for assignment in assignments:
                result = await self.execute_specialist_assignment(assignment)
                completed_assignments.append(result)
        
        elif workflow_type == WorkflowType.PARALLEL:
            # Execute in parallel
            tasks = [self.execute_specialist_assignment(a) for a in assignments]
            results = await asyncio.gather(*tasks)
            completed_assignments = list(results)
        
        elif workflow_type == WorkflowType.HIERARCHICAL:
            # Hierarchical: architect first, then others
            arch_assignments = [a for a in assignments if "architect" in a.specialist_name]
            other_assignments = [a for a in assignments if "architect" not in a.specialist_name]
            
            # Execute architect first
            arch_results = []
            for assignment in arch_assignments:
                result = await self.execute_specialist_assignment(assignment)
                arch_results.append(result)
            
            # Then execute others
            other_results = []
            for assignment in other_assignments:
                result = await self.execute_specialist_assignment(assignment)
                other_results.append(result)
            
            completed_assignments = arch_results + other_results
        
        else:
            # Default to sequential
            completed_assignments = []
            for assignment in assignments:
                result = await self.execute_specialist_assignment(assignment)
                completed_assignments.append(result)
        
        # Integrate results
        final_output = self.integrate_specialist_results(completed_assignments, task_analysis)
        
        total_execution_time = time.time() - start_time
        
        # Calculate confidence
        confidences = [a.confidence_score for a in completed_assignments if a.confidence_score > 0]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        result = OrchestrationResult(
            task_id=task_id,
            original_task=task,
            final_output=final_output,
            specialists_used=[a.specialist_name for a in completed_assignments],
            gates_passed=[],  # No gates in simplified workflow
            total_execution_time=total_execution_time,
            confidence_score=overall_confidence,
            task_analysis=task_analysis,
            specialist_results={a.specialist_name: a for a in completed_assignments},
            gate_results={},
            metadata={
                "workflow_type": workflow_type.value,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        self.task_history.append(result)
        return result
    
    def get_specialist_recommendations(self, task: str) -> List[Tuple[str, float]]:
        """
        Get recommended specialists for a task with suitability scores.
        """
        task_analysis = self.analyze_task(task)
        
        recommendations = []
        for spec_name, specialist in self.specialist_registry.items():
            # Calculate coverage of required capabilities
            coverage = sum(1 for cap in task_analysis.required_capabilities 
                          if cap in specialist.capabilities)
            coverage_score = coverage / len(task_analysis.required_capabilities) if task_analysis.required_capabilities else 0
            
            # Factor in confidence threshold
            confidence_factor = specialist.confidence_threshold
            
            # Combined score
            score = (coverage_score * 0.7) + (confidence_factor * 0.3)
            
            if score > 0:  # Only include if some relevance
                recommendations.append((spec_name, score))
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations
    
    def save_orchestration_history(self, filepath: str) -> None:
        """Save orchestration history to file."""
        history_data = []
        for result in self.task_history:
            history_data.append({
                "task_id": result.task_id,
                "task": result.original_task,
                "specialists_used": result.specialists_used,
                "gates_passed": [g.value for g in result.gates_passed],
                "execution_time": result.total_execution_time,
                "confidence": result.confidence_score,
                "timestamp": result.metadata.get("timestamp", ""),
                "workflow_type": result.metadata.get("workflow_type", "")
            })
        
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        print(f"Saved {len(history_data)} orchestration records to {filepath}")
    
    def load_orchestration_history(self, filepath: str) -> None:
        """Load orchestration history from file."""
        try:
            with open(filepath, 'r') as f:
                history_data = json.load(f)
            
            print(f"Loaded {len(history_data)} orchestration records from {filepath}")
            # Note: This doesn't restore full OrchestrationResult objects, just metadata
        except FileNotFoundError:
            print(f"No history file found at {filepath}")
    
    def print_task_analysis(self, task: str) -> None:
        """Print detailed task analysis."""
        analysis = self.analyze_task(task)
        
        print(f"\n{'='*60}")
        print(f"TASK ANALYSIS")
        print(f"{'='*60}")
        print(f"Task: {analysis.original_task}")
        print(f"Hash: {analysis.task_hash}")
        print(f"Complexity: {analysis.complexity_score:.2f}")
        print(f"Risk Level: {analysis.risk_level}")
        print(f"Estimated Effort: {analysis.estimated_effort}")
        
        print(f"\nRequired Capabilities:")
        for cap in analysis.required_capabilities:
            print(f"  - {cap.value}")
        
        print(f"\nSuggested Specialists:")
        for spec in analysis.suggested_specialists:
            print(f"  - {spec}")
        
        print(f"\nSpecialist Recommendations:")
        recommendations = self.get_specialist_recommendations(task)
        for spec, score in recommendations[:5]:  # Top 5
            print(f"  - {spec}: {score:.2f}")
        
        print(f"{'='*60}\n")


# Example usage and demonstration
async def example_usage():
    """Demonstrate enhanced ACP orchestration with Intent Agent Starter Kit patterns."""
    
    print("Enhanced ACP Agent Protocol - Intent Agent Starter Kit Patterns")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = EnhancedACPOrchestrator()
    
    # Example tasks
    tasks = [
        "Develop a secure web application with user authentication and payment processing",
        "Create a comprehensive API documentation system with interactive examples",
        "Design a multi-agent AI system for automated code review and testing",
        "Build a scalable data pipeline for real-time analytics with monitoring"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{'#'*70}")
        print(f"EXAMPLE {i}: {task}")
        print(f"{'#'*70}")
        
        # Analyze task
        orchestrator.print_task_analysis(task)
        
        # Execute with gated workflow (Intent Agent Starter Kit pattern)
        print("Executing with GATED workflow (verification gates)...")
        result = await orchestrator.execute_complex_task(
            task=task,
            workflow_type=WorkflowType.GATED,
            gates=[VerificationGate.RISK_REVIEW, VerificationGate.COVERAGE_AUDIT]
        )
        
        print(f"\nExecution completed in {result.total_execution_time:.2f} seconds")
        print(f"Specialists used: {result.specialists_used}")
        print(f"Gates passed: {[g.value for g in result.gates_passed]}")
        print(f"Overall confidence: {result.confidence_score:.2f}")
        
        # Show snippet of final output
        print(f"\nResult snippet (first 300 chars):")
        print(result.final_output[:300] + "...")
        
        print(f"\n{'='*70}")
    
    # Save history
    orchestrator.save_orchestration_history("/tmp/acp_orchestration_history.json")
    
    print("\n" + "="*70)
    print("EXAMPLE COMPLETE")
    print("="*70)
    
    return orchestrator


async def demonstrate_specialist_coordination():
    """Demonstrate specialist coordination for a complex task."""
    
    orchestrator = EnhancedACPOrchestrator()
    
    complex_task = """
    Create a full-stack application for project management with:
    1. User authentication and authorization
    2. Real-time collaboration features
    3. File upload and management
    4. Analytics dashboard
    5. Mobile-responsive design
    6. Comprehensive testing suite
    7. Deployment pipeline
    """
    
    print("\n" + "="*70)
    print("SPECIALIST COORDINATION DEMONSTRATION")
    print("="*70)
    
    # Get specialist recommendations
    recommendations = orchestrator.get_specialist_recommendations(complex_task)
    print("\nTop 5 Specialist Recommendations:")
    for spec, score in recommendations[:5]:
        print(f"  {spec}: {score:.2f}")
    
    # Execute with selected specialists
    selected_specialists = [spec for spec, _ in recommendations[:3]]  # Top 3
    
    print(f"\nExecuting with specialists: {selected_specialists}")
    
    result = await orchestrator.execute_complex_task(
        task=complex_task,
        workflow_type=WorkflowType.HIERARCHICAL,
        specialist_agents=selected_specialists
    )
    
    print(f"\nExecution Summary:")
    print(f"  Time: {result.total_execution_time:.2f}s")
    print(f"  Confidence: {result.confidence_score:.2f}")
    print(f"  Specialists: {result.specialists_used}")
    
    # Show integrated recommendations
    print(f"\nIntegrated Recommendations:")
    lines = result.final_output.split('\n')
    recommendation_lines = [line for line in lines if '**' in line or '✅' in line or '⚠️' in line]
    for line in recommendation_lines[:10]:  # First 10 recommendation lines
        print(f"  {line}")
    
    return result


if __name__ == "__main__":
    # Run examples
    print("Enhanced ACP Agent Protocol with Intent Agent Starter Kit Patterns")
    print("=" * 70)
    
    # Run main example
    orchestrator = asyncio.run(example_usage())
    
    # Run specialist coordination demo
    asyncio.run(demonstrate_specialist_coordination())
    
    print("\n" + "="*70)
    print("All demonstrations complete")
    print("="*70)
