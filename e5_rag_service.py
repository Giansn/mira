#!/usr/bin/env python3
"""
E5 RAG Service for OpenClaw Integration
Provides semantic memory search as a service that OpenClaw can call
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from memory_rag import MemoryRAG
    HAS_RAG = True
except ImportError as e:
    print(f"❌ Failed to import MemoryRAG: {e}")
    HAS_RAG = False


class E5RAGService:
    """Service wrapper for E5 Memory RAG system."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.dirname(os.path.abspath(__file__))
        self.rag = None
        self.initialized = False
        
    def initialize(self) -> Dict[str, Any]:
        """Initialize the RAG system."""
        try:
            if not HAS_RAG:
                return {
                    "success": False,
                    "error": "MemoryRAG not available",
                    "mock_mode": True
                }
            
            self.rag = MemoryRAG(workspace_dir=self.workspace_dir)
            self.initialized = True
            
            # Get stats
            stats = self.get_stats()
            
            return {
                "success": True,
                "message": "E5 RAG Service initialized",
                "stats": stats,
                "mock_mode": self.rag.mock_mode if hasattr(self.rag, 'mock_mode') else False
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "initialized": False
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        if not self.initialized or not self.rag:
            return {"error": "Service not initialized"}
        
        try:
            # Try to get chunk count
            chunk_count = 0
            if hasattr(self.rag, 'memory_store') and hasattr(self.rag.memory_store, 'chunks'):
                chunk_count = len(self.rag.memory_store.chunks)
            elif hasattr(self.rag, 'chunks'):
                chunk_count = len(self.rag.chunks)
            
            return {
                "chunks": chunk_count,
                "initialized": self.initialized,
                "workspace": self.workspace_dir,
                "service": "E5 RAG Memory Search"
            }
        except:
            return {"chunks": "unknown", "initialized": self.initialized}
    
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform semantic search."""
        if not self.initialized:
            init_result = self.initialize()
            if not init_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to initialize RAG service",
                    "details": init_result
                }
        
        try:
            results = self.rag.retrieve(query, top_k=top_k)
            
            # Format results for OpenClaw compatibility
            formatted_results = []
            for result in results:
                if isinstance(result, dict):
                    formatted_results.append(result)
                else:
                    # Convert object to dict
                    formatted_results.append({
                        "score": getattr(result, 'score', 0.0),
                        "text": getattr(result, 'text', ''),
                        "source": getattr(result, 'source', ''),
                        "lines": f"{getattr(result, 'line_start', 0)}-{getattr(result, 'line_end', 0)}",
                        "chunk_id": getattr(result, 'chunk_id', '')
                    })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "provider": "e5-rag-service",
                "model": "intfloat/e5-small-v2"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def update_embeddings(self) -> Dict[str, Any]:
        """Update embeddings for new/changed memory files."""
        if not self.initialized:
            return {"success": False, "error": "Service not initialized"}
        
        try:
            if hasattr(self.rag, 'update_embeddings'):
                result = self.rag.update_embeddings()
                return {
                    "success": True,
                    "message": "Embeddings updated",
                    "details": result
                }
            else:
                return {
                    "success": False,
                    "error": "update_embeddings method not available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# CLI Interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="E5 RAG Service for OpenClaw")
    parser.add_argument("--init", action="store_true", help="Initialize service")
    parser.add_argument("--stats", action="store_true", help="Get service statistics")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    parser.add_argument("--update", action="store_true", help="Update embeddings")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    service = E5RAGService()
    
    if args.init:
        result = service.initialize()
    elif args.stats:
        result = service.get_stats()
    elif args.search:
        result = service.search(args.search, args.top_k)
    elif args.update:
        result = service.update_embeddings()
    else:
        # Default: show status
        result = service.initialize()
        if result.get("success"):
            result = service.get_stats()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success", False):
            print("✅ Success:")
            for key, value in result.items():
                if key != "success":
                    print(f"  {key}: {value}")
        else:
            print("❌ Failed:")
            for key, value in result.items():
                if key != "success":
                    print(f"  {key}: {value}")