#!/usr/bin/env python3
"""
Basic usage example for Multi-Model Orchestrator.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_model_orchestrator import MultiModelOrchestrator, WorkflowType


async def main():
    """Demonstrate multi-model orchestration."""
    print("=== Multi-Model Orchestrator Demo ===\n")
    
    # Initialize orchestrator
    orchestrator = MultiModelOrchestrator()
    
    # Example complex tasks
    complex_tasks = [
        "Create a comprehensive market analysis report for quantum computing startups",
        "Develop a full-stack web application for task management with user authentication",
        "Research and compare different machine learning frameworks for image classification",
        "Write a technical white paper on blockchain scalability solutions",
        "Design and implement a recommendation system for e-commerce"
    ]
    
    for i, task in enumerate(complex_tasks[:2], 1):  # Just demo first 2
        print(f"\n{'='*60}")
        print(f"Task {i}: {task}")
        print(f"{'='*60}")
        
        # Get model recommendations
        recommendations = orchestrator.get_model_recommendations(task)
        print("\nModel Recommendations:")
        for model, score in recommendations[:3]:  # Top 3
            print(f"  • {model}: {score:.2f}")
        
        # Analyze task complexity
        decomposition = orchestrator.decompose_task(task)
        print(f"\nTask Analysis:")
        print(f"  Complexity: {decomposition.complexity.value}")
        print(f"  Subtasks: {len(decomposition.subtasks)}")
        print(f"  Suggested workflow: {decomposition.suggested_workflow.value}")
        
        print("\nSubtask Breakdown:")
        for j, subtask in enumerate(decomposition.subtasks, 1):
            print(f"  {j}. {subtask.description}")
            print(f"     Capabilities needed: {[c.value for c in subtask.required_capabilities]}")
            if subtask.dependencies:
                print(f"     Dependencies: {subtask.dependencies}")
        
        # Execute with sequential workflow
        print(f"\nExecuting with {decomposition.suggested_workflow.value} workflow...")
        result = await orchestrator.execute_complex_task(
            task=task,
            workflow_type=decomposition.suggested_workflow
        )
        
        print(f"\nExecution Results:")
        print(f"  Time: {result.execution_time:.2f} seconds")
        print(f"  Models used: {', '.join(result.models_used)}")
        print(f"  Confidence: {result.confidence:.2f}")
        
        # Show subtask results
        print(f"\nSubtask Results:")
        for subtask_id, model_result in result.subtask_results.items():
            print(f"  • {subtask_id}: {model_result.model_name} "
                  f"({model_result.execution_time:.2f}s, "
                  f"confidence: {model_result.confidence:.2f})")
        
        # Show preview of final content
        print(f"\nFinal Output Preview:")
        preview = result.final_content[:300] + "..." if len(result.final_content) > 300 else result.final_content
        print(f"{preview}\n")
    
    # Save history
    orchestrator.save_orchestration_history("/tmp/multi_model_history.json")
    print(f"\nOrchestration history saved to /tmp/multi_model_history.json")
    
    # Demonstrate model selection for a specific task
    print(f"\n{'='*60}")
    print("Model Selection Example")
    print(f"{'='*60}")
    
    coding_task = "Implement a Python REST API with authentication and database integration"
    print(f"\nTask: {coding_task}")
    
    recommendations = orchestrator.get_model_recommendations(coding_task)
    print("\nTop models for coding task:")
    for model, score in recommendations[:5]:
        capabilities = orchestrator.model_registry[model].capabilities
        cap_str = ", ".join([c.value for c in capabilities[:3]])
        print(f"  • {model}: {score:.2f} ({cap_str})")
    
    return orchestrator


if __name__ == "__main__":
    # Run async main
    orchestrator = asyncio.run(main())