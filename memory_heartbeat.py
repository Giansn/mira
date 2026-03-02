#!/usr/bin/env python3
"""
OpenClaw heartbeat integration for enhanced memory graph.
Run this during heartbeats to maintain and analyze memory organization.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add workspace to path
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace')

try:
    from enhanced_memory_graph import EnhancedMemoryGraph
    ENHANCED_AVAILABLE = True
except ImportError as e:
    print(f"EnhancedMemoryGraph import failed: {e}")
    ENHANCED_AVAILABLE = False

class MemoryHeartbeat:
    """Memory management for OpenClaw heartbeats."""
    
    def __init__(self, workspace_path: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.memory_dir = Path(workspace_path) / "memory"
        self.analysis_file = Path(workspace_path) / "memory_heartbeat_state.json"
        
        # Load or create state
        self.state = self._load_state()
        
        # Initialize memory graph if available
        self.memory_graph = None
        if ENHANCED_AVAILABLE:
            try:
                self.memory_graph = EnhancedMemoryGraph(workspace_path)
                print(f"Memory graph loaded: {len(self.memory_graph.memories)} memories")
            except Exception as e:
                print(f"Failed to load memory graph: {e}")
    
    def _load_state(self) -> dict:
        """Load heartbeat state from file."""
        default_state = {
            "last_run": None,
            "last_analysis": None,
            "stats": {
                "total_memories": 0,
                "total_tags": 0,
                "total_relationships": 0
            },
            "recent_activity": [],
            "pending_tasks": []
        }
        
        if self.analysis_file.exists():
            try:
                with open(self.analysis_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                # Merge with defaults
                for key, value in default_state.items():
                    if key not in state:
                        state[key] = value
                return state
            except Exception as e:
                print(f"Error loading state: {e}")
        
        return default_state
    
    def _save_state(self):
        """Save heartbeat state to file."""
        self.state["last_run"] = datetime.now().isoformat()
        
        try:
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def check_new_memories(self) -> list:
        """Check for new memory files since last run."""
        if not self.memory_graph:
            return []
        
        last_run = None
        if self.state["last_run"]:
            try:
                last_run = datetime.fromisoformat(self.state["last_run"])
            except:
                pass
        
        new_memories = []
        
        # Check MEMORY.md
        memory_file = Path(self.workspace_path) / "MEMORY.md"
        if memory_file.exists():
            mtime = datetime.fromtimestamp(memory_file.stat().st_mtime)
            if not last_run or mtime > last_run:
                new_memories.append(str(memory_file))
        
        # Check daily memory files
        if self.memory_dir.exists():
            for mem_file in self.memory_dir.glob("*.md"):
                mtime = datetime.fromtimestamp(mem_file.stat().st_mtime)
                if not last_run or mtime > last_run:
                    new_memories.append(str(mem_file))
        
        return new_memories
    
    def analyze_memory_health(self) -> dict:
        """Analyze memory system health."""
        if not self.memory_graph:
            return {"error": "Memory graph not available"}
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "basic_stats": {
                "total_memories": len(self.memory_graph.memories),
                "total_tags": len(self.memory_graph.tag_index),
                "total_keywords": len(self.memory_graph.keyword_index),
                "total_relationships": sum(len(m.relationships) for m in self.memory_graph.memories.values())
            },
            "recent_activity": [],
            "recommendations": []
        }
        
        # Check for memory files without recent updates
        memory_files = []
        memory_md_path = Path(self.workspace_path) / "MEMORY.md"
        if memory_md_path.exists():
            memory_files.append("MEMORY.md")
        
        if self.memory_dir.exists():
            memory_files.extend([f.name for f in self.memory_dir.glob("*.md")])
        
        # Check last modification times
        week_ago = datetime.now() - timedelta(days=7)
        stale_files = []
        
        for mem_file in memory_files:
            if mem_file == "MEMORY.md":
                path = Path(self.workspace_path) / mem_file
            else:
                path = self.memory_dir / mem_file
            
            if path.exists():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime < week_ago:
                    stale_files.append({
                        "file": mem_file,
                        "last_modified": mtime.isoformat(),
                        "days_stale": (datetime.now() - mtime).days
                    })
        
        if stale_files:
            analysis["recommendations"].append({
                "type": "stale_memory",
                "message": f"{len(stale_files)} memory files haven't been updated in over a week",
                "files": stale_files[:3]  # Show top 3
            })
        
        # Check memory distribution
        if self.memory_graph.memories:
            # Count by source
            sources = {}
            for memory in self.memory_graph.memories.values():
                source = memory.source_file
                sources[source] = sources.get(source, 0) + 1
            
            analysis["distribution"] = {
                "by_source": sources,
                "largest_source": max(sources.items(), key=lambda x: x[1]) if sources else None
            }
            
            # Check if MEMORY.md is being updated (should be largest source)
            if "MEMORY.md" in sources:
                mem_count = sources["MEMORY.md"]
                total = len(self.memory_graph.memories)
                percentage = (mem_count / total * 100) if total > 0 else 0
                
                if percentage < 20:  # Less than 20% of memories in MEMORY.md
                    analysis["recommendations"].append({
                        "type": "memory_curation",
                        "message": f"Only {percentage:.1f}% of memories are in MEMORY.md (curated long-term memory)",
                        "suggestion": "Consider moving significant learnings from daily files to MEMORY.md"
                    })
        
        # Check relationship health
        if analysis["basic_stats"]["total_relationships"] > 0:
            # Calculate average connections per memory
            avg_connections = analysis["basic_stats"]["total_relationships"] / len(self.memory_graph.memories)
            analysis["relationship_health"] = {
                "avg_connections_per_memory": round(avg_connections, 2),
                "isolated_memories": sum(1 for m in self.memory_graph.memories.values() if not m.relationships)
            }
            
            if avg_connections < 2:
                analysis["recommendations"].append({
                    "type": "relationship_quality",
                    "message": f"Low relationship density: {avg_connections:.1f} connections per memory",
                    "suggestion": "Add more context to memories to improve semantic connections"
                })
        
        # Save analysis to state
        self.state["last_analysis"] = analysis["timestamp"]
        self.state["stats"] = analysis["basic_stats"]
        
        # Add to recent activity
        self.state["recent_activity"].append({
            "timestamp": analysis["timestamp"],
            "action": "memory_analysis",
            "stats": analysis["basic_stats"]
        })
        
        # Keep only last 10 activities
        if len(self.state["recent_activity"]) > 10:
            self.state["recent_activity"] = self.state["recent_activity"][-10:]
        
        return analysis
    
    def generate_daily_summary(self) -> str:
        """Generate a human-readable daily summary."""
        if not self.memory_graph:
            return "Memory graph not available for summary."
        
        analysis = self.analyze_memory_health()
        
        summary_lines = ["📊 Memory System Summary"]
        summary_lines.append("=" * 40)
        
        # Basic stats
        stats = analysis["basic_stats"]
        summary_lines.append(f"Memories: {stats['total_memories']}")
        summary_lines.append(f"Tags: {stats['total_tags']}")
        summary_lines.append(f"Keywords: {stats['total_keywords']}")
        summary_lines.append(f"Relationships: {stats['total_relationships']}")
        
        # Recent activity
        new_files = self.check_new_memories()
        if new_files:
            summary_lines.append(f"\n📝 New since last check: {len(new_files)} files")
            for file in new_files[:3]:  # Show first 3
                summary_lines.append(f"  - {Path(file).name}")
            if len(new_files) > 3:
                summary_lines.append(f"  ... and {len(new_files) - 3} more")
        
        # Recommendations
        if analysis.get("recommendations"):
            summary_lines.append("\n💡 Recommendations:")
            for rec in analysis["recommendations"][:3]:  # Show top 3
                summary_lines.append(f"  - {rec['message']}")
        
        # Top tags
        if self.memory_graph.tag_index:
            tag_counts = {tag: len(mem_ids) for tag, mem_ids in self.memory_graph.tag_index.items()}
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            summary_lines.append("\n🏷️ Top tags:")
            for tag, count in top_tags:
                summary_lines.append(f"  #{tag}: {count} memories")
        
        # Save state
        self._save_state()
        
        return "\n".join(summary_lines)
    
    def run_heartbeat(self) -> str:
        """Main heartbeat entry point."""
        print("Running memory heartbeat...")
        
        if not ENHANCED_AVAILABLE:
            return "Enhanced memory system not available. Install sentence-transformers for full features."
        
        if not self.memory_graph:
            return "Failed to initialize memory graph."
        
        try:
            summary = self.generate_daily_summary()
            return summary
        except Exception as e:
            return f"Memory heartbeat error: {e}"

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Memory Heartbeat")
    parser.add_argument('--summary', action='store_true', help='Generate daily summary')
    parser.add_argument('--analyze', action='store_true', help='Run full analysis')
    parser.add_argument('--check-new', action='store_true', help='Check for new memories')
    
    args = parser.parse_args()
    
    heartbeat = MemoryHeartbeat()
    
    if args.analyze:
        result = heartbeat.analyze_memory_health()
        print(json.dumps(result, indent=2))
    
    elif args.check_new:
        new_files = heartbeat.check_new_memories()
        if new_files:
            print(f"New memory files since last run: {len(new_files)}")
            for file in new_files:
                print(f"  - {file}")
        else:
            print("No new memory files found.")
    
    elif args.summary:
        summary = heartbeat.generate_daily_summary()
        print(summary)
    
    else:
        # Default: run full heartbeat
        result = heartbeat.run_heartbeat()
        print(result)

if __name__ == "__main__":
    main()