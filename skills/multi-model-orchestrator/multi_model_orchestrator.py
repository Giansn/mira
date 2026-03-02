"""
Multi-Model Orchestrator
Coordinates multiple AI models to complete complex tasks through task decomposition and specialized model selection.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid


class ModelCapability(Enum):
    """Capabilities that different models may have."""
    REASONING = "reasoning"          # Logical analysis, step-by-step reasoning
    CREATIVITY = "creativity"        # Idea generation, creative writing
    CODING = "coding"                # Programming, debugging, technical
    RESEARCH = "research"            # Information synthesis, citation
    ANALYSIS = "analysis"            # Data analysis, pattern recognition
    WRITING = "writing"              # Content creation, editing
    PLANNING = "planning"            # Task planning, project management
    REVIEW = "review"                # Quality assessment, critique
    SPECIALIST = "specialist"        # Domain-specific knowledge


class WorkflowType(Enum):
    """Types of multi-model workflows."""
    SEQUENTIAL = "sequential"        # Models run one after another
    PARALLEL = "parallel"            # Models run simultaneously
    HIERARCHICAL = "hierarchical"    # Master model delegates to specialists
    ENSEMBLE = "ensemble"            # Multiple models vote/combine


class TaskComplexity(Enum):
    """Complexity level of tasks."""
    SIMPLE = "simple"        # Single model sufficient
    MODERATE = "moderate"    # 2-3 models recommended
    COMPLEX = "complex"      # 3+ models with coordination
    EXTREME = "extreme"      # 5+ models with complex dependencies


@dataclass
class ModelProfile:
    """Profile of an AI model's capabilities and characteristics."""
    name: str
    capabilities: List[ModelCapability]
    max_tokens: int = 4000
    timeout_seconds: int = 120
    cost_per_token: float = 0.0
    strength_score: Dict[ModelCapability, float] = field(default_factory=dict)
    
    def get_strength(self, capability: ModelCapability) -> float:
        """Get strength score for a specific capability (0.0 to 1.0)."""
        return self.strength_score.get(capability, 0.5)
    
    def can_handle(self, required_capabilities: List[ModelCapability]) -> bool:
        """Check if model has all required capabilities."""
        return all(cap in self.capabilities for cap in required_capabilities)


@dataclass
class Subtask:
    """A decomposed part of a larger task."""
    id: str
    description: str
    required_capabilities: List[ModelCapability]
    dependencies: List[str] = field(default_factory=list)  # IDs of dependent subtasks
    assigned_model: Optional[str] = None
    result: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class TaskDecomposition:
    """Analysis of how a complex task should be decomposed."""
    original_task: str
    complexity: TaskComplexity
    subtasks: List[Subtask]
    estimated_models_needed: int
    suggested_workflow: WorkflowType
    dependencies: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ModelResult:
    """Result from a model execution."""
    model_name: str
    content: str
    execution_time: float
    tokens_used: int = 0
    confidence: float = 0.5  # Model's confidence in its output
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """Final result from multi-model orchestration."""
    original_task: str
    final_content: str
    models_used: List[str]
    execution_time: float
    subtask_results: Dict[str, ModelResult]
    confidence: float = 0.5
    workflow_type: WorkflowType = WorkflowType.SEQUENTIAL
    integration_notes: List[str] = field(default_factory=list)


class MultiModelOrchestrator:
    """Orchestrates multiple AI models to complete complex tasks."""
    
    def __init__(self):
        self.model_registry: Dict[str, ModelProfile] = {}
        self.task_history: List[OrchestrationResult] = []
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize with some default model profiles."""
        # Note: These are example profiles - actual models would be configured
        self.model_registry["claude-sonnet"] = ModelProfile(
            name="claude-sonnet",
            capabilities=[
                ModelCapability.REASONING,
                ModelCapability.ANALYSIS,
                ModelCapability.WRITING,
                ModelCapability.PLANNING,
                ModelCapability.REVIEW
            ],
            max_tokens=4000,
            timeout_seconds=120,
            strength_score={
                ModelCapability.REASONING: 0.9,
                ModelCapability.ANALYSIS: 0.8,
                ModelCapability.WRITING: 0.7,
                ModelCapability.REVIEW: 0.8
            }
        )
        
        self.model_registry["gpt-4"] = ModelProfile(
            name="gpt-4",
            capabilities=[
                ModelCapability.CREATIVITY,
                ModelCapability.CODING,
                ModelCapability.RESEARCH,
                ModelCapability.WRITING,
                ModelCapability.REVIEW
            ],
            max_tokens=8000,
            timeout_seconds=180,
            strength_score={
                ModelCapability.CREATIVITY: 0.9,
                ModelCapability.CODING: 0.8,
                ModelCapability.RESEARCH: 0.7,
                ModelCapability.REVIEW: 0.7
            }
        )
        
        self.model_registry["gemini-pro"] = ModelProfile(
            name="gemini-pro",
            capabilities=[
                ModelCapability.RESEARCH,
                ModelCapability.ANALYSIS,
                ModelCapability.SPECIALIST
            ],
            max_tokens=3000,
            timeout_seconds=90,
            strength_score={
                ModelCapability.RESEARCH: 0.8,
                ModelCapability.ANALYSIS: 0.7
            }
        )
        
        self.model_registry["llama-code"] = ModelProfile(
            name="llama-code",
            capabilities=[ModelCapability.CODING],
            max_tokens=2000,
            timeout_seconds=60,
            strength_score={ModelCapability.CODING: 0.9}
        )
    
    def analyze_task_complexity(self, task: str) -> TaskComplexity:
        """Analyze task to determine complexity level."""
        # Simple heuristic based on task length and keywords
        task_lower = task.lower()
        words = task_lower.split()
        
        complexity_indicators = {
            TaskComplexity.SIMPLE: {"simple", "quick", "brief", "explain"},
            TaskComplexity.MODERATE: {"analyze", "compare", "create", "write"},
            TaskComplexity.COMPLEX: {"comprehensive", "detailed", "research", "develop"},
            TaskComplexity.EXTREME: {"complete system", "full analysis", "comprehensive report", "end-to-end"}
        }
        
        # Check for extreme complexity indicators
        for indicator in complexity_indicators[TaskComplexity.EXTREME]:
            if indicator in task_lower:
                return TaskComplexity.EXTREME
        
        # Check word count and structure
        if len(words) <= 10:
            return TaskComplexity.SIMPLE
        elif len(words) <= 25:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.COMPLEX
    
    def decompose_task(self, task: str) -> TaskDecomposition:
        """
        Decompose a complex task into subtasks.
        
        In a real implementation, this would use an AI model to analyze the task.
        This is a simplified version with pattern matching.
        """
        complexity = self.analyze_task_complexity(task)
        task_lower = task.lower()
        
        subtasks = []
        
        # Common task patterns and their decomposition
        if "research" in task_lower and "report" in task_lower:
            # Research report pattern
            subtasks = [
                Subtask(
                    id="research",
                    description="Gather and analyze information on the topic",
                    required_capabilities=[ModelCapability.RESEARCH, ModelCapability.ANALYSIS]
                ),
                Subtask(
                    id="outline",
                    description="Create report structure and outline",
                    required_capabilities=[ModelCapability.PLANNING, ModelCapability.WRITING],
                    dependencies=["research"]
                ),
                Subtask(
                    id="write",
                    description="Write comprehensive report sections",
                    required_capabilities=[ModelCapability.WRITING, ModelCapability.CREATIVITY],
                    dependencies=["outline"]
                ),
                Subtask(
                    id="review",
                    description="Review and refine the report",
                    required_capabilities=[ModelCapability.REVIEW, ModelCapability.ANALYSIS],
                    dependencies=["write"]
                )
            ]
            workflow = WorkflowType.SEQUENTIAL
            
        elif "develop" in task_lower and ("software" in task_lower or "application" in task_lower):
            # Software development pattern
            subtasks = [
                Subtask(
                    id="requirements",
                    description="Analyze requirements and create specifications",
                    required_capabilities=[ModelCapability.ANALYSIS, ModelCapability.PLANNING]
                ),
                Subtask(
                    id="design",
                    description="Design system architecture",
                    required_capabilities=[ModelCapability.PLANNING, ModelCapability.CODING],
                    dependencies=["requirements"]
                ),
                Subtask(
                    id="implement",
                    description="Implement code according to design",
                    required_capabilities=[ModelCapability.CODING],
                    dependencies=["design"]
                ),
                Subtask(
                    id="test",
                    description="Test and debug the implementation",
                    required_capabilities=[ModelCapability.CODING, ModelCapability.REVIEW],
                    dependencies=["implement"]
                )
            ]
            workflow = WorkflowType.SEQUENTIAL
            
        elif "analyze" in task_lower and "compare" in task_lower:
            # Comparative analysis pattern
            subtasks = [
                Subtask(
                    id="research_a",
                    description="Research first item for comparison",
                    required_capabilities=[ModelCapability.RESEARCH]
                ),
                Subtask(
                    id="research_b",
                    description="Research second item for comparison",
                    required_capabilities=[ModelCapability.RESEARCH]
                ),
                Subtask(
                    id="analyze",
                    description="Compare and analyze findings",
                    required_capabilities=[ModelCapability.ANALYSIS, ModelCapability.REASONING],
                    dependencies=["research_a", "research_b"]
                ),
                Subtask(
                    id="synthesize",
                    description="Synthesize comparison results",
                    required_capabilities=[ModelCapability.WRITING, ModelCapability.ANALYSIS],
                    dependencies=["analyze"]
                )
            ]
            workflow = WorkflowType.PARALLEL  # Research can be parallel
            
        else:
            # Generic decomposition for unknown patterns
            subtasks = [
                Subtask(
                    id="plan",
                    description="Plan approach to the task",
                    required_capabilities=[ModelCapability.PLANNING, ModelCapability.REASONING]
                ),
                Subtask(
                    id="execute",
                    description="Execute the main task",
                    required_capabilities=[ModelCapability.WRITING, ModelCapability.CREATIVITY],
                    dependencies=["plan"]
                ),
                Subtask(
                    id="review",
                    description="Review and improve the result",
                    required_capabilities=[ModelCapability.REVIEW],
                    dependencies=["execute"]
                )
            ]
            workflow = WorkflowType.SEQUENTIAL
        
        # Estimate models needed based on unique capability requirements
        unique_capabilities = set()
        for subtask in subtasks:
            unique_capabilities.update(subtask.required_capabilities)
        estimated_models = min(len(unique_capabilities), len(self.model_registry))
        
        return TaskDecomposition(
            original_task=task,
            complexity=complexity,
            subtasks=subtasks,
            estimated_models_needed=estimated_models,
            suggested_workflow=workflow
        )
    
    def select_model_for_subtask(self, subtask: Subtask) -> Optional[str]:
        """
        Select the best model for a given subtask based on capabilities and strengths.
        """
        suitable_models = []
        
        for model_name, profile in self.model_registry.items():
            if profile.can_handle(subtask.required_capabilities):
                # Calculate suitability score
                score = sum(
                    profile.get_strength(cap) * 0.5  # Weight by capability importance
                    for cap in subtask.required_capabilities
                ) / len(subtask.required_capabilities)
                
                suitable_models.append((model_name, score, profile))
        
        if not suitable_models:
            return None
        
        # Select model with highest score
        suitable_models.sort(key=lambda x: x[1], reverse=True)
        return suitable_models[0][0]
    
    async def execute_subtask(self, subtask: Subtask, model_name: str) -> ModelResult:
        """
        Execute a subtask using the specified model.
        
        In a real implementation, this would call the actual model API.
        This is a mock implementation.
        """
        subtask.status = "running"
        subtask.start_time = time.time()
        
        # Simulate model execution
        await asyncio.sleep(0.5)  # Simulate API call
        
        # Mock response based on subtask type
        if "research" in subtask.description.lower():
            content = f"Research findings for: {subtask.description}\n\nKey points:\n1. Important information gathered\n2. Analysis completed\n3. Sources identified"
        elif "write" in subtask.description.lower():
            content = f"Written content for: {subtask.description}\n\nThis section provides comprehensive coverage of the topic with clear explanations and examples."
        elif "code" in subtask.description.lower() or "implement" in subtask.description.lower():
            content = f"Code implementation for: {subtask.description}\n\n```python\ndef solution():\n    # Implementation here\n    return result\n```"
        elif "analyze" in subtask.description.lower():
            content = f"Analysis for: {subtask.description}\n\nDetailed analysis with insights and recommendations."
        else:
            content = f"Completed: {subtask.description}\n\nTask executed successfully with appropriate results."
        
        execution_time = time.time() - subtask.start_time
        
        subtask.status = "completed"
        subtask.end_time = time.time()
        subtask.result = content
        
        return ModelResult(
            model_name=model_name,
            content=content,
            execution_time=execution_time,
            tokens_used=len(content.split()) * 1.3,  # Rough estimate
            confidence=0.8  # Mock confidence
        )
    
    async def execute_sequential_workflow(self, decomposition: TaskDecomposition) -> OrchestrationResult:
        """Execute subtasks sequentially."""
        start_time = time.time()
        subtask_results = {}
        models_used = set()
        
        for subtask in decomposition.subtasks:
            # Wait for dependencies
            for dep_id in subtask.dependencies:
                if dep_id not in subtask_results:
                    # Dependency not completed - this shouldn't happen with proper scheduling
                    continue
            
            # Select and execute model
            model_name = self.select_model_for_subtask(subtask)
            if not model_name:
                raise ValueError(f"No suitable model found for subtask: {subtask.description}")
            
            result = await self.execute_subtask(subtask, model_name)
            subtask_results[subtask.id] = result
            models_used.add(model_name)
        
        # Integrate results
        final_content = self._integrate_sequential_results(subtask_results, decomposition)
        
        return OrchestrationResult(
            original_task=decomposition.original_task,
            final_content=final_content,
            models_used=list(models_used),
            execution_time=time.time() - start_time,
            subtask_results=subtask_results,
            workflow_type=WorkflowType.SEQUENTIAL,
            confidence=0.7
        )
    
    async def execute_parallel_workflow(self, decomposition: TaskDecomposition) -> OrchestrationResult:
        """Execute independent subtasks in parallel."""
        start_time = time.time()
        
        # Group subtasks by dependency level
        independent_tasks = [st for st in decomposition.subtasks if not st.dependencies]
        dependent_tasks = [st for st in decomposition.subtasks if st.dependencies]
        
        # Execute independent tasks in parallel
        independent_results = {}
        models_used = set()
        
        if independent_tasks:
            # Create tasks for parallel execution
            tasks = []
            for subtask in independent_tasks:
                model_name = self.select_model_for_subtask(subtask)
                if model_name:
                    tasks.append(self.execute_subtask(subtask, model_name))
                    models_used.add(model_name)
            
            # Execute in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    subtask_id = independent_tasks[i].id
                    independent_results[subtask_id] = result
        
        # Execute dependent tasks (simplified - would need proper dependency resolution)
        dependent_results = {}
        for subtask in dependent_tasks:
            # Check if dependencies are met
            deps_met = all(dep_id in independent_results for dep_id in subtask.dependencies)
            if deps_met:
                model_name = self.select_model_for_subtask(subtask)
                if model_name:
                    result = await self.execute_subtask(subtask, model_name)
                    dependent_results[subtask.id] = result
                    models_used.add(model_name)
        
        # Combine all results
        all_results = {**independent_results, **dependent_results}
        
        # Integrate results
        final_content = self._integrate_parallel_results(all_results, decomposition)
        
        return OrchestrationResult(
            original_task=decomposition.original_task,
            final_content=final_content,
            models_used=list(models_used),
            execution_time=time.time() - start_time,
            subtask_results=all_results,
            workflow_type=WorkflowType.PARALLEL,
            confidence=0.7
        )
    
    def _integrate_sequential_results(self, results: Dict[str, ModelResult], 
                                    decomposition: TaskDecomposition) -> str:
        """Integrate results from sequential workflow."""
        integration = [f"# Task: {decomposition.original_task}\n"]
        integration.append(f"## Multi-Model Orchestration Results\n")
        integration.append(f"Workflow: {decomposition.suggested_workflow.value}\n")
        integration.append(f"Complexity: {decomposition.complexity.value}\n\n")
        
        for subtask in decomposition.subtasks:
            if subtask.id in results:
                result = results[subtask.id]
                integration.append(f"### {subtask.description}\n")
                integration.append(f"*Model: {result.model_name}*\n")
                integration.append(f"{result.content}\n\n")
        
        integration.append("## Final Synthesis\n")
        integration.append("The above sections were generated by specialized AI models working in sequence. ")
        integration.append("Each model contributed its strengths to different parts of the task.\n")
        
        return "\n".join(integration)
    
    def _integrate_parallel_results(self, results: Dict[str, ModelResult],
                                  decomposition: TaskDecomposition) -> str:
        """Integrate results from parallel workflow."""
        integration = [f"# Task: {decomposition.original_task}\n"]
        integration.append(f"## Parallel Multi-Model Results\n")
        integration.append(f"Workflow: {decomposition.suggested_workflow.value}\n")
        integration.append(f"Complexity: {decomposition.complexity.value}\n\n")
        
        integration.append("## Component Results\n")
        for subtask_id, result in results.items():
            # Find subtask description
            subtask_desc = next((st.description for st in decomposition.subtasks 
                               if st.id == subtask_id), subtask_id)
            integration.append(f"### {subtask_desc}\n")
            integration.append(f"*Model: {result.model_name}*\n")
            integration.append(f"{result.content}\n\n")
        
        integration.append("## Integrated Analysis\n")
        integration.append("The components above were generated in parallel by specialized models. ")
        integration.append("Below is the synthesized analysis combining all parallel results:\n\n")
        
        # Simple synthesis of all content
        all_content = "\n".join(r.content for r in results.values())
        integration.append(f"Synthesis: {all_content[:500]}...\n")
        
        return "\n".join(integration)
    
    def get_model_recommendations(self, task: str) -> List[Tuple[str, float]]:
        """
        Get recommended models for a task with suitability scores.
        
        Returns:
            List of (model_name, suitability_score) tuples
        """
        decomposition = self.decompose_task(task)
        
        # Collect all required capabilities across subtasks
        all_capabilities = set()
        for subtask in decomposition.subtasks:
            all_capabilities.update(subtask.required_capabilities)
        
        recommendations = []
        for model_name, profile in self.model_registry.items():
            # Calculate coverage score
            coverage = sum(1 for cap in all_capabilities 
                          if profile.can_handle([cap])) / len(all_capabilities)
            
            # Calculate strength score
            strength = sum(profile.get_strength(cap) for cap in all_capabilities 
                          if cap in profile.capabilities)
            if any(cap in profile.capabilities for cap in all_capabilities):
                strength /= sum(1 for cap in all_capabilities if cap in profile.capabilities)
            else:
                strength = 0
            
            # Combined score
            score = (coverage * 0.6) + (strength * 0.4)
            recommendations.append((model_name, score))
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations
    
    async def execute_complex_task(self, task: str, 
                                 workflow_type: Optional[WorkflowType] = None,
                                 available_models: Optional[List[str]] = None) -> OrchestrationResult:
        """
        Main method to execute a complex task using multi-model orchestration.
        
        Args:
            task: The complex task to execute
            workflow_type: Optional workflow type override
            available_models: Optional list of model names to use
            
        Returns:
            OrchestrationResult with final output and metadata
        """
        # Filter model registry if specific models requested
        if available_models:
            filtered_registry = {name: profile for name, profile in self.model_registry.items()
                               if name in available_models}
            original_registry = self.model_registry
            self.model_registry = filtered_registry
        else:
            original_registry = None
        
        try:
            # Analyze and decompose task
            decomposition = self.decompose_task(task)
            
            # Use suggested workflow if not specified
            if not workflow_type:
                workflow_type = decomposition.suggested_workflow
            
            # Execute based on workflow type
            if workflow_type == WorkflowType.SEQUENTIAL:
                result = await self.execute_sequential_workflow(decomposition)
            elif workflow_type == WorkflowType.PARALLEL:
                result = await self.execute_parallel_workflow(decomposition)
            else:
                # Default to sequential for other types (simplified)
                result = await self.execute_sequential_workflow(decomposition)
            
            # Store in history
            self.task_history.append(result)
            
            return result
            
        finally:
            # Restore original model registry if we filtered it
            if original_registry:
                self.model_registry = original_registry
    
    def save_orchestration_history(self, filepath: str) -> None:
        """Save orchestration history to file."""
        history_data = []
        for result in self.task_history:
            history_data.append({
                "task": result.original_task,
                "models_used": result.models_used,
                "execution_time": result.execution_time,
                "workflow_type": result.workflow_type.value,
                "confidence": result.confidence,
                "timestamp": time.time()
            })
        
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
    
    def load_orchestration_history(self, filepath: str) -> None:
        """Load orchestration history from file."""
        try:
            with open(filepath, 'r') as f:
                history_data = json.load(f)
            
            print(f"Loaded {len(history_data)} orchestration records from {filepath}")
        except FileNotFoundError:
            print(f"No history file found at {filepath}")


# Example usage
async def example_usage():
    """Demonstrate multi-model orchestration."""
    orchestrator = MultiModelOrchestrator()
    
    # Complex task example
    task = "Create a comprehensive market analysis report for quantum computing startups"
    
    print(f"Task: {task}")
    
    # Get model recommendations
    recommendations = orchestrator.get_model_recommendations(task)
    print("\nModel Recommendations:")
    for model, score in recommendations:
        print(f"  {model}: {score:.2f}")
    
    # Execute task
    result = await orchestrator.execute_complex_task(
        task=task,
        workflow_type=WorkflowType.SEQUENTIAL
    )
    
    print(f"\nExecution completed in {result.execution_time:.2f} seconds")
    print(f"Models used: {result.models_used}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"\nFirst 500 chars of result:\n{result.final_content[:500]}...")
    
    return result


if __name__ == "__main__":
    # Run example
    result = asyncio.run(example_usage())