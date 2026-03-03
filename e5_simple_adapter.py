#!/usr/bin/env python3
"""
Simple E5 Embeddings Adapter for OpenClaw

Provides OpenAI-compatible embeddings endpoint that returns simple,
deterministic embeddings for testing.
"""

import json
import logging
import argparse
from typing import Dict, List, Any
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleEmbeddingsAdapter:
    """Simple embeddings adapter for OpenClaw testing"""
    
    def __init__(self):
        self.stats = {
            "started": datetime.now().isoformat(),
            "requests_served": 0,
            "errors": 0
        }
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate deterministic embedding from text"""
        # Create deterministic hash from text
        text_hash = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        
        # Generate 384-dimensional embedding (like E5-small-v2)
        embedding = []
        for i in range(384):
            # Deterministic value based on hash and position
            val = ((text_hash + i) % 1000) / 1000.0
            embedding.append(float(val))
        
        return embedding
    
    def embed(self, input_text: str, model: str = "e5-small-v2") -> Dict[str, Any]:
        """Generate embeddings in OpenAI format"""
        self.stats["requests_served"] += 1
        
        try:
            # Handle both string and list inputs
            if isinstance(input_text, str):
                texts = [input_text]
            elif isinstance(input_text, list):
                texts = input_text
            else:
                texts = [str(input_text)]
            
            embeddings = []
            for i, text in enumerate(texts):
                embedding = self.generate_embedding(text)
                embeddings.append({
                    "object": "embedding",
                    "embedding": embedding,
                    "index": i
                })
            
            # Estimate token count (rough approximation)
            total_tokens = sum(len(t.split()) for t in texts)
            
            return {
                "object": "list",
                "data": embeddings,
                "model": model,
                "usage": {
                    "prompt_tokens": total_tokens,
                    "total_tokens": total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Embedding error: {e}")
            self.stats["errors"] += 1
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
            "current_time": datetime.now().isoformat()
        }

class SimpleAdapterHandler(BaseHTTPRequestHandler):
    """HTTP handler for simple embeddings adapter"""
    
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
        
        if parsed_path.path == '/health':
            self._handle_health()
        elif parsed_path.path == '/stats':
            self._handle_stats()
        elif parsed_path.path == '/v1/models':
            self._handle_models()
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
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": {
                    "message": f"Not found: {self.path}",
                    "type": "invalid_request_error"
                }
            }).encode())
    
    def _handle_health(self):
        """Handle /health endpoint"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Simple E5 Embeddings Adapter"
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
    
    def _handle_models(self):
        """Handle /v1/models endpoint"""
        import time
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
                }
            ]
        }
        self._set_headers(200)
        self.wfile.write(json.dumps(models, indent=2).encode())
    
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
    
    def log_message(self, format, *args):
        """Custom log message format"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """Main function to run the simple adapter"""
    parser = argparse.ArgumentParser(description='Simple E5 Embeddings Adapter for OpenClaw')
    parser.add_argument('--port', type=int, default=8002, help='Port to listen on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--test', action='store_true', help='Test mode')
    
    args = parser.parse_args()
    
    # Initialize adapter
    adapter = SimpleEmbeddingsAdapter()
    
    if args.test:
        print("🧪 Testing Simple E5 Embeddings Adapter:")
        result = adapter.embed("Test text for embeddings")
        print(f"1. Embedding test: {json.dumps(result, indent=2)[:200]}...")
        print("✅ Test completed")
        return
    
    # Set adapter instance for HTTP handler
    SimpleAdapterHandler.adapter = adapter
    
    # Create and start server
    server_address = (args.host, args.port)
    httpd = HTTPServer(server_address, SimpleAdapterHandler)
    
    logger.info(f"🚀 Starting Simple E5 Embeddings Adapter on {args.host}:{args.port}")
    logger.info("📋 Available endpoints:")
    logger.info("  GET  /v1/models     - List available models")
    logger.info("  POST /v1/embeddings - OpenAI-compatible embeddings")
    logger.info("  GET  /health        - Health check")
    logger.info("  GET  /stats         - Service statistics")
    logger.info("")
    logger.info("🔧 OpenClaw Configuration:")
    logger.info('  "memorySearch": {')
    logger.info('    "provider": "openai",')
    logger.info(f'    "remote": {{')
    logger.info(f'      "apiKey": "sk-simple-adapter",')
    logger.info(f'      "baseUrl": "http://{args.host}:{args.port}/v1"')
    logger.info(f'    }}')
    logger.info('  }')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down Simple E5 Embeddings Adapter")
        httpd.server_close()

if __name__ == '__main__':
    main()