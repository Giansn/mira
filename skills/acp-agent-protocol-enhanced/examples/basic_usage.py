"""
Basic Usage Examples for Enhanced ACP Agent Protocol

This file demonstrates how to use the enhanced ACP skill with
Intent Agent Starter Kit patterns for multi-agent orchestration.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acp_enhanced import (
    EnhancedACPOrchestrator,
    WorkflowType,
    VerificationGate
)


async def example_simple_task():
    """Example 1: Simple task with automatic specialist selection."""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Task with Automatic Specialist Selection")
    print("="*70)
    
    orchestrator = EnhancedACPOrchestrator()
    
    task = "Design a REST API for a todo list application"
    
    print(f"\nTask: {task}")
    
    # Analyze the task
    analysis = orchestrator.analyze_task(task)
    print(f"\nTask Analysis:")
    print(f"  Complexity: {analysis.complexity_score:.2f}")
    print(f"  Risk Level: {analysis.risk_level}")
    print(f"  Required Capabilities: {[c.value for c in analysis.required_capabilities]}")
    print(f"  Suggested Specialists: {analysis.suggested_specialists}")
    
    # Get specialist recommendations
    recommendations = orchestrator.get_specialist_recommendations(task)
    print(f"\nSpecialist Recommendations:")
    for spec, score in recommendations[:3]:
        print(f"  {spec}: {score:.2f}")
    
    # Execute with gated workflow
    print(f"\nExecuting with GATED workflow...")
    result = await orchestrator.execute_complex_task(
        task=task,
        workflow_type=WorkflowType.GATED,
        gates=[VerificationGate.RISK_REVIEW, VerificationGate.COVERAGE_AUDIT]
    )
    
    print(f"\nExecution Complete:")
    print(f"  Time: {result.total_execution_time:.2f}s")
    print(f"  Specialists Used: {result.specialists_used}")
    print(f"  Gates Passed: {[g.value for g in result.gates_passed]}")
    print(f"  Confidence: {result.confidence_score:.2f}")
    
    # Show key findings
    print(f"\nKey Findings:")
    lines = result.final_output.split('\n')
    key_lines = [line for line in lines if line.startswith('- ') or line.startswith('✅') or line.startswith('⚠️')]
    for line in key_lines[:5]:
        print(f"  {line}")
    
    return result


async def example_complex_development_task():
    """Example 2: Complex development task with multiple specialists."""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Complex Development Task")
    print("="*70)
    
    orchestrator = EnhancedACPOrchestrator()
    
    task = """
    Develop a secure e-commerce platform with:
    - User authentication and authorization
    - Product catalog with search and filtering
    - Shopping cart and checkout process
    - Payment integration (Stripe/PayPal)
    - Order management system
    - Admin dashboard
    - Comprehensive testing suite
    - Deployment to cloud (AWS/GCP)
    """
    
    print(f"\nTask: {task[:100]}...")
    
    # Use specific specialists
    specialists = [
        "lead-architect",
        "security-specialist", 
        "qa-engineer",
        "devops-engineer"
    ]
    
    print(f"\nUsing Specialists: {specialists}")
    
    # Execute with hierarchical workflow
    result = await orchestrator.execute_complex_task(
        task=task,
        workflow_type=WorkflowType.HIERARCHICAL,
        specialist_agents=specialists
    )
    
    print(f"\nExecution Complete:")
    print(f"  Time: {result.total_execution_time:.2f}s")
    print(f"  Specialists Used: {result.specialists_used}")
    print(f"  Confidence: {result.confidence_score:.2f}")
    
    # Show architecture recommendations
    print(f"\nArchitecture Recommendations:")
    lines = result.final_output.split('\n')
    arch_lines = []
    in_arch_section = False
    for line in lines:
        if "Architecture" in line and "##" in line:
            in_arch_section = True
        elif in_arch_section and "##" in line and "Architecture" not in line:
            in_arch_section = False
        
        if in_arch_section and line.strip():
            arch_lines.append(line)
    
    for line in arch_lines[:10]:
        print(f"  {line}")
    
    return result


async def example_research_and_analysis():
    """Example 3: Research and analysis task."""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Research and Analysis Task")
    print("="*70)
    
    orchestrator = EnhancedACPOrchestrator()
    
    task = """
    Research and analyze the current landscape of AI coding assistants.
    Compare Claude Code, GitHub Copilot, Codeium, and Tabnine.
    Provide recommendations for enterprise adoption.
    """
    
    print(f"\nTask: {task}")
    
    # Use research-focused specialists
    specialists = [
        "research-analyst",
        "ai-agent-architect",
        "technical-writer"
    ]
    
    # Execute with parallel workflow
    result = await orchestrator.execute_complex_task(
        task=task,
        workflow_type=WorkflowType.PARALLEL,
        specialist_agents=specialists
    )
    
    print(f"\nExecution Complete:")
    print(f"  Time: {result.total_execution_time:.2f}s")
    print(f"  Specialists Used: {result.specialists_used}")
    print(f"  Confidence: {result.confidence_score:.2f}")
    
    # Show research findings
    print(f"\nResearch Findings Summary:")
    lines = result.final_output.split('\n')
    summary_lines = []
    collecting = False
    
    for i, line in enumerate(lines):
        if "## Integrated Analysis" in line or "## Overall Assessment" in line:
            collecting = True
        elif collecting and line.strip() and "##" not in line:
            summary_lines.append(line)
        elif collecting and "##" in line and "Integrated Analysis" not in line:
            collecting = False
    
    for line in summary_lines[:8]:
        print(f"  {line}")
    
    return result


async def example_with_custom_gates():
    """Example 4: Task with custom verification gates."""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Task with Custom Verification Gates")
    print("="*70)
    
    orchestrator = EnhancedACPOrchestrator()
    
    task = "Create a responsive dashboard for monitoring system metrics"
    
    print(f"\nTask: {task}")
    
    # Define custom gates based on task requirements
    custom_gates = [
        VerificationGate.RISK_REVIEW,      # Always include risk review
        VerificationGate.VISUAL_VALIDATION, # Important for UI tasks
        VerificationGate.TEST_SUITE        # Testing for functionality
    ]
    
    print(f"\nCustom Gates: {[g.value for g in custom_gates]}")
    
    # Execute with custom gates
    result = await orchestrator.execute_complex_task(
        task=task,
        workflow_type=WorkflowType.GATED,
        gates=custom_gates
    )
    
    print(f"\nExecution Complete:")
    print(f"  Time: {result.total_execution_time:.2f}s")
    print(f"  Specialists Used: {result.specialists_used}")
    print(f"  Gates Run: {[g.value for g in result.gate_results.keys()]}")
    print(f"  Gates Passed: {[g.value for g in result.gates_passed]}")
    print(f"  All Gates Passed: {all(gr.passed for gr in result.gate_results.values())}")
    print(f"  Confidence: {result.confidence_score:.2f}")
    
    # Show gate results
    print(f"\nGate Results:")
    for gate, gate_result in result.gate_results.items():
        status = "✅ PASS" if gate_result.passed else "❌ FAIL"
        print(f"  {gate.value}: {status} (confidence: {gate_result.confidence_score:.2f})")
    
    return result


async def example_integration_with_openclaw():
    """Example 5: Integration with OpenClaw sessions and memory."""
    
    print("\n" + "="*70)
    print("EXAMPLE 5: Integration with OpenClaw")
    print("="*70)
    
    orchestrator = EnhancedACPOrchestrator()
    
    # Simulate OpenClaw integration
    task = "Implement a feature to save orchestration results to OpenClaw memory"
    
    print(f"\nTask: {task}")
    
    # This would integrate with actual OpenClaw tools
    print("\nSimulating OpenClaw Integration:")
    print("  1. sessions_spawn() - Create ACP sessions for specialists")
    print("  2. sessions_list() - Monitor specialist sessions")
    print("  3. sessions_send() - Send tasks to specialist sessions")
    print("  4. memory_search() - Search for related patterns in memory")
    print("  5. memory_get() - Retrieve relevant context")
    print("  6. memory_update() - Save orchestration results")
    
    # Execute task
    result = await orchestrator.execute_complex_task(
        task=task,
        workflow_type=WorkflowType.GATED
    )
    
    print(f"\nExecution Complete:")
    print(f"  Time: {result.total_execution_time:.2f}s")
    print(f"  Specialists Used: {result.specialists_used}")
    
    # Simulate saving to OpenClaw memory
    print(f"\nSimulating Memory Operations:")
    print(f"  Would save to: ~/.openclaw/workspace/memory/acp_orchestration/{result.task_id}.json")
    print(f"  Would update: ~/.openclaw/workspace/MEMORY.md with orchestration insights")
    
    # Save actual history
    history_path = "/tmp/openclaw_integration_demo.json"
    orchestrator.save_orchestration_history(history_path)
    print(f"  Saved history to: {history_path}")
    
    return result


async def main():
    """Run all examples."""
    
    print("Enhanced ACP Agent Protocol - Usage Examples")
    print("=" * 70)
    print("Demonstrating Intent Agent Starter Kit patterns for OpenClaw ACP")
    print("=" * 70)
    
    results = []
    
    # Run examples
    print("\nRunning Example 1...")
    results.append(await example_simple_task())
    
    print("\nRunning Example 2...")
    results.append(await example_complex_development_task())
    
    print("\nRunning Example 3...")
    results.append(await example_research_and_analysis())
    
    print("\nRunning Example 4...")
    results.append(await example_with_custom_gates())
    
    print("\nRunning Example 5...")
    results.append(await example_integration_with_openclaw())
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    total_time = sum(r.total_execution_time for r in results)
    avg_confidence = sum(r.confidence_score for r in results) / len(results)
    
    print(f"Total Examples Run: {len(results)}")
    print(f"Total Execution Time: {total_time:.2f}s")
    print(f"Average Confidence: {avg_confidence:.2f}")
    
    # Specialist usage statistics
    all_specialists = []
    for result in results:
        all_specialists.extend(result.specialists_used)
    
    from collections import Counter
    specialist_counts = Counter(all_specialists)
    
    print(f"\nSpecialist Usage:")
    for spec, count in specialist_counts.most_common():
        print(f"  {spec}: {count} times")
    
    print(f"\nGate Success Rate:")
    gate_results = []
    for result in results:
        gate_results.extend(result.gate_results.values())
    
    if gate_results:
        passed_gates = sum(1 for gr in gate_results if gr.passed)
        total_gates = len(gate_results)
        success_rate = passed_gates / total_gates if total_gates > 0 else 0
        print(f"  Gates Passed: {passed_gates}/{total_gates} ({success_rate:.1%})")
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70)
    
    return results


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())