---
name: multi-model-orchestrator
description: Orchestrates multiple AI models to complete complex tasks through task decomposition, model specialization, and result integration.
user-invocable: true
---

# Multi-Model Orchestrator

Coordinates multiple AI models to accomplish complex tasks that no single model can handle alone.

## Architecture

### 1. Task Analysis & Decomposition
- Analyzes complex tasks to identify required capabilities
- Breaks tasks into manageable subtasks
- Determines optimal model for each subtask

### 2. Model Registry & Specialization
- Maintains registry of available models with capabilities
- Maps subtasks to appropriate models based on strengths
- Handles model switching and fallback strategies

### 3. Workflow Coordination
- Manages sequential, parallel, and hierarchical workflows
- Handles dependencies between subtasks
- Monitors progress and handles failures

### 4. Result Integration
- Combines outputs from multiple models
- Resolves conflicts between model outputs
- Synthesizes final coherent result

## Model Capabilities Mapping

| Model Type | Strengths | Use Cases |
|------------|-----------|-----------|
| **Reasoning Models** | Logical analysis, step-by-step reasoning | Problem solving, planning, analysis |
| **Creative Models** | Idea generation, writing, design | Content creation, brainstorming |
| **Technical Models** | Coding, debugging, technical explanation | Programming, system design |
| **Research Models** | Information synthesis, citation | Research, fact-checking |
| **Specialist Models** | Domain-specific knowledge | Legal, medical, financial tasks |

## Workflow Patterns

### Sequential Chain
```
Input → Model A (Analysis) → Model B (Execution) → Model C (Review) → Output
```

### Parallel Processing
```
Input → [Model A, Model B, Model C] → Integration → Output
```

### Hierarchical Delegation
```
Master Model (Coordination)
    ├── Specialist A (Subtask 1)
    ├── Specialist B (Subtask 2)
    └── Specialist C (Subtask 3)
```

## Usage

```python
from multi_model_orchestrator import MultiModelOrchestrator

# Initialize orchestrator
orchestrator = MultiModelOrchestrator()

# Define complex task
task = "Create a comprehensive market analysis report for quantum computing startups"

# Execute with multi-model orchestration
result = orchestrator.execute_complex_task(
    task=task,
    workflow_type="hierarchical",
    available_models=["claude-sonnet", "gpt-4", "gemini-pro", "llama-code"]
)

print(f"Result: {result.content}")
print(f"Models used: {result.models_used}")
print(f"Confidence: {result.confidence}")
```

## Integration with Existing Systems

1. **OpenClaw Models**: Uses available OpenClaw model configurations
2. **Perplexity-Inspired**: Integrates query analysis and source tracking
3. **Async Agent Pattern**: Handles long-running multi-model workflows
4. **Memory System**: Maintains context across model transitions

## Error Handling & Fallbacks

- **Model failures**: Automatic fallback to alternative models
- **Timeout management**: Configurable timeouts per model/subtask
- **Quality validation**: Cross-checking between model outputs
- **Progress tracking**: Resume interrupted workflows

## Configuration

```yaml
models:
  claude-sonnet:
    capabilities: [reasoning, analysis, writing]
    max_tokens: 4000
    timeout: 120
  
  gpt-4:
    capabilities: [creativity, coding, research]
    max_tokens: 8000
    timeout: 180
  
  gemini-pro:
    capabilities: [multimodal, technical, fast]
    max_tokens: 3000
    timeout: 90

workflows:
  sequential:
    default_timeout: 600
    retry_attempts: 2
  
  parallel:
    max_concurrent: 3
    integration_method: "consensus"
```

## Example Use Cases

### 1. Research Paper Writing
- Model A: Research and gather sources
- Model B: Outline structure
- Model C: Write sections
- Model D: Review and cite

### 2. Software Development
- Model A: Requirements analysis
- Model B: Architecture design
- Model C: Code implementation
- Model D: Testing and debugging

### 3. Business Analysis
- Model A: Market research
- Model B: Financial analysis
- Model C: Risk assessment
- Model D: Report synthesis

## Performance Considerations

- **Cost optimization**: Use cheaper models for simple subtasks
- **Latency management**: Parallelize independent subtasks
- **Token efficiency**: Minimize context passing between models
- **Quality vs speed**: Configurable trade-offs

## Inspired By

Perplexity Computer's approach to using multiple models for comprehensive task completion, combining specialized capabilities for optimal results.