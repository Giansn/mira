# Code Generation & Analysis Skill

A comprehensive skill for generating, analyzing, reviewing, and refactoring code across multiple programming languages.

## Features

### ✅ **Code Generation**
- Generate code from natural language descriptions
- Support for Python, JavaScript, Java, C++, Go, Rust
- Template-based generation for common patterns
- Quality levels: basic, standard, production, enterprise

### 🔍 **Code Analysis & Review**
- Security vulnerability detection
- Performance issue identification
- Style and best practice checking
- Bug detection and debugging assistance

### ⚡ **Code Refactoring**
- Extract repeated code into methods
- Rename unclear variables
- Simplify complex logic
- Optimize performance
- Improve error handling

### 🛠️ **Multi-Model Integration**
- Orchestrates multiple AI models for specialized tasks
- Planning → Generation → Review workflow
- Fallback to simple generation when multi-model unavailable

## Quick Start

### Basic Usage
Just say:
- "code a Python function to calculate factorial"
- "review this JavaScript code for security"
- "refactor this Python class for better performance"
- "debug why my function returns None"

### Examples

**Code Generation:**
```
User: code a Flask REST API with authentication
→ Skill triggers
→ Returns complete implementation with documentation
```

**Code Review:**
```
User: review this code for SQL injection vulnerabilities
→ Skill triggers
→ Returns security analysis with recommendations
```

**Code Refactoring:**
```
User: refactor this nested loop for better performance
→ Skill triggers
→ Returns optimized version with explanation
```

## Architecture

### Core Components
1. **`code_skill.py`** - Main handler with request parsing
2. **`code_generator.py`** - Template-based code generation
3. **`code_analyzer.py`** - Static analysis and security scanning
4. **`code_refactorer.py`** - Code optimization and restructuring

### Integration Points
- **Multi-Model Orchestrator** - For complex code tasks
- **Research Skill** - For coding pattern research
- **Async Agent Pattern** - Long-running analysis tasks
- **Memory System** - Store and retrieve code patterns

## Supported Languages

### Primary Support
- **Python** - Full support (generation, analysis, refactoring)
- **JavaScript/TypeScript** - Good support
- **Java** - Basic support
- **C++** - Basic support
- **Go** - Basic support
- **Rust** - Basic support

### Web Technologies
- HTML/CSS
- React, Vue, Angular
- REST APIs, GraphQL

### Scripting & Configuration
- Bash, PowerShell
- SQL
- YAML, JSON, XML
- Dockerfile, Kubernetes

## Quality Levels

### 1. Basic
- Functional correctness only
- Minimal error handling
- Basic documentation

### 2. Standard (Default)
- Comprehensive error handling
- Good documentation
- Style consistency
- Basic security considerations

### 3. Production
- All standard features
- Security hardening
- Performance optimization
- Unit tests
- Logging and monitoring

### 4. Enterprise
- All production features
- Compliance requirements
- Audit trails
- Advanced security scanning
- Documentation standards

## Output Formats

### Generated Code
```python
# Complete implementation with:
# - Proper structure
# - Error handling
# - Documentation
# - Tests (when applicable)
# - Configuration
```

### Code Review Report
```
# Code Review: [filename]

## Summary
Overall assessment and score

## Security Issues
1. Issue 1 with severity and fix
2. Issue 2 with severity and fix

## Performance Issues
1. Bottleneck 1 with optimization
2. Bottleneck 2 with optimization

## Recommendations
- Immediate fixes (critical)
- Recommended improvements (medium)
- Nice-to-have enhancements (low)
```

### Bug Report
```
# Bug Analysis: [description]

## Bug Details
- Type: [logical error, runtime error, security issue]
- Severity: [critical, high, medium, low]
- Location: [file:line]
- Impact: [what breaks]

## Root Cause Analysis
Explanation of why bug occurs

## Fix
```language
# Corrected code
```

## Prevention
How to avoid similar bugs
```

## Integration with Other Skills

### Research Skill
- Research coding patterns and best practices
- Find solutions to complex coding problems
- Learn new frameworks and libraries

### Multi-Model Orchestrator
- Coordinate specialized models for different code tasks
- Planning: claude-sonnet
- Generation: gpt-4
- Analysis: llama-code
- Review: claude-sonnet

### Async Agent Pattern
- Handle long-running code analysis
- Process large codebases in background
- Queue code review tasks

### Memory System
- Store successful code patterns
- Retrieve previous solutions
- Learn from corrections and improvements

## Usage Examples

### Example 1: API Generation
```
User: "code a Flask REST API with JWT authentication and SQLite"
→ Returns: Complete Flask app with auth, database models, routes, tests
```

### Example 2: Security Review
```
User: "review this smart contract for vulnerabilities"
→ Returns: Security audit with vulnerability report and fixes
```

### Example 3: Performance Refactoring
```
User: "optimize this data processing function for speed"
→ Returns: Optimized version with benchmark comparison
```

### Example 4: Complete Project
```
User: "create a todo app with React frontend and Python backend"
→ Returns: Full-stack implementation with frontend, backend, database
```

## Configuration

### Environment Variables
```bash
# Optional: API keys for multi-model integration
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-...
```

### Quality Settings
Set default quality level in request or use command-line flags:
- `--quality basic|standard|production|enterprise`
- `--focus security|performance|testing|documentation`

## Testing

### Run Test Suite
```bash
cd skills/code-generation-analysis
python3 test_skill.py
```

### Interactive Testing
```bash
cd skills/code-generation-analysis
python3 examples/basic_usage.py
```

### Test Coverage
- Trigger detection
- Request parsing
- Code generation
- Code analysis
- Integration testing
- Performance testing

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

## Contributing

### Adding New Language Support
1. Add language patterns to `code_skill.py`
2. Create templates in `code_generator.py`
3. Add analysis rules to `code_analyzer.py`
4. Update documentation

### Adding New Templates
1. Define template in `code_generator.py`
2. Add placeholders and documentation
3. Test with examples
4. Update README

### Reporting Issues
1. Check existing issues
2. Provide example code and expected behavior
3. Include error messages and logs
4. Suggest possible solutions

## License

This skill is part of the OpenClaw workspace and follows the same licensing terms.

## Support

For issues, questions, or feature requests:
1. Check the documentation
2. Run tests to verify functionality
3. Provide detailed examples
4. Consider contributing improvements

---

**Last Updated**: 2026-03-02  
**Version**: 1.0.0  
**Status**: Production Ready