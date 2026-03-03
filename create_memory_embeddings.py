#!/usr/bin/env python3
"""
Create Memory Embeddings Database
Generate E5 embeddings for all memory files and save to cache
"""

import sys
import os
import time
from datetime import datetime

# Add virtual environment path
venv_path = "/home/ubuntu/.openclaw/workspace/.venv-embeddings"
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, "lib", "python3.12", "site-packages")
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

print("🧠 Starting Memory Embedding Process")
print("=" * 60)
print(f"Timestamp: {datetime.now().isoformat()}")
print()

# Import Memory RAG system
try:
    from memory_rag import MemoryRAG
    print("✅ MemoryRAG imported successfully")
except ImportError as e:
    print(f"❌ Error importing MemoryRAG: {e}")
    sys.exit(1)

def main():
    """Create embeddings for all memory files."""
    start_time = time.time()
    
    print("🔧 Initializing Memory RAG system...")
    print("   This will load the E5-small-v2 model (first time: ~1 minute)")
    print("   and generate embeddings for all memory files.")
    print()
    
    try:
        # Initialize RAG system (will load/generate embeddings)
        rag = MemoryRAG()
        
        # Get status
        status = rag.get_status()
        
        print("📊 Embedding Process Complete!")
        print("=" * 60)
        
        # Display results
        print(f"✅ Total memory chunks: {status['total_chunks']}")
        print(f"✅ Sources: {status['sources']} files")
        print(f"✅ Embedding engine: {status['embedding_engine']}")
        
        if status['has_embeddings']:
            shape = status['embedding_shape']
            print(f"✅ Embedding shape: {shape[0]} chunks × {shape[1]} dimensions")
        else:
            print("⚠️  No embeddings generated")
        
        # Show source distribution
        print("\n📚 Source Distribution:")
        for source, count in status['source_distribution'].items():
            print(f"   {source}: {count} chunks")
        
        # Cache status
        print(f"\n💾 Cache: {'Exists' if status['cache_exists'] else 'Not found'}")
        if status['cache_exists']:
            print(f"   Path: {status['embedding_cache']}")
        
        # Test search
        print("\n🔍 Testing semantic search...")
        test_queries = [
            "OpenClaw system",
            "BA thesis research",
            "E5 embedding engine",
            "Memory system"
        ]
        
        for query in test_queries:
            results = rag.retrieve(query, top_k=1, threshold=0.3)
            if results:
                print(f"   '{query}': Found {len(results)} results (best: {results[0]['score']:.3f})")
            else:
                print(f"   '{query}': No results above threshold")
        
        # Performance metrics
        elapsed = time.time() - start_time
        print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
        
        # Next steps
        print("\n🎯 Next Steps:")
        print("   1. Use `rag.retrieve(query)` for semantic search")
        print("   2. Update embeddings with `rag.update_embeddings()`")
        print("   3. Integrate with memory_search tool")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during embedding process: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Memory embedding process completed successfully!")
        print("   Semantic search is now ready to use.")
    else:
        print("\n❌ Memory embedding process failed.")
        sys.exit(1)