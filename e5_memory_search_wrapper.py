#!/usr/bin/env python3
"""
E5 Memory Search Wrapper - Use standalone E5 Memory RAG for semantic search
when OpenClaw's built-in memory search can't handle E5 context limitations.
"""

import json
import sys
import os
from pathlib import Path

# Add the workspace to path to import memory_rag
sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace'))

try:
    from memory_rag import MemoryRAG, E5EmbeddingEngine
except ImportError:
    print("❌ Error: memory_rag module not found")
    print("Run: python3 create_memory_embeddings.py first")
    sys.exit(1)

class E5MemorySearch:
    """Wrapper for E5 Memory RAG semantic search."""
    
    def __init__(self, workspace_dir=None):
        """Initialize E5 Memory RAG system."""
        self.workspace_dir = workspace_dir or str(Path.home() / '.openclaw' / 'workspace')
        self.rag = None
        self.initialized = False
        
    def initialize(self):
        """Initialize the E5 Memory RAG system."""
        try:
            print(f"🧠 Initializing E5 Memory RAG from workspace: {self.workspace_dir}")
            self.rag = MemoryRAG(workspace_dir=self.workspace_dir)
            # MemoryRAG automatically loads embeddings in __init__
            self.initialized = True
            print(f"✅ E5 Memory RAG initialized: {len(self.rag.store.chunks)} chunks loaded")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize E5 Memory RAG: {e}")
            return False
    
    def search(self, query, max_results=5, min_score=0.3):
        """Perform semantic search using E5 embeddings."""
        if not self.initialized:
            if not self.initialize():
                return []
        
        try:
            results = self.rag.retrieve(query, top_k=max_results, threshold=min_score)
            
            # Format results similar to OpenClaw's memory_search
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result.get("text", ""),
                    "path": result.get("source", ""),
                    "lines": f"{result.get('start_line', 1)}-{result.get('end_line', result.get('start_line', 1) + 10)}",
                    "score": float(result.get("score", 0.0)),
                    "provider": "e5-small-v2",
                    "model": "intfloat/e5-small-v2"
                })
            
            return formatted_results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def get_stats(self):
        """Get statistics about the memory system."""
        if not self.initialized:
            return {"initialized": False}
        
        return {
            "initialized": True,
            "chunks": len(self.rag.store.chunks),
            "files": len(self.rag.store.files),
            "embedding_dim": self.rag.store.embedding_engine.dimension,
            "model": "intfloat/e5-small-v2",
            "chunk_size": 256,  # Our configured chunk size
            "chunk_overlap": 64
        }

def main():
    """Command-line interface for E5 memory search."""
    import argparse
    
    parser = argparse.ArgumentParser(description="E5 Memory Search Wrapper")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum results to return")
    parser.add_argument("--min-score", type=float, default=0.3, help="Minimum similarity score")
    parser.add_argument("--stats", action="store_true", help="Show system statistics")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    # Initialize E5 Memory Search
    e5_search = E5MemorySearch()
    
    if args.stats:
        stats = e5_search.get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("📊 E5 Memory Search Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        return
    
    if not args.query:
        print("❌ Error: Query required (or use --stats)")
        parser.print_help()
        return
    
    # Perform search
    results = e5_search.search(args.query, max_results=args.max_results, min_score=args.min_score)
    
    if args.json:
        output = {
            "query": args.query,
            "results": results,
            "count": len(results)
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"🔍 Search results for: '{args.query}'")
        print(f"📊 Found {len(results)} results")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   Source: {result['path']} (lines {result['lines']})")
            print(f"   Text: {result['text'][:200]}...")
            print()

if __name__ == "__main__":
    main()