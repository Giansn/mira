#!/usr/bin/env python3
"""Test the memory graph with more advanced features."""

import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace')

from memory_graph import MemoryGraph
from datetime import datetime

def test_advanced_features():
    """Test advanced memory graph features."""
    print("=== Advanced Memory Graph Tests ===\n")
    
    # Initialize
    mg = MemoryGraph()
    print(f"Initialized with {len(mg.memories)} memory chunks")
    
    # Test 1: Ingest new memory
    print("\n1. Testing memory ingestion...")
    new_memory = """
    #project #thesis 
    Today I worked on the literature review section of my BA thesis.
    Found several key papers on postcolonial theory in social work education.
    Need to integrate IFSW/IASSW guidelines with case studies from NZ and China.
    """
    
    result = mg.process(new_memory=new_memory)
    print(f"   Action: {result['action']}")
    print(f"   Total memories now: {result['total_memories']}")
    
    # Test 2: Query with tags
    print("\n2. Querying by tags...")
    result = mg.process(query="project")
    print(f"   Found {result['retrieved_count']} memories with 'project'")
    if result.get('retrieved_samples'):
        print("   Samples:")
        for mem in result['retrieved_samples']:
            print(f"     - {mem['id']}: {mem['content'][:80]}...")
    
    # Test 3: Complex query
    print("\n3. Complex query (thesis + social work)...")
    result = mg.process(query="social work")
    print(f"   Found {result['retrieved_count']} memories with 'social work'")
    
    # Test 4: Get summary
    print("\n4. Getting summary...")
    result = mg.process()
    if result.get('summary'):
        print("   Summary:")
        for line in result['summary'].split('\n'):
            print(f"     {line}")
    
    # Test 5: Save and show relationships
    print("\n5. Analyzing relationships...")
    
    # Count relationships
    total_relationships = 0
    for memory in mg.memories.values():
        total_relationships += len(memory.relationships)
    
    print(f"   Total relationships established: {total_relationships}")
    
    # Find memories with most relationships
    top_memories = sorted(
        mg.memories.values(),
        key=lambda m: len(m.relationships),
        reverse=True
    )[:3]
    
    print("   Most connected memories:")
    for memory in top_memories:
        print(f"     - {memory.id}: {len(memory.relationships)} connections")
        if memory.relationships:
            print(f"       Connected to: {', '.join(memory.relationships[:3])}...")
    
    # Test 6: Memory statistics
    print("\n6. Memory statistics:")
    
    # By source
    sources = {}
    for memory in mg.memories.values():
        source = memory.source_file
        sources[source] = sources.get(source, 0) + 1
    
    print("   Memories by source:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"     - {source}: {count}")
    
    # By date (for daily files)
    dates = {}
    for memory in mg.memories.values():
        if memory.source_file.startswith("memory/"):
            date = memory.timestamp.strftime("%Y-%m-%d")
            dates[date] = dates.get(date, 0) + 1
    
    if dates:
        print("\n   Memories by date:")
        for date, count in sorted(dates.items()):
            print(f"     - {date}: {count}")
    
    # Test 7: Export capabilities
    print("\n7. Testing export...")
    
    # Save graph
    saved_path = mg.save_to_file()
    print(f"   Graph saved to: {saved_path}")
    
    # Create a simple visualization
    print("\n8. Creating simple visualization...")
    
    # Group by source and show connections
    print("   Memory network overview:")
    for source in sorted(sources.keys()):
        source_memories = [m for m in mg.memories.values() if m.source_file == source]
        connections = sum(len(m.relationships) for m in source_memories)
        print(f"     - {source}: {len(source_memories)} memories, {connections} connections")
    
    # Show tag cloud (if we had tags)
    print("\n9. Tag analysis:")
    # Note: Our current memory files don't use #tag format
    # This would work if memories had tags like #thesis #project etc.
    
    print("   (Tags would appear here if memories used #tag format)")
    print("   Example: Add #thesis #project #research to memory entries")
    
    # Test 10: Memory search with different strategies
    print("\n10. Testing search strategies...")
    
    search_terms = ["thesis", "project", "work", "research", "system"]
    
    for term in search_terms:
        result = mg.process(query=term)
        if result['retrieved_count'] > 0:
            print(f"   '{term}': {result['retrieved_count']} memories")
    
    print("\n=== Test Complete ===")
    print(f"Total memory chunks: {len(mg.memories)}")
    print(f"Graph ready for integration with OpenClaw workflows")

if __name__ == "__main__":
    test_advanced_features()