#!/usr/bin/env python3
"""
Memory Tagger Implementation
Tags memory entries and can apply tags to files.
"""

import re
import os
from datetime import datetime

# Tag definitions with keywords (expanded from prototype)
TAG_RULES = {
    "[VOICE]": ["voice", "accent", "tts", "audio", "whisper", "transcription", "speech", "sound"],
    "[DISK]": ["disk", "space", "gb", "cleanup", "cache", "delete", "storage", "temp", "tmp"],
    "[CRON]": ["cron", "schedule", "daily", "job", "automated", "scheduled", "cronjob"],
    "[HEARTBEAT]": ["heartbeat", "monitoring", "check", "health", "status"],
    "[AUDIO]": ["audio", "ogg", "mp3", "sound", "listen", "hear", "play"],
    "[TTS]": ["tts", "text-to-speech", "synthes", "voice"],
    "[TRANSCRIPTION]": ["transcription", "whisper", "speech-to-text", "transcribe"],
    "[CLEANUP]": ["cleanup", "delete", "remove", "prune", "optimize", "free", "space"],
    "[DECISION]": ["decision", "choose", "option", "select", "prefer", "decision"],
    "[ERROR]": ["error", "fail", "broken", "issue", "problem", "warning", "failed"],
    "[SUCCESS]": ["success", "completed", "working", "fixed", "resolved", "successful"],
    "[SYSTEM]": ["system", "status", "monitor", "performance", "optimize", "configuration"],
    "[MEMORY]": ["memory", "flush", "compaction", "recall", "remember", "embedding", "search"],
    "[CONVERSATION]": ["conversation", "chat", "discuss", "talk", "message", "reply", "response"],
    "[GPU]": ["gpu", "cuda", "nvidia", "gpu", "acceleration", "torch"],
    "[CPU]": ["cpu", "processor", "compute", "performance"],
    "[NETWORK]": ["network", "internet", "api", "http", "web", "url"],
    "[SECURITY]": ["security", "auth", "password", "token", "key", "access"],
    "[DEVELOPMENT]": ["development", "code", "script", "program", "implementation", "prototype"],
}

def suggest_tags(text, max_tags=5):
    """Suggest tags for a text entry based on keyword matching."""
    text_lower = text.lower()
    suggested_tags = []
    
    for tag, keywords in TAG_RULES.items():
        for keyword in keywords:
            if keyword in text_lower:
                if tag not in suggested_tags:
                    suggested_tags.append(tag)
                break  # One keyword match is enough for the tag
    
    # Limit number of tags
    return suggested_tags[:max_tags]

def analyze_memory_file(filepath):
    """Analyze a memory file and return tagged entries."""
    print(f"Analyzing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by pre-compaction flush headers
        entries = []
        pattern = r'(#{2,4} \*{2}Pre-Compaction Memory Flush.*?\n)(.*?)(?=\n#{2,4} \*{2}Pre-Compaction Memory Flush|\Z)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            header = match.group(1).strip()
            body = match.group(2).strip()
            if len(body) < 50:  # Skip small entries
                continue
                
            tags = suggest_tags(body)
            entries.append({
                'header': header,
                'body': body,
                'tags': tags,
                'full_entry': header + '\n' + body
            })
        
        return entries
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return []

def create_tagged_entry(original_header, original_body, tags):
    """Create a tagged version of a memory entry."""
    # Extract timestamp from header if present
    timestamp_match = re.search(r'\((\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)\)', original_header)
    timestamp = timestamp_match.group(1) if timestamp_match else datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    # Create new header with tags
    tag_string = ' '.join(tags) if tags else '[UNCATEGORIZED]'
    new_header = f"### **{tag_string} Memory Entry ({timestamp})**"
    
    return new_header + '\n\n' + original_body + '\n\n'

def demonstrate_tagging(filepath):
    """Demonstrate tagging without modifying file."""
    entries = analyze_memory_file(filepath)
    
    print(f"\nFound {len(entries)} memory entries to tag")
    print("=" * 60)
    
    for i, entry in enumerate(entries[:5]):  # Show first 5
        print(f"\nEntry #{i+1}:")
        print(f"Header: {entry['header'][:80]}...")
        print(f"Tags suggested: {', '.join(entry['tags'])}")
        
        # Show tagged version
        tagged = create_tagged_entry(entry['header'], entry['body'], entry['tags'])
        print(f"Tagged version (first 200 chars): {tagged[:200]}...")
    
    if len(entries) > 5:
        print(f"\n... and {len(entries) - 5} more entries")
    
    return entries

def apply_tags_to_file(input_file, output_file=None, backup=True):
    """Apply tags to a memory file (creates new tagged version)."""
    if output_file is None:
        output_file = input_file + '.tagged'
    
    entries = analyze_memory_file(input_file)
    
    if backup and os.path.exists(input_file):
        backup_file = input_file + '.backup'
        import shutil
        shutil.copy2(input_file, backup_file)
        print(f"Created backup: {backup_file}")
    
    # Reconstruct file with tagged entries
    with open(input_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # For now, just create tagged version alongside original
    tagged_content = "# Tagged Memory File\n\n"
    for entry in entries:
        tagged_entry = create_tagged_entry(entry['header'], entry['body'], entry['tags'])
        tagged_content += tagged_entry + '\n---\n\n'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(tagged_content)
    
    print(f"Created tagged version: {output_file}")
    print(f"Original entries: {len(entries)}")
    print(f"Tag distribution: {sum(len(e['tags']) for e in entries)} total tags")
    
    return output_file

def main():
    """Main function to demonstrate tagging."""
    print("Memory Tagger Implementation")
    print("=" * 60)
    
    # Test with today's memory file
    today_file = "memory/2026-03-03.md"
    if os.path.exists(today_file):
        print(f"1. Analyzing: {today_file}")
        entries = demonstrate_tagging(today_file)
        
        print(f"\n2. Tag statistics:")
        tag_counts = {}
        for entry in entries:
            for tag in entry['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {tag}: {count} entries")
        
        print(f"\n3. Sample tagged entry creation:")
        if entries:
            sample = create_tagged_entry(entries[0]['header'], entries[0]['body'][:500], entries[0]['tags'])
            print(sample[:300] + "...")
        
        # Optional: Create tagged version
        # apply_tags_to_file(today_file, today_file + '.tagged')
    else:
        print(f"File not found: {today_file}")

if __name__ == "__main__":
    main()