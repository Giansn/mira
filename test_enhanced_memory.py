#!/usr/bin/env python3
"""Test the enhanced memory graph system."""

import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace')

from enhanced_memory_graph import EnhancedMemoryGraph
from datetime import datetime

def test_enhanced_features():
    """Test all three enhancement aspects."""
    print("=== Testing Enhanced Memory Graph ===\n")
    
    # Initialize
    print("1. Initializing enhanced memory graph...")
    mg = EnhancedMemoryGraph()
    
    print(f"   Loaded {len(mg.memories)} memory chunks")
    print(f"   Semantic model available: {mg.semantic_model is not None}")
    
    # Test tag extraction
    print("\n2. Testing tag extraction...")
    
    # Check tags extracted from existing content
    tags_found = set()
    for memory in mg.memories.values():
        tags_found.update(memory.tags)
    
    print(f"   Total unique tags extracted: {len(tags_found)}")
    if tags_found:
        print(f"   Sample tags: {list(tags_found)[:10]}")
    
    # Test keyword extraction
    print("\n3. Testing keyword extraction...")
    
    keywords_found = set()
    keyword_counts = {}
    for memory in mg.memories.values():
        for keyword in memory.keywords:
            keywords_found.add(keyword)
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    print(f"   Total unique keywords: {len(keywords_found)}")
    
    # Show top keywords
    top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("   Top 10 keywords:")
    for keyword, count in top_keywords:
        print(f"     - {keyword}: {count} memories")
    
    # Test semantic relationships
    print("\n4. Testing semantic relationships...")
    
    # Count relationships
    total_relationships = 0
    strong_relationships = 0  # similarity > 0.5
    
    for memory in mg.memories.values():
        total_relationships += len(memory.relationships)
        for score in memory.relationships.values():
            if score > 0.5:
                strong_relationships += 1
    
    print(f"   Total relationships: {total_relationships}")
    print(f"   Strong relationships (>0.5): {strong_relationships}")
    
    # Find most connected memories
    if mg.memories:
        most_connected = sorted(
            mg.memories.values(),
            key=lambda m: len(m.relationships),
            reverse=True
        )[:3]
        
        print("   Most connected memories:")
        for memory in most_connected:
            print(f"     - {memory.id}: {len(memory.relationships)} connections")
            if memory.relationships:
                # Show top relationships
                top_rel = sorted(memory.relationships.items(), key=lambda x: x[1], reverse=True)[:2]
                for rel_id, score in top_rel:
                    print(f"       -> {rel_id}: {score:.3f}")
    
    # Test search with enhanced capabilities
    print("\n5. Testing enhanced search...")
    
    test_queries = ["thesis", "openclaw", "error", "security", "memory"]
    
    for query in test_queries:
        # Create a simple test state
        test_state = {
            "query": query,
            "new_memory_text": None,
            "retrieved_memories": [],
            "similar_memories": [],
            "summary": None,
            "action_taken": None,
            "tags_found": []
        }
        
        # Run retrieve node
        result = mg.graph.get_node("retrieve").func(test_state)
        
        print(f"   Query '{query}': {len(result['retrieved_memories'])} memories found")
        
        # Check if found via tags
        if query in mg.tag_index:
            print(f"     Found via tag index: {len(mg.tag_index[query])} memories")
    
    # Test adding new memory with enhancements
    print("\n6. Testing memory ingestion with enhancements...")
    
    new_memory = """
    #test #enhancement
    Testing the enhanced memory system with LangGraph.
    This should extract tags: test, enhancement.
    Keywords should include: testing, enhanced, memory, system, langgraph.
    This relates to existing memories about memory organization.
    """
    
    test_state = {
        "query": None,
        "new_memory_text": new_memory,
        "retrieved_memories": [],
        "similar_memories": [],
        "summary": None,
        "action_taken": None,
        "tags_found": []
    }
    
    # Run ingest node
    result = mg.graph.get_node("ingest").func(test_state)
    print(f"   {result['action_taken']}")
    print(f"   Tags found: {result['tags_found']}")
    
    # Check the new memory
    new_id = result['action_taken'].split(": ")[-1]
    if new_id in mg.memories:
        new_mem = mg.memories[new_id]
        print(f"   New memory created with {len(new_mem.keywords)} keywords")
        print(f"   Keywords: {new_mem.keywords[:5]}...")
        print(f"   Has embedding: {new_mem.embedding is not None}")
        print(f"   Relationships established: {len(new_mem.relationships)}")
    
    # Test summary
    print("\n7. Testing enhanced summary...")
    
    test_state = {
        "query": None,
        "new_memory_text": None,
        "retrieved_memories": [],
        "similar_memories": [],
        "summary": None,
        "action_taken": None,
        "tags_found": []
    }
    
    result = mg.graph.get_node("summarize").func(test_state)
    if result.get('summary'):
        print("   Summary generated:")
        for line in result['summary'].split('\n'):
            if line.strip():
                print(f"     {line}")
    
    # Save enhanced graph
    print("\n8. Saving enhanced graph...")
    
    # Create save method
    def save_enhanced_graph(mg, filepath):
        data = {
            "memories": {mid: mem.to_dict() for mid, mem in mg.memories.items()},
            "tag_index": {tag: list(mem_ids) for tag, mem_ids in mg.tag_index.items()},
            "keyword_index": {kw: list(mem_ids) for kw, mem_ids in mg.keyword_index.items()},
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "total_memories": len(mg.memories),
                "total_tags": len(mg.tag_index),
                "total_keywords": len(mg.keyword_index),
                "total_relationships": sum(len(m.relationships) for m in mg.memories.values())
            }
        }
        
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    saved_path = save_enhanced_graph(mg, "/home/ubuntu/.openclaw/workspace/enhanced_memory_graph.json")
    print(f"   Saved to: {saved_path}")
    
    # Show final statistics
    print("\n=== Final Statistics ===")
    print(f"Total memories: {len(mg.memories)}")
    print(f"Total tags: {len(mg.tag_index)}")
    print(f"Total keywords: {len(mg.keyword_index)}")
    print(f"Total relationships: {total_relationships}")
    print(f"Semantic capabilities: {'Enabled' if mg.semantic_model else 'Disabled (install sentence-transformers)'}")
    
    # Recommendations for improvement
    print("\n=== Recommendations ===")
    if not mg.semantic_model:
        print("1. Install sentence-transformers for better semantic relationships:")
        print("   pip install sentence-transformers")
    
    print("2. Add explicit #tags to memory entries for better organization")
    print("3. Consider adding a vector database (ChromaDB) for scalable similarity search")
    print("4. Integrate with OpenClaw heartbeat for automatic memory updates")

if __name__ == "__main__":
    test_enhanced_features()