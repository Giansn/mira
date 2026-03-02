---
name: code-generation-analysis
description: "Code generation and analysis skill - automated code review, generation, refactoring, and bug detection"
trigger: "code"
---

# Code Generation & Analysis Skill

## Overview

A comprehensive code skill for generating, analyzing, reviewing, and refactoring code across multiple programming languages. Uses multi-model orchestration for specialized code tasks.

## Trigger Phrases

The skill activates when messages contain:
- "code" (as verb: "code X", "generate code for Y")
- "write code"
- "review code"
- "analyze code"
- "refactor"
- "debug"
- "fix code"
- "implement"
- "develop"
- "program"

## Architecture

### 1. Code Pipeline
```
Code Request → Language Detection → Multi-Model Orchestration → Code Generation/Analysis → Review → Output
```

### 2. Model Coordination
- **Planning Phase:** claude-sonnet (reasoning + planning)
- **Generation Phase:** gpt-4 (creativity + coding)
- **Analysis Phase:** llama-code (specialized coding)
- **Review Phase:** claude-sonnet (review + security)
- **Optimization Phase:** gpt-4 (performance + best practices)

### 3. Supported Languages
- **Primary:** Python, JavaScript/TypeScript, Java, C++, Go, Rust
- **Web:** HTML/CSS, React, Vue, Angular
- **Scripting:** Bash, PowerShell, SQL
- **Configuration:** YAML, JSON, XML, Dockerfile, Kubernetes

## Usage

### Code Generation
```
User: "code a Python REST API with authentication"
→ Skill triggers
→ Multi-model orchestration executes
→ Returns complete implementation with documentation
```

### Code Review
```
User: "review this Python code for security issues"
→ Skill triggers with code analysis
→ Security vulnerability detection
→ Returns detailed review with recommendations
```

### Code Refactoring
```
User: "refactor this JavaScript function for better performance"
→ Skill triggers with performance analysis
→ Identifies bottlenecks
→ Returns optimized version with benchmarks
```

### Bug Detection
```
User: "find bugs in this code snippet"
→ Skill triggers with debugging analysis
→ Identifies logical errors, edge cases
→ Returns bug report with fixes
```

## Implementation

### Core Components

1. **`code_skill.py`** - Main skill handler
2. **`code_generator.py`** - Code generation with templates
3. **`code_analyzer.py`** - Static analysis and review
4. **`code_refactorer.py`** - Refactoring and optimization
5. **`language_detector.py`** - Programming language identification

### Integration Points

- **Multi-Model Orchestrator** - Coordinates AI models for code tasks
- **Research Skill** - For researching coding patterns and best practices
- **Async Agent Pattern** - Long-running code analysis tasks
- **Memory System** - Store and retrieve code patterns and solutions

## Code Methodology

### 1. Requirements Analysis
- Parse code requirements
- Identify language and framework
- Determine complexity level
- Set quality standards

### 2. Code Generation Process
- Template selection
- Pattern application
- Best practices integration
- Documentation generation

### 3. Analysis & Review
- Static code analysis
- Security vulnerability scanning
- Performance benchmarking
- Style consistency checking
- Dependency analysis

### 4. Refactoring Process
- Code smell detection
- Performance optimization
- Architecture improvement
- Test coverage enhancement
- Documentation update

## Output Formats

### Generated Code
```language
# Complete implementation with:
# - Proper structure
# - Error handling
# - Documentation
# - Tests (when applicable)
# - Configuration
```

### Code Review Report
```
# Code Review: [filename/language]

## Summary
Overall assessment and score

## Security Issues
1. Issue 1 with severity and fix
2. Issue 2 with severity and fix

## Performance Issues
1. Bottleneck 1 with optimization
2. Bottleneck 2 with optimization

## Style & Best Practices
1. Violation 1 with correction
2. Violation 2 with correction

## Recommendations
- Immediate fixes (critical)
- Recommended improvements (medium)
- Nice-to-have enhancements (low)

## Review Metadata
- Lines reviewed: [count]
- Issues found: [count]
- Estimated fix time: [duration]
- Confidence score: [0.0-1.0]
```

### Bug Report
```
# Bug Analysis: [description]

## Bug Details
- Type: [logical error, runtime error, security issue, etc.]
- Severity: [critical, high, medium, low]
- Location: [file:line]
- Impact: [what breaks]

## Root Cause Analysis
Explanation of why bug occurs

## Reproduction Steps
1. Step 1
2. Step 2
3. Step 3

## Fix
```language
# Corrected code
```

## Prevention
How to avoid similar bugs in future
```

## Configuration

### Code Quality Standards
1. **Basic** - Functional correctness only
2. **Standard** - + Error handling + Documentation
3. **Production** - + Security + Performance + Tests
4. **Enterprise** - All standards + compliance + auditing

### Analysis Depth
1. **Quick** - Surface-level issues only
2. **Standard** - Comprehensive analysis
3. **Deep** - In-depth with performance profiling
4. **Security** - Focus on vulnerabilities and threats

## Examples

### Example 1: API Generation
```
User: "code a Flask REST API with JWT authentication and SQLite"
→ Triggers code skill
→ Uses: planning → generation → review
→ Returns: Complete Flask app with auth, database, tests
```

### Example 2: Security Review
```
User: "review this smart contract for vulnerabilities"
→ Triggers code skill with security focus
→ Uses: analysis (security) → review
→ Returns: Security audit with vulnerability report
```

### Example 3: Performance Refactoring
```
User: "optimize this data processing function for speed"
→ Triggers code skill with performance focus
→ Uses: analysis (performance) → refactoring
→ Returns: Optimized version with benchmark comparison
```

### Example 4: Bug Hunting
```
User: "find why this function returns wrong results"
→ Triggers code skill with debugging focus
→ Uses: analysis (debugging) → bug detection
→ Returns: Bug identification with fix
```

## Integration with Existing Workflow

### Project Integration
- Link to thesis coding projects
- Track code quality over time
- Generate documentation
- Maintain code standards

### Development Pipeline
1. **Planning** → Requirements analysis
2. **Generation** → Initial implementation
3. **Review** → Quality assurance
4. **Refactoring** → Optimization
5. **Documentation** → Knowledge transfer

### Heartbeat Integration
Code tasks can be scheduled via heartbeat for:
- Daily code reviews
- Weekly refactoring sessions
- Ongoing project development
- Security scanning

## Quality Assurance

### Validation Methods
1. **Syntax checking** - Ensure code compiles/parses
2. **Test generation** - Create unit tests
3. **Edge case analysis** - Test boundary conditions
4. **Performance testing** - Benchmark execution
5. **Security scanning** - Vulnerability detection

### Confidence Scoring
- **High (0.8-1.0)** - Well-tested patterns, multiple validation passes
- **Medium (0.5-0.8)** - Generally correct, some uncertainty
- **Low (0.0-0.5)** - Experimental, needs manual review

## Limitations

### Current Constraints
1. **No execution** - Cannot run generated code (safety)
2. **Limited context** - Large codebases may be challenging
3. **Language support** - Some niche languages limited
4. **Framework knowledge** - Rapidly evolving frameworks

### Mitigation Strategies
- Focus on core language features
- Provide clear requirements
- Break large tasks into smaller ones
- Use established patterns and templates

## Future Enhancements

### Planned Features
1. **Live code execution** - Safe sandbox for testing
2. **Learning from corrections** - Improve based on feedback
3. **Code pattern library** - Reusable templates and solutions
4. **Collaborative coding** - Pair programming simulation
5. **Project scaffolding** - Complete project generation

### Integration Goals
1. **IDE integration** - Direct editor support
2. **CI/CD pipeline** - Automated code review
3. **Version control** - Git integration
4. **Team collaboration** - Multi-developer support

## Usage Notes

### Best Practices
1. **Be specific** - Clear requirements yield better code
2. **Provide context** - Include existing code when relevant
3. **Set standards** - Specify quality/security requirements
4. **Iterate** - Start simple, then enhance

### Common Use Cases
- Prototype development
- Code review and auditing
- Learning and education
- Legacy code modernization
- Interview preparation
- Open source contribution

## Quick Start

### Basic Usage
Just say "code [what]" and the skill will automatically:
1. Analyze your requirements
2. Determine appropriate language and approach
3. Generate or analyze code
4. Return results with documentation

### Advanced Usage
For more control, specify:
- "review code: [code snippet]" - Code analysis
- "refactor: [code]" - Optimization
- "debug: [problem description]" - Bug finding
- "implement [feature] in [language]" - Specific generation

### Integration with Other Skills
- Use with **research skill** for coding pattern research
- Use with **multi-model orchestrator** for complex tasks
- Use with **async pattern** for long-running analysis
- Use for **crypto skill** development (smart contracts, etc.)