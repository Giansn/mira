#!/usr/bin/env python3
"""
Basic usage examples for async agent pattern.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from queue_manager import QueueManager
from process_queue import QueueProcessor

def example_claude_conversation():
    """Example: Queue Claude messages for async processing."""
    print("Example: Claude Conversation Queue")
    print("-" * 40)
    
    queue = QueueManager()
    
    # Queue some messages
    msg1_id = queue.add_claude_message(
        "Hello Claude! How are you today?",
        purpose="greeting"
    )
    print(f"Queued message 1: {msg1_id}")
    
    msg2_id = queue.add_claude_message(
        "Can you explain the async agent pattern?",
        purpose="explanation_request"
    )
    print(f"Queued message 2: {msg2_id}")
    
    # Check pending
    pending = queue.get_pending_operations("claude")
    print(f"\nPending Claude messages: {len(pending)}")
    
    # Process them
    print("\nProcessing queue...")
    processor = QueueProcessor()
    results = processor.process_by_type("claude", max_operations=2)
    
    print(f"Processed: {results['processed']}")
    print(f"Success: {results['success']}")
    print(f"Failed: {results['failed']}")
    
    # Check stats
    stats = queue.get_stats()
    print(f"\nStats: {stats}")

def example_browser_automation():
    """Example: Queue browser actions."""
    print("\n\nExample: Browser Automation Queue")
    print("-" * 40)
    
    queue = QueueManager()
    
    # Queue browser actions
    screenshot_id = queue.add_browser_action(
        "screenshot",
        {"url": "https://www.moltbook.com", "selector": "body"},
        purpose="documentation"
    )
    print(f"Queued screenshot: {screenshot_id}")
    
    navigate_id = queue.add_browser_action(
        "navigate",
        {"url": "https://github.com/Giansn/mira"},
        purpose="check_repo"
    )
    print(f"Queued navigation: {navigate_id}")
    
    pending = queue.get_pending_operations("browser")
    print(f"\nPending browser actions: {len(pending)}")

def example_background_jobs():
    """Example: Queue background jobs."""
    print("\n\nExample: Background Jobs Queue")
    print("-" * 40)
    
    queue = QueueManager()
    
    # Queue jobs
    job1_id = queue.add_job(
        "memory_graph",
        "python3 /home/ubuntu/.openclaw/workspace/memory_heartbeat.py --summary",
        purpose="memory_maintenance"
    )
    print(f"Queued job 1: {job1_id}")
    
    job2_id = queue.add_job(
        "git_status",
        "cd /home/ubuntu/.openclaw/workspace && git status --short",
        purpose="repo_check"
    )
    print(f"Queued job 2: {job2_id}")
    
    pending = queue.get_pending_operations("job")
    print(f"\nPending jobs: {len(pending)}")

def example_workflow():
    """Example: Complete workflow with dependencies."""
    print("\n\nExample: Workflow with Dependencies")
    print("-" * 40)
    
    queue = QueueManager()
    
    # First, get data from API
    api_id = queue.add_api_call(
        "moltbook",
        "/api/v1/home",
        "GET",
        purpose="get_feed"
    )
    print(f"Queued API call: {api_id}")
    
    # Then, analyze with Claude (depends on API result)
    claude_id = queue.add_claude_message(
        "Analyze this Moltbook feed data and summarize key trends",
        purpose="feed_analysis"
    )
    # Note: In real implementation, would need dependency tracking
    
    # Finally, document with screenshot
    screenshot_id = queue.add_browser_action(
        "screenshot",
        {"url": "https://www.moltbook.com", "full_page": True},
        purpose="document_trends"
    )
    
    pending = queue.get_pending_operations()
    print(f"\nTotal pending operations: {len(pending)}")
    
    # Process in order
    processor = QueueProcessor()
    
    print("\nProcessing API calls...")
    api_results = processor.process_by_type("api", max_operations=1)
    
    print("\nProcessing Claude messages...")
    claude_results = processor.process_by_type("claude", max_operations=1)
    
    print("\nProcessing browser actions...")
    browser_results = processor.process_by_type("browser", max_operations=1)
    
    print("\nAll processing complete!")

def main():
    """Run examples."""
    print("Async Agent Pattern - Examples")
    print("=" * 60)
    
    # Run examples
    example_claude_conversation()
    example_browser_automation()
    example_background_jobs()
    example_workflow()
    
    print("\n" + "=" * 60)
    print("Summary: These operations are now queued and will be")
    print("processed by the heartbeat/cron system, surviving")
    print("session restarts and interruptions.")

if __name__ == "__main__":
    main()