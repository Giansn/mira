#!/usr/bin/env python3
"""Semantic memory search using sentence-transformers."""

import os
import json
import numpy as np
from pathlib import Path

MEMORY_DIR = Path("/home/ubuntu/.openclaw/workspace/memory")
INDEX_FILE = MEMORY_DIR / ".embeddings.json"

# Files to index
INDEXED_FILES = [
    "/home/ubuntu/.openclaw/workspace/MEMORY.md",
    "/home/ubuntu/.openclaw/workspace/memory/2026-02-23.md",
    "/home/ubuntu/.openclaw/workspace/memory/2026-02-24.md",
    "/home/ubuntu/.openclaw/workspace/memory/2026-02-25.md",
    "/home/ubuntu/.openclaw/workspace/memory/2026-02-26.md",
]

def load_model():
    """Load sentence-transformer model (cached after first load)."""
    from sentence_transformers import SentenceTransformer
    if not hasattr(load_model, "_model"):
        load_model._model = SentenceTransformer('all-MiniLM-L6-v2')
    return load_model._model

def chunk_text(text, chunk_size=500):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size // 5):  # ~5 chars per word avg
        chunk = " ".join(words[i:i + chunk_size // 5])
        if chunk:
            chunks.append(chunk)
    return chunks

def build_index(force=False):
    """Build or update the embeddings index."""
    model = load_model()
    
    if INDEX_FILE.exists() and not force:
        with open(INDEX_FILE) as f:
            index_data = json.load(f)
        return index_data
    
    documents = []
    
    for filepath in INDEXED_FILES:
        p = Path(filepath)
        if p.exists():
            text = p.read_text()
            # Store file reference and full text for retrieval
            documents.append({
                "file": str(p),
                "name": p.name,
                "text": text,
                "chunks": chunk_text(text)
            })
    
    # Generate embeddings for each chunk
    all_chunks = []
    for doc in documents:
        for i, chunk in enumerate(doc["chunks"]):
            all_chunks.append({
                "file": doc["file"],
                "name": doc["name"],
                "chunk_id": i,
                "text": chunk,
                "full_text": doc["text"]
            })
    
    if not all_chunks:
        return {"chunks": [], "embeddings": []}
    
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    
    index_data = {
        "chunks": all_chunks,
        "embeddings": embeddings.tolist()
    }
    
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(index_data, f)
    
    print(f"Indexed {len(all_chunks)} chunks from {len(documents)} files")
    return index_data

def search(query, top_k=3):
    """Semantic search across indexed memory files."""
    index_data = build_index()
    
    if not index_data["chunks"]:
        return []
    
    model = load_model()
    query_embedding = model.encode([query])
    embeddings = np.array(index_data["embeddings"])
    
    # Cosine similarity
    similarities = np.dot(embeddings, query_embedding.T).flatten()
    similarities = similarities / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding))
    
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        chunk = index_data["chunks"][idx]
        results.append({
            "file": chunk["file"],
            "name": chunk["name"],
            "score": float(similarities[idx]),
            "text": chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"]
        })
    
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        results = search(query)
        for r in results:
            print(f"\n[{r['name']}] score: {r['score']:.3f}")
            print(r['text'])
    else:
        print("Building index...")
        build_index()
        print("Done.")
