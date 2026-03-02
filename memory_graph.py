#!/usr/bin/env python3
"""
LangGraph-based memory organization system for OpenClaw.
Organizes MEMORY.md and memory/*.md files into a graph structure.
"""

import os
import re
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass, field
import json

# LangGraph imports
from langgraph.graph import StateGraph, END

# Define the memory state
class MemoryState(TypedDict):
    """State for the memory graph workflow."""
    # Input
    query: Optional[str]
    new_memory_text: Optional[str]
    
    # Processing
    raw_memories: List[Dict[str, Any]]
    curated_memories: List[Dict[str, Any]]
    related_memories: List[Dict[str, Any]]
    
    # Output
    retrieved_memories: List[Dict[str, Any]]
    summary: Optional[str]
    action_taken: Optional[str]

@dataclass
class MemoryChunk:
    """Represents a single memory chunk."""
    id: str
    content: str
    source_file: str
    line_range: tuple[int, int]
    timestamp: datetime
    tags: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)  # IDs of related memories
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "source_file": self.source_file,
            "line_range": self.line_range,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "relationships": self.relationships
        }

class MemoryGraph:
    """Main memory graph system."""
    
    def __init__(self, workspace_path: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.memory_dir = os.path.join(workspace_path, "memory")
        self.memory_file = os.path.join(workspace_path, "MEMORY.md")
        
        # Initialize graph
        self.graph = self._build_graph()
        
        # Load existing memories
        self.memories: Dict[str, MemoryChunk] = {}
        self._load_existing_memories()
    
    def _load_existing_memories(self):
        """Load existing memories from files."""
        # Load from MEMORY.md
        if os.path.exists(self.memory_file):
            self._parse_memory_file(self.memory_file, "MEMORY.md")
        
        # Load from daily memory files
        if os.path.exists(self.memory_dir):
            for filename in os.listdir(self.memory_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(self.memory_dir, filename)
                    self._parse_memory_file(filepath, f"memory/{filename}")
    
    def _parse_memory_file(self, filepath: str, source: str):
        """Parse a memory file into chunks."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract date from filename for daily files
            if source.startswith("memory/"):
                date_str = os.path.basename(source).replace(".md", "")
                try:
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            # Split by sections (headers starting with ## or ###)
            sections = re.split(r'\n##+\s+', content)
            
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                
                # Extract header (first line)
                lines = section.strip().split('\n')
                header = lines[0] if lines else "Untitled"
                
                # Create memory chunk
                chunk_id = f"{source.replace('/', '_')}_{i}"
                memory = MemoryChunk(
                    id=chunk_id,
                    content=section.strip(),
                    source_file=source,
                    line_range=(0, len(lines)),  # Approximate
                    timestamp=timestamp,
                    tags=self._extract_tags(section),
                    relationships=[]
                )
                
                self.memories[chunk_id] = memory
                
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text (words starting with #)."""
        tags = re.findall(r'#(\w+)', text)
        return list(set(tags))  # Remove duplicates
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Define node functions
        def ingest_node(state: MemoryState) -> MemoryState:
            """Ingest new memory text."""
            if state.get("new_memory_text"):
                # Create new memory chunk
                chunk_id = f"new_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                memory = MemoryChunk(
                    id=chunk_id,
                    content=state["new_memory_text"],
                    source_file="new_input",
                    line_range=(0, 1),
                    timestamp=datetime.now(),
                    tags=self._extract_tags(state["new_memory_text"]),
                    relationships=[]
                )
                
                self.memories[chunk_id] = memory
                state["action_taken"] = f"Ingested new memory: {chunk_id}"
            
            return state
        
        def retrieve_node(state: MemoryState) -> MemoryState:
            """Retrieve memories based on query."""
            query = state.get("query")
            if not query:
                return state
            
            # Simple keyword matching for now
            query_lower = query.lower()
            retrieved = []
            
            for memory in self.memories.values():
                # Check if query appears in content or tags
                if (query_lower in memory.content.lower() or
                    any(query_lower in tag.lower() for tag in memory.tags)):
                    retrieved.append(memory.to_dict())
            
            state["retrieved_memories"] = retrieved
            state["action_taken"] = f"Retrieved {len(retrieved)} memories"
            
            return state
        
        def summarize_node(state: MemoryState) -> MemoryState:
            """Generate summary of recent memories."""
            # Get memories from last 7 days
            week_ago = datetime.now().timestamp() - (7 * 24 * 3600)
            recent_memories = [
                m for m in self.memories.values()
                if m.timestamp.timestamp() > week_ago
            ]
            
            if recent_memories:
                # Simple summary: count by source
                sources = {}
                for memory in recent_memories:
                    source = memory.source_file
                    sources[source] = sources.get(source, 0) + 1
                
                summary_lines = [f"Recent memories (last 7 days): {len(recent_memories)} total"]
                for source, count in sources.items():
                    summary_lines.append(f"  - {source}: {count}")
                
                state["summary"] = "\n".join(summary_lines)
                state["action_taken"] = "Generated weekly summary"
            
            return state
        
        def relate_node(state: MemoryState) -> MemoryState:
            """Find relationships between memories."""
            # Simple relationship finding: memories with common tags
            tag_to_memories: Dict[str, List[str]] = {}
            
            for memory_id, memory in self.memories.items():
                for tag in memory.tags:
                    tag_to_memories.setdefault(tag, []).append(memory_id)
            
            # Update relationships
            for memory_id, memory in self.memories.items():
                related = set()
                for tag in memory.tags:
                    for other_id in tag_to_memories.get(tag, []):
                        if other_id != memory_id:
                            related.add(other_id)
                
                memory.relationships = list(related)[:5]  # Limit to 5
            
            state["action_taken"] = "Updated memory relationships"
            return state
        
        # Build the graph
        workflow = StateGraph(MemoryState)
        
        # Add nodes
        workflow.add_node("ingest", ingest_node)
        workflow.add_node("retrieve", retrieve_node)
        workflow.add_node("summarize", summarize_node)
        workflow.add_node("relate", relate_node)
        
        # Set entry point based on input
        workflow.set_conditional_entry_point(
            lambda state: "ingest" if state.get("new_memory_text") else "retrieve",
            {
                "ingest": "ingest",
                "retrieve": "retrieve"
            }
        )
        
        # Add edges
        workflow.add_edge("ingest", "relate")
        workflow.add_edge("retrieve", END)
        workflow.add_edge("summarize", END)
        workflow.add_edge("relate", "summarize")
        
        return workflow.compile()
    
    def process(self, query: Optional[str] = None, new_memory: Optional[str] = None) -> Dict[str, Any]:
        """Process a memory operation."""
        initial_state: MemoryState = {
            "query": query,
            "new_memory_text": new_memory,
            "raw_memories": [],
            "curated_memories": [],
            "related_memories": [],
            "retrieved_memories": [],
            "summary": None,
            "action_taken": None
        }
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        # Prepare response
        response = {
            "action": result.get("action_taken", "No action taken"),
            "retrieved_count": len(result.get("retrieved_memories", [])),
            "summary": result.get("summary"),
            "total_memories": len(self.memories)
        }
        
        if result.get("retrieved_memories"):
            response["retrieved_samples"] = result["retrieved_memories"][:3]
        
        return response
    
    def save_to_file(self, filepath: Optional[str] = None):
        """Save memory graph to JSON file."""
        if not filepath:
            filepath = os.path.join(self.workspace_path, "memory_graph.json")
        
        data = {
            "memories": {mid: mem.to_dict() for mid, mem in self.memories.items()},
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath

def main():
    """Test the memory graph system."""
    print("Initializing Memory Graph...")
    memory_graph = MemoryGraph()
    
    print(f"Loaded {len(memory_graph.memories)} memory chunks")
    
    # Test retrieval
    print("\n--- Testing retrieval ---")
    result = memory_graph.process(query="thesis")
    print(f"Action: {result['action']}")
    print(f"Found {result['retrieved_count']} memories related to 'thesis'")
    if result.get('retrieved_samples'):
        print("Sample memories:")
        for mem in result['retrieved_samples']:
            print(f"  - {mem['id']}: {mem['content'][:100]}...")
    
    # Test summarization
    print("\n--- Testing summarization ---")
    result = memory_graph.process()
    if result.get('summary'):
        print("Summary:")
        print(result['summary'])
    
    # Save graph
    saved_path = memory_graph.save_to_file()
    print(f"\nGraph saved to: {saved_path}")
    
    # Show some statistics
    print("\n--- Statistics ---")
    tags_count = {}
    for memory in memory_graph.memories.values():
        for tag in memory.tags:
            tags_count[tag] = tags_count.get(tag, 0) + 1
    
    print(f"Total tags: {len(tags_count)}")
    if tags_count:
        top_tags = sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Top 5 tags:")
        for tag, count in top_tags:
            print(f"  - #{tag}: {count} memories")

if __name__ == "__main__":
    main()