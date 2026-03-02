#!/usr/bin/env python3
"""
Test the complete code generation & analysis skill
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_skill import handle_code_request


async def test_comprehensive():
    """Test comprehensive code skill functionality."""
    test_cases = [
        # Code generation
        ("code a Python function to calculate factorial", "generate"),
        
        # Code review
        ("""review this Python code:
```python
def insecure(input):
    return eval(input)
```""", "review"),
        
        # Code refactoring
        ("refactor JavaScript code for better performance", "refactor"),
        
        # Debugging
        ("debug why my Python function returns None", "debug"),
        
        # With language specification
        ("write Java code for a simple calculator", "generate"),
        
        # Complex request
        ("generate production-quality Python REST API with authentication", "generate"),
    ]
    
    print("Testing Code Generation & Analysis Skill")
    print("="*80)
    
    for query, expected_type in test_cases:
        print(f"\nTest: {query[:50]}...")
        print("-"*40)
        
        try:
            result = await handle_code_request(query)
            if result:
                print(f"✓ Triggered (expected: {expected_type})")
                # Check if result contains expected elements
                if "Code" in result and expected_type.title() in result:
                    print("✓ Correct response format")
                else:
                    print("⚠️ Unexpected format")
                
                # Show preview
                lines = result.split('\n')
                preview = "\n".join(lines[:8])
                print(f"Preview:\n{preview}...")
            else:
                print("✗ Not triggered (unexpected)")
        
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print()


async def test_integration():
    """Test integration with other components."""
    print("\n" + "="*80)
    print("Testing Integration Points")
    print("="*80)
    
    # Test code generator
    try:
        from code_generator import CodeGenerator
        generator = CodeGenerator()
        templates = generator.get_available_templates('python')
        print(f"✓ Code Generator: {len(templates)} Python templates available")
        
        # Generate sample code
        code = generator.generate_code('python', 'function', {
            'function_name': 'test_function',
            'description': 'Test function'
        })
        if code:
            print("✓ Code generation working")
    except Exception as e:
        print(f"✗ Code Generator error: {e}")
    
    # Test code analyzer
    try:
        from code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        test_code = "def test(): pass"
        result = analyzer.analyze_code(test_code, 'python')
        print(f"✓ Code Analyzer: Analyzed {result.lines_analyzed} lines")
    except Exception as e:
        print(f"✗ Code Analyzer error: {e}")
    
    # Test multi-model integration
    print("\nMulti-model integration:")
    try:
        from code_skill import MULTI_MODEL_AVAILABLE
        if MULTI_MODEL_AVAILABLE:
            print("✓ Multi-model orchestrator available")
        else:
            print("⚠️ Multi-model orchestrator not available (using fallback)")
    except:
        print("⚠️ Could not check multi-model integration")


async def test_performance():
    """Test performance with realistic code."""
    print("\n" + "="*80)
    print("Performance Testing")
    print("="*80)
    
    # Larger code sample for review
    large_code = '''
def process_data(data):
    """Process input data."""
    result = []
    for item in data:
        if item and item.get("valid"):
            processed = transform(item)
            if processed:
                result.append(processed)
    return result

def transform(item):
    """Transform item."""
    try:
        value = item["value"]
        if value > 100:
            return value * 0.9
        elif value > 50:
            return value * 0.8
        else:
            return value * 0.7
    except KeyError:
        return None
    except TypeError:
        return None

def calculate_stats(data):
    """Calculate statistics."""
    if not data:
        return {"count": 0, "average": 0, "total": 0}
    
    total = sum(data)
    count = len(data)
    average = total / count if count > 0 else 0
    
    return {
        "count": count,
        "total": total,
        "average": average,
        "max": max(data) if data else 0,
        "min": min(data) if data else 0
    }
'''
    
    test_query = f"""review this Python code for security and performance:
```python
{large_code}
```"""
    
    print("Testing with larger code sample...")
    start_time = asyncio.get_event_loop().time()
    
    try:
        result = await handle_code_request(test_query)
        elapsed = asyncio.get_event_loop().time() - start_time
        
        if result:
            print(f"✓ Completed in {elapsed:.2f}s")
            lines = len(result.split('\n'))
            print(f"✓ Response: {lines} lines")
        else:
            print("✗ Not triggered")
    
    except Exception as e:
        print(f"✗ Error: {e}")


async def interactive_test():
    """Interactive testing."""
    print("\n" + "="*80)
    print("Interactive Testing")
    print("="*80)
    print("Enter code requests (or 'quit' to exit):")
    
    while True:
        try:
            query = input("\n> ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if query:
                print("Processing...")
                result = await handle_code_request(query)
                
                if result:
                    print("\n" + "="*80)
                    print(result[:500] + "..." if len(result) > 500 else result)
                    print("="*80)
                else:
                    print("Code skill not triggered. Try starting with 'code', 'review', etc.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Run all tests."""
    print("Code Generation & Analysis Skill - Comprehensive Test Suite")
    
    await test_comprehensive()
    await test_integration()
    await test_performance()
    
    # Optional: interactive testing
    # await interactive_test()
    
    print("\n" + "="*80)
    print("Test Suite Complete")
    print("="*80)
    
    # Final status
    from code_skill import CodeSkill
    skill = CodeSkill()
    
    test_phrases = [
        "code something",
        "review my code",
        "refactor this",
        "debug issue",
        "just a normal message"
    ]
    
    print("\nTrigger detection test:")
    for phrase in test_phrases:
        triggers = skill.should_trigger(phrase)
        status = "✓" if triggers else "✗"
        print(f"  {status} '{phrase}'")


if __name__ == "__main__":
    asyncio.run(main())