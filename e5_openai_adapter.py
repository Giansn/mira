#!/usr/bin/env python3
"""
E5 to OpenAI Embeddings API Adapter

Converts E5 RAG service responses to OpenAI-compatible format for OpenClaw integration.

OpenAI Embeddings API format:
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ],
  "model": "text-embedding-3-small",
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}

Our E5 service returns:
{
  "success": true,
  "query": "query",
  "results": [
    {
      "score": 0.85,
      "text": "memory text",
      "source": "MEMORY.md",
      "lines": "1-10"
    }
  ]
}

We need to:
1. Accept OpenAI-style requests
2. Convert to E5 query
3. Convert E5 results back to OpenAI format
"""

import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import requests
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class E5OpenAIAdapter:
    """Adapter between OpenAI Embeddings API and E5 RAG service"""
    
    def __init__(self, e5_endpoint: str = "http://localhost:8000"):
        self.e5_endpoint = e5_endpoint
        self.stats = {
            "started": datetime.now().isoformat(),
            "requests_served": 0,
            "errors": 0,
            "last_error": None
        }
    
    def embed(self, input_text: str, model: str = "e5-small-v2") -> Dict[str, Any]:
        """Convert OpenAI embeddings request to E5 search"""
        self.stats["requests_served"] += 1
        
        try:
            # For embeddings, we need to return vector embeddings
            # But E5 service only returns search results
            # We'll create mock embeddings based on search results
            
            # First, get search results from E5
            search_url = f"{self.e5_endpoint}/search"
            params = {"q": input_text}
            
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            search_results = response.json()
            
            if not search_results.get("success", False):
                raise ValueError(f"E5 search failed: {search_results.get('error', 'Unknown error')}")
            
            # Create mock embeddings based on search results
            # In a real implementation, we'd call E5 embedding endpoint
            # For now, create deterministic mock embeddings
            results = search_results.get("results", [])
            
            # Generate mock embeddings (384 dimensions like E5-small-v2)
            embeddings = []
            for i, result in enumerate(results[:10]):  # Limit to 10 results
                # Create deterministic embedding based on score and text hash
                score = result.get("score", 0.5)
                text = result.get("text", "")
                
                # Simple deterministic embedding generation
                embedding = []
                for j in range(384):
                    # Create deterministic value based on score, text, and position
                    val = (score * 100 + hash(text) % 100 + j) % 100 / 100.0
                    embedding.append(val)
                
                embeddings.append({
                    "object": "embedding",
                    "embedding": embedding,
                    "index": i
                })
            
            # If no results, return empty embedding
            if not embeddings:
                embeddings.append({
                    "object": "embedding",
                    "embedding": [0.0] * 384,
                    "index": 0
                })
            
            return {
                "object": "list",
                "data": embeddings,
                "model": model,
                "usage": {
                    "prompt_tokens": len(input_text.split()),
                    "total_tokens": len(input_text.split())
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Embedding error: {e}")
            self.stats["errors"] += 1
            self.stats["last_error"] = str(e)
            
            # Return error in OpenAI format
            return {
                "error": {
                    "message": str(e),
                    "type": "api_error",
                    "code": "embedding_failed"
                }
            }
    
    def search_to_embeddings(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Alternative: Convert search results to embeddings format"""
        try:
            search_url = f"{self.e5_endpoint}/search"
            params = {"q": query}
            
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            search_results = response.json()
            
            if not search_results.get("success", False):
                raise ValueError(f"E5 search failed: {search_results.get('error', 'Unknown error')}")
            
            # Return search results in a structured format
            results = search_results.get("results", [])[:top_k]
            
            return {
                "object": "list",
                "data": results,
                "model": "e5-search-adapter",
                "query": query,
                "count": len(results),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return {
                "error": {
                    "message": str(e),
                    "type": "api_error"
                }
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            **self.stats,
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(
                self.stats["started"]
            )).total_seconds(),
            "current_time": datetime.now().isoformat(),
            "e5_endpoint": self.e5_endpoint
        }

class OpenAIAdapterHandler(BaseHTTPRequestHandler):
    """HTTP handler for OpenAI-compatible API"""
    
    adapter = None  # Will be set by main()
    
    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self._set_headers(200)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/v1/models':
            self._handle_models()
        elif parsed_path.path == '/health':
            self._handle_health()
        elif parsed_path.path == '/stats':
            self._handle_stats()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": {
                    "message": f"Not found: {parsed_path.path}",
                    "type": "invalid_request_error"
                }
            }).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/v1/embeddings':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self._handle_embeddings(post_data)
        elif self.path == '/v1/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self._handle_search(post_data)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": {
                    "message": f"Not found: {self.path}",
                    "type": "invalid_request_error"
                }
            }).encode())
    
    def _handle_models(self):
        """Handle /v1/models endpoint"""
        models = {
            "object": "list",
            "data": [
                {
                    "id": "e5-small-v2",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "intfloat",
                    "permission": [],
                    "root": "e5-small-v2",
                    "parent": None
                },
                {
                    "id": "e5-search-adapter",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "openclaw-adapter",
                    "permission": [],
                    "root": "e5-search-adapter",
                    "parent": None
                }
            ]
        }
        self._set_headers(200)
        self.wfile.write(json.dumps(models, indent=2).encode())
    
    def _handle_health(self):
        """Handle /health endpoint"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "E5 OpenAI Adapter",
            "e5_endpoint": self.adapter.e5_endpoint if self.adapter else "not set"
        }
        self._set_headers(200)
        self.wfile.write(json.dumps(health, indent=2).encode())
    
    def _handle_stats(self):
        """Handle /stats endpoint"""
        if self.adapter:
            stats = self.adapter.get_stats()
            self._set_headers(200)
            self.wfile.write(json.dumps(stats, indent=2).encode())
        else:
            self._set_headers(503)
            self.wfile.write(json.dumps({
                "error": "Adapter not initialized"
            }).encode())
    
    def _handle_embeddings(self, post_data: bytes):
        """Handle /v1/embeddings endpoint"""
        try:
            data = json.loads(post_data.decode('utf-8'))
            input_text = data.get('input', '')
            model = data.get('model', 'e5-small-v2')
            
            if not input_text:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": {
                        "message": "Missing required field: input",
                        "type": "invalid_request_error"
                    }
                }).encode())
                return
            
            if not self.adapter:
                self._set_headers(503)
                self.wfile.write(json.dumps({
                    "error": {
                        "message": "Service not initialized",
                        "type": "internal_server_error"
                    }
                }).encode())
                return
            
            result = self.adapter.embed(input_text, model)
            
            if "error" in result:
                self._set_headers(500)
                self.wfile.write(json.dumps(result).encode())
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps(result, indent=2).encode())
            
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({
                "error": {
                    "message": "Invalid JSON in request body",
                    "type": "invalid_request_error"
                }
            }).encode())
        except Exception as e:
            logger.error(f"❌ Embeddings handler error: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": {
                    "message": str(e),
                    "type": "internal_server_error"
                }
            }).encode())
    
    def _handle_search(self, post_data: bytes):
        """Handle /v1/search endpoint (custom endpoint for semantic search)"""
        try:
            data = json.loads(post_data.decode('utf-8'))
            query = data.get('query', '')
            top_k = data.get('top_k', 5)
            
            if not query:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": {
                        "message": "Missing required field: query",
                        "type": "invalid_request_error"
                    }
                }).encode())
                return
            
            if not self.adapter:
                self._set_headers(503)
                self.wfile.write(json.dumps({
                    "error": {
                        "message": "Service not initialized",
                        "type": "internal_server_error"
                    }
                }).encode())
                return
            
            result = self.adapter.search_to_embeddings(query, top_k)
            
            if "error" in result:
                self._set_headers(500)
                self.wfile.write(json.dumps(result).encode())
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps(result, indent=2).encode())
            
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({
                "error": {
                    "message": "Invalid JSON in request body",
                    "type": "invalid_request_error"
                }
            }).encode())
        except Exception as e:
            logger.error(f"❌ Search handler error: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": {
                    "message": str(e),
                    "type": "internal_server_error"
                }
            }).encode())
    
    def log_message(self, format, *args):
        """Custom log message format"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """Main function to run the adapter service"""
    parser = argparse.ArgumentParser(description='E5 OpenAI Adapter for OpenClaw')
    parser.add_argument('--port', type=int, default=8001, help='Port to listen on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--e5-endpoint', default='http://localhost:8000',
                       help='E5 RAG service endpoint')
    parser.add_argument('--test', action='store_true', help='Test mode')
    
    args = parser.parse_args()
    
    # Initialize adapter
    adapter = E5OpenAIAdapter(args.e5_endpoint)
    
    if args.test:
        print("🧪 Testing E5 OpenAI Adapter:")
        print(f"1. E5 endpoint: {args.e5_endpoint}")
        
        # Test health check
        try:
            health_url = f"{args.e5_endpoint}/status"
            response = requests.get(health_url, timeout=5)
            print(f"2. E5 service health: {response.status_code}")
        except Exception as e:
            print(f"2. E5 service health: ❌ {e}")
        
        # Test search
        result = adapter.search_to_embeddings("OpenClaw system", top_k=3)
        print(f"3. Search test: {json.dumps(result, indent=2)[:200]}...")
        
        print("✅ Test completed")
        return
    
    # Set adapter instance for HTTP handler
    OpenAIAdapterHandler.adapter = adapter
    
    # Create and start server
    server_address = (args.host, args.port)
    httpd = HTTPServer(server_address, OpenAIAdapterHandler)
    
    logger.info(f"🚀 Starting E5 OpenAI Adapter on {args.host}:{args.port}")
    logger.info(f"🔗 E5 endpoint: {args.e5_endpoint}")
    logger.info("📋 Available endpoints:")
    logger.info("  GET  /v1/models     - List available models")
    logger.info("  POST /v1/embeddings - OpenAI-compatible embeddings")
    logger.info("  POST /v1/search     - Semantic search (custom)")
    logger.info("  GET  /health        - Health check")
    logger.info("  GET  /stats         - Service statistics")
    logger.info("")
    logger.info("🔧 OpenClaw Configuration:")
    logger.info('  "memorySearch": {')
    logger.info('    "provider": "openai",')
    logger.info(f'    "remote": {{')
    logger.info(f'      "apiKey": "sk-e5-adapter",')
    logger.info(f'      "baseUrl": "http://{args.host}:{args.port}/v1"')
    logger.info(f'    }}')
    logger.info('  }')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down E5 OpenAI Adapter")
        httpd.server_close()

if __name__ == '__main__':
    main()