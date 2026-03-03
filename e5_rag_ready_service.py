#!/usr/bin/env python3
"""
E5 RAG Service with Readiness Probes
Handles initialization properly for OpenClaw integration
"""

import json
import sys
import os
import time
import threading
from typing import Dict, List, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import queue

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Global state
class ServiceState:
    """Thread-safe service state management."""
    
    def __init__(self):
        self.initializing = False
        self.ready = False
        self.error = None
        self.service = None
        self.start_time = time.time()
        self.initialization_thread = None
        self.request_queue = queue.Queue()
        self.lock = threading.Lock()
    
    def start_initialization(self):
        """Start service initialization in background."""
        with self.lock:
            if self.initializing or self.ready:
                return False
            
            self.initializing = True
            self.initialization_thread = threading.Thread(
                target=self._initialize_service,
                daemon=True
            )
            self.initialization_thread.start()
            return True
    
    def _initialize_service(self):
        """Initialize service in background thread."""
        try:
            from e5_rag_service import E5RAGService
            
            print("🚀 Starting E5 RAG service initialization...")
            self.service = E5RAGService()
            
            print("🔧 Initializing service...")
            result = self.service.initialize()
            
            if result.get("success"):
                print("✅ Service initialized successfully")
                with self.lock:
                    self.ready = True
                    self.error = None
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"❌ Service initialization failed: {error_msg}")
                with self.lock:
                    self.error = error_msg
                    
        except Exception as e:
            print(f"❌ Service initialization error: {e}")
            import traceback
            traceback.print_exc()
            with self.lock:
                self.error = str(e)
        finally:
            with self.lock:
                self.initializing = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        with self.lock:
            uptime = time.time() - self.start_time
            
            if self.ready:
                return {
                    "status": "ready",
                    "uptime": uptime,
                    "message": "Service ready for requests"
                }
            elif self.initializing:
                return {
                    "status": "initializing",
                    "uptime": uptime,
                    "message": "Service is starting up, please wait..."
                }
            elif self.error:
                return {
                    "status": "error",
                    "uptime": uptime,
                    "error": self.error,
                    "message": "Service failed to initialize"
                }
            else:
                return {
                    "status": "stopped",
                    "uptime": uptime,
                    "message": "Service not started"
                }
    
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform search if service is ready."""
        with self.lock:
            if not self.ready or not self.service:
                return {
                    "success": False,
                    "error": "Service not ready",
                    "status": self.get_status()["status"]
                }
        
        try:
            return self.service.search(query, top_k)
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "query": query
            }


# Global service state
service_state = ServiceState()


class ReadyE5RAGHandler(BaseHTTPRequestHandler):
    """HTTP handler with readiness probes."""
    
    def _json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self._handle_root()
        elif path == '/status':
            self._handle_status()
        elif path == '/ready':
            self._handle_ready()
        elif path == '/health':
            self._handle_health()
        elif path == '/search':
            self._handle_search_get(parsed_path.query)
        elif path == '/init':
            self._handle_init()
        else:
            self._json_response(404, {
                "error": "Endpoint not found",
                "path": path
            })
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except:
            data = {}
        
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/search':
            self._handle_search_post(data)
        elif path == '/init':
            self._handle_init_post(data)
        else:
            self._json_response(404, {
                "error": "Endpoint not found",
                "path": path
            })
    
    def _handle_root(self):
        """Handle root endpoint."""
        status = service_state.get_status()
        
        response = {
            "service": "E5 RAG Ready Service",
            "version": "1.1.0",
            "status": status,
            "endpoints": {
                "GET": ["/", "/status", "/ready", "/health", "/search?q=query", "/init"],
                "POST": ["/search", "/init"]
            },
            "openclaw_compatible": True,
            "readiness_probe": "/ready",
            "health_check": "/health"
        }
        self._json_response(200, response)
    
    def _handle_status(self):
        """Handle detailed status endpoint."""
        status = service_state.get_status()
        self._json_response(200, status)
    
    def _handle_ready(self):
        """Handle readiness probe (for OpenClaw/k8s)."""
        status = service_state.get_status()
        
        if status["status"] == "ready":
            self._json_response(200, {
                "ready": True,
                "status": "ready"
            })
        else:
            self._json_response(503, {
                "ready": False,
                "status": status["status"],
                "message": status.get("message", "Service not ready")
            })
    
    def _handle_health(self):
        """Handle health check (always returns 200)."""
        status = service_state.get_status()
        self._json_response(200, {
            "healthy": True,
            "status": status["status"],
            "uptime": status["uptime"]
        })
    
    def _handle_search_get(self, query_string):
        """Handle GET search requests."""
        query_params = urllib.parse.parse_qs(query_string)
        search_query = query_params.get('q', [''])[0]
        
        if not search_query:
            self._json_response(400, {
                "error": "Missing query parameter 'q'",
                "example": "/search?q=your+query"
            })
            return
        
        top_k = 5
        if 'top_k' in query_params:
            try:
                top_k = int(query_params['top_k'][0])
            except:
                pass
        
        self._perform_search(search_query, top_k)
    
    def _handle_search_post(self, data):
        """Handle POST search requests."""
        search_query = data.get('query', data.get('q', ''))
        
        if not search_query:
            self._json_response(400, {
                "error": "Missing 'query' or 'q' field"
            })
            return
        
        top_k = data.get('top_k', 5)
        self._perform_search(search_query, top_k)
    
    def _perform_search(self, query, top_k):
        """Perform search with proper readiness handling."""
        status = service_state.get_status()
        
        if status["status"] != "ready":
            # Service not ready - return appropriate error
            if status["status"] == "initializing":
                self._json_response(503, {
                    "success": False,
                    "error": "Service initializing",
                    "message": "E5 RAG service is still starting up. Please wait 30 seconds and try again.",
                    "status": "initializing",
                    "estimated_wait": 30  # seconds
                })
            elif status["status"] == "error":
                self._json_response(500, {
                    "success": False,
                    "error": "Service initialization failed",
                    "message": status.get("error", "Unknown error"),
                    "status": "error"
                })
            else:
                # Service not started - auto-start initialization
                service_state.start_initialization()
                self._json_response(503, {
                    "success": False,
                    "error": "Service not started",
                    "message": "Service initialization has been started. Please wait and try again.",
                    "status": "starting",
                    "action": "auto_started"
                })
            return
        
        # Service is ready - perform search
        result = service_state.search(query, top_k)
        
        if result.get("success"):
            self._json_response(200, result)
        else:
            self._json_response(500, result)
    
    def _handle_init(self):
        """Handle initialization request (GET)."""
        if service_state.start_initialization():
            self._json_response(202, {
                "success": True,
                "message": "Service initialization started",
                "status": "initializing"
            })
        else:
            status = service_state.get_status()
            self._json_response(200, {
                "message": "Service already initializing or ready",
                "status": status
            })
    
    def _handle_init_post(self, data):
        """Handle initialization request (POST)."""
        self._handle_init()
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        # Don't log health checks
        if '/health' in args or '/ready' in args:
            return
        super().log_message(format, *args)


def start_service(host='localhost', port=8000):
    """Start the ready service."""
    print(f"🚀 Starting E5 RAG Ready Service on http://{host}:{port}")
    print(f"   This service handles initialization properly for OpenClaw")
    print(f"")
    print(f"   Endpoints:")
    print(f"   - GET  /          Service info")
    print(f"   - GET  /status    Detailed status")
    print(f"   - GET  /ready     Readiness probe (returns 200 when ready)")
    print(f"   - GET  /health    Health check (always returns 200)")
    print(f"   - GET  /search    Search with query parameter")
    print(f"   - POST /search    Search with JSON body")
    print(f"   - GET  /init      Start initialization")
    print(f"")
    print(f"   OpenClaw should use: /ready for readiness checks")
    print(f"")
    
    # Auto-start initialization
    print("🔧 Auto-starting service initialization...")
    service_state.start_initialization()
    
    # Start HTTP server
    server = HTTPServer((host, port), ReadyE5RAGHandler)
    
    print(f"✅ Server ready at http://{host}:{port}")
    print(f"   Service status: {service_state.get_status()['status']}")
    print(f"   Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="E5 RAG Ready Service for OpenClaw")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    start_service(args.host, args.port)