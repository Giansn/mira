#!/usr/bin/env python3
"""
E5 HTTP Service Example
Demonstrates the "Don't fight OpenClaw, work with it" principle

This service provides semantic search that OpenClaw can consume via HTTP provider.
Instead of trying to fix OpenClaw's context size limitation, we build a service
that OpenClaw can use through its existing HTTP provider capability.
"""

import http.server
import socketserver
import json
import threading
import time
import sys
import os
from typing import Dict, Any, List
from urllib.parse import urlparse, parse_qs

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock E5 RAG service for demonstration
# In real implementation, this would import actual E5 RAG system
class MockE5RAGService:
    """Mock E5 RAG service for demonstration purposes."""
    
    def __init__(self):
        self.initialized = False
        self.chunk_count = 234  # Mock data
        self.model = "intfloat/e5-small-v2"
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the mock service."""
        self.initialized = True
        return {
            "success": True,
            "message": "Mock E5 RAG Service initialized",
            "chunks": self.chunk_count,
            "model": self.model
        }
    
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform mock semantic search."""
        if not self.initialized:
            self.initialize()
        
        # Mock search results
        mock_results = [
            {
                "score": 0.8579,
                "text": f"Memory about {query} - relevant content here",
                "source": "MEMORY.md",
                "lines": "1-11",
                "chunk_id": "abc123"
            },
            {
                "score": 0.8123,
                "text": f"Another memory related to {query}",
                "source": "memory/2026-03-02.md",
                "lines": "45-60",
                "chunk_id": "def456"
            }
        ]
        
        # Return only top_k results
        results = mock_results[:top_k]
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "provider": "e5-http-service",
            "model": self.model
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "initialized": self.initialized,
            "chunks": self.chunk_count,
            "model": self.model,
            "service": "E5 HTTP Service (Mock)"
        }


class E5RAGHTTPHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for E5 RAG service."""
    
    def __init__(self, *args, **kwargs):
        self.service = MockE5RAGService()
        super().__init__(*args, **kwargs)
    
    def _send_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/status':
            # Service status endpoint
            stats = self.service.get_stats()
            self._send_response(200, stats)
            
        elif parsed_path.path == '/search':
            # Search via query parameter
            query_params = parse_qs(parsed_path.query)
            query = query_params.get('q', [''])[0]
            top_k = int(query_params.get('top_k', [5])[0])
            
            if not query:
                self._send_response(400, {
                    "success": False,
                    "error": "Query parameter 'q' is required"
                })
                return
            
            result = self.service.search(query, top_k)
            self._send_response(200, result)
            
        elif parsed_path.path == '/':
            # Root endpoint - service info
            self._send_response(200, {
                "service": "E5 RAG HTTP Service",
                "version": "1.0.0",
                "endpoints": {
                    "GET /status": "Service status",
                    "GET /search?q=query": "Search with query parameter",
                    "POST /search": "Search with JSON body",
                    "GET /": "This information"
                },
                "openclaw_integration": {
                    "provider": "http",
                    "config_example": {
                        "memorySearch": {
                            "provider": "http",
                            "endpoint": "http://localhost:8000/search"
                        }
                    }
                }
            })
            
        else:
            self._send_response(404, {
                "success": False,
                "error": f"Endpoint not found: {parsed_path.path}"
            })
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                query = data.get('query', '')
                top_k = data.get('top_k', 5)
                
                if not query:
                    self._send_response(400, {
                        "success": False,
                        "error": "Query field 'query' is required in JSON body"
                    })
                    return
                
                result = self.service.search(query, top_k)
                self._send_response(200, result)
                
            except json.JSONDecodeError:
                self._send_response(400, {
                    "success": False,
                    "error": "Invalid JSON in request body"
                })
        else:
            self._send_response(404, {
                "success": False,
                "error": f"Endpoint not found: {self.path}"
            })
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        # Uncomment for debugging:
        # print(f"{self.address_string()} - {format % args}")
        pass


def run_server(port: int = 8000):
    """Run the HTTP server."""
    handler = E5RAGHTTPHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"✅ E5 RAG HTTP Service running on port {port}")
        print(f"📡 OpenClaw configuration:")
        print(json.dumps({
            "memorySearch": {
                "provider": "http",
                "endpoint": f"http://localhost:{port}/search",
                "fallback": "none"
            }
        }, indent=2))
        print("\n🔧 Endpoints:")
        print(f"  http://localhost:{port}/status")
        print(f"  http://localhost:{port}/search?q=your_query")
        print(f"  http://localhost:{port}/search (POST with JSON)")
        print("\n🚀 Service ready for OpenClaw integration!")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="E5 RAG HTTP Service for OpenClaw")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on")
    parser.add_argument("--test", action="store_true", help="Test the service")
    
    args = parser.parse_args()
    
    if args.test:
        # Test the service
        service = MockE5RAGService()
        service.initialize()
        
        print("🧪 Testing E5 RAG HTTP Service:")
        print(f"1. Service stats: {service.get_stats()}")
        print(f"2. Search test: {service.search('OpenClaw system', top_k=2)}")
        print("✅ Test completed successfully")
    else:
        # Run the server
        run_server(args.port)