#!/usr/bin/env python3
"""
Basic usage examples for the code generation & analysis skill.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_skill import handle_code_request


async def run_examples():
    """Run example code requests."""
    examples = [
        # Code generation
        "code a Python function to calculate fibonacci sequence",
        
        # Code review
        """review this Python code for security issues:
```python
def process_input(user_input):
    return eval(user_input)
```""",
        
        # Code refactoring
        """refactor this JavaScript function for better performance:
```javascript
function findDuplicates(arr) {
    let duplicates = [];
    for (let i = 0; i < arr.length; i++) {
        for (let j = i + 1; j < arr.length; j++) {
            if (arr[i] === arr[j]) {
                duplicates.push(arr[i]);
            }
        }
    }
    return duplicates;
}
```""",
        
        # Debugging
        """debug why this Python function returns wrong results:
```python
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers) if numbers else 0

# Test case: calculate_average([1, 2, 3, 4, 5]) returns 2.0 instead of 3.0
```""",
        
        # API generation
        "code a Flask REST API for todo list management",
        
        # With specific language
        "write JavaScript code for form validation",
        
        # With quality level
        "generate production-quality Python code for data processing",
        
        # With focus area
        "review this code for security vulnerabilities focus on SQL injection"
    ]
    
    print("=== Code Skill Examples ===\n")
    
    for i, query in enumerate(examples[:3], 1):  # Just test first 3 for speed
        print(f"\n{'='*80}")
        print(f"Example {i}: {query[:60]}...")
        print(f"{'='*80}")
        
        try:
            result = await handle_code_request(query)
            if result:
                # Show preview
                lines = result.split('\n')
                print("\n".join(lines[:30]))  # First 30 lines
                print("...\n")
            else:
                print("Code skill not triggered.")
        except Exception as e:
            print(f"Error: {e}")
        
        # Pause between examples
        if i < len(examples[:3]):
            print("\n" + "-"*40 + "\n")
            await asyncio.sleep(1)


async def test_trigger_detection():
    """Test which phrases trigger the code skill."""
    test_phrases = [
        "code a function",
        "write Python code",
        "review this code",
        "analyze JavaScript code",
        "refactor the function",
        "debug this issue",
        "fix the bug",
        "implement a solution",
        "develop an API",
        "program a calculator",
        "generate code for",
        "create a script",
        "tell me about Python",  # Should NOT trigger
        "what is JavaScript",  # Should NOT trigger
        "help me with coding"  # Should trigger
    ]
    
    print("\n=== Trigger Detection Test ===\n")
    
    from code_skill import CodeSkill
    skill = CodeSkill()
    
    for phrase in test_phrases:
        triggers = skill.should_trigger(phrase)
        status = "✓ TRIGGERS" if triggers else "✗ NO TRIGGER"
        print(f"{status}: {phrase}")


async def test_request_parsing():
    """Test request parsing functionality."""
    test_requests = [
        "code a Python function to sort list",
        "review JavaScript code for security",
        "refactor this Python class for performance",
        "debug why this function returns null",
        "analyze Go code for best practices",
        "implement REST API in Python",
        "write production-quality Java code"
    ]
    
    print("\n=== Request Parsing Test ===\n")
    
    from code_skill import CodeSkill
    skill = CodeSkill()
    
    for request in test_requests:
        parsed = skill.parse_request(request)
        print(f"\nRequest: {request}")
        print(f"  Type: {parsed.request_type}")
        print(f"  Language: {parsed.language}")
        print(f"  Description: {parsed.description[:50]}...")
        print(f"  Quality: {parsed.quality_level}")
        print(f"  Focus areas: {parsed.focus_areas}")


async def test_code_generator():
    """Test code generator templates."""
    print("\n=== Code Generator Test ===\n")
    
    from code_generator import CodeGenerator
    generator = CodeGenerator()
    
    # Show available templates
    print("Available Python templates:")
    templates = generator.get_available_templates('python')
    for template in templates:
        print(f"  - {template['key']}: {template['name']}")
    
    # Generate example code
    print("\nGenerating Python API template:")
    code = generator.generate_code(
        language='python',
        template_type='api',
        placeholders={
            'api_name': 'Todo API',
            'resource_name': 'TodoResource',
            'resource_description': 'Manage todo items',
            'endpoint': 'todos'
        }
    )
    
    print(code[:500] + "..." if len(code) > 500 else code)
    
    # Analyze requirements
    print("\nAnalyzing: 'Create user authentication API'")
    analysis = generator.analyze_code_requirements("Create user authentication API")
    print(f"  Language: {analysis['language']}")
    print(f"  Templates: {analysis['templates']}")
    print(f"  Complexity: {analysis['complexity']}")
    print(f"  Focus areas: {analysis['focus_areas']}")


async def main():
    """Run all tests."""
    print("Code Generation & Analysis Skill Testing Suite")
    print("="*80)
    
    # Test trigger detection
    await test_trigger_detection()
    
    # Test request parsing
    await test_request_parsing()
    
    # Test code generator
    await test_code_generator()
    
    # Run examples
    await run_examples()
    
    print("\n" + "="*80)
    print("Testing complete!")
    
    # Quick interactive test
    print("\nTry your own code request (or 'quit' to exit):")
    while True:
        try:
            user_query = input("\n> ").strip()
            if user_query.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_query:
                result = await handle_code_request(user_query)
                if result:
                    print("\n" + "="*80)
                    print(result[:800] + "..." if len(result) > 800 else result)
                    print("="*80)
                else:
                    print("Code skill not triggered. Try starting with 'code', 'review', etc.")
                    
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())