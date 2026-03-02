#!/usr/bin/env python3
"""
Memory Visualization Web Interface
A Flask web application for visualizing OpenClaw memory files.
"""

import os
import json
import re
from datetime import datetime
from collections import Counter
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import markdown
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'memory-viz-secret-key-2026-03-01'

# Paths
WORKSPACE_DIR = Path.home() / '.openclaw' / 'workspace'
MEMORY_DIR = WORKSPACE_DIR / 'memory'
MEMORY_FILE = WORKSPACE_DIR / 'MEMORY.md'

class MemoryParser:
    """Parse and analyze memory files."""
    
    def __init__(self):
        self.memory_data = {
            'daily_files': [],
            'memory_entries': [],
            'stats': {},
            'topics': [],
            'timeline': []
        }
        self.last_updated = None
        
    def parse_memory_files(self):
        """Parse all memory files and extract structured data."""
        self.memory_data = {
            'daily_files': [],
            'memory_entries': [],
            'stats': {},
            'topics': [],
            'timeline': []
        }
        
        # Parse daily memory files
        daily_entries = []
        if MEMORY_DIR.exists():
            for file_path in MEMORY_DIR.glob('*.md'):
                if file_path.name.startswith('.'):
                    continue
                    
                try:
                    date_str = file_path.stem
                    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract date from filename
                        try:
                            date = datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            date = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        # Parse content
                        entries = self._parse_daily_content(content, date)
                        daily_entries.extend(entries)
                        
                        self.memory_data['daily_files'].append({
                            'filename': file_path.name,
                            'date': date.isoformat(),
                            'size': os.path.getsize(file_path),
                            'entry_count': len(entries),
                            'path': str(file_path.relative_to(WORKSPACE_DIR))
                        })
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")
        
        # Parse main MEMORY.md
        main_entries = []
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse sections from MEMORY.md
                sections = self._parse_memory_sections(content)
                main_entries = sections
                
                # Add as a special file
                self.memory_data['daily_files'].append({
                    'filename': 'MEMORY.md',
                    'date': datetime.fromtimestamp(MEMORY_FILE.stat().st_mtime).isoformat(),
                    'size': os.path.getsize(MEMORY_FILE),
                    'entry_count': len(sections),
                    'path': 'MEMORY.md',
                    'is_main': True
                })
            except Exception as e:
                print(f"Error parsing MEMORY.md: {e}")
        
        # Combine all entries
        all_entries = daily_entries + main_entries
        self.memory_data['memory_entries'] = all_entries
        
        # Generate statistics
        self._generate_statistics(all_entries)
        
        # Generate timeline
        self._generate_timeline(all_entries)
        
        # Extract topics
        self._extract_topics(all_entries)
        
        self.last_updated = datetime.now()
        
        return self.memory_data
    
    def _parse_daily_content(self, content, date):
        """Parse content from a daily memory file."""
        entries = []
        
        # Split by sections (lines starting with ## or ###)
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('## '):
                # Save previous section
                if current_section and current_content:
                    entries.append({
                        'date': date.isoformat(),
                        'section': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'type': 'daily',
                        'word_count': len('\n'.join(current_content).split())
                    })
                
                # Start new section
                current_section = line[3:].strip()
                current_content = []
            elif line.startswith('### '):
                # Subsection - treat as separate entry
                if current_section and current_content:
                    entries.append({
                        'date': date.isoformat(),
                        'section': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'type': 'daily',
                        'word_count': len('\n'.join(current_content).split())
                    })
                
                current_section = line[4:].strip()
                current_content = []
            elif line.strip() and current_section:
                current_content.append(line)
        
        # Add last section
        if current_section and current_content:
            entries.append({
                'date': date.isoformat(),
                'section': current_section,
                'content': '\n'.join(current_content).strip(),
                'type': 'daily',
                'word_count': len('\n'.join(current_content).split())
            })
        
        return entries
    
    def _parse_memory_sections(self, content):
        """Parse sections from MEMORY.md."""
        entries = []
        
        # Split by major sections (##)
        sections = re.split(r'\n## ', content)
        
        for i, section in enumerate(sections):
            if i == 0:
                # First part is the title/header
                lines = section.strip().split('\n')
                if lines:
                    title = lines[0].replace('# ', '').strip()
                    content_text = '\n'.join(lines[1:]).strip()
                    
                    if content_text:
                        entries.append({
                            'date': datetime.now().isoformat(),
                            'section': title,
                            'content': content_text,
                            'type': 'main',
                            'word_count': len(content_text.split())
                        })
            else:
                # Regular section
                lines = section.strip().split('\n')
                if lines:
                    title = lines[0].strip()
                    content_text = '\n'.join(lines[1:]).strip()
                    
                    if content_text:
                        entries.append({
                            'date': datetime.now().isoformat(),
                            'section': title,
                            'content': content_text,
                            'type': 'main',
                            'word_count': len(content_text.split())
                        })
        
        return entries
    
    def _generate_statistics(self, entries):
        """Generate statistics from memory entries."""
        if not entries:
            return
        
        # Basic counts
        total_entries = len(entries)
        total_words = sum(entry.get('word_count', 0) for entry in entries)
        
        # Count by type
        type_counts = Counter(entry.get('type', 'unknown') for entry in entries)
        
        # Count by section (top 10)
        section_counts = Counter(entry.get('section', 'Unknown') for entry in entries)
        top_sections = dict(section_counts.most_common(10))
        
        # Date range
        dates = [datetime.fromisoformat(entry['date']) for entry in entries if 'date' in entry]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            date_range_days = (max_date - min_date).days
        else:
            min_date = max_date = datetime.now()
            date_range_days = 0
        
        self.memory_data['stats'] = {
            'total_entries': total_entries,
            'total_words': total_words,
            'type_counts': dict(type_counts),
            'top_sections': top_sections,
            'date_range': {
                'min': min_date.isoformat(),
                'max': max_date.isoformat(),
                'days': date_range_days
            },
            'file_count': len(self.memory_data['daily_files'])
        }
    
    def _generate_timeline(self, entries):
        """Generate timeline data for visualization."""
        timeline_data = []
        
        # Group by date
        date_groups = {}
        for entry in entries:
            date_str = entry['date'][:10]  # YYYY-MM-DD
            if date_str not in date_groups:
                date_groups[date_str] = {
                    'date': date_str,
                    'entries': [],
                    'count': 0,
                    'words': 0
                }
            
            date_groups[date_str]['entries'].append({
                'section': entry.get('section', 'Unknown'),
                'type': entry.get('type', 'unknown'),
                'word_count': entry.get('word_count', 0)
            })
            date_groups[date_str]['count'] += 1
            date_groups[date_str]['words'] += entry.get('word_count', 0)
        
        # Convert to list and sort
        for date_str, data in date_groups.items():
            timeline_data.append({
                'date': date_str,
                'count': data['count'],
                'words': data['words'],
                'entries': data['entries'][:5]  # Limit entries in timeline
            })
        
        timeline_data.sort(key=lambda x: x['date'])
        self.memory_data['timeline'] = timeline_data
    
    def _extract_topics(self, entries):
        """Extract common topics from memory entries."""
        # Simple keyword extraction
        keywords = []
        common_words = set(['the', 'and', 'for', 'with', 'that', 'this', 'have', 'from', 'what', 'when', 'how', 'why'])
        
        for entry in entries:
            content = entry.get('content', '').lower()
            words = re.findall(r'\b[a-z]{4,}\b', content)
            
            # Filter out common words and add to list
            filtered_words = [w for w in words if w not in common_words]
            keywords.extend(filtered_words)
        
        # Count and get top topics
        if keywords:
            topic_counts = Counter(keywords)
            self.memory_data['topics'] = [
                {'topic': topic, 'count': count}
                for topic, count in topic_counts.most_common(20)
            ]
        else:
            self.memory_data['topics'] = []

# Initialize parser
parser = MemoryParser()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/memory-data')
def get_memory_data():
    """Get parsed memory data."""
    data = parser.parse_memory_files()
    return jsonify(data)

@app.route('/api/timeline')
def get_timeline():
    """Get timeline data."""
    data = parser.parse_memory_files()
    return jsonify(data['timeline'])

@app.route('/api/search')
def search_memory():
    """Search memory entries."""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'results': [], 'count': 0})
    
    data = parser.parse_memory_files()
    results = []
    
    for entry in data['memory_entries']:
        content = entry.get('content', '').lower()
        section = entry.get('section', '').lower()
        
        if query in content or query in section:
            results.append({
                'date': entry.get('date'),
                'section': entry.get('section'),
                'content_preview': entry.get('content', '')[:200] + '...',
                'type': entry.get('type'),
                'word_count': entry.get('word_count', 0)
            })
    
    return jsonify({
        'results': results[:50],  # Limit results
        'count': len(results)
    })

@app.route('/api/stats')
def get_stats():
    """Get memory statistics."""
    data = parser.parse_memory_files()
    return jsonify(data['stats'])

@app.route('/api/refresh')
def refresh_data():
    """Force refresh of memory data."""
    data = parser.parse_memory_files()
    return jsonify({
        'status': 'success',
        'last_updated': parser.last_updated.isoformat() if parser.last_updated else None,
        'entry_count': len(data['memory_entries'])
    })

@app.route('/view/<path:filename>')
def view_file(filename):
    """View a specific memory file."""
    # Secure the filename
    filename = secure_filename(filename)
    
    # Check if it's a daily file or MEMORY.md
    if filename == 'MEMORY.md':
        file_path = MEMORY_FILE
    else:
        file_path = MEMORY_DIR / filename
    
    if not file_path.exists():
        return "File not found", 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['extra', 'tables'])
        
        return render_template('view_file.html', 
                             filename=filename, 
                             content=html_content,
                             raw_content=content)
    except Exception as e:
        return f"Error reading file: {str(e)}", 500

if __name__ == '__main__':
    # Parse initial data
    parser.parse_memory_files()
    
    # Run the app
    print("Starting Memory Visualization Web Interface...")
    print(f"Access at: http://localhost:5000")
    print(f"Memory directory: {MEMORY_DIR}")
    print(f"Main memory file: {MEMORY_FILE}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)