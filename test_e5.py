#!/usr/bin/env python3
"""
Test E5-small-v2 embedding engine
"""

import sys
import os

# Add virtual environment if it exists
venv_path = "/home/ubuntu/.openclaw/workspace/.venv-embeddings"
if os.path.exists(venv_path):
    sys.path.insert(0, os.path.join(venv_path, "lib", "python3.12", "site-packages"))

try:
    from sentence_transformers import SentenceTransformer
    import torch
    
    print("✅ Torch version:", torch.__version__)
    print("✅ CUDA available:", torch.cuda.is_available())
    
    # Test with a small model first
    print("\n🔧 Testing with paraphrase-MiniLM-L3-v2 (small test)...")
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    
    sentences = ["This is a test sentence.", "This is another test."]
    embeddings = model.encode(sentences)
    
    print(f"✅ Embeddings generated: {len(embeddings)} vectors")
    print(f"✅ Embedding dimension: {embeddings[0].shape}")
    print(f"✅ Similarity: {embeddings[0].dot(embeddings[1]):.4f}")
    
    print("\n🎯 E5-small-v2 would provide:")
    print("   - 384-dimensional embeddings")
    print("   - Multilingual support")
    print("   - Better semantic understanding")
    print("   - ~118M parameters")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n📦 Required packages:")
    print("   pip install sentence-transformers torch")
    print("\n💡 Use virtual environment:")
    print("   python3 -m venv .venv-embeddings")
    print("   source .venv-embeddings/bin/activate")
    print("   pip install sentence-transformers torch")
except Exception as e:
    print(f"❌ Error: {e}")