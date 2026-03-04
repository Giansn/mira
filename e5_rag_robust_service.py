#!/usr/bin/env python3
"""
Robust E5 RAG HTTP Service with better error handling
Designed for stable OpenClaw integration
"""

import json
import sys
import os
import time
import traceback
from typing import Dict, List, Any, Optional
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import signal
import atexit

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Global service instance
_service_instance = None
_server_instance = None

def get_service():
    """Get or create service instance with lazy loading."""
    global _service_instance
    
    if _service_instance is None:
        try:
            from e5_rag_service import E5RAGService
            _service_instance = E5RAGService()
            
            # Initialize but don't fail if it takes time
            def init_in_background():
                try:
                    result = _service_instance.initialize()
                    if not result.get("success"):
                        print(f"⚠️  Background initialization failed: {result.get('error')}")
                except Exception as e:
                    print(f"⚠️  Background initialization error: {e}")
            
            # Start initialization in background
            thread = threading.Thread(target=init_in_background, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"❌ Failed to create service: {e}")
            _service_instance = None
    
    return _service_instance


class RobustE5RAGHandler(BaseHTTPRequestHandler):
    """HTTP handler with robust error handling."""
    
    def _safe_response(self, status_code: int, data: Dict[str, Any]):
        """Safely send response with error handling."""
        try:
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_json = json.dumps(data, indent=2)
            self.wfile.write(response_json.encode('utf-8'))
        except Exception as e:
            print(f"❌ Failed to send response: {e}")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self._safe_response(200, {"status": "ok"})
    
    def do_GET(self):
        """Handle GET requests with error handling."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == '/':
                self._handle_root()
            elif path == '/status':
                self._handle_status()
            elif path == '/stats':
                self._handle_stats()
            elif path == '/search':
                self._handle_search_get(parsed_path.query)
            elif path == '/health':
                self._handle_health()
            else:
                self._safe_response(404, {
                    "error": "Endpoint not found",
                    "path": path,
                    "available_endpoints": ["/", "/status", "/stats", "/search", "/health"]
                })
        except Exception as e:
            print(f"❌ GET handler error: {e}")
            self._safe_response(500, {
                "error": "Internal server error",
                "message": str(e)
            })
    
    def do_POST(self):
        """Handle POST requests with error handling."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 10 * 1024 * 1024:  # 10MB limit
                self._safe_response(413, {"error": "Payload too large"})
                return
            
            post_data = b''
            if content_length > 0:
                post_data = self.rfile.read(content_length)
            
            data = {}
            if post_data:
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self._safe_response(400, {"error": "Invalid JSON"})
                    return
            
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == '/search':
                self._handle_search_post(data)
            elif path == '/update':
                self._handle_update(data)
            elif path == '/initialize':
                self._handle_initialize(data)
            else:
                self._safe_response(404, {
                    "error": "Endpoint not found",
                    "path": path
                })
        except Exception as e:
            print(f"❌ POST handler error: {e}")
            self._safe_response(500, {
                "error": "Internal server error",
                "message": str(e)
            })
    
    def _handle_root(self):
        """Handle root endpoint."""
        response = {
            "service": "Robust E5 RAG HTTP Service",
            "version": "1.0.0",
            "status": "running",
            "openclaw_compatible": True,
            "endpoints": {
                "GET": ["/", "/status", "/stats", "/search?q=query", "/health"],
                "POST": ["/search", "/update", "/initialize"]
            }
        }
        self._safe_response(200, response)
    
    def _handle_status(self):
        """Handle status endpoint."""
        service = get_service()
        if service and service.initialized:
            response = {
                "status": "running",
                "initialized": True,
                "model": "intfloat/e5-small-v2",
                "service": "E5 RAG Memory Search"
            }
        else:
            response = {
                "status": "initializing",
                "initialized": False,
                "message": "Service is starting up, please wait..."
            }
        self._safe_response(200, response)
    
    def _handle_stats(self):
        """Handle stats endpoint."""
        service = get_service()
        if not service:
            self._safe_response(503, {"error": "Service not available"})
            return
        
        try:
            stats = service.get_stats()
            self._safe_response(200, stats)
        except Exception as e:
            self._safe_response(500, {
                "error": "Failed to get stats",
                "message": str(e)
            })
    
    def _handle_search_get(self, query_string):
        """Handle GET search requests."""
        query_params = urllib.parse.parse_qs(query_string)
        search_query = query_params.get('q', [''])[0]
        
        if not search_query:
            self._safe_response(400, {"error": "Missing query parameter 'q'"})
            return
        
        self._perform_search(search_query)
    
    def _handle_search_post(self, data):
        """Handle POST search requests."""
        search_query = data.get('query', data.get('q', ''))
        
        if not search_query:
            self._safe_response(400, {"error": "Missing 'query' or 'q' field"})
            return
        
        top_k = data.get('top_k', 5)
        if not isinstance(top_k, int) or top_k < 1 or top_k > 50:
            top_k = 5
        
        self._perform_search(search_query, top_k)
    
    def _perform_search(self, query, top_k=5):
        """Perform search with timeout protection."""
        service = get_service()
        if not service:
            self._safe_response(503, {
                "error": "Service not available",
                "message": "E5 RAG service is still starting up"
            })
            return
        
        # Use a thread with timeout to prevent hanging
        result = None
        error = None
        
        def search_worker():
            nonlocal result, error
            try:
                result = service.search(query, top_k)
            except Exception as e:
                error = str(e)
        
        thread = threading.Thread(target=search_worker, daemon=True)
        thread.start()
        thread.join(timeout=30)  # 30 second timeout
        
        if thread.is_alive():
            self._safe_response(504, {
                "error": "Search timeout",
                "query": query,
                "message": "Search took too long (30s timeout)"
            })
            return
        
        if error:
            self._safe_response(500, {
                "error": "Search failed",
                "query": query,
                "message": error
            })
            return
        
        if result and result.get("success"):
            self._safe_response(200, result)
        else:
            self._safe_response(500, result or {
                "error": "Unknown search error",
                "query": query
            })
    
    def _handle_update(self, data):
        """Handle update embeddings request."""
        service = get_service()
        if not service:
            self._safe_response(503, {"error": "Service not available"})
            return
        
        try:
            result = service.update_embeddings()
            if result.get("success"):
                self._safe_response(200, result)
            else:
                self._safe_response(500, result)
        except Exception as e:
            self._safe_response(500, {
                "error": "Update failed",
                "message": str(e)
            })
    
    def _handle_initialize(self, data):
        """Handle initialize request."""
        service = get_service()
        if not service:
            self._safe_response(503, {"error": "Service creation failed"})
            return
        
        try:
            result = service.initialize()
            if result.get("success"):
                self._safe_response(200, result)
            else:
                self._safe_response(500, result)
        except Exception as e:
            self._safe_response(500, {
                "error": "Initialization failed",
                "message": str(e)
            })
    
    def _handle_health(self):
        """Handle health check endpoint."""
        service = get_service()
        if service:
            response = {
                "status": "healthy",
                "service": "available",
                "timestamp": time.time()
            }
        else:
            response = {
                "status": "degraded",
                "service": "unavailable",
                "timestamp": time.time()
            }
        self._safe_response(200, response)
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        # Only log errors and important events
        if '404' in args or '500' in args or '503' in args or '504' in args:
            super().log_message(format, *args)
        elif 'GET /health' in args or 'GET /status' in args:
            # Log health checks at debug level
            pass


class RobustE5RAGServer:
    """Robust HTTP server wrapper."""
    
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Register cleanup
        atexit.register(self.stop)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self, background=False):
        """Start the HTTP server."""
        print(f"🚀 Starting Robust E5 RAG HTTP Service on http://{self.host}:{self.port}")
        print(f"   Designed for stable OpenClaw integration")
        
        try:
            self.server = HTTPServer((self.host, self.port), RobustE5RAGHandler)
            self.running = True
            
            if background:
                self.thread = threading.Thread(target=self._run_server, daemon=True)
                self.thread.start()
                print(f"   ✅ Running in background thread")
                print(f"   Health check: http://{self.host}:{self.port}/health")
                return True
            else:
                print(f"   ✅ Server ready")
                print(f"   Press Ctrl+C to stop")
                self.server.serve_forever()
                return True
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def _run_server(self):
        """Run server in background thread."""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the HTTP server."""
        if self.server and self.running:
            print("🛑 Stopping server...")
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            print("✅ Server stopped")
            return True
        return False
    
    def is_running(self):
        """Check if server is running."""
        return self.running


def test_robust_service():
    """Test the robust service."""
    import requests
    
    print("🧪 Testing Robust E5 RAG Service")
    print("=" * 50)
    
    # Start server
    server = RobustE5RAGServer('localhost', 8003)
    server.start(background=True)
    
    # Give server time to start
    time.sleep(2)
    
    tests_passed = 0
    total_tests = 0
    
    try:
        # Test 1: Root endpoint
        total_tests += 1
        response = requests.get('http://localhost:8003/', timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint: OK")
            tests_passed += 1
        else:
            print(f"❌ Root endpoint: HTTP {response.status_code}")
        
        # Test 2: Health check
        total_tests += 1
        response = requests.get('http://localhost:8003/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health check: OK")
            tests_passed += 1
        else:
            print(f"❌ Health check: HTTP {response.status_code}")
        
        # Test 3: Status
        total_tests += 1
        response = requests.get('http://localhost:8003/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            tests_passed += 1
        else:
            print(f"❌ Status: HTTP {response.status_code}")
        
        # Test 4: Search with timeout simulation
        total_tests += 1
        try:
            # This should return quickly even if service is still initializing
            response = requests.get('http://localhost:8003/search?q=test', timeout=10)
            print(f"✅ Search endpoint responsive: HTTP {response.status_code}")
            tests_passed += 1
        except requests.exceptions.Timeout:
            print("❌ Search endpoint timeout")
        
        # Test 5: Invalid endpoint
        total_tests += 1
        response = requests.get('http://localhost:8003/invalid', timeout=5)
        if response.status_code == 404:
            print("✅ Invalid endpoint: Returns 404 as expected")
            tests_passed += 1
        else:
            print(f"❌ Invalid endpoint: HTTP {response.status_code} (expected 404)")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    finally:
        # Stop server
        server.stop()
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    if tests_passed == total_tests:
        print("✅ All tests passed - Service is robust and ready")
    else:
        print("⚠️  Some tests failed - Service needs improvement")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Robust E5 RAG HTTP Service for OpenClaw")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--test", action="store_true", help="Run robustness tests")
    parser.add_argument("--background", action="store_true", help="Run in background")
    
    args = parser.parse_args()
    
    if args.test:
        success = test_robust_service()
        sys.exit(0 if success else 1)
    else:
        server = RobustE5RAGServer(args.host, args.port)
        
        try:
            server.start(background=args.background)
            
            if args.background:
                # Keep main thread alive
                while server.is_running():
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            server.stop()
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            server.stop()
            sys.exit(1)