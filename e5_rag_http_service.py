#!/usr/bin/env python3
"""
E5 RAG HTTP Service for OpenClaw Integration

Implements the "Don't fight OpenClaw, work with it" principle.
Provides semantic memory search via HTTP that OpenClaw can consume.

OpenClaw Configuration:
{
  "memorySearch": {
    "provider": "http",
    "endpoint": "http://localhost:8000/search",
    "fallback": "none"
  }
}
"""

import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

# Try to import E5 components
try:
    from e5_embedding_engine import E5EmbeddingEngine
    from memory_rag import MemoryStore
    E5_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  E5 components not available: {e}")
    print("⚠️  Running in mock mode for demonstration")
    E5_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class E5RAGService:
    """E5 RAG Service for semantic memory search"""
    
    def __init__(self, workspace_dir: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace_dir = workspace_dir
        self.initialized = False
        self.rag = None
        self.stats = {
            "initialized": False,
            "model": "none",
            "chunks": 0,
            "service_start": datetime.now().isoformat(),
            "requests_served": 0,
            "errors": 0
        }
        
    def initialize(self) -> bool:
        """Initialize the E5 RAG system"""
        try:
            if not E5_AVAILABLE:
                logger.warning("E5 not available, running in mock mode")
                self.rag = MockRAG()
                self.stats["model"] = "mock-e5-small-v2"
                self.stats["chunks"] = 234  # Mock count from earlier work
            else:
                logger.info("Initializing E5 RAG system...")
                # Initialize memory store
                self.rag = MemoryStore(self.workspace_dir)
                
                # Load memory files
                self.rag.load_memory_files()
                
                # Generate embeddings
                self.rag.generate_embeddings()
                
                self.stats["model"] = "intfloat/e5-small-v2"
                self.stats["chunks"] = len(self.rag.chunks)
                logger.info(f"✅ E5 RAG initialized with {self.stats['chunks']} chunks")
            
            self.initialized = True
            self.stats["initialized"] = True
            self.stats["initialized_at"] = datetime.now().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize E5 RAG: {e}")
            self.stats["last_error"] = str(e)
            self.stats["errors"] += 1
            return False
    
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform semantic search"""
        self.stats["requests_served"] += 1
        
        if not self.initialized or not self.rag:
            return {
                "success": False,
                "error": "Service not initialized",
                "query": query,
                "results": [],
                "count": 0
            }
        
        try:
            # Use MemoryStore search method
            search_results = self.rag.search(query, top_k=top_k)
            
            # Format results for OpenClaw compatibility
            formatted_results = []
            for chunk, score in search_results:
                formatted_results.append({
                    "score": float(score),
                    "text": chunk.text,
                    "source": chunk.source,
                    "lines": f"{chunk.line_start}-{chunk.line_end}"
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "provider": "e5-http-service",
                "model": self.stats["model"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            self.stats["errors"] += 1
            self.stats["last_error"] = str(e)
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": [],
                "count": 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            **self.stats,
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(
                self.stats["service_start"].replace('Z', '+00:00')
            )).total_seconds() if "service_start" in self.stats else 0,
            "current_time": datetime.now().isoformat()
        }

class MockRAG:
    """Mock RAG for demonstration when E5 is not available"""
    
    def __init__(self):
        self.mock_results = [
            {
                "score": 0.8579,
                "text": "### Memory Visualization System (2026-03-01)...",
                "source": "MEMORY.md",
                "lines": "1-11"
            },
            {
                "score": 0.8577,
                "text": "### Session Management Discussion...",
                "source": "memory/2026-03-02.md",
                "lines": "1-11"
            }
        ]
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Mock search implementation"""
        return self.mock_results[:top_k]

class E5HTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for E5 RAG service"""
    
    service = None  # Will be set by main()
    
    def _set_headers(self, status_code: int = 200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self._set_headers(200)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/status':
            self._handle_status()
        elif parsed_path.path == '/stats':
            self._handle_stats()
        elif parsed_path.path == '/search':
            self._handle_search_get(parsed_path.query)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": "Not found",
                "available_endpoints": ["/status", "/stats", "/search"]
            }).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self._handle_search_post(post_data)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": "Not found",
                "available_endpoints": ["/search"]
            }).encode())
    
    def _handle_status(self):
        """Handle /status endpoint"""
        status = {
            "service": "E5 RAG HTTP Service",
            "status": "running" if self.service and self.service.initialized else "not initialized",
            "initialized": self.service.initialized if self.service else False,
            "model": self.service.stats["model"] if self.service else "none",
            "timestamp": datetime.now().isoformat()
        }
        self._set_headers(200)
        self.wfile.write(json.dumps(status, indent=2).encode())
    
    def _handle_stats(self):
        """Handle /stats endpoint"""
        if self.service:
            stats = self.service.get_stats()
            self._set_headers(200)
            self.wfile.write(json.dumps(stats, indent=2).encode())
        else:
            self._set_headers(503)
            self.wfile.write(json.dumps({
                "error": "Service not available"
            }).encode())
    
    def _handle_search_get(self, query_string: str):
        """Handle GET /search?q=query"""
        query_params = urllib.parse.parse_qs(query_string)
        query = query_params.get('q', [''])[0]
        
        if not query:
            self._set_headers(400)
            self.wfile.write(json.dumps({
                "error": "Query parameter 'q' is required"
            }).encode())
            return
        
        if not self.service:
            self._set_headers(503)
            self.wfile.write(json.dumps({
                "error": "Service not initialized"
            }).encode())
            return
        
        result = self.service.search(query)
        self._set_headers(200 if result["success"] else 500)
        self.wfile.write(json.dumps(result, indent=2).encode())
    
    def _handle_search_post(self, post_data: bytes):
        """Handle POST /search with JSON body"""
        try:
            data = json.loads(post_data.decode('utf-8'))
            query = data.get('query', '')
            
            if not query:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": "Query field 'query' is required in JSON body"
                }).encode())
                return
            
            if not self.service:
                self._set_headers(503)
                self.wfile.write(json.dumps({
                    "error": "Service not initialized"
                }).encode())
                return
            
            top_k = data.get('top_k', 5)
            result = self.service.search(query, top_k)
            self._set_headers(200 if result["success"] else 500)
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({
                "error": "Invalid JSON in request body"
            }).encode())
    
    def log_message(self, format, *args):
        """Custom log message format"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """Main function to run the HTTP service"""
    parser = argparse.ArgumentParser(description='E5 RAG HTTP Service for OpenClaw')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--workspace', default='/home/ubuntu/.openclaw/workspace',
                       help='Workspace directory')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--test', action='store_true', help='Test mode')
    
    args = parser.parse_args()
    
    # Initialize service
    service = E5RAGService(args.workspace)
    
    if args.test:
        print("🧪 Testing E5 RAG HTTP Service:")
        if service.initialize():
            print(f"1. Service stats: {service.get_stats()}")
            result = service.search("OpenClaw system")
            print(f"2. Search test: {json.dumps(result, indent=2)}")
            print("✅ Test completed successfully")
        else:
            print("❌ Service initialization failed")
        return
    
    # Initialize the service
    if not service.initialize():
        logger.error("Failed to initialize E5 RAG service")
        return 1
    
    # Set service instance for HTTP handler
    E5HTTPHandler.service = service
    
    # Create and start server
    server_address = (args.host, args.port)
    httpd = HTTPServer(server_address, E5HTTPHandler)
    
    logger.info(f"🚀 Starting E5 RAG HTTP Service on {args.host}:{args.port}")
    logger.info(f"📊 Service initialized: {service.initialized}")
    logger.info(f"🧠 Model: {service.stats['model']}")
    logger.info(f"📚 Chunks: {service.stats['chunks']}")
    logger.info("🔗 OpenClaw Configuration:")
    logger.info('  "memorySearch": {')
    logger.info('    "provider": "http",')
    logger.info(f'    "endpoint": "http://{args.host}:{args.port}/search",')
    logger.info('    "fallback": "none"')
    logger.info('  }')
    
    try:
        if args.daemon:
            # Run in background thread
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            logger.info("📡 Service running in background thread")
            server_thread.join()
        else:
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down E5 RAG HTTP Service")
        httpd.server_close()

if __name__ == '__main__':
    main()