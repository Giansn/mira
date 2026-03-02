#!/usr/bin/env python3
"""
Basic usage example for Perplexity-Inspired module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perplexity_inspired import PerplexityInspired, InformationSource, SourceType
import datetime


def main():
    """Demonstrate basic usage of Perplexity-Inspired features."""
    
    print("=== Perplexity-Inspired Module Demo ===\n")
    
    # Initialize
    pi = PerplexityInspired()
    
    # Example queries to analyze
    queries = [
        "What are the latest developments in quantum computing?",
        "Explain the history of artificial intelligence",
        "How does photosynthesis work in plants?",
        "Current weather in New York City",
        "Compare Python and JavaScript for web development"
    ]
    
    for query in queries:
        print(f"\n--- Analyzing Query: '{query}' ---")
        
        # Analyze query
        analysis = pi.analyze_query(query)
        
        print(f"Key terms: {analysis.key_terms}")
        print(f"Time sensitivity: {analysis.time_sensitivity}")
        print(f"Requires web search: {analysis.requires_web_search}")
        print(f"Information needs: {analysis.information_needs}")
        print(f"Potential sources: {[s.value for s in analysis.potential_sources]}")
        
        # Create mock sources based on query type
        mock_sources = create_mock_sources(query, analysis)
        for source in mock_sources:
            pi.add_source(source)
        
        # Synthesize response
        response = pi.synthesize_response(analysis, mock_sources)
        
        print(f"\nSynthesized Response (confidence: {response.confidence:.2f}):")
        print(f"{response.content[:200]}...")
        
        if response.contradictions:
            print(f"Contradictions identified: {response.contradictions}")
        
        if response.knowledge_gaps:
            print(f"Knowledge gaps: {response.knowledge_gaps}")
    
    # Demonstrate citation formatting
    print("\n=== Citation Formatting Example ===")
    
    # Create a sample source
    sample_source = InformationSource(
        id="sample1",
        type=SourceType.ACADEMIC,
        content="This study demonstrates significant improvements in machine learning accuracy.",
        url="https://arxiv.org/abs/2501.12345",
        title="Advances in Deep Learning Architectures",
        author="Smith et al.",
        date=datetime.datetime(2025, 6, 15),
        credibility_score=0.9
    )
    
    print(f"\nSource citation: {sample_source.to_citation()}")
    
    # Save analysis history
    pi.save_analysis("/tmp/perplexity_analysis.json")
    print("\nAnalysis saved to /tmp/perplexity_analysis.json")


def create_mock_sources(query: str, analysis) -> list:
    """Create mock sources for demonstration purposes."""
    sources = []
    
    # Base on query content
    if "quantum" in query.lower():
        sources.append(InformationSource(
            id="quantum1",
            type=SourceType.NEWS,
            content="Researchers achieved quantum supremacy with 127-qubit processor.",
            url="https://example.com/quantum-supremacy",
            title="Quantum Supremacy Milestone Reached",
            date=datetime.datetime(2025, 10, 1),
            credibility_score=0.8
        ))
        sources.append(InformationSource(
            id="quantum2",
            type=SourceType.ACADEMIC,
            content="New error correction methods improve quantum computation stability.",
            url="https://arxiv.org/abs/quantum-error",
            title="Advances in Quantum Error Correction",
            date=datetime.datetime(2025, 8, 15),
            credibility_score=0.9
        ))
    
    elif "history" in query.lower() and "artificial intelligence" in query.lower():
        sources.append(InformationSource(
            id="ai1",
            type=SourceType.ACADEMIC,
            content="AI research began in the 1950s with the Dartmouth Conference.",
            url="https://example.com/ai-history",
            title="The Dawn of Artificial Intelligence",
            date=datetime.datetime(2020, 5, 10),
            credibility_score=0.85
        ))
    
    elif "photosynthesis" in query.lower():
        sources.append(InformationSource(
            id="bio1",
            type=SourceType.ACADEMIC,
            content="Photosynthesis converts light energy to chemical energy in plants.",
            url="https://example.com/photosynthesis",
            title="Plant Biology: Photosynthesis",
            date=datetime.datetime(2019, 3, 20),
            credibility_score=0.9
        ))
    
    else:
        # Generic source
        sources.append(InformationSource(
            id="generic1",
            type=SourceType.WEB,
            content=f"Information about {query} from various online sources.",
            url="https://example.com/info",
            title=f"Overview: {query}",
            date=datetime.datetime(2024, 1, 1),
            credibility_score=0.7
        ))
    
    return sources


if __name__ == "__main__":
    main()