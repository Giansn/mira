#!/usr/bin/env python3
"""
Memory Parser for OpenClaw Memory Visualization
Parses MEMORY.md and daily memory files into structured JSON
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
import markdown
from bs4 import BeautifulSoup

class MemoryParser:
    def __init__(self, workspace_path="/home/ubuntu/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.memory_path = self.workspace_path / "MEMORY.md"
        self.daily_memory_dir = self.workspace_path / "memory"
        
    def parse_memory_file(self, file_path):
        """Parse a single memory file (MEMORY.md or daily file)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract date from filename
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
        file_date = date_match.group(1) if date_match else None
        
        # Parse markdown structure
        lines = content.split('\n')
        entries = []
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for headers
            if line.startswith('# '):
                if current_section and current_content:
                    entries.append({
                        'section': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'type': 'section'
                    })
                current_section = line.strip('# ').strip()
                current_content = []
            elif line.startswith('## '):
                if current_section and current_content:
                    entries.append({
                        'section': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'type': 'section'
                    })
                current_section = line.strip('# ').strip()
                current_content = []
            elif line.startswith('### '):
                if current_section and current_content:
                    entries.append({
                        'section': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'type': 'subsection'
                    })
                current_section = line.strip('# ').strip()
                current_content = []
            elif line.strip() and not line.startswith('---'):
                current_content.append(line)
            elif line.strip() == '' and current_content:
                # End of paragraph
                if current_section:
                    entries.append({
                        'section': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'type': 'paragraph'
                    })
                current_content = []
        
        # Add last entry
        if current_section and current_content:
            entries.append({
                'section': current_section,
                'content': '\n'.join(current_content).strip(),
                'type': 'section'
            })
        
        # Extract dates from content
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        dates_in_content = re.findall(date_pattern, content)
        
        # Extract bullet points and lists
        bullets = []
        for line in lines:
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                bullets.append(line.strip())
        
        return {
            'file': file_path.name,
            'date': file_date,
            'path': str(file_path),
            'entries': entries,
            'dates_mentioned': list(set(dates_in_content)),
            'bullets': bullets,
            'line_count': len(lines),
            'word_count': len(content.split())
        }
    
    def parse_all_memory(self):
        """Parse all memory files"""
        memory_data = {
            'main_memory': None,
            'daily_memories': [],
            'stats': {}
        }
        
        # Parse main memory
        if self.memory_path.exists():
            memory_data['main_memory'] = self.parse_memory_file(self.memory_path)
        
        # Parse daily memories
        daily_files = []
        if self.daily_memory_dir.exists():
            for file in self.daily_memory_dir.glob('*.md'):
                if file.name != 'MEMORY.md':
                    daily_files.append(file)
        
        # Sort by date (newest first)
        daily_files.sort(key=lambda x: x.name, reverse=True)
        
        for file in daily_files:
            try:
                parsed = self.parse_memory_file(file)
                memory_data['daily_memories'].append(parsed)
            except Exception as e:
                print(f"Error parsing {file}: {e}")
        
        # Calculate statistics
        memory_data['stats'] = {
            'total_daily_files': len(memory_data['daily_memories']),
            'total_entries': sum(len(m.get('entries', [])) for m in memory_data['daily_memories']),
            'date_range': self.get_date_range(memory_data),
            'topics': self.extract_topics(memory_data)
        }
        
        return memory_data
    
    def get_date_range(self, memory_data):
        """Get the date range of all memory files"""
        dates = []
        if memory_data['main_memory'] and memory_data['main_memory']['date']:
            dates.append(memory_data['main_memory']['date'])
        
        for daily in memory_data['daily_memories']:
            if daily['date']:
                dates.append(daily['date'])
        
        if dates:
            dates.sort()
            return {
                'start': dates[0],
                'end': dates[-1],
                'days': (datetime.strptime(dates[-1], '%Y-%m-%d') - datetime.strptime(dates[0], '%Y-%m-%d')).days
            }
        return None
    
    def extract_topics(self, memory_data):
        """Extract common topics from memory entries"""
        topics = {}
        
        # Common topic patterns
        topic_patterns = {
            'heartbeat': r'heartbeat|HEARTBEAT',
            'security': r'security|audit|fail2ban|swap|upgrade',
            'thesis': r'thesis|FHNW|Soziale Arbeit|research',
            'telegram': r'telegram|rate limit|Open Router',
            'tools': r'tool|skill|AEAP|LangChain',
            'error': r'error|fehler|mistake|bug',
            'policy': r'policy|rule|config|configuration',
            'cron': r'cron|job|schedule|Moltbook'
        }
        
        all_content = []
        if memory_data['main_memory']:
            all_content.append(memory_data['main_memory'])
        all_content.extend(memory_data['daily_memories'])
        
        for memory in all_content:
            for entry in memory.get('entries', []):
                content = f"{entry.get('section', '')} {entry.get('content', '')}".lower()
                for topic, pattern in topic_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        topics[topic] = topics.get(topic, 0) + 1
        
        return dict(sorted(topics.items(), key=lambda x: x[1], reverse=True))
    
    def export_json(self, output_path):
        """Export parsed memory data to JSON"""
        data = self.parse_all_memory()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data

if __name__ == "__main__":
    parser = MemoryParser()
    output_path = Path("/home/ubuntu/.openclaw/workspace/memory-viz/data/memory_data.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Parsing memory files...")
    data = parser.export_json(output_path)
    print(f"Exported to {output_path}")
    print(f"Stats: {data['stats']}")