#!/home/ubuntu/.openclaw/workspace/.venv-embeddings/bin/python3
"""
On-the-run LangGraph-E5 Sync System
Lightweight, incremental sync that runs continuously
"""

import os
import sys
import json
import time
import hashlib
import glob
import multiprocessing
from datetime import datetime, timedelta
from pathlib import Path
import traceback

# Add workspace to path
workspace_dir = "/home/ubuntu/.openclaw/workspace"
sys.path.insert(0, workspace_dir)

class OnTheRunSync:
    """Continuous sync system for LangGraph ↔ E5 embeddings."""
    
    def __init__(self):
        self.workspace_dir = workspace_dir
        self.memory_dir = os.path.join(workspace_dir, "memory")
        self.e5_cache_dir = os.path.join(self.memory_dir, "embeddings")
        self.state_file = os.path.join(self.e5_cache_dir, "sync_state.json")
        
        # Create directories if they don't exist
        os.makedirs(self.e5_cache_dir, exist_ok=True)
        
        # Load or initialize sync state
        self.state = self._load_state()
        
        # Performance tracking
        self.last_sync_time = None
        self.sync_count = 0
        
        print(f"🔁 On-The-Run Sync System initialized")
        print(f"   Memory dir: {self.memory_dir}")
        print(f"   E5 cache: {self.e5_cache_dir}")
        print(f"   State: {len(self.state.get('file_hashes', {}))} files tracked")
    
    def _load_state(self) -> dict:
        """Load sync state from file."""
        default_state = {
            "last_sync": None,
            "file_hashes": {},  # filepath -> hash
            "sync_count": 0,
            "total_files_synced": 0,
            "last_error": None
        }
        
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                return {**default_state, **state}  # Merge with defaults
            except Exception as e:
                print(f"⚠️  Failed to load state: {e}")
                return default_state
        return default_state
    
    def _save_state(self):
        """Save sync state to file."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Failed to save state: {e}")
    
    def _file_hash(self, filepath: str) -> str:
        """Calculate hash of file content."""
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"⚠️  Failed to hash {filepath}: {e}")
            return ""
    
    def _check_for_changes(self) -> list:
        """Check which tracked files have changed since last sync."""
        changed_files = []
        
        # Get all tracked files (same patterns as EnhancedMemoryGraph)
        tracked_files = []
        
        # 1. Memory files
        tracked_files.extend(list(Path(self.memory_dir).glob("*.md")))
        tracked_files.append(Path(os.path.join(self.workspace_dir, "MEMORY.md")))
        
        # 2. Configuration files
        config_files = [
            "SOUL.md", "AGENTS.md", "TOOLS.md", "IDENTITY.md",
            "HEARTBEAT.md", "USER.md", "PROJECT.md"
        ]
        for config_file in config_files:
            filepath = Path(os.path.join(self.workspace_dir, config_file))
            if filepath.exists():
                tracked_files.append(filepath)
        
        # 3. Thesis chapters and writing
        thesis_patterns = [
            "ba_thesis_chapter*.md",
            "writing/*.md"
        ]
        for pattern in thesis_patterns:
            tracked_files.extend(Path(self.workspace_dir).glob(pattern))
        
        # 4. Skills documentation
        tracked_files.extend(Path(self.workspace_dir).glob("skills/*/SKILL.md"))
        
        # Remove duplicates and non-existent files
        unique_files = []
        seen = set()
        for filepath in tracked_files:
            if not filepath.exists():
                continue
            filepath_str = str(filepath)
            if filepath_str not in seen:
                seen.add(filepath_str)
                unique_files.append(filepath)
        
        # Check each file for changes
        for filepath in unique_files:
            filepath_str = str(filepath)
            current_hash = self._file_hash(filepath_str)
            
            if not current_hash:
                continue
            
            # Check if file is new or changed
            if filepath_str not in self.state["file_hashes"]:
                changed_files.append(filepath_str)
                print(f"   📄 New file: {os.path.basename(filepath_str)}")
            elif self.state["file_hashes"][filepath_str] != current_hash:
                changed_files.append(filepath_str)
                print(f"   📄 Changed: {os.path.basename(filepath_str)}")
        
        return changed_files
    
    def _load_langgraph_memories(self):
        """Load memories from LangGraph system."""
        try:
            # Try to import EnhancedMemoryGraph
            sys.path.insert(0, self.workspace_dir)
            from enhanced_memory_graph import EnhancedMemoryGraph
            
            print("   Loading EnhancedMemoryGraph...")
            memory_graph = EnhancedMemoryGraph()
            
            # Extract embeddings and metadata
            embeddings_data = []
            metadata = []
            
            for memory_id, memory in memory_graph.memories.items():
                if memory.embedding:  # Only include memories with embeddings
                    # Skip memories with empty content
                    if not memory.content.strip():
                        print(f"   ⚠️  Skipping memory {memory_id} with empty content")
                        continue
                    
                    embeddings_data.append({
                        "id": memory_id,
                        "embedding": memory.embedding,
                        "source": memory.source_file,
                        "timestamp": memory.timestamp.isoformat() if hasattr(memory.timestamp, 'isoformat') else str(memory.timestamp)
                    })
                    
                    metadata.append({
                        "id": memory_id,
                        "content": memory.content,  # Full content for memory_rag.py
                        "tags": memory.tags,
                        "keywords": memory.keywords,
                        "source": memory.source_file,
                        "line_start": memory.line_range[0] if hasattr(memory, 'line_range') else 1,
                        "line_end": memory.line_range[1] if hasattr(memory, 'line_range') else 10
                    })
            
            return {
                "success": True,
                "embeddings": embeddings_data,
                "metadata": metadata,
                "total_memories": len(memory_graph.memories),
                "embedded_memories": len(embeddings_data)
            }
            
        except ImportError as e:
            print(f"   ⚠️  LangGraph not available: {e}")
            return {"success": False, "error": f"LangGraph import failed: {e}"}
        except Exception as e:
            print(f"   ⚠️  Failed to load LangGraph: {e}")
            return {"success": False, "error": str(e)}
    
    def _save_to_e5_cache(self, data: dict):
        """Save embeddings to E5 cache."""
        try:
            # Create timestamped backup of current cache
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.e5_cache_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup existing files
            for filename in ["memory_embeddings.json", "memory_embeddings.npy"]:
                src = os.path.join(self.e5_cache_dir, filename)
                if os.path.exists(src):
                    dst = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
                    import shutil
                    shutil.copy2(src, dst)
            
            # Save new embeddings
            import numpy as np
            
            # Convert to numpy array
            embeddings = [item["embedding"] for item in data["embeddings"]]
            if not embeddings:
                print("   ⚠️  No embeddings to save, skipping cache update")
                return False
            
            embedding_matrix = np.array(embeddings)
            npy_path = os.path.join(self.e5_cache_dir, "memory_embeddings.npy")
            np.save(npy_path, embedding_matrix)
            print(f"   💾 Saved {len(embeddings)} embeddings to {npy_path}")
            
            # Save metadata in memory_rag.py compatible format
            # Convert metadata to memory_rag.py format: chunk_ids list and chunks dict
            chunk_ids = []
            chunks_dict = {}
            
            for i, emb_item in enumerate(data["embeddings"]):
                # Find corresponding metadata
                meta_item = None
                for meta in data["metadata"]:
                    if meta["id"] == emb_item["id"]:
                        meta_item = meta
                        break
                
                if not meta_item:
                    print(f"   ⚠️  No metadata found for chunk {emb_item['id']}")
                    continue
                
                chunk_id = emb_item["id"]
                chunk_ids.append(chunk_id)
                
                # Extract line range from metadata if available
                # metadata from LangGraph might not have line range, use defaults
                line_start = meta_item.get("line_start", 1)
                line_end = meta_item.get("line_end", line_start + 10)
                
                chunks_dict[chunk_id] = {
                    "id": chunk_id,
                    "text": meta_item.get("content", ""),
                    "source": meta_item.get("source", ""),
                    "line_start": line_start,
                    "line_end": line_end,
                    "timestamp": emb_item.get("timestamp", datetime.now().isoformat()),
                    "embedding_shape": [len(emb_item["embedding"])]  # Store embedding dimension
                }
            
            json_data = {
                "chunk_ids": chunk_ids,
                "chunks": chunks_dict,
                "timestamp": datetime.now().isoformat(),
                "embedding_shape": [len(data["embeddings"]), len(data["embeddings"][0]["embedding"])]
            }
            
            json_path = os.path.join(self.e5_cache_dir, "memory_embeddings.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 Saved metadata for {len(chunk_ids)} chunks to {json_path}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to save to E5 cache: {e}")
            return False
    
    def sync_if_needed(self, force: bool = False, fast_mode: bool = False, timeout_seconds: int = 120) -> dict:
        """
        Perform sync if files have changed.
        
        Args:
            force: Force sync even if no changes detected
            fast_mode: Only check changes, don't load LangGraph or sync
            
        Returns:
            Dictionary with sync results
        """
        start_time = time.time()
        
        print(f"\n🔍 Checking for changes...")
        
        # Check for changes
        changed_files = self._check_for_changes()
        
        if not changed_files and not force:
            print(f"   ✅ No changes detected. Last sync: {self.state.get('last_sync', 'never')}")
            return {
                "success": True,
                "synced": False,
                "reason": "no_changes",
                "changed_files": [],
                "time_elapsed": time.time() - start_time,
                "fast_mode": fast_mode
            }
        
        print(f"   📊 Changes detected: {len(changed_files)} files")
        for file in changed_files[:3]:  # Show first 3 only
            print(f"      - {os.path.basename(file)}")
        if len(changed_files) > 3:
            print(f"      ... and {len(changed_files) - 3} more")
        
        # Fast mode: just report changes, don't sync
        if fast_mode:
            print(f"   ⚡ Fast mode: changes detected but skipping sync")
            time_elapsed = time.time() - start_time
            return {
                "success": True,
                "synced": False,
                "reason": "fast_mode",
                "changed_files": changed_files,
                "time_elapsed": time_elapsed,
                "fast_mode": True,
                "recommendation": f"Run full sync to update {len(changed_files)} changed files"
            }
        
        # Full mode: load LangGraph and sync
        print(f"   🔄 Loading LangGraph memories...")
        langgraph_data = self._load_langgraph_memories()
        
        if not langgraph_data.get("success"):
            return {
                "success": False,
                "error": langgraph_data.get("error", "Unknown error"),
                "time_elapsed": time.time() - start_time,
                "fast_mode": False
            }
        
        print(f"   ✅ Loaded {langgraph_data['embedded_memories']} embeddings from {langgraph_data['total_memories']} memories")
        
        # Save to E5 cache
        print(f"   💾 Saving to E5 cache...")
        save_success = self._save_to_e5_cache(langgraph_data)
        
        if not save_success:
            return {
                "success": False,
                "error": "Failed to save to E5 cache",
                "time_elapsed": time.time() - start_time,
                "fast_mode": False
            }
        
        # Update state
        self.sync_count += 1
        self.state["last_sync"] = datetime.now().isoformat()
        self.state["sync_count"] = self.sync_count
        self.state["total_files_synced"] = self.state.get("total_files_synced", 0) + len(changed_files)
        
        # Update file hashes
        for filepath in changed_files:
            self.state["file_hashes"][filepath] = self._file_hash(filepath)
        
        self._save_state()
        
        time_elapsed = time.time() - start_time
        
        print(f"   ✅ Sync completed in {time_elapsed:.2f}s")
        print(f"      Files: {len(changed_files)}")
        print(f"      Embeddings: {langgraph_data['embedded_memories']}")
        print(f"      Total syncs: {self.sync_count}")
        
        return {
            "success": True,
            "synced": True,
            "changed_files": changed_files,
            "embeddings_synced": langgraph_data['embedded_memories'],
            "total_memories": langgraph_data['total_memories'],
            "time_elapsed": time_elapsed,
            "sync_count": self.sync_count,
            "fast_mode": False
        }
    
    def get_status(self) -> dict:
        """Get current sync status."""
        status = {
            "system": "on_the_run_sync",
            "last_sync": self.state.get("last_sync"),
            "sync_count": self.state.get("sync_count", 0),
            "total_files_tracked": len(self.state.get("file_hashes", {})),
            "total_files_synced": self.state.get("total_files_synced", 0),
            "last_error": self.state.get("last_error"),
            "e5_cache_exists": os.path.exists(os.path.join(self.e5_cache_dir, "memory_embeddings.json")),
            "state_file_exists": os.path.exists(self.state_file)
        }
        
        # Check E5 cache age
        e5_json = os.path.join(self.e5_cache_dir, "memory_embeddings.json")
        if os.path.exists(e5_json):
            mtime = os.path.getmtime(e5_json)
            status["e5_cache_age_seconds"] = time.time() - mtime
            status["e5_cache_age_human"] = str(timedelta(seconds=int(time.time() - mtime)))
        
        return status


def main():
    """Main function with command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="On-the-run LangGraph-E5 Sync System")
    parser.add_argument("--sync", action="store_true", help="Perform sync if needed")
    parser.add_argument("--fast", action="store_true", help="Fast mode: check changes only, don't load LangGraph")
    parser.add_argument("--force", action="store_true", help="Force sync even if no changes")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    parser.add_argument("--watch", action="store_true", help="Watch for changes continuously")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval in seconds (default: 60)")
    parser.add_argument("--reset", action="store_true", help="Reset sync state")
    
    args = parser.parse_args()
    
    # Initialize sync system
    sync_system = OnTheRunSync()
    
    if args.reset:
        # Reset state
        import shutil
        if os.path.exists(sync_system.state_file):
            backup = f"{sync_system.state_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.move(sync_system.state_file, backup)
            print(f"✅ State reset. Backup saved to: {backup}")
        
        # Reinitialize
        sync_system = OnTheRunSync()
        print("✅ Sync system reinitialized with fresh state")
    
    elif args.status:
        # Show status
        status = sync_system.get_status()
        print("\n📊 Sync System Status")
        print("=" * 50)
        for key, value in status.items():
            print(f"{key:25}: {value}")
        
        # Check if sync is needed
        changed_files = sync_system._check_for_changes()
        if changed_files:
            print(f"\n⚠️  Pending changes: {len(changed_files)} files")
            for file in changed_files[:3]:  # Show first 3
                print(f"   - {os.path.basename(file)}")
            if len(changed_files) > 3:
                print(f"   ... and {len(changed_files) - 3} more")
        else:
            print(f"\n✅ No pending changes")
    
    elif args.watch:
        # Continuous watch mode
        print(f"👀 Starting watch mode (interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                result = sync_system.sync_if_needed()
                
                if result.get("synced"):
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Synced {result['embeddings_synced']} embeddings")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏸️  No changes")
                
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\n👋 Watch mode stopped")
    
    elif args.sync or (not args.status and not args.watch and not args.reset):
        # Perform sync (default action)
        result = sync_system.sync_if_needed(force=args.force)
        
        print("\n📋 Sync Result")
        print("=" * 50)
        
        if result.get("success"):
            if result.get("synced"):
                print(f"✅ Sync successful")
                print(f"   Time: {result.get('time_elapsed', 0):.2f}s")
                print(f"   Files: {len(result.get('changed_files', []))}")
                print(f"   Embeddings: {result.get('embeddings_synced', 0)}")
                print(f"   Total syncs: {result.get('sync_count', 0)}")
            else:
                print(f"✅ No sync needed")
                print(f"   Reason: {result.get('reason', 'unknown')}")
        else:
            print(f"❌ Sync failed")
            print(f"   Error: {result.get('error', 'unknown')}")
        
        # Show status after sync
        status = sync_system.get_status()
        print(f"\n📅 Last sync: {status.get('last_sync', 'never')}")
        print(f"🔄 Sync count: {status.get('sync_count', 0)}")
        print(f"📁 Files tracked: {status.get('total_files_tracked', 0)}")
        
        if status.get("e5_cache_age_human"):
            print(f"⏰ E5 cache age: {status['e5_cache_age_human']}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 On-The-Run LangGraph ↔ E5 Sync System")
    print("=" * 60)
    main()