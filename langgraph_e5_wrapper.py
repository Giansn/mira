#!/usr/bin/env python3
"""
LangGraph E5 RAG Wrapper
Orchestrates E5 semantic search with LangGraph workflows
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️  LangGraph not available. Install with: pip install langgraph")

try:
    from e5_rag_service import E5RAGService
    E5_AVAILABLE = True
except ImportError:
    E5_AVAILABLE = False
    print("⚠️  E5 RAG service not available")

try:
    from enhanced_memory_graph import EnhancedMemoryGraph
    MEMORY_GRAPH_AVAILABLE = True
except ImportError:
    MEMORY_GRAPH_AVAILABLE = False
    print("⚠️  EnhancedMemoryGraph not available")


class LangGraphE5State(TypedDict):
    """State for LangGraph E5 workflow."""
    query: Optional[str]
    user_context: Optional[str]
    e5_results: List[Dict[str, Any]]
    graph_results: List[Dict[str, Any]]
    enhanced_results: List[Dict[str, Any]]
    summary: Optional[str]
    recommendations: List[str]
    workflow_step: str
    error: Optional[str]


class LangGraphE5Wrapper:
    """LangGraph wrapper for E5 RAG with workflow orchestration."""
    
    def __init__(self):
        self.e5_service = None
        self.memory_graph = None
        self.workflow_graph = None
        
        # Initialize services
        self._initialize_services()
        
        # Build workflow graph
        if LANGGRAPH_AVAILABLE:
            self._build_workflow_graph()
    
    def _initialize_services(self):
        """Initialize E5 and memory graph services."""
        # Initialize E5 service
        if E5_AVAILABLE:
            try:
                self.e5_service = E5RAGService()
                init_result = self.e5_service.initialize()
                if init_result.get("success"):
                    print("✅ E5 RAG service initialized")
                else:
                    print(f"⚠️  E5 service initialization: {init_result.get('error')}")
            except Exception as e:
                print(f"⚠️  Failed to initialize E5 service: {e}")
        
        # Initialize memory graph
        if MEMORY_GRAPH_AVAILABLE:
            try:
                self.memory_graph = EnhancedMemoryGraph()
                print("✅ EnhancedMemoryGraph initialized")
                print(f"   Memories: {len(self.memory_graph.memories)}")
                print(f"   Tags: {len(self.memory_graph.tag_index)}")
            except Exception as e:
                print(f"⚠️  Failed to initialize memory graph: {e}")
    
    def _build_workflow_graph(self):
        """Build LangGraph workflow for E5 RAG orchestration."""
        if not LANGGRAPH_AVAILABLE:
            return
        
        print("🔧 Building LangGraph workflow...")
        
        # Define workflow nodes
        def query_analysis_node(state: LangGraphE5State) -> LangGraphE5State:
            """Analyze query and determine search strategy."""
            state["workflow_step"] = "query_analysis"
            
            query = state.get("query", "")
            if not query:
                state["error"] = "No query provided"
                return state
            
            # Simple query analysis
            query_lower = query.lower()
            
            # Determine search strategy based on query
            if any(word in query_lower for word in ["how", "what", "why", "when", "where"]):
                state["recommendations"].append("Question detected - using semantic search")
            elif len(query.split()) > 3:
                state["recommendations"].append("Complex query - using E5 semantic search")
            else:
                state["recommendations"].append("Simple query - using keyword + semantic")
            
            return state
        
        def e5_semantic_search_node(state: LangGraphE5State) -> LangGraphE5State:
            """Perform E5 semantic search."""
            state["workflow_step"] = "e5_semantic_search"
            
            if not self.e5_service or not self.e5_service.initialized:
                state["error"] = "E5 service not available"
                return state
            
            query = state.get("query", "")
            if not query:
                return state
            
            try:
                result = self.e5_service.search(query, top_k=10)
                if result.get("success"):
                    state["e5_results"] = result.get("results", [])
                    state["recommendations"].append(f"E5 found {len(state['e5_results'])} results")
                else:
                    state["error"] = f"E5 search failed: {result.get('error')}"
            except Exception as e:
                state["error"] = f"E5 search error: {str(e)}"
            
            return state
        
        def memory_graph_analysis_node(state: LangGraphE5State) -> LangGraphE5State:
            """Analyze results using memory graph."""
            state["workflow_step"] = "memory_graph_analysis"
            
            if not self.memory_graph:
                return state
            
            # Use memory graph to find related content
            query = state.get("query", "")
            if not query:
                return state
            
            try:
                # Get related memories from graph
                related = []
                for memory in self.memory_graph.memories.values():
                    if query.lower() in memory.content.lower():
                        related.append(memory.to_dict())
                
                state["graph_results"] = related
                if related:
                    state["recommendations"].append(f"Memory graph found {len(related)} related entries")
            except Exception as e:
                state["error"] = f"Memory graph analysis error: {str(e)}"
            
            return state
        
        def result_enhancement_node(state: LangGraphE5State) -> LangGraphE5State:
            """Enhance and combine results."""
            state["workflow_step"] = "result_enhancement"
            
            # Combine E5 and graph results
            enhanced = []
            seen_ids = set()
            
            # Add E5 results
            for result in state.get("e5_results", []):
                result_id = result.get("id", "")
                if result_id and result_id not in seen_ids:
                    enhanced.append({
                        **result,
                        "source": "e5_semantic",
                        "priority": 1  # E5 results get higher priority
                    })
                    seen_ids.add(result_id)
            
            # Add graph results
            for result in state.get("graph_results", []):
                result_id = result.get("id", "")
                if result_id and result_id not in seen_ids:
                    enhanced.append({
                        **result,
                        "source": "memory_graph",
                        "priority": 2
                    })
                    seen_ids.add(result_id)
            
            # Sort by priority and score
            enhanced.sort(key=lambda x: (
                x.get("priority", 3),
                -x.get("score", 0) if x.get("score") else 0
            ))
            
            state["enhanced_results"] = enhanced
            state["recommendations"].append(f"Enhanced to {len(enhanced)} total results")
            
            return state
        
        def summary_generation_node(state: LangGraphE5State) -> LangGraphE5State:
            """Generate summary of findings."""
            state["workflow_step"] = "summary_generation"
            
            enhanced = state.get("enhanced_results", [])
            query = state.get("query", "")
            
            if not enhanced:
                state["summary"] = f"No results found for query: '{query}'"
                return state
            
            # Generate summary
            lines = [f"## Search Results for: '{query}'"]
            lines.append(f"Total results: {len(enhanced)}")
            
            # Group by source
            sources = {}
            for result in enhanced:
                source = result.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
            
            if sources:
                lines.append("\n**Results by source:**")
                for source, count in sources.items():
                    lines.append(f"- {source}: {count}")
            
            # Top 3 results
            if len(enhanced) >= 3:
                lines.append("\n**Top 3 results:**")
                for i, result in enumerate(enhanced[:3]):
                    score = result.get("score", 0)
                    source = result.get("source", "unknown")
                    preview = result.get("text", "")[:100]
                    lines.append(f"{i+1}. [{source}] Score: {score:.3f} - {preview}...")
            
            state["summary"] = "\n".join(lines)
            return state
        
        # Build the graph
        workflow = StateGraph(LangGraphE5State)
        
        # Add nodes
        workflow.add_node("query_analysis", query_analysis_node)
        workflow.add_node("e5_search", e5_semantic_search_node)
        workflow.add_node("graph_analysis", memory_graph_analysis_node)
        workflow.add_node("enhancement", result_enhancement_node)
        workflow.add_node("summary", summary_generation_node)
        
        # Define workflow
        workflow.set_entry_point("query_analysis")
        
        # Main flow
        workflow.add_edge("query_analysis", "e5_search")
        workflow.add_edge("e5_search", "graph_analysis")
        workflow.add_edge("graph_analysis", "enhancement")
        workflow.add_edge("enhancement", "summary")
        workflow.add_edge("summary", END)
        
        # Compile
        self.workflow_graph = workflow.compile()
        print("✅ LangGraph workflow built and compiled")
    
    def search(self, query: str, user_context: str = "") -> Dict[str, Any]:
        """Execute LangGraph workflow for search."""
        if not self.workflow_graph:
            return {
                "success": False,
                "error": "LangGraph workflow not available",
                "query": query
            }
        
        # Initial state
        initial_state: LangGraphE5State = {
            "query": query,
            "user_context": user_context,
            "e5_results": [],
            "graph_results": [],
            "enhanced_results": [],
            "summary": None,
            "recommendations": [],
            "workflow_step": "start",
            "error": None
        }
        
        try:
            # Execute workflow
            result = self.workflow_graph.invoke(initial_state)
            
            # Prepare response
            response = {
                "success": True,
                "query": query,
                "workflow": "langgraph_e5_orchestration",
                "steps_completed": result.get("workflow_step", "unknown"),
                "summary": result.get("summary"),
                "recommendations": result.get("recommendations", []),
                "total_results": len(result.get("enhanced_results", [])),
                "results": result.get("enhanced_results", []),
                "sources": {
                    "e5_semantic": len(result.get("e5_results", [])),
                    "memory_graph": len(result.get("graph_results", []))
                }
            }
            
            if result.get("error"):
                response["warning"] = result["error"]
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}",
                "query": query
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = {
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "e5_available": E5_AVAILABLE and self.e5_service and self.e5_service.initialized,
            "memory_graph_available": MEMORY_GRAPH_AVAILABLE and self.memory_graph,
            "workflow_built": self.workflow_graph is not None
        }
        
        if self.e5_service and self.e5_service.initialized:
            e5_stats = self.e5_service.get_stats()
            stats["e5"] = e5_stats
        
        if self.memory_graph:
            stats["memory_graph"] = {
                "memories": len(self.memory_graph.memories),
                "tags": len(self.memory_graph.tag_index),
                "keywords": len(self.memory_graph.keyword_index)
            }
        
        return stats
    
    def add_memory(self, content: str, tags: List[str] = None) -> Dict[str, Any]:
        """Add new memory to the system."""
        if not self.memory_graph:
            return {
                "success": False,
                "error": "Memory graph not available"
            }
        
        try:
            # This would use the memory graph's ingestion capabilities
            # For now, return success
            return {
                "success": True,
                "message": "Memory addition would be handled by EnhancedMemoryGraph",
                "content_length": len(content),
                "tags": tags or []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to add memory: {str(e)}"
            }


# HTTP Service Wrapper
class LangGraphE5HTTPService:
    """HTTP service for LangGraph E5 wrapper."""
    
    def __init__(self, host='localhost', port=8001):
        self.host = host
        self.port = port
        self.wrapper = None
        self.server = None
    
    def start(self):
        """Start the HTTP service."""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse
        import threading
        
        # Initialize wrapper
        self.wrapper = LangGraphE5Wrapper()
        
        class Handler(BaseHTTPRequestHandler):
            wrapper = self.wrapper
            
            def _json_response(self, status, data):
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
            
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path
                
                if path == '/':
                    self._json_response(200, {
                        "service": "LangGraph E5 Wrapper",
                        "endpoints": ["/search", "/stats", "/health"]
                    })
                elif path == '/stats':
                    stats = self.wrapper.get_stats() if self.wrapper else {}
                    self._json_response(200, stats)
                elif path == '/health':
                    self._json_response(200, {"status": "healthy"})
                elif path == '/search':
                    # GET search with query parameter
                    query = urllib.parse.parse_qs(parsed.query).get('q', [''])[0]
                    if query:
                        result = self.wrapper.search(query) if self.wrapper else {
                            "error": "Wrapper not initialized"
                        }
                        self._json_response(200, result)
                    else:
                        self._json_response(400, {"error": "Missing query parameter 'q'"})
                else:
                    self._json_response(404, {"error": "Endpoint not found"})
            
            def do_POST(self):
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path
                
                if path == '/search':
                    # POST search with JSON body
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        data = json.loads(post_data.decode('utf-8'))
                        query = data.get('query', '')
                        
                        if query:
                            result = self.wrapper.search(query) if self.wrapper else {
                                "error": "Wrapper not initialized"
                            }
                            self._json_response(200, result)
                        else:
                            self._json_response(400, {"error": "Missing 'query' field"})
                    except:
                        self._json_response(400, {"error": "Invalid JSON"})
                else:
                    self._json_response(404, {"error": "Endpoint not found"})
        
        self.server = HTTPServer((self.host, self.port), Handler)
        
        print(f"🚀 LangGraph E5 HTTP Service starting on http://{self.host}:{self.port}")
        print(f"   Wrapper initialized: {self.wrapper is not None}")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Service stopped")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LangGraph E5 RAG Wrapper")
    parser.add_argument("--http", action="store_true", help="Start HTTP service")
    parser.add_argument("--host", default="localhost", help="HTTP host")
    parser.add_argument("--port", type=int, default=8001, help="HTTP port")
    parser.add_argument("--search", help="Test search query")
    
    args = parser.parse_args()
    
    if args.http:
        service = LangGraphE5HTTPService(args.host, args.port)
        service.start()
    elif args.search:
        wrapper = LangGraphE5Wrapper()
        result = wrapper.search(args.search)
        print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        wrapper = LangGraphE5Wrapper()
        
        print("🧠 LangGraph E5 RAG Wrapper")
        print("=" * 50)
        
        stats = wrapper.get_stats()
        print("System Status:")
        print(f"  LangGraph: {'✅' if stats['langgraph_available'] else '❌'}")
        print(f"  E5 Service: {'✅' if stats['e5_available'] else '❌'}")
        print(f"  Memory Graph: {'✅' if stats['memory_graph_available'] else '❌'}")
        print(f"  Workflow: {'✅' if stats['workflow_built'] else '❌'}")
        
        if stats.get("e5"):
            print(f"\nE5 Stats:")
            print(f"  Chunks: {stats['e5'].get('chunks', 'unknown')}")
        
        if stats.get("memory_graph"):
            print(f"\nMemory Graph Stats:")
            print(f"  Memories: {stats['memory_graph'].get('memories', 0)}")
            print(f"  Tags: {stats['memory_graph'].get('tags', 0)}")
            print(f"  Keywords: {stats['memory_graph'].get('keywords', 0)}")
        
        print("\nUsage:")
        print("  python3 langgraph_e5_wrapper.py --search 'your query'")
        print("  python3 langgraph_e5_wrapper.py --http --port 8001")
        print("\nExample workflow:")
        print("  1. Query analysis → 2. E5 semantic search → 3. Memory graph analysis")
        print("  4. Result enhancement → 5. Summary generation")


if __name__ == "__main__":
    main()