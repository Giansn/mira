#!/usr/bin/env python3
"""
Memory RAG System with E5-small-v2 Embeddings
Simple Retrieval-Augmented Generation for OpenClaw Memory
"""

import os
import sys
import json
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import hashlib
from pathlib import Path

# Add virtual environment path
venv_path = "/home/ubuntu/.openclaw/workspace/.venv-embeddings"
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, "lib", "python3.12", "site-packages")
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

try:
    from e5_embedding_engine import E5EmbeddingEngine
    HAS_E5 = True
except ImportError:
    HAS_E5 = False
    print("⚠️  E5EmbeddingEngine not found. Using mock mode.")


class MemoryChunk:
    """Represents a chunk of memory with metadata."""
    
    def __init__(self, text: str, source: str, line_start: int, line_end: int, 
                 timestamp: Optional[str] = None):
        self.text = text.strip()
        self.source = source  # e.g., "MEMORY.md", "memory/2026-03-02.md"
        self.line_start = line_start
        self.line_end = line_end
        self.timestamp = timestamp or datetime.now().isoformat()
        self.embedding = None
        self.chunk_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for this memory chunk."""
        content = f"{self.source}:{self.line_start}:{self.line_end}:{self.text}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.chunk_id,
            "text": self.text,
            "source": self.source,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "timestamp": self.timestamp,
            "embedding_shape": self.embedding.shape if self.embedding is not None else None
        }
    
    def __repr__(self) -> str:
        return f"MemoryChunk(id={self.chunk_id}, source={self.source}, lines={self.line_start}-{self.line_end})"


class MemoryStore:
    """Manages memory chunks and their embeddings."""
    
    def __init__(self, workspace_dir: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace_dir = workspace_dir
        self.memory_dir = os.path.join(workspace_dir, "memory")
        self.chunks: Dict[str, MemoryChunk] = {}
        self.embeddings: np.ndarray = None
        self.chunk_ids: List[str] = []
        
        # Create memory directory if it doesn't exist
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Initialize embedding engine
        if HAS_E5:
            self.embedder = E5EmbeddingEngine()
        else:
            self.embedder = None
            print("⚠️  Running in mock mode (no E5 engine)")
    
    def load_memory_files(self) -> List[MemoryChunk]:
        """
        Load all memory files and chunk them.
        
        Returns:
            List of MemoryChunk objects
        """
        chunks = []
        
        # Load MEMORY.md
        memory_file = os.path.join(self.workspace_dir, "MEMORY.md")
        if os.path.exists(memory_file):
            chunks.extend(self._chunk_file(memory_file, "MEMORY.md"))
        
        # Load daily memory files
        if os.path.exists(self.memory_dir):
            for filename in sorted(os.listdir(self.memory_dir)):
                if filename.endswith(".md"):
                    filepath = os.path.join(self.memory_dir, filename)
                    chunks.extend(self._chunk_file(filepath, f"memory/{filename}"))
        
        # Store chunks
        for chunk in chunks:
            self.chunks[chunk.chunk_id] = chunk
            self.chunk_ids.append(chunk.chunk_id)
        
        print(f"📚 Loaded {len(chunks)} memory chunks from {len(set(c.source for c in chunks))} files")
        return chunks
    
    def _chunk_file(self, filepath: str, source_name: str) -> List[MemoryChunk]:
        """
        Chunk a memory file into manageable pieces.
        
        Args:
            filepath: Path to the memory file
            source_name: Name for the source (e.g., "MEMORY.md")
            
        Returns:
            List of MemoryChunk objects
        """
        chunks = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Simple chunking: group by sections (lines starting with ## or ###)
            current_chunk = []
            current_start = 1
            in_code_block = False
            
            for i, line in enumerate(lines, 1):
                # Skip code blocks
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                
                if in_code_block:
                    continue
                
                # Start new chunk on section headers or after 10 lines
                is_section_header = line.strip().startswith("##")
                is_large_chunk = len(current_chunk) >= 10
                
                if (is_section_header or is_large_chunk) and current_chunk:
                    # Save current chunk
                    chunk_text = "".join(current_chunk).strip()
                    if chunk_text and len(chunk_text) > 20:  # Minimum length
                        chunk = MemoryChunk(
                            text=chunk_text,
                            source=source_name,
                            line_start=current_start,
                            line_end=i-1,
                            timestamp=self._extract_timestamp(chunk_text)
                        )
                        chunks.append(chunk)
                    
                    # Start new chunk
                    current_chunk = []
                    current_start = i
                
                current_chunk.append(line)
            
            # Add final chunk
            if current_chunk:
                chunk_text = "".join(current_chunk).strip()
                if chunk_text and len(chunk_text) > 20:
                    chunk = MemoryChunk(
                        text=chunk_text,
                        source=source_name,
                        line_start=current_start,
                        line_end=len(lines),
                        timestamp=self._extract_timestamp(chunk_text)
                    )
                    chunks.append(chunk)
        
        except Exception as e:
            print(f"❌ Error chunking {filepath}: {e}")
        
        return chunks
    
    def _extract_timestamp(self, text: str) -> Optional[str]:
        """Extract timestamp from memory text."""
        # Look for timestamp patterns
        import re
        patterns = [
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)",
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",
            r"Timestamp.*?(\d{4}-\d{2}-\d{2})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def generate_embeddings(self) -> np.ndarray:
        """
        Generate embeddings for all memory chunks.
        
        Returns:
            numpy array of embeddings
        """
        if not self.chunks:
            print("⚠️  No memory chunks to embed")
            return np.array([])
        
        if self.embedder is None:
            print("⚠️  No embedding engine available")
            return np.array([])
        
        print(f"🔧 Generating embeddings for {len(self.chunks)} memory chunks...")
        
        # Extract texts
        texts = [self.chunks[chunk_id].text for chunk_id in self.chunk_ids]
        
        # Generate embeddings
        embeddings = self.embedder.embed_passages(texts)
        
        # Store embeddings in chunks
        for i, chunk_id in enumerate(self.chunk_ids):
            self.chunks[chunk_id].embedding = embeddings[i]
        
        # Store as class attribute
        self.embeddings = embeddings
        
        print(f"✅ Generated {embeddings.shape[0]} embeddings ({embeddings.shape[1]} dimensions each)")
        return embeddings
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Tuple[MemoryChunk, float]]:
        """
        Semantic search across memory chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (MemoryChunk, similarity_score) tuples
        """
        if not self.chunks or self.embeddings is None:
            print("⚠️  No embeddings available for search")
            return []
        
        if self.embedder is None:
            print("⚠️  No embedding engine available")
            return []
        
        # Search using E5 engine
        texts = [self.chunks[chunk_id].text for chunk_id in self.chunk_ids]
        results = self.embedder.search(query, texts, top_k=top_k, threshold=threshold)
        
        # Convert to MemoryChunk results
        chunk_results = []
        for idx, score, _ in results:
            chunk_id = self.chunk_ids[idx]
            chunk = self.chunks[chunk_id]
            chunk_results.append((chunk, score))
        
        return chunk_results
    
    def save_embeddings(self, filepath: str):
        """Save embeddings and metadata to file."""
        if self.embeddings is None:
            print("⚠️  No embeddings to save")
            return
        
        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save embeddings
        np.save(filepath + ".npy", self.embeddings)
        
        # Save metadata
        metadata = {
            "chunk_ids": self.chunk_ids,
            "chunks": {chunk_id: self.chunks[chunk_id].to_dict() for chunk_id in self.chunk_ids},
            "timestamp": datetime.now().isoformat(),
            "embedding_shape": self.embeddings.shape
        }
        
        with open(filepath + ".json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved embeddings and metadata to {filepath}")
    
    def load_embeddings(self, filepath: str) -> bool:
        """
        Load embeddings and metadata from file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load embeddings
            embeddings_path = filepath + ".npy"
            if not os.path.exists(embeddings_path):
                print(f"⚠️  Embeddings file not found: {embeddings_path}")
                return False
            
            self.embeddings = np.load(embeddings_path)
            
            # Load metadata
            metadata_path = filepath + ".json"
            if not os.path.exists(metadata_path):
                print(f"⚠️  Metadata file not found: {metadata_path}")
                return False
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Reconstruct chunks
            self.chunk_ids = metadata["chunk_ids"]
            self.chunks = {}
            
            for chunk_id, chunk_data in metadata["chunks"].items():
                chunk = MemoryChunk(
                    text=chunk_data["text"],
                    source=chunk_data["source"],
                    line_start=chunk_data["line_start"],
                    line_end=chunk_data["line_end"],
                    timestamp=chunk_data["timestamp"]
                )
                chunk.chunk_id = chunk_id
                chunk.embedding = None  # Will be loaded from embeddings array
                self.chunks[chunk_id] = chunk
            
            print(f"📂 Loaded {len(self.chunks)} memory chunks with {self.embeddings.shape[0]} embeddings")
            return True
            
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory store."""
        stats = {
            "total_chunks": len(self.chunks),
            "sources": len(set(chunk.source for chunk in self.chunks.values())),
            "has_embeddings": self.embeddings is not None,
            "embedding_shape": self.embeddings.shape if self.embeddings is not None else None,
            "embedding_engine": "E5-small-v2" if HAS_E5 and self.embedder is not None else "Mock",
            "timestamp": datetime.now().isoformat()
        }
        
        # Add source distribution
        source_dist = {}
        for chunk in self.chunks.values():
            source_dist[chunk.source] = source_dist.get(chunk.source, 0) + 1
        stats["source_distribution"] = source_dist
        
        return stats


class MemoryRAG:
    """Simple RAG system for memory retrieval and generation."""
    
    def __init__(self, workspace_dir: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace_dir = workspace_dir
        self.store = MemoryStore(workspace_dir)
        self.embedding_cache = os.path.join(workspace_dir, "memory", "embeddings", "memory_embeddings")
        
        # Load or generate embeddings
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize memory store with embeddings."""
        print("🧠 Initializing Memory RAG System...")
        
        # Try to load cached embeddings
        if os.path.exists(self.embedding_cache + ".npy"):
            print("📂 Loading cached embeddings...")
            if self.store.load_embeddings(self.embedding_cache):
                print("✅ Loaded embeddings from cache")
                return
        
        # Generate new embeddings
        print("🔧 Generating new embeddings...")
        self.store.load_memory_files()
        self.store.generate_embeddings()
        
        # Save to cache
        if self.store.embeddings is not None:
            self.store.save_embeddings(self.embedding_cache)
    
    def retrieve(self, query: str, top_k: int = 5, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memory chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of result dictionaries
        """
        print(f"🔍 Searching memory for: '{query}'")
        
        results = self.store.search(query, top_k=top_k, threshold=threshold)
        
        formatted_results = []
        for chunk, score in results:
            formatted_results.append({
                "score": float(score),
                "text": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                "source": chunk.source,
                "lines": f"{chunk.line_start}-{chunk.line_end}",
                "timestamp": chunk.timestamp,
                "full_text": chunk.text
            })
        
        print(f"✅ Found {len(formatted_results)} relevant memories")
        return formatted_results
    
    def answer(self, query: str, include_context: bool = True) -> Dict[str, Any]:
        """
        Generate answer based on memory retrieval.
        
        Args:
            query: User question
            include_context: Whether to include retrieved context
            
        Returns:
            Dictionary with answer and metadata
        """
        # Retrieve relevant memories
        context_results = self.retrieve(query, top_k=3)
        
        if not context_results:
            return {
                "answer": "I couldn't find relevant information in memory to answer this question.",
                "context": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Build context string
        context_parts = []
        for i, result in enumerate(context_results, 1):
            context_parts.append(f"[Memory {i} from {result['source']} lines {result['lines']}]:\n{result['full_text']}")
        
        context = "\n\n".join(context_parts)
        
        # For now, return context (in real RAG, this would feed to LLM)
        if include_context:
            answer = f"Based on my memory, here's what I found:\n\n{context}\n\nIs this information helpful for your question about '{query}'?"
        else:
            answer = f"I found relevant information in memory about '{query}'. The most relevant memories come from {context_results[0]['source']} with {context_results[0]['score']:.2f} similarity."
        
        return {
            "answer": answer,
            "context": context_results,
            "confidence": float(context_results[0]["score"]) if context_results else 0.0,
            "timestamp": datetime.now().isoformat(),
            "query": query
        }
    
    def update_embeddings(self):
        """Update embeddings with latest memory files."""
        print("🔄 Updating memory embeddings...")
        self.store.load_memory_files()
        self.store.generate_embeddings()
        self.store.save_embeddings(self.embedding_cache)
        print("✅ Embeddings updated")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        stats = self.store.get_stats()
        stats.update({
            "embedding_cache": self.embedding_cache,
            "cache_exists": os.path.exists(self.embedding_cache + ".npy"),
            "workspace_dir": self.workspace_dir,
            "system": "Memory RAG with E5-small-v2"
        })
        return stats


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Memory RAG System")
    print("=" * 50)
    
    # Initialize RAG system
    rag = MemoryRAG()
    
    # Get status
    status = rag.get_status()
    print("📊 System Status:")
    for key, value in status.items():
        if key == "source_distribution":
            print(f"  {key}:")
            for source, count in value.items():
                print(f"    {source}: {count} chunks")
        elif key != "timestamp":
            print(f"  {key}: {value}")
    
    # Test queries
    test_queries = [
        "What is OpenClaw?",
        "Tell me about the BA thesis",
        "What skills have been created?",
        "How does the memory system work?",
        "What is E5 embedding engine?"
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} queries...")
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        # Retrieve memories
        results = rag.retrieve(query, top_k=2)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  Result {i} (score: {result['score']:.4f}):")
                print(f"    Source: {result['source']} lines {result['lines']}")
                print(f"    Text: {result['text'][:100]}...")
        else:
            print("  No relevant memories found")
    
    # Test full answer generation
    print(f"\n🤖 Testing answer generation...")
    test_query = "What has been implemented recently?"
    answer = rag.answer(test_query)
    
    print(f"Query: {answer['query']}")
    print(f"Confidence: {answer['confidence']:.4f}")
    print(f"Answer preview: {answer['answer'][:150]}...")
    
    # Update embeddings (simulate new memory)
    print(f"\n🔄 Testing embedding update...")
    rag.update_embeddings()
    
    print("\n✅ Memory RAG System test completed!")
