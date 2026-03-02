#!/usr/bin/env python3
"""
Basic usage examples for the research skill.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_skill import handle_research_request


async def run_examples():
    """Run example research queries."""
    examples = [
        # Basic research
        "research quantum computing",
        
        # Deep research
        "deep research on renewable energy policies",
        
        # Quick research
        "quick research on Python web frameworks",
        
        # Academic research
        "academic research on machine learning ethics",
        
        # Research with scope
        "research artificial intelligence in healthcare, focus on diagnostics",
        
        # Current research
        "research recent developments in space exploration 2025",
        
        # Research with constraints
        "research social media platforms, excluding Facebook"
    ]
    
    print("=== Research Skill Examples ===\n")
    
    for i, query in enumerate(examples, 1):
        print(f"\n{'='*80}")
        print(f"Example {i}: {query}")
        print(f"{'='*80}")
        
        try:
            result = await handle_research_request(query)
            if result:
                # Show preview
                lines = result.split('\n')
                print("\n".join(lines[:20]))  # First 20 lines
                print("...\n")
            else:
                print("Research skill not triggered.")
        except Exception as e:
            print(f"Error: {e}")
        
        # Pause between examples
        if i < len(examples):
            print("\n" + "-"*40 + "\n")
            await asyncio.sleep(1)


async def test_trigger_detection():
    """Test which phrases trigger the research skill."""
    test_phrases = [
        "research something",
        "look into quantum computing",
        "investigate the issue",
        "find information about Python",
        "analyze the data for trends",
        "study the effects of climate change",
        "explore this topic further",
        "examine in detail",
        "tell me about quantum computing",  # Should NOT trigger
        "what is machine learning",  # Should NOT trigger
        "help me with research",  # Should trigger
        "do research on this"
    ]
    
    print("\n=== Trigger Detection Test ===\n")
    
    from research_skill import ResearchSkill
    skill = ResearchSkill()
    
    for phrase in test_phrases:
        triggers = skill.should_trigger(phrase)
        status = "✓ TRIGGERS" if triggers else "✗ NO TRIGGER"
        print(f"{status}: {phrase}")


async def test_query_parsing():
    """Test query parsing functionality."""
    test_queries = [
        "research quantum computing applications",
        "deep research on renewable energy policies in Europe",
        "quick research Python vs JavaScript",
        "academic research machine learning ethics with citations",
        "research artificial intelligence in healthcare focus on diagnostics",
        "research recent space exploration developments excluding Mars missions"
    ]
    
    print("\n=== Query Parsing Test ===\n")
    
    from research_skill import ResearchSkill
    skill = ResearchSkill()
    
    for query in test_queries:
        parsed = skill.parse_query(query)
        print(f"\nQuery: {query}")
        print(f"  Topic: {parsed.topic}")
        print(f"  Depth: {parsed.depth}")
        print(f"  Time sensitivity: {parsed.time_sensitivity}")
        print(f"  Scope: {parsed.scope}")
        print(f"  Constraints: {parsed.constraints}")
        print(f"  Citations: {parsed.requires_citations}")
        print(f"  Analysis: {parsed.requires_analysis}")
        print(f"  Recommendations: {parsed.requires_recommendations}")


async def main():
    """Run all tests."""
    print("Research Skill Testing Suite")
    print("="*80)
    
    # Test trigger detection
    await test_trigger_detection()
    
    # Test query parsing
    await test_query_parsing()
    
    # Run examples
    await run_examples()
    
    print("\n" + "="*80)
    print("Testing complete!")
    
    # Quick interactive test
    print("\nTry your own research query (or 'quit' to exit):")
    while True:
        try:
            user_query = input("\n> ").strip()
            if user_query.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_query:
                result = await handle_research_request(user_query)
                if result:
                    print("\n" + "="*80)
                    print(result[:500] + "..." if len(result) > 500 else result)
                    print("="*80)
                else:
                    print("Research skill not triggered. Try starting with 'research'.")
                    
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())