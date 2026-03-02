#!/usr/bin/env python3
"""
Integration of LangGraph memory system with OpenClaw.
Provides CLI interface and automatic memory management.
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Optional

# Add workspace to path
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace')

from memory_graph import MemoryGraph

class OpenClawMemoryManager:
    """Manages memory integration with OpenClaw workflows."""
    
    def __init__(self):
        self.memory_graph = MemoryGraph()
        self.workspace_path = "/home/ubuntu/.openclaw/workspace"
        
    def search(self, query: str, limit: int = 5) -> None:
        """Search memories."""
        print(f"\n🔍 Searching for: '{query}'")
        result = self.memory_graph.process(query=query)
        
        if result['retrieved_count'] == 0:
            print("   No memories found.")
            return
        
        print(f"   Found {result['retrieved_count']} memories:")
        
        # Get all memories (not just samples)
        memories = []
        for memory in self.memory_graph.memories.values():
            if query.lower() in memory.content.lower():
                memories.append(memory)
        
        # Sort by relevance (simple: longer content match)
        memories.sort(key=lambda m: len(m.content), reverse=True)
        
        for i, memory in enumerate(memories[:limit]):
            print(f"\n   {i+1}. [{memory.source_file}]")
            print(f"      ID: {memory.id}")
            print(f"      Date: {memory.timestamp.strftime('%Y-%m-%d')}")
            
            # Show preview
            preview = memory.content[:150].replace('\n', ' ')
            if len(memory.content) > 150:
                preview += "..."
            print(f"      Preview: {preview}")
            
            if memory.tags:
                print(f"      Tags: {', '.join(f'#{tag}' for tag in memory.tags)}")
    
    def add(self, content: str, tags: Optional[str] = None) -> None:
        """Add a new memory."""
        print("\n📝 Adding new memory...")
        
        # Add tags if provided
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            content_with_tags = content + "\n\n" + " ".join(f"#{tag}" for tag in tag_list)
        else:
            content_with_tags = content
        
        result = self.memory_graph.process(new_memory=content_with_tags)
        print(f"   {result['action']}")
        print(f"   Total memories: {result['total_memories']}")
        
        # Save the updated graph
        self.memory_graph.save_to_file()
    
    def summary(self) -> None:
        """Show memory summary."""
        print("\n📊 Memory Summary")
        print("=" * 50)
        
        result = self.memory_graph.process()
        
        if result.get('summary'):
            print(result['summary'])
        
        # Additional statistics
        total = len(self.memory_graph.memories)
        by_source = {}
        by_date = {}
        
        for memory in self.memory_graph.memories.values():
            # By source
            source = memory.source_file
            by_source[source] = by_source.get(source, 0) + 1
            
            # By date (for daily files)
            if memory.source_file.startswith("memory/"):
                date = memory.timestamp.strftime("%Y-%m-%d")
                by_date[date] = by_date.get(date, 0) + 1
        
        print(f"\nTotal memory chunks: {total}")
        
        print("\nBy source file:")
        for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")
        
        if by_date:
            print("\nBy date (daily files):")
            for date, count in sorted(by_date.items()):
                print(f"  {date}: {count}")
    
    def stats(self) -> None:
        """Show detailed statistics."""
        print("\n📈 Memory Statistics")
        print("=" * 50)
        
        total = len(self.memory_graph.memories)
        
        # Content analysis
        total_chars = sum(len(m.content) for m in self.memory_graph.memories.values())
        avg_chars = total_chars // total if total > 0 else 0
        
        # Date range
        dates = [m.timestamp for m in self.memory_graph.memories.values()]
        if dates:
            min_date = min(dates).strftime("%Y-%m-%d")
            max_date = max(dates).strftime("%Y-%m-%d")
        else:
            min_date = max_date = "N/A"
        
        print(f"Total memory chunks: {total}")
        print(f"Total characters: {total_chars:,}")
        print(f"Average length: {avg_chars:,} chars")
        print(f"Date range: {min_date} to {max_date}")
        
        # Word frequency (simple)
        all_text = " ".join(m.content.lower() for m in self.memory_graph.memories.values())
        words = all_text.split()
        
        from collections import Counter
        word_freq = Counter(words)
        
        # Remove common words
        common_words = {'the', 'and', 'to', 'of', 'a', 'in', 'is', 'that', 'for', 'on', 'with', 'as', 'by', 'an', 'be', 'this', 'or', 'at', 'from', 'but', 'not', 'are', 'it', 'if', 'you', 'was', 'we', 'have', 'has', 'had', 'what', 'when', 'where', 'how', 'why', 'which', 'who', 'whom', 'whose'}
        
        significant_words = {word: count for word, count in word_freq.items() 
                            if word not in common_words and len(word) > 3}
        
        print(f"\nTop 10 significant words:")
        for word, count in sorted(significant_words.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {word}: {count}")
    
    def export(self, format: str = "json") -> None:
        """Export memories."""
        print(f"\n💾 Exporting memories as {format}...")
        
        if format == "json":
            path = self.memory_graph.save_to_file()
            print(f"   Exported to: {path}")
            
            # Show file size
            import os
            size = os.path.getsize(path)
            print(f"   File size: {size:,} bytes")
        
        elif format == "markdown":
            path = os.path.join(self.workspace_path, "exported_memories.md")
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write("# Exported Memories\n\n")
                f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total memories: {len(self.memory_graph.memories)}\n\n")
                
                for memory in sorted(self.memory_graph.memories.values(), 
                                   key=lambda m: m.timestamp):
                    f.write(f"## {memory.id}\n")
                    f.write(f"**Source:** {memory.source_file}\n")
                    f.write(f"**Date:** {memory.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    if memory.tags:
                        f.write(f"**Tags:** {', '.join(memory.tags)}\n")
                    
                    f.write("\n```\n")
                    f.write(memory.content)
                    f.write("\n```\n\n")
            
            print(f"   Exported to: {path}")
        
        else:
            print(f"   Unknown format: {format}")
    
    def interactive(self) -> None:
        """Interactive mode."""
        print("\n🤖 OpenClaw Memory Manager - Interactive Mode")
        print("=" * 50)
        print("Commands: search <query>, add <text>, summary, stats, export, quit")
        
        while True:
            try:
                command = input("\nmemory> ").strip()
                
                if not command:
                    continue
                
                if command.lower() == 'quit':
                    print("Goodbye!")
                    break
                
                elif command.lower() == 'summary':
                    self.summary()
                
                elif command.lower() == 'stats':
                    self.stats()
                
                elif command.lower() == 'export':
                    self.export()
                
                elif command.startswith('search '):
                    query = command[7:].strip()
                    if query:
                        self.search(query)
                    else:
                        print("   Please provide a search query.")
                
                elif command.startswith('add '):
                    content = command[4:].strip()
                    if content:
                        tags = input("   Tags (comma-separated, optional): ").strip()
                        self.add(content, tags if tags else None)
                    else:
                        print("   Please provide memory content.")
                
                else:
                    print(f"   Unknown command: {command}")
                    print("   Available: search, add, summary, stats, export, quit")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"   Error: {e}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="OpenClaw Memory Manager")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search memories')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-l', '--limit', type=int, default=5, help='Maximum results')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new memory')
    add_parser.add_argument('content', help='Memory content')
    add_parser.add_argument('-t', '--tags', help='Comma-separated tags')
    
    # Summary command
    subparsers.add_parser('summary', help='Show memory summary')
    
    # Stats command
    subparsers.add_parser('stats', help='Show detailed statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export memories')
    export_parser.add_argument('-f', '--format', choices=['json', 'markdown'], default='json', help='Export format')
    
    # Interactive mode
    subparsers.add_parser('interactive', help='Interactive mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = OpenClawMemoryManager()
    
    if args.command == 'search':
        manager.search(args.query, args.limit)
    
    elif args.command == 'add':
        manager.add(args.content, args.tags)
    
    elif args.command == 'summary':
        manager.summary()
    
    elif args.command == 'stats':
        manager.stats()
    
    elif args.command == 'export':
        manager.export(args.format)
    
    elif args.command == 'interactive':
        manager.interactive()

if __name__ == "__main__":
    main()