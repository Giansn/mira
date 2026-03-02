#!/usr/bin/env python3
"""
Test the full LangGraph memory system integration.
"""

import os
import sys
import json
from datetime import datetime

print("=== Testing Full LangGraph Memory Integration ===\n")

# Test 1: Enhanced memory graph
print("1. Testing enhanced memory graph...")
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace')

try:
    from enhanced_memory_graph import EnhancedMemoryGraph
    mg = EnhancedMemoryGraph()
    print(f"   ✓ Loaded: {len(mg.memories)} memories")
    print(f"   ✓ Tags extracted: {len(mg.tag_index)}")
    print(f"   ✓ Keywords extracted: {len(mg.keyword_index)}")
    print(f"   ✓ Relationships computed: {sum(len(m.relationships) for m in mg.memories.values())}")
    print(f"   ✓ Semantic model: {'Loaded' if mg.semantic_model else 'Not available'}")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 2: Heartbeat integration
print("\n2. Testing heartbeat integration...")
try:
    from memory_heartbeat import MemoryHeartbeat
    heartbeat = MemoryHeartbeat()
    print("   ✓ MemoryHeartbeat initialized")
    
    # Check new memories
    new_files = heartbeat.check_new_memories()
    print(f"   ✓ New files check: {len(new_files)} files since last run")
    
    # Generate summary
    summary = heartbeat.generate_daily_summary()
    print("   ✓ Daily summary generated")
    print(f"   Summary length: {len(summary)} characters")
    
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 3: File outputs
print("\n3. Checking file outputs...")
output_files = [
    "/home/ubuntu/.openclaw/workspace/memory_graph.json",
    "/home/ubuntu/.openclaw/workspace/enhanced_memory_graph.json",
    "/home/ubuntu/.openclaw/workspace/memory_analysis.json",
    "/home/ubuntu/.openclaw/workspace/memory_heartbeat_state.json"
]

for filepath in output_files:
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"   ✓ {os.path.basename(filepath)}: {size:,} bytes")
    else:
        print(f"   ✗ {os.path.basename(filepath)}: Not found")

# Test 4: Integration with existing memory system
print("\n4. Testing integration with existing memory system...")

# Check if memory files exist
memory_files = []
if os.path.exists("/home/ubuntu/.openclaw/workspace/MEMORY.md"):
    memory_files.append("MEMORY.md")

memory_dir = "/home/ubuntu/.openclaw/workspace/memory"
if os.path.exists(memory_dir):
    daily_files = [f for f in os.listdir(memory_dir) if f.endswith('.md')]
    memory_files.extend(daily_files)

print(f"   Found {len(memory_files)} memory files:")
for file in memory_files[:5]:  # Show first 5
    print(f"     - {file}")
if len(memory_files) > 5:
    print(f"     ... and {len(memory_files) - 5} more")

# Test 5: Search capability
print("\n5. Testing search capability...")
if 'mg' in locals():
    test_queries = ["thesis", "openclaw", "error", "heartbeat"]
    
    for query in test_queries:
        # Simple search
        found = []
        for memory in mg.memories.values():
            if query.lower() in memory.content.lower():
                found.append(memory.id)
        
        # Tag search
        tag_found = query in mg.tag_index
        
        print(f"   Query '{query}': {len(found)} matches, tag exists: {tag_found}")

# Test 6: Performance check
print("\n6. Performance check...")
import time

if 'mg' in locals():
    start = time.time()
    
    # Test embedding computation
    test_text = "This is a test memory for performance evaluation."
    embedding = mg._compute_embedding(test_text)
    
    # Test similarity calculation
    if embedding and mg.memories:
        sample_memory = list(mg.memories.values())[0]
        if sample_memory.embedding:
            similarity = mg._calculate_similarity(embedding, sample_memory.embedding)
    
    elapsed = time.time() - start
    print(f"   Embedding + similarity computation: {elapsed:.3f} seconds")
    print(f"   Embedding generated: {embedding is not None}")
    if 'similarity' in locals():
        print(f"   Similarity score: {similarity:.3f}")

# Test 7: HEARTBEAT.md integration
print("\n7. Checking HEARTBEAT.md integration...")
heartbeat_path = "/home/ubuntu/.openclaw/workspace/HEARTBEAT.md"
if os.path.exists(heartbeat_path):
    with open(heartbeat_path, 'r') as f:
        content = f.read()
    
    if "Memory Graph Maintenance" in content:
        print("   ✓ Memory graph task added to HEARTBEAT.md")
        
        # Extract the command
        import re
        match = re.search(r'Run:\s*(python3.*memory_heartbeat\.py)', content)
        if match:
            print(f"   ✓ Command found: {match.group(1)}")
        else:
            print("   ✗ Command not found in HEARTBEAT.md")
    else:
        print("   ✗ Memory graph task not in HEARTBEAT.md")
else:
    print("   ✗ HEARTBEAT.md not found")

# Test 8: Create a test cron job
print("\n8. Creating test cron entry...")
cron_entry = "*/30 * * * * cd /home/ubuntu/.openclaw/workspace && /usr/bin/python3.12 memory_heartbeat.py --summary >> /tmp/memory_heartbeat.log 2>&1"
print(f"   Sample cron entry (every 30 minutes):")
print(f"   {cron_entry}")

# Test 9: Recommendations
print("\n9. System recommendations:")

recommendations = []

# Check if sentence-transformers is installed
try:
    import sentence_transformers
    recommendations.append("✓ sentence-transformers installed")
except ImportError:
    recommendations.append("✗ Install: pip install sentence-transformers")

# Check LangGraph installation
try:
    import langgraph
    recommendations.append("✓ LangGraph installed")
except ImportError:
    recommendations.append("✗ Install: pip install langgraph langgraph-sdk")

# Check memory files
if len(memory_files) < 5:
    recommendations.append("⚠️  Few memory files - consider adding more context")
else:
    recommendations.append(f"✓ {len(memory_files)} memory files available")

# Check relationships
if 'mg' in locals():
    total_relationships = sum(len(m.relationships) for m in mg.memories.values())
    if total_relationships > 0:
        avg = total_relationships / len(mg.memories)
        recommendations.append(f"✓ {total_relationships} relationships ({avg:.1f} per memory)")
    else:
        recommendations.append("⚠️  No relationships computed - check semantic model")

for rec in recommendations:
    print(f"   {rec}")

print("\n=== Integration Test Complete ===")
print("\nNext steps:")
print("1. Add memory_heartbeat.py to actual cron job")
print("2. Test during next heartbeat (trigger with 'Read HEARTBEAT.md if it exists...')")
print("3. Monitor /tmp/memory_heartbeat.log for output")
print("4. Use memory search in main sessions: 'search thesis' etc.")
print("5. Consider adding memory visualization (web interface)")