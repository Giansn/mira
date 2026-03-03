#!/usr/bin/env python3
"""
E5-small-v2 Embedding Engine for OpenClaw Memory System
"""

import os
import sys
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import json
from datetime import datetime

# Add virtual environment path
venv_path = "/home/ubuntu/.openclaw/workspace/.venv-embeddings"
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, "lib", "python3.12", "site-packages")
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

try:
    from sentence_transformers import SentenceTransformer
    import torch
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    print("⚠️  Warning: sentence-transformers not available. Using mock embeddings.")


class E5EmbeddingEngine:
    """E5-small-v2 embedding engine for semantic memory search."""
    
    def __init__(self, model_name: str = "intfloat/e5-small-v2", 
                 cache_dir: Optional[str] = None,
                 device: str = "cpu"):
        """
        Initialize E5 embedding engine.
        
        Args:
            model_name: HuggingFace model name (default: e5-small-v2)
            cache_dir: Directory to cache model weights
            device: 'cpu' or 'cuda'
        """
        self.model_name = model_name
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/e5_embeddings")
        self.device = device
        self.model = None
        self.embedding_dim = 384  # E5-small-v2 dimension
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize model if dependencies available
        if HAS_DEPENDENCIES:
            self._initialize_model()
        else:
            print("⚠️  Running in mock mode (no sentence-transformers)")
    
    def _initialize_model(self):
        """Initialize the SentenceTransformer model."""
        try:
            print(f"🔧 Loading model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=self.cache_dir,
                device=self.device
            )
            print(f"✅ Model loaded: {self.model_name}")
            print(f"   Device: {self.device}")
            print(f"   Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.model = None
    
    def embed(self, texts: List[str], prefix: str = "query") -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            prefix: "query" or "passage" (E5 models require prefix)
            
        Returns:
            numpy array of embeddings (n_texts x embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # E5 models require prefix: "query: " or "passage: "
        prefixed_texts = [f"{prefix}: {text}" for text in texts]
        
        if self.model is not None and HAS_DEPENDENCIES:
            # Use real model
            embeddings = self.model.encode(
                prefixed_texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return embeddings
        else:
            # Mock embeddings for testing
            n_texts = len(texts)
            embeddings = np.random.randn(n_texts, self.embedding_dim).astype(np.float32)
            # Normalize mock embeddings
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms
            return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a search query."""
        return self.embed([query], prefix="query")[0]
    
    def embed_passages(self, passages: List[str]) -> np.ndarray:
        """Embed memory passages for storage."""
        return self.embed(passages, prefix="passage")
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (-1 to 1)
        """
        if embedding1.ndim == 1:
            embedding1 = embedding1.reshape(1, -1)
        if embedding2.ndim == 1:
            embedding2 = embedding2.reshape(1, -1)
        
        # Cosine similarity = dot product of normalized vectors
        return float(np.dot(embedding1, embedding2.T).item())
    
    def search(self, query: str, passages: List[str], 
               top_k: int = 5, threshold: float = 0.0) -> List[Tuple[int, float, str]]:
        """
        Semantic search for passages most similar to query.
        
        Args:
            query: Search query string
            passages: List of passage strings to search
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (index, similarity, passage) tuples sorted by similarity
        """
        if not passages:
            return []
        
        # Embed query and passages
        query_embedding = self.embed_query(query)
        passage_embeddings = self.embed_passages(passages)
        
        # Compute similarities
        similarities = []
        for i, passage_embedding in enumerate(passage_embeddings):
            sim = self.similarity(query_embedding, passage_embedding)
            if sim >= threshold:
                similarities.append((i, sim, passages[i]))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        return similarities[:top_k]
    
    def batch_search(self, queries: List[str], passages: List[str],
                     top_k: int = 5) -> List[List[Tuple[int, float, str]]]:
        """
        Batch semantic search for multiple queries.
        
        Args:
            queries: List of query strings
            passages: List of passage strings
            top_k: Number of top results per query
            
        Returns:
            List of results for each query
        """
        if not queries or not passages:
            return []
        
        # Embed all queries and passages
        query_embeddings = self.embed(queries, prefix="query")
        passage_embeddings = self.embed_passages(passages)
        
        # Compute similarity matrix
        similarity_matrix = np.dot(query_embeddings, passage_embeddings.T)
        
        # Get top_k for each query
        results = []
        for i in range(len(queries)):
            similarities = similarity_matrix[i]
            top_indices = np.argsort(similarities)[::-1][:top_k]
            query_results = []
            for idx in top_indices:
                query_results.append((int(idx), float(similarities[idx]), passages[idx]))
            results.append(query_results)
        
        return results
    
    def save_embeddings(self, embeddings: np.ndarray, filepath: str):
        """Save embeddings to file."""
        np.save(filepath, embeddings)
        print(f"💾 Saved embeddings to {filepath}")
    
    def load_embeddings(self, filepath: str) -> np.ndarray:
        """Load embeddings from file."""
        if os.path.exists(filepath):
            embeddings = np.load(filepath)
            print(f"📂 Loaded embeddings from {filepath}")
            return embeddings
        else:
            print(f"⚠️  Embeddings file not found: {filepath}")
            return np.array([])
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        info = {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "device": self.device,
            "has_dependencies": HAS_DEPENDENCIES,
            "model_loaded": self.model is not None,
            "cache_dir": self.cache_dir,
            "timestamp": datetime.now().isoformat()
        }
        return info


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing E5 Embedding Engine")
    print("=" * 50)
    
    # Initialize engine
    engine = E5EmbeddingEngine()
    
    # Get model info
    info = engine.get_model_info()
    print("📊 Model Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test embeddings
    test_texts = [
        "OpenClaw is an AI assistant platform.",
        "Memory systems store long-term context.",
        "Embedding engines convert text to vectors.",
        "Semantic search finds similar content."
    ]
    
    print(f"\n🔧 Testing with {len(test_texts)} texts...")
    
    # Test query embedding
    query = "AI assistant memory systems"
    query_embedding = engine.embed_query(query)
    print(f"✅ Query embedding shape: {query_embedding.shape}")
    
    # Test passage embeddings
    passage_embeddings = engine.embed_passages(test_texts)
    print(f"✅ Passage embeddings shape: {passage_embeddings.shape}")
    
    # Test similarity
    sim = engine.similarity(query_embedding, passage_embeddings[0])
    print(f"✅ Similarity score: {sim:.4f}")
    
    # Test search
    print(f"\n🔍 Testing semantic search...")
    results = engine.search(query, test_texts, top_k=3)
    
    print("📋 Search Results:")
    for i, (idx, score, text) in enumerate(results):
        print(f"  {i+1}. Score: {score:.4f}")
        print(f"     Text: {text[:80]}...")
    
    # Test batch search
    print(f"\n📚 Testing batch search...")
    queries = ["AI assistants", "memory storage"]
    batch_results = engine.batch_search(queries, test_texts, top_k=2)
    
    for q_idx, q in enumerate(queries):
        print(f"  Query: '{q}'")
        for r_idx, (idx, score, text) in enumerate(batch_results[q_idx]):
            print(f"    {r_idx+1}. Score: {score:.4f} - {text[:60]}...")
    
    print("\n✅ E5 Embedding Engine test completed!")