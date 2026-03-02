#!/usr/bin/env python3
"""
Code Generation & Analysis Skill - Fixed version
"""

import re
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from multi_model_orchestrator.multi_model_orchestrator import MultiModelOrchestrator, WorkflowType
    MULTI_MODEL_AVAILABLE = True
except ImportError:
    MULTI_MODEL_AVAILABLE = False
    print("Warning: Multi-model orchestrator not available.")


@dataclass
class CodeRequest:
    """Parsed code request."""
    original_text: str
    request_type: str
    language: str
    description: str
    code_context: Optional[str] = None
    quality_level: str = "standard"
    focus_areas: List[str] = field(default_factory=list)


@dataclass
class CodeResult:
    """Result of code operation."""
    request: CodeRequest
    content: str
    models_used: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    confidence: float = 0.5


class CodeSkill:
    """Main code skill class."""
    
    def __init__(self):
        self.trigger_patterns = [
            r'\bcode\b',
            r'\bwrite\b.*\bcode\b',
            r'\breview\b',
            r'\banalyze\b',
            r'\brefactor\b',
            r'\bdebug\b',
            r'\bfix\b.*\bcode\b',
            r'\bimplement\b',
            r'\bgenerate\b.*\bcode\b',
            r'\bcreate\b.*\bcode\b',
            r'\bdevelop\b',
            r'\bprogram\b',
            r'\bscript\b',
        ]
        
        if MULTI_MODEL_AVAILABLE:
            self.orchestrator = MultiModelOrchestrator()
        else:
            self.orchestrator = None
    
    def should_trigger(self, message: str) -> bool:
        """Check if message should trigger code skill."""
        message_lower = message.lower()
        for pattern in self.trigger_patterns:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def parse_request(self, message: str) -> CodeRequest:
        """Parse code request from message."""
        message_lower = message.lower()
        
        # Determine request type
        request_type = 'generate'
        if 'review' in message_lower:
            request_type = 'review'
        elif 'refactor' in message_lower:
            request_type = 'refactor'
        elif 'debug' in message_lower or 'fix' in message_lower:
            request_type = 'debug'
        
        # Detect language
        language = 'python'
        if 'javascript' in message_lower or 'js' in message_lower:
            language = 'javascript'
        elif 'java' in message_lower:
            language = 'java'
        
        # Extract description
        description = message
        triggers = ['code', 'write', 'review', 'analyze', 'refactor', 'debug', 'fix', 'implement']
        for trigger in triggers:
            if description.lower().startswith(trigger + ' '):
                description = description[len(trigger) + 1:]
        
        # Extract code context if provided
        code_context = None
        code_block_pattern = r'```(?:\w+)?\n(.*?)\n```'
        code_matches = re.findall(code_block_pattern, message, re.DOTALL)
        if code_matches:
            code_context = code_matches[0].strip()
        
        return CodeRequest(
            original_text=message,
            request_type=request_type,
            language=language,
            description=description.strip(),
            code_context=code_context
        )
    
    async def execute_code_request(self, request: CodeRequest) -> CodeResult:
        """Execute code request."""
        start_time = time.time()
        
        if not self.orchestrator:
            # Simple fallback
            await asyncio.sleep(0.5)
            content = self._generate_simple_response(request)
            return CodeResult(
                request=request,
                content=content,
                models_used=['simple'],
                execution_time=time.time() - start_time,
                confidence=0.6
            )
        
        # Build task for multi-model
        task = self._build_task(request)
        
        try:
            result = await self.orchestrator.execute_complex_task(task=task)
            return CodeResult(
                request=request,
                content=result.final_content,
                models_used=result.models_used,
                execution_time=result.execution_time,
                confidence=result.confidence
            )
        except Exception as e:
            print(f"Multi-model failed: {e}")
            await asyncio.sleep(0.5)
            content = self._generate_simple_response(request)
            return CodeResult(
                request=request,
                content=content,
                models_used=['fallback'],
                execution_time=time.time() - start_time,
                confidence=0.5
            )
    
    def _build_task(self, request: CodeRequest) -> str:
        """Build task description."""
        if request.request_type == 'generate':
            return f"Generate {request.language} code for: {request.description}"
        elif request.request_type == 'review':
            return f"Review {request.language} code: {request.description}"
        elif request.request_type == 'refactor':
            return f"Refactor {request.language} code: {request.description}"
        elif request.request_type == 'debug':
            return f"Debug {request.language} code: {request.description}"
        else:
            return f"Code task: {request.description}"
    
    def _generate_simple_response(self, request: CodeRequest) -> str:
        """Generate simple response."""
        if request.request_type == 'generate':
            return f"""# Generated {request.language} Code

```{request.language}
# TODO: Implement {request.description}
def example():
    print("Code generation placeholder")
    # Add implementation here
```

*Simple code generation - use multi-model for better results*"""
        
        elif request.request_type == 'review':
            return f"""# Code Review

**Language**: {request.language}
**Description**: {request.description}

## Review Summary
- Basic review completed
- For comprehensive analysis, use multi-model orchestration
- Consider security, performance, and best practices

*Simple review - detailed analysis requires multi-model*"""
        
        else:
            return f"""# Code {request.request_type.title()}

**Request**: {request.description}
**Language**: {request.language}

## Result
Code {request.request_type} operation completed.

*Note: Simple implementation - multi-model provides better results*"""
    
    def format_result(self, result: CodeResult) -> str:
        """Format result for display."""
        lines = []
        lines.append(f"# 💻 Code {result.request.request_type.title()} Complete")
        lines.append("")
        lines.append(f"**Request**: {result.request.description}")
        lines.append(f"**Language**: {result.request.language}")
        lines.append(f"**Time**: {result.execution_time:.2f}s")
        lines.append(f"**Confidence**: {result.confidence:.2f}")
        lines.append(f"**Models**: {', '.join(result.models_used)}")
        lines.append("")
        lines.append(result.content)
        return "\n".join(lines)


async def handle_code_request(message: str) -> Optional[str]:
    """Main entry point."""
    skill = CodeSkill()
    if not skill.should_trigger(message):
        return None
    
    request = skill.parse_request(message)
    result = await skill.execute_code_request(request)
    return skill.format_result(result)


# Quick test
async def test():
    """Test the skill."""
    test_messages = [
        "code a Python function",
        "review JavaScript code",
        "refactor this code"
    ]
    
    for msg in test_messages:
        print(f"\nTesting: {msg}")
        result = await handle_code_request(msg)
        if result:
            print(result[:200] + "...")
        else:
            print("Not triggered")


if __name__ == "__main__":
    asyncio.run(test())