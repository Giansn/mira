#!/usr/bin/env python3
"""
Queue manager for async agent pattern.
Implements externalized state for session-fragile operations.
"""

import json
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class QueueManager:
    """Manages message queues for async operations."""
    
    def __init__(self, base_path: str = None):
        """Initialize queue manager.
        
        Args:
            base_path: Base directory for queue files (default: skill directory)
        """
        if base_path is None:
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)
        
        # Create directories
        self.queue_dir = self.base_path / "queue"
        self.state_dir = self.base_path / "state"
        self.results_dir = self.base_path / "results"
        
        for dir_path in [self.queue_dir, self.state_dir, self.results_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Queue files
        self.claude_queue = self.queue_dir / "claude.jsonl"
        self.browser_queue = self.queue_dir / "browser.jsonl"
        self.job_queue = self.queue_dir / "job.jsonl"
        self.api_queue = self.queue_dir / "api.jsonl"
        
        # State file
        self.state_file = self.state_dir / "operations_state.json"
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID for operation."""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    def _append_to_queue(self, queue_file: Path, data: Dict) -> str:
        """Append operation to queue file (JSONL format)."""
        operation_id = data.get("id", self._generate_id("op"))
        data["id"] = operation_id
        data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        data["status"] = "pending"
        
        with open(queue_file, "a") as f:
            f.write(json.dumps(data) + "\n")
        
        # Update state file
        self._update_state_file(data)
        
        return operation_id
    
    def _update_state_file(self, operation: Dict):
        """Update state checkpoint file."""
        state = self._load_state()
        
        # Remove from pending if already exists (idempotent)
        state["pending_operations"] = [
            op for op in state["pending_operations"] 
            if op.get("id") != operation.get("id")
        ]
        
        # Add to pending
        state["pending_operations"].append(operation)
        
        # Save state
        self._save_state(state)
    
    def _load_state(self) -> Dict:
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default state
        return {
            "pending_operations": [],
            "completed_operations": [],
            "failed_operations": [],
            "last_processed": None,
            "stats": {
                "total_processed": 0,
                "total_failed": 0,
                "total_pending": 0
            }
        }
    
    def _save_state(self, state: Dict):
        """Save state to file."""
        # Update stats
        state["stats"]["total_pending"] = len(state["pending_operations"])
        state["stats"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def add_claude_message(self, message: str, context: str = None, purpose: str = None) -> str:
        """Add Claude message to queue.
        
        Args:
            message: Text to send to Claude
            context: Optional context for the conversation
            purpose: Why this message is being sent (for tracking)
            
        Returns:
            Operation ID
        """
        data = {
            "type": "claude",
            "message": message,
            "context": context,
            "purpose": purpose or "conversation",
            "queue_file": "claude.jsonl"
        }
        
        return self._append_to_queue(self.claude_queue, data)
    
    def add_browser_action(self, action: str, params: Dict, purpose: str = None) -> str:
        """Add browser action to queue.
        
        Args:
            action: Action type (screenshot, navigate, click, etc.)
            params: Action parameters
            purpose: Why this action is needed
            
        Returns:
            Operation ID
        """
        data = {
            "type": "browser",
            "action": action,
            "params": params,
            "purpose": purpose or "browser_automation",
            "queue_file": "browser.jsonl"
        }
        
        return self._append_to_queue(self.browser_queue, data)
    
    def add_job(self, name: str, command: str, dependencies: List[str] = None, purpose: str = None) -> str:
        """Add job to queue.
        
        Args:
            name: Job name
            command: Command to execute
            dependencies: List of operation IDs that must complete first
            purpose: Why this job is needed
            
        Returns:
            Operation ID
        """
        data = {
            "type": "job",
            "name": name,
            "command": command,
            "dependencies": dependencies or [],
            "purpose": purpose or "background_job",
            "queue_file": "job.jsonl"
        }
        
        return self._append_to_queue(self.job_queue, data)
    
    def add_api_call(self, service: str, endpoint: str, method: str = "GET", 
                    params: Dict = None, data: Dict = None, purpose: str = None) -> str:
        """Add API call to queue.
        
        Args:
            service: API service name (moltbook, scrapesense, etc.)
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            data: Request body
            purpose: Why this API call is needed
            
        Returns:
            Operation ID
        """
        data_dict = {
            "type": "api",
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "params": params or {},
            "data": data or {},
            "purpose": purpose or "api_call",
            "queue_file": "api.jsonl"
        }
        
        return self._append_to_queue(self.api_queue, data_dict)
    
    def get_pending_operations(self, operation_type: str = None) -> List[Dict]:
        """Get pending operations, optionally filtered by type.
        
        Args:
            operation_type: Filter by type (claude, browser, job, api)
            
        Returns:
            List of pending operations
        """
        state = self._load_state()
        
        if operation_type:
            return [
                op for op in state["pending_operations"]
                if op.get("type") == operation_type
            ]
        
        return state["pending_operations"]
    
    def mark_completed(self, operation_id: str, result: Dict = None):
        """Mark operation as completed.
        
        Args:
            operation_id: ID of completed operation
            result: Operation results
        """
        state = self._load_state()
        
        # Find operation in pending
        operation = None
        for i, op in enumerate(state["pending_operations"]):
            if op.get("id") == operation_id:
                operation = state["pending_operations"].pop(i)
                break
        
        if operation:
            # Add result
            operation["completed_at"] = datetime.utcnow().isoformat() + "Z"
            operation["status"] = "completed"
            operation["result"] = result or {}
            
            # Move to completed
            state["completed_operations"].append(operation)
            state["stats"]["total_processed"] += 1
            
            # Clean up queue file entry
            self._remove_from_queue_file(operation)
            
            self._save_state(state)
            
            # Save detailed result
            self._save_result(operation_id, operation)
    
    def mark_failed(self, operation_id: str, error: str, details: Dict = None):
        """Mark operation as failed.
        
        Args:
            operation_id: ID of failed operation
            error: Error message
            details: Additional error details
        """
        state = self._load_state()
        
        # Find operation in pending
        operation = None
        for i, op in enumerate(state["pending_operations"]):
            if op.get("id") == operation_id:
                operation = state["pending_operations"].pop(i)
                break
        
        if operation:
            # Add error info
            operation["failed_at"] = datetime.utcnow().isoformat() + "Z"
            operation["status"] = "failed"
            operation["error"] = error
            operation["details"] = details or {}
            
            # Move to failed
            state["failed_operations"].append(operation)
            state["stats"]["total_failed"] += 1
            
            # Clean up queue file entry
            self._remove_from_queue_file(operation)
            
            self._save_state(state)
    
    def _remove_from_queue_file(self, operation: Dict):
        """Remove operation from its queue file."""
        queue_file = self.queue_dir / operation.get("queue_file", "")
        if not queue_file.exists():
            return
        
        # Read all lines, skip the one with this operation ID
        with open(queue_file, "r") as f:
            lines = f.readlines()
        
        with open(queue_file, "w") as f:
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    if data.get("id") != operation.get("id"):
                        f.write(line)
                except json.JSONDecodeError:
                    f.write(line)  # Keep malformed lines
    
    def _save_result(self, operation_id: str, operation: Dict):
        """Save detailed result to results directory."""
        result_file = self.results_dir / f"{operation_id}.json"
        
        result_data = {
            "operation_id": operation_id,
            "type": operation.get("type"),
            "purpose": operation.get("purpose"),
            "submitted_at": operation.get("timestamp"),
            "completed_at": operation.get("completed_at"),
            "status": operation.get("status"),
            "result": operation.get("result", {}),
            "original_operation": {k: v for k, v in operation.items() 
                                  if k not in ["result", "completed_at", "failed_at", "status"]}
        }
        
        with open(result_file, "w") as f:
            json.dump(result_data, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get queue statistics."""
        state = self._load_state()
        return state.get("stats", {})
    
    def cleanup_old_results(self, days: int = 7):
        """Clean up results older than specified days.
        
        Args:
            days: Remove results older than this many days
        """
        cutoff = datetime.utcnow().timestamp() - (days * 24 * 3600)
        
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, "r") as f:
                    result = json.load(f)
                
                completed_at = result.get("completed_at")
                if completed_at:
                    # Parse ISO timestamp
                    completed_time = datetime.fromisoformat(
                        completed_at.replace("Z", "+00:00")
                    ).timestamp()
                    
                    if completed_time < cutoff:
                        result_file.unlink()
                        
            except (IOError, json.JSONDecodeError, ValueError):
                # Skip files we can't read
                pass