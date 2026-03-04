#!/usr/bin/env python3
"""
Retention Enforcer
Implements 5-day archive, 20-day deletion policy based on file tags.
"""

import os
import json
import shutil
from datetime import datetime, timedelta
import time
from pathlib import Path

class RetentionEnforcer:
    """Enforce retention policies based on tagging results."""
    
    def __init__(self, workspace_path=".", archive_path="/data/archive"):
        self.workspace_path = workspace_path
        self.archive_path = archive_path
        self.now = datetime.now()
        
        # Retention policies (from user: archive 5 days, delete 20 days)
        self.archive_days = 5
        self.delete_days = 20
        
        # Create archive directory if needed
        os.makedirs(self.archive_path, exist_ok=True)
        
        # Load tagging results
        self.tagging_results = self.load_tagging_results()
        
        # Statistics
        self.stats = {
            "total_files": 0,
            "archived": 0,
            "deleted": 0,
            "skipped": 0,
            "errors": 0
        }
    
    def load_tagging_results(self):
        """Load tagging results from JSON file."""
        results_file = "tagging_results.json"
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                print(f"Warning: Could not load {results_file}")
                return None
        else:
            print(f"Warning: {results_file} not found")
            return None
    
    def get_file_age_days(self, filepath):
        """Get file age in days based on modification time."""
        try:
            mtime = os.path.getmtime(filepath)
            file_dt = datetime.fromtimestamp(mtime)
            age = (self.now - file_dt).days
            return age
        except:
            return None
    
    def should_archive(self, file_info, age_days):
        """Determine if file should be archived (5+ days old)."""
        if age_days is None:
            return False
        
        # Always archive logs and cache older than archive threshold
        tags = file_info.get('tags', [])
        if '[LOG-FILE]' in tags or '[CACHE-FILE]' in tags:
            return age_days >= self.archive_days
        
        # Archive other files based on age
        return age_days >= self.archive_days
    
    def should_delete(self, file_info, age_days):
        """Determine if file should be deleted (20+ days old)."""
        if age_days is None:
            return False
        
        # Always delete old temp/cache files
        tags = file_info.get('tags', [])
        if '[TEMP-CACHE]' in tags or '[LOG-FILE]' in tags:
            return age_days >= self.delete_days
        
        # For memory files, be more careful
        if '[MEMORY-FILE]' in tags:
            # Memory files older than 20 days can be archived more aggressively
            # but maybe not deleted (they ARE the memory)
            return age_days >= 90  # More conservative for memory
        
        # Default: delete if 20+ days
        return age_days >= self.delete_days
    
    def archive_file(self, filepath, file_info):
        """Archive a file by compressing and moving to archive directory."""
        try:
            rel_path = file_info['path']
            archive_filepath = os.path.join(self.archive_path, f"{rel_path.replace('/', '_')}.gz")
            
            # Create parent directories in archive
            os.makedirs(os.path.dirname(archive_filepath), exist_ok=True)
            
            # Compress and move (simple gzip)
            import gzip
            import shutil
            
            with open(filepath, 'rb') as f_in:
                with gzip.open(archive_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print(f"  Archived: {rel_path} -> {archive_filepath}")
            self.stats["archived"] += 1
            return True
            
        except Exception as e:
            print(f"  Error archiving {filepath}: {e}")
            self.stats["errors"] += 1
            return False
    
    def delete_file(self, filepath, file_info):
        """Delete a file."""
        try:
            rel_path = file_info['path']
            os.remove(filepath)
            print(f"  Deleted: {rel_path}")
            self.stats["deleted"] += 1
            return True
        except Exception as e:
            print(f"  Error deleting {filepath}: {e}")
            self.stats["errors"] += 1
            return False
    
    def process_file(self, file_info):
        """Process a single file based on retention policies."""
        self.stats["total_files"] += 1
        
        rel_path = file_info['path']
        filepath = os.path.join(self.workspace_path, rel_path)
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"  File not found: {rel_path}")
            self.stats["skipped"] += 1
            return
        
        # Get file age
        age_days = self.get_file_age_days(filepath)
        if age_days is None:
            print(f"  Could not get age: {rel_path}")
            self.stats["skipped"] += 1
            return
        
        # Check for deletion (20+ days)
        if self.should_delete(file_info, age_days):
            if self.delete_file(filepath, file_info):
                return  # File deleted, no need to archive
        
        # Check for archiving (5+ days)
        elif self.should_archive(file_info, age_days):
            if self.archive_file(filepath, file_info):
                # After archiving, delete original if it's not a memory file
                tags = file_info.get('tags', [])
                if '[MEMORY-FILE]' not in tags:
                    self.delete_file(filepath, file_info)
        
        else:
            # File doesn't meet criteria
            tags_str = ', '.join(file_info.get('tags', []))
            print(f"  Keep: {rel_path} ({age_days}d) [{tags_str}]")
            self.stats["skipped"] += 1
    
    def run(self, dry_run=False):
        """Run retention enforcement."""
        print("=" * 60)
        print("RETENTION ENFORCEMENT")
        print(f"Policy: Archive >{self.archive_days}d, Delete >{self.delete_days}d")
        print(f"Workspace: {self.workspace_path}")
        print(f"Archive: {self.archive_path}")
        print(f"Dry run: {dry_run}")
        print("=" * 60)
        
        if dry_run:
            print("DRY RUN - No changes will be made")
        
        if not self.tagging_results:
            print("Error: No tagging results available")
            return False
        
        # Process all files from tagging results
        all_files = []
        all_files.extend(self.tagging_results.get('memory_files', []))
        all_files.extend(self.tagging_results.get('log_files', []))
        all_files.extend(self.tagging_results.get('cache_files', []))
        all_files.extend(self.tagging_results.get('other_files', []))
        
        print(f"Processing {len(all_files)} files...")
        
        # Sort by age (oldest first)
        all_files.sort(key=lambda x: x.get('modified', 0), reverse=False)
        
        # Process files
        for i, file_info in enumerate(all_files):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(all_files)}")
            
            if dry_run:
                # Just show what would happen
                rel_path = file_info['path']
                age_days = self.get_file_age_days(os.path.join(self.workspace_path, rel_path))
                if age_days is not None:
                    if self.should_delete(file_info, age_days):
                        print(f"  [DRY] Would DELETE: {rel_path} ({age_days}d)")
                    elif self.should_archive(file_info, age_days):
                        print(f"  [DRY] Would ARCHIVE: {rel_path} ({age_days}d)")
                    else:
                        print(f"  [DRY] Would KEEP: {rel_path} ({age_days}d)")
            else:
                self.process_file(file_info)
        
        # Print summary
        print("\n" + "=" * 60)
        print("RETENTION ENFORCEMENT COMPLETE")
        print("=" * 60)
        print(f"Total files: {self.stats['total_files']}")
        print(f"Archived: {self.stats['archived']}")
        print(f"Deleted: {self.stats['deleted']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")
        
        if dry_run:
            print("\nThis was a DRY RUN. No changes were made.")
            print("Run without --dry-run to actually archive/delete files.")
        
        return True

def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enforce retention policies")
    parser.add_argument("--dry-run", action="store_true", help="Dry run only")
    parser.add_argument("--workspace", default="/home/ubuntu/.openclaw/workspace", help="Workspace path")
    parser.add_argument("--archive", default="/data/archive", help="Archive directory")
    
    args = parser.parse_args()
    
    enforcer = RetentionEnforcer(
        workspace_path=args.workspace,
        archive_path=args.archive
    )
    
    enforcer.run(dry_run=args.dry_run)

if __name__ == "__main__":
    main()