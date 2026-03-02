#!/usr/bin/env python3
"""Simple test of enhanced memory features."""

import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace')

from enhanced_memory_graph import EnhancedMemoryGraph
from datetime import datetime

def main():
    print("=== Testing Enhanced Memory Features ===\n")
    
    # Initialize
    print("1. Loading enhanced memory graph...")
    mg = EnhancedMemoryGraph()
    
    print(f"   Memories loaded: {len(mg.memories)}")
    print(f"   Semantic model: {'Loaded' if mg.semantic_model else 'Not available'}")
    
    # Show extracted tags
    print("\n2. Extracted tags from existing content:")
    all_tags = set()
    for memory in mg.memories.values():
        all_tags.update(memory.tags)
    
    print(f"   Total unique tags: {len(all_tags)}")
    print(f"   Tags: {sorted(list(all_tags))}")
    
    # Show keyword extraction
    print("\n3. Keyword extraction results:")
    keyword_counts = {}
    for memory in mg.memories.values():
        for keyword in memory.keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    print(f"   Total unique keywords: {len(keyword_counts)}")
    
    # Top keywords
    top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    print("   Top 15 keywords:")
    for i, (keyword, count) in enumerate(top_keywords, 1):
        print(f"     {i:2d}. {keyword:20s} ({count} memories)")
    
    # Show semantic relationships
    print("\n4. Semantic relationships found:")
    
    # Count relationships by strength
    relationship_counts = {
        "weak (0.3-0.4)": 0,
        "medium (0.4-0.5)": 0,
        "strong (0.5-0.6)": 0,
        "very strong (>0.6)": 0
    }
    
    for memory in mg.memories.values():
        for score in memory.relationships.values():
            if score >= 0.6:
                relationship_counts["very strong (>0.6)"] += 1
            elif score >= 0.5:
                relationship_counts["strong (0.5-0.6)"] += 1
            elif score >= 0.4:
                relationship_counts["medium (0.4-0.5)"] += 1
            else:
                relationship_counts["weak (0.3-0.4)"] += 1
    
    total_relationships = sum(relationship_counts.values())
    print(f"   Total relationships: {total_relationships}")
    for category, count in relationship_counts.items():
        if count > 0:
            percentage = (count / total_relationships * 100) if total_relationships > 0 else 0
            print(f"   {category}: {count} ({percentage:.1f}%)")
    
    # Show most connected memories
    print("\n5. Most connected memories:")
    most_connected = sorted(
        mg.memories.values(),
        key=lambda m: len(m.relationships),
        reverse=True
    )[:5]
    
    for i, memory in enumerate(most_connected, 1):
        print(f"   {i}. {memory.id}")
        print(f"      Source: {memory.source_file}")
        print(f"      Connections: {len(memory.relationships)}")
        print(f"      Tags: {memory.tags[:3]}{'...' if len(memory.tags) > 3 else ''}")
        
        # Show strongest relationship
        if memory.relationships:
            strongest = max(memory.relationships.items(), key=lambda x: x[1])
            other_memory = mg.memories.get(strongest[0])
            if other_memory:
                print(f"      Strongest link: {other_memory.id} (score: {strongest[1]:.3f})")
                print(f"        -> {other_memory.content[:80]}...")
    
    # Test search by tag
    print("\n6. Testing search by extracted tags:")
    
    test_tags = ["thesis", "openclaw", "error", "security"]
    
    for tag in test_tags:
        if tag in mg.tag_index:
            memory_ids = mg.tag_index[tag]
            print(f"   Tag '#{tag}': {len(memory_ids)} memories")
            
            # Show sample
            sample_id = list(memory_ids)[0]
            if sample_id in mg.memories:
                memory = mg.memories[sample_id]
                print(f"     Sample: {memory.content[:100]}...")
        else:
            print(f"   Tag '#{tag}': Not found in extracted tags")
    
    # Test adding new memory
    print("\n7. Testing new memory ingestion with enhancements:")
    
    new_content = """
    #test #integration #heartbeat
    Testing the enhanced memory system integration with OpenClaw heartbeat.
    This should automatically extract tags: test, integration, heartbeat.
    Keywords should include: testing, enhanced, memory, system, integration, openclaw, heartbeat.
    This relates to existing memories about system monitoring and cron jobs.
    """
    
    # Create a simple memory chunk manually
    from enhanced_memory_graph import EnhancedMemoryChunk
    
    chunk_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    tags = mg._extract_tags_from_content(new_content)
    keywords = mg._extract_keywords(new_content)
    embedding = mg._compute_embedding(new_content)
    
    new_memory = EnhancedMemoryChunk(
        id=chunk_id,
        content=new_content,
        source_file="test_input",
        line_range=(0, 1),
        timestamp=datetime.now(),
        tags=tags,
        keywords=keywords,
        embedding=embedding,
        relationships={}
    )
    
    mg.memories[chunk_id] = new_memory
    
    # Update indices
    for tag in tags:
        mg.tag_index[tag].add(chunk_id)
    for keyword in keywords:
        mg.keyword_index[keyword].add(chunk_id)
    
    # Compute relationships
    mg._update_relationships_for_memory(chunk_id)
    
    print(f"   Added test memory: {chunk_id}")
    print(f"   Extracted tags: {tags}")
    print(f"   Extracted keywords: {keywords[:5]}...")
    print(f"   Has embedding: {embedding is not None}")
    print(f"   Relationships established: {len(new_memory.relationships)}")
    
    if new_memory.relationships:
        strongest = max(new_memory.relationships.items(), key=lambda x: x[1])
        print(f"   Strongest relationship: {strongest[0]} (score: {strongest[1]:.3f})")
    
    # Save results
    print("\n8. Saving enhanced memory analysis...")
    
    import json
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "total_memories": len(mg.memories),
            "total_tags": len(mg.tag_index),
            "total_keywords": len(mg.keyword_index),
            "total_relationships": sum(len(m.relationships) for m in mg.memories.values()),
            "semantic_model": mg.semantic_model is not None
        },
        "top_tags": list(all_tags),
        "top_keywords": top_keywords[:20],
        "most_connected": [
            {
                "id": m.id,
                "source": m.source_file,
                "connections": len(m.relationships),
                "tags": m.tags
            }
            for m in most_connected
        ]
    }
    
    with open("/home/ubuntu/.openclaw/workspace/memory_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"   Analysis saved to: /home/ubuntu/.openclaw/workspace/memory_analysis.json")
    
    # Recommendations
    print("\n=== Summary ===")
    print(f"✓ Tag extraction: {len(all_tags)} tags extracted from existing content")
    print(f"✓ Keyword extraction: {len(keyword_counts)} keywords identified")
    print(f"✓ Semantic relationships: {total_relationships} relationships established")
    print(f"✓ Strong relationships (>0.5): {relationship_counts['strong (0.5-0.6)'] + relationship_counts['very strong (>0.6)']}")
    
    print("\n=== Next Steps for OpenClaw Integration ===")
    print("1. Add memory graph updates to HEARTBEAT.md")
    print("2. Create cron job for periodic memory analysis")
    print("3. Integrate with existing memory search in main session")
    print("4. Add tag suggestions when creating new memories")
    print("5. Visualize memory relationships in web interface")

if __name__ == "__main__":
    main()