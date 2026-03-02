#!/usr/bin/env python3
"""
Basic LangGraph memory system for OpenClaw.
"""

from typing import Dict, List, TypedDict, Optional
from datetime import datetime
import json
from pathlib import Path


class Memory(TypedDict):
    id: str
    content: str
    timestamp: str
    tags: List[str]
    related_to: List[str]  # IDs of related memories


class MemoryState(TypedDict):
    query: Optional[str]
    memories: List[Memory]
    relevant: List[Memory]
    response: Optional[str]


class MemoryGraph:
    """Simple graph-based memory system."""
    
    def __init__(self, storage_path: str = "/home/ubuntu/.openclaw/memory_graph.json"):
        self.storage_path = Path(storage_path)
        self.memories: Dict[str, Memory] = {}
        self.load()
    
    def load(self):
        """Load memories from storage."""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for mem in data.get("memories", []):
                    self.memories[mem["id"]] = mem
    
    def save(self):
        """Save memories to storage."""
        data = {
            "memories": list(self.memories.values()),
            "updated": datetime.now().isoformat()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_memory(self, content: str, tags: List[str] = None, related_to: List[str] = None) -> str:
        """Add a new memory."""
        memory_id = f"mem_{len(self.memories) + 1:04d}"
        
        memory = Memory(
            id=memory_id,
            content=content,
            timestamp=datetime.now().isoformat(),
            tags=tags or [],
            related_to=related_to or []
        )
        
        self.memories[memory_id] = memory
        self.save()
        
        return memory_id
    
    def find_by_tags(self, tags: List[str]) -> List[Memory]:
        """Find memories by tags."""
        results = []
        for memory in self.memories.values():
            if any(tag in memory["tags"] for tag in tags):
                results.append(memory)
        return results
    
    def find_related(self, memory_id: str, depth: int = 1) -> List[Memory]:
        """Find memories related to a given memory."""
        if memory_id not in self.memories:
            return []
        
        related = []
        to_explore = [memory_id]
        explored = set()
        
        for _ in range(depth):
            next_level = []
            for mem_id in to_explore:
                if mem_id in explored:
                    continue
                explored.add(mem_id)
                
                memory = self.memories[mem_id]
                for related_id in memory["related_to"]:
                    if related_id in self.memories and related_id not in explored:
                        related.append(self.memories[related_id])
                        next_level.append(related_id)
            
            to_explore = next_level
        
        return related
    
    def link_memories(self, memory_id1: str, memory_id2: str):
        """Link two memories together."""
        if memory_id1 in self.memories and memory_id2 in self.memories:
            if memory_id2 not in self.memories[memory_id1]["related_to"]:
                self.memories[memory_id1]["related_to"].append(memory_id2)
            if memory_id1 not in self.memories[memory_id2]["related_to"]:
                self.memories[memory_id2]["related_to"].append(memory_id1)
            self.save()
    
    def get_timeline(self, limit: int = 10) -> List[Memory]:
        """Get recent memories in chronological order."""
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda x: x["timestamp"],
            reverse=True
        )
        return sorted_memories[:limit]
    
    def search(self, query: str) -> List[Memory]:
        """Simple search by content (would use embeddings in production)."""
        query_lower = query.lower()
        results = []
        for memory in self.memories.values():
            if query_lower in memory["content"].lower():
                results.append(memory)
        return results


def create_sample_graph():
    """Create a sample memory graph with today's events."""
    graph = MemoryGraph()
    
    # Today's key events
    mem1 = graph.add_memory(
        "Disk space crisis: Root volume 100% full, only 180MB free",
        tags=["disk", "crisis", "infrastructure"],
        related_to=[]
    )
    
    mem2 = graph.add_memory(
        "Created 50GB EBS volume (gp3, 3000 IOPS) and mounted at /data",
        tags=["ebs", "storage", "solution", "aws"],
        related_to=[mem1]
    )
    
    mem3 = graph.add_memory(
        "Installed Whisper in virtual environment for audio transcription",
        tags=["whisper", "audio", "transcription", "python"],
        related_to=[mem2]
    )
    
    mem4 = graph.add_memory(
        "Successfully transcribed 9 audio files including 'Do you understand me now?'",
        tags=["success", "audio", "transcription", "telegram"],
        related_to=[mem3]
    )
    
    mem5 = graph.add_memory(
        "Created skill creation protocol: 'If you cannot do something, create a skill to do it'",
        tags=["protocol", "skills", "self-improvement"],
        related_to=[]
    )
    
    mem6 = graph.add_memory(
        "Created 7 skills: notion-browser-bridge, audio-transcription, audio-transcriber, audio-transcription-alt, multimedia-processing, system-diagnostics, service-management",
        tags=["skills", "productivity", "automation"],
        related_to=[mem5]
    )
    
    # Link related memories
    graph.link_memories(mem1, mem2)  # Problem → Solution
    graph.link_memories(mem3, mem4)  # Installation → Success
    graph.link_memories(mem5, mem6)  # Protocol → Implementation
    
    return graph


def main():
    """Demo the memory graph."""
    print("=== LangGraph Memory System Demo ===\n")
    
    # Create sample graph
    graph = create_sample_graph()
    
    # Demo 1: Timeline
    print("1. Recent Timeline:")
    for memory in graph.get_timeline(5):
        print(f"   [{memory['timestamp'][:16]}] {memory['content'][:60]}...")
    
    # Demo 2: Search
    print("\n2. Search for 'audio':")
    for memory in graph.search("audio"):
        print(f"   - {memory['content'][:50]}...")
    
    # Demo 3: Related memories
    print("\n3. Memories related to disk crisis:")
    disk_mem = graph.search("disk")[0]
    for memory in graph.find_related(disk_mem["id"]):
        print(f"   - {memory['content'][:50]}...")
    
    # Demo 4: Tag-based retrieval
    print("\n4. Memories tagged 'success':")
    for memory in graph.find_by_tags(["success"]):
        print(f"   - {memory['content']}")
    
    # Stats
    print(f"\n=== Stats ===")
    print(f"Total memories: {len(graph.memories)}")
    print(f"Storage: {graph.storage_path}")
    
    # Save to file
    graph.save()
    print(f"\nGraph saved to: {graph.storage_path}")


if __name__ == "__main__":
    main()
