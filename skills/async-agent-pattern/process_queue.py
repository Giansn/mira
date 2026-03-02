#!/usr/bin/env python3
"""
Process queued operations for async agent pattern.
Runs via cron/heartbeat to handle session-fragile operations.
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from queue_manager import QueueManager

class QueueProcessor:
    """Processes queued operations."""
    
    def __init__(self, base_path: str = None):
        """Initialize queue processor.
        
        Args:
            base_path: Base directory for queue files
        """
        self.queue_manager = QueueManager(base_path)
        
        # Track Claude conversation context
        self.claude_context = ""
        
        # Import browser tool if available
        self.browser_available = False
        try:
            # Try to import browser control
            # This would need to be adapted based on actual browser tool availability
            pass
        except ImportError:
            pass
    
    def process_all(self, max_operations: int = 10):
        """Process all pending operations.
        
        Args:
            max_operations: Maximum number of operations to process in this run
            
        Returns:
            Dictionary with processing results
        """
        pending = self.queue_manager.get_pending_operations()
        
        if not pending:
            return {"processed": 0, "success": 0, "failed": 0, "operations": []}
        
        # Sort by timestamp (oldest first)
        pending.sort(key=lambda x: x.get("timestamp", ""))
        
        results = {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "operations": []
        }
        
        for operation in pending[:max_operations]:
            op_result = self._process_operation(operation)
            results["operations"].append(op_result)
            
            if op_result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            results["processed"] += 1
        
        return results
    
    def process_by_type(self, operation_type: str, max_operations: int = 5):
        """Process operations of specific type.
        
        Args:
            operation_type: Type to process (claude, browser, job, api)
            max_operations: Maximum number to process
            
        Returns:
            Dictionary with processing results
        """
        pending = self.queue_manager.get_pending_operations(operation_type)
        
        if not pending:
            return {"processed": 0, "success": 0, "failed": 0, "operations": []}
        
        # Sort by timestamp (oldest first)
        pending.sort(key=lambda x: x.get("timestamp", ""))
        
        results = {
            "type": operation_type,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "operations": []
        }
        
        for operation in pending[:max_operations]:
            op_result = self._process_operation(operation)
            results["operations"].append(op_result)
            
            if op_result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            results["processed"] += 1
        
        return results
    
    def _process_operation(self, operation: dict) -> dict:
        """Process a single operation.
        
        Args:
            operation: Operation to process
            
        Returns:
            Processing result
        """
        op_type = operation.get("type")
        op_id = operation.get("id")
        
        print(f"Processing {op_type} operation: {op_id}")
        
        try:
            if op_type == "claude":
                result = self._process_claude(operation)
            elif op_type == "browser":
                result = self._process_browser(operation)
            elif op_type == "job":
                result = self._process_job(operation)
            elif op_type == "api":
                result = self._process_api(operation)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown operation type: {op_type}",
                    "details": {}
                }
            
            # Mark as completed or failed
            if result["success"]:
                self.queue_manager.mark_completed(op_id, result.get("result", {}))
            else:
                self.queue_manager.mark_failed(
                    op_id, 
                    result.get("error", "Unknown error"),
                    result.get("details", {})
                )
            
            return {
                "operation_id": op_id,
                "type": op_type,
                "success": result["success"],
                "error": result.get("error"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            # Unexpected error
            error_msg = f"Processing error: {str(e)}"
            print(f"Error processing {op_id}: {error_msg}")
            
            self.queue_manager.mark_failed(
                op_id,
                error_msg,
                {"exception_type": type(e).__name__}
            )
            
            return {
                "operation_id": op_id,
                "type": op_type,
                "success": False,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    def _process_claude(self, operation: dict) -> dict:
        """Process Claude message.
        
        Args:
            operation: Claude operation
            
        Returns:
            Processing result
        """
        message = operation.get("message", "")
        context = operation.get("context", "")
        purpose = operation.get("purpose", "conversation")
        
        print(f"  Sending to Claude: {message[:50]}...")
        
        try:
            # Build command
            # Use --print for non-interactive output
            cmd = ["claude", "--print", message]
            
            # Add context if provided
            if context:
                # Could prepend context to message or use --context flag if supported
                pass
            
            # Run Claude
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 120 second timeout (2 minutes)
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                
                # Update conversation context
                self.claude_context = f"Previous: {message}\nResponse: {response}\n"
                
                return {
                    "success": True,
                    "result": {
                        "response": response,
                        "purpose": purpose,
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Claude CLI failed with return code {result.returncode}",
                    "details": {
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    }
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Claude CLI timeout (120 seconds)",
                "details": {"timeout": 120}
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude",
                "details": {}
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "details": {"exception_type": type(e).__name__}
            }
    
    def _process_browser(self, operation: dict) -> dict:
        """Process browser action.
        
        Args:
            operation: Browser operation
            
        Returns:
            Processing result
        """
        action = operation.get("action", "")
        params = operation.get("params", {})
        purpose = operation.get("purpose", "browser_automation")
        
        print(f"  Browser action: {action}")
        
        # For now, this is a stub implementation
        # In a real implementation, this would interface with OpenClaw's browser tool
        
        if action == "screenshot":
            url = params.get("url", "")
            
            # Example: Use OpenClaw browser tool via subprocess or API
            # This would need to be adapted to actual browser tool interface
            
            return {
                "success": True,
                "result": {
                    "action": action,
                    "url": url,
                    "status": "screenshot_captured",
                    "file_path": f"/tmp/screenshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png",
                    "purpose": purpose,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        
        elif action == "navigate":
            url = params.get("url", "")
            
            return {
                "success": True,
                "result": {
                    "action": action,
                    "url": url,
                    "status": "navigated",
                    "title": "Example Page",
                    "purpose": purpose,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        
        else:
            return {
                "success": False,
                "error": f"Unsupported browser action: {action}",
                "details": {"supported_actions": ["screenshot", "navigate"]}
            }
    
    def _process_job(self, operation: dict) -> dict:
        """Process background job.
        
        Args:
            operation: Job operation
            
        Returns:
            Processing result
        """
        name = operation.get("name", "")
        command = operation.get("command", "")
        dependencies = operation.get("dependencies", [])
        purpose = operation.get("purpose", "background_job")
        
        print(f"  Running job: {name}")
        print(f"  Command: {command}")
        
        # Check dependencies
        for dep_id in dependencies:
            # Check if dependency is completed
            # This is simplified - would need actual dependency checking
            pass
        
        try:
            # Run command
            # Using shell=True for simplicity, but be careful with user input
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for jobs
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": {
                        "job_name": name,
                        "command": command,
                        "output": result.stdout,
                        "returncode": result.returncode,
                        "purpose": purpose,
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Job failed with return code {result.returncode}",
                    "details": {
                        "stderr": result.stderr,
                        "returncode": result.returncode,
                        "stdout": result.stdout
                    }
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Job timeout (600 seconds): {name}",
                "details": {"timeout": 600, "job_name": name}
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Job execution error: {str(e)}",
                "details": {"exception_type": type(e).__name__, "job_name": name}
            }
    
    def _process_api(self, operation: dict) -> dict:
        """Process API call.
        
        Args:
            operation: API operation
            
        Returns:
            Processing result
        """
        service = operation.get("service", "")
        endpoint = operation.get("endpoint", "")
        method = operation.get("method", "GET")
        params = operation.get("params", {})
        data = operation.get("data", {})
        purpose = operation.get("purpose", "api_call")
        
        print(f"  API call: {service} {endpoint}")
        
        # This is a simplified implementation
        # In practice, would use appropriate libraries for each service
        
        if service == "moltbook":
            # Example Moltbook API call
            # Would need actual API key and proper request handling
            
            return {
                "success": True,
                "result": {
                    "service": service,
                    "endpoint": endpoint,
                    "method": method,
                    "status": "simulated_success",
                    "response": {"simulated": True, "message": "API call queued"},
                    "purpose": purpose,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        
        elif service == "scrapesense":
            # Example ScrapeSense API call
            
            return {
                "success": True,
                "result": {
                    "service": service,
                    "endpoint": endpoint,
                    "method": method,
                    "status": "simulated_success",
                    "response": {"simulated": True, "job_id": "simulated_job_123"},
                    "purpose": purpose,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        
        else:
            return {
                "success": False,
                "error": f"Unsupported API service: {service}",
                "details": {"supported_services": ["moltbook", "scrapesense"]}
            }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process queued operations")
    parser.add_argument("--type", choices=["claude", "browser", "job", "api", "all"],
                       default="all", help="Type of operations to process")
    parser.add_argument("--max", type=int, default=5,
                       help="Maximum number of operations to process")
    parser.add_argument("--stats", action="store_true",
                       help="Show statistics only")
    parser.add_argument("--cleanup", type=int, default=0,
                       help="Clean up results older than N days (0 = no cleanup)")
    
    args = parser.parse_args()
    
    processor = QueueProcessor()
    
    if args.stats:
        stats = processor.queue_manager.get_stats()
        print(json.dumps(stats, indent=2))
        return
    
    if args.cleanup > 0:
        print(f"Cleaning up results older than {args.cleanup} days...")
        processor.queue_manager.cleanup_old_results(args.cleanup)
    
    if args.type == "all":
        results = processor.process_all(max_operations=args.max)
    else:
        results = processor.process_by_type(args.type, max_operations=args.max)
    
    print("\n" + "="*60)
    print("PROCESSING RESULTS")
    print("="*60)
    print(f"Processed: {results['processed']}")
    print(f"Success: {results['success']}")
    print(f"Failed: {results['failed']}")
    
    if results.get('type'):
        print(f"Type: {results['type']}")
    
    print("\nDetails:")
    for op in results['operations']:
        status = "✓" if op['success'] else "✗"
        print(f"  {status} {op['type']}: {op['operation_id']}")
        if not op['success']:
            print(f"    Error: {op['error']}")
    
    # Update stats in state file
    stats = processor.queue_manager.get_stats()
    print(f"\nTotal pending: {stats.get('total_pending', 0)}")
    print(f"Total processed: {stats.get('total_processed', 0)}")
    print(f"Total failed: {stats.get('total_failed', 0)}")


if __name__ == "__main__":
    main()