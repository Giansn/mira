"""
Perplexity-Inspired Module
Implements features inspired by Perplexity AI's approach to information retrieval and synthesis.
"""

import re
import json
import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class InformationRecency(Enum):
    """Classification of information recency."""
    CURRENT = "current"  # Within last 6 months
    RECENT = "recent"   # 6 months to 2 years
    HISTORICAL = "historical"  # More than 2 years
    TIMELESS = "timeless"  # Not time-sensitive


class SourceType(Enum):
    """Types of information sources."""
    WEB = "web"
    ACADEMIC = "academic"
    NEWS = "news"
    OFFICIAL = "official"
    USER = "user"
    MEMORY = "memory"


@dataclass
class InformationSource:
    """Represents a source of information with metadata."""
    id: str
    type: SourceType
    content: str
    url: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[datetime.datetime] = None
    credibility_score: float = 0.5  # 0.0 to 1.0
    
    def to_citation(self) -> str:
        """Convert source to citation format."""
        parts = []
        if self.title:
            parts.append(f'"{self.title}"')
        if self.author:
            parts.append(f"by {self.author}")
        if self.date:
            parts.append(f"({self.date.strftime('%Y-%m-%d')})")
        if self.url:
            parts.append(f"[{self.url}]")
        return " ".join(parts) if parts else f"Source: {self.id}"


@dataclass
class QueryAnalysis:
    """Analysis of a user query."""
    original_query: str
    key_terms: List[str]
    information_needs: List[str]
    time_sensitivity: InformationRecency
    complexity_level: int  # 1-5
    requires_web_search: bool
    potential_sources: List[SourceType] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_query": self.original_query,
            "key_terms": self.key_terms,
            "information_needs": self.information_needs,
            "time_sensitivity": self.time_sensitivity.value,
            "complexity_level": self.complexity_level,
            "requires_web_search": self.requires_web_search,
            "potential_sources": [s.value for s in self.potential_sources]
        }


@dataclass
class SynthesizedResponse:
    """A response synthesized from multiple sources."""
    content: str
    sources: List[InformationSource]
    confidence: float  # 0.0 to 1.0
    recency: InformationRecency
    contradictions: List[str] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    
    def with_citations(self) -> str:
        """Return content with inline citations."""
        if not self.sources:
            return self.content
        
        # Simple citation format: [1], [2], etc.
        cited_content = self.content
        for i, source in enumerate(self.sources, 1):
            # Add citation markers (simplified)
            pass  # Implementation would depend on content structure
        
        # Add source list at the end
        source_list = "\n\n**Sources:**\n"
        for i, source in enumerate(self.sources, 1):
            source_list += f"{i}. {source.to_citation()}\n"
        
        return cited_content + source_list


class PerplexityInspired:
    """Main class implementing Perplexity-inspired features."""
    
    def __init__(self):
        self.sources_db: Dict[str, InformationSource] = {}
        self.query_history: List[QueryAnalysis] = []
        
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze a user query to determine information needs and search strategy.
        
        Args:
            query: The user's query string
            
        Returns:
            QueryAnalysis object with analysis results
        """
        # Extract key terms (simple implementation)
        key_terms = self._extract_key_terms(query)
        
        # Determine time sensitivity
        time_sensitivity = self._assess_time_sensitivity(query, key_terms)
        
        # Determine if web search is needed
        requires_web_search = self._requires_web_search(query, key_terms)
        
        # Identify potential source types
        potential_sources = self._identify_potential_sources(query, key_terms)
        
        # Estimate complexity (simple heuristic)
        complexity_level = min(5, max(1, len(key_terms) // 2))
        
        # Identify information needs
        information_needs = self._identify_information_needs(query, key_terms)
        
        analysis = QueryAnalysis(
            original_query=query,
            key_terms=key_terms,
            information_needs=information_needs,
            time_sensitivity=time_sensitivity,
            complexity_level=complexity_level,
            requires_web_search=requires_web_search,
            potential_sources=potential_sources
        )
        
        self.query_history.append(analysis)
        return analysis
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query."""
        # Remove common words and punctuation
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = re.findall(r'\b\w+\b', query.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]
    
    def _assess_time_sensitivity(self, query: str, key_terms: List[str]) -> InformationRecency:
        """Assess how time-sensitive the query is."""
        time_indicators = {
            "current", "latest", "recent", "new", "today", "now", "2026", "2025", "2024",
            "update", "breaking", "announced", "released"
        }
        
        historical_indicators = {
            "history", "historical", "past", "formerly", "origin", "invented", "founded",
            "century", "decade", "ancient"
        }
        
        query_lower = query.lower()
        
        # Check for time indicators
        if any(indicator in query_lower for indicator in time_indicators):
            return InformationRecency.CURRENT
        elif any(indicator in query_lower for indicator in historical_indicators):
            return InformationRecency.HISTORICAL
        elif any(term.isdigit() and len(term) == 4 for term in key_terms):  # Year mentions
            year = int([t for t in key_terms if t.isdigit() and len(t) == 4][0])
            current_year = datetime.datetime.now().year
            if current_year - year <= 2:
                return InformationRecency.CURRENT
            else:
                return InformationRecency.HISTORICAL
        
        # Default based on topic
        timeless_topics = {"philosophy", "mathematics", "physics", "theory", "principle"}
        if any(topic in query_lower for topic in timeless_topics):
            return InformationRecency.TIMELESS
        
        return InformationRecency.RECENT
    
    def _requires_web_search(self, query: str, key_terms: List[str]) -> bool:
        """Determine if web search is likely needed."""
        # Queries about current events, specific facts, or technical details likely need web
        needs_web_indicators = {
            "news", "update", "statistics", "data", "study", "research", "report",
            "article", "website", "online", "internet", "web"
        }
        
        query_lower = query.lower()
        if any(indicator in query_lower for indicator in needs_web_indicators):
            return True
        
        # Queries with specific names, places, or technical terms
        if len(key_terms) >= 3 and any(len(term) > 6 for term in key_terms):
            return True
        
        return False
    
    def _identify_potential_sources(self, query: str, key_terms: List[str]) -> List[SourceType]:
        """Identify what types of sources would be useful."""
        sources = []
        query_lower = query.lower()
        
        # Always consider memory and user context
        sources.append(SourceType.MEMORY)
        sources.append(SourceType.USER)
        
        # Web sources for most queries
        if self._requires_web_search(query, key_terms):
            sources.append(SourceType.WEB)
        
        # Academic sources for technical/scientific queries
        academic_indicators = {"study", "research", "paper", "journal", "academic", "scientific"}
        if any(indicator in query_lower for indicator in academic_indicators):
            sources.append(SourceType.ACADEMIC)
        
        # News sources for current events
        news_indicators = {"news", "breaking", "update", "today", "recent"}
        if any(indicator in query_lower for indicator in news_indicators):
            sources.append(SourceType.NEWS)
        
        # Official sources for formal information
        official_indicators = {"government", "official", "agency", "department", "law", "regulation"}
        if any(indicator in query_lower for indicator in official_indicators):
            sources.append(SourceType.OFFICIAL)
        
        return sources
    
    def _identify_information_needs(self, query: str, key_terms: List[str]) -> List[str]:
        """Identify what information is being requested."""
        needs = []
        query_lower = query.lower()
        
        # Common information needs patterns
        patterns = {
            "definition": r"what (is|are) .*\?",
            "how_to": r"how (to|do|can) .*\?",
            "why": r"why .*\?",
            "comparison": r"compare|difference between|vs",
            "examples": r"examples? of|for example",
            "statistics": r"how many|how much|percentage|statistics",
            "timeline": r"when|timeline|history of",
            "location": r"where|location|place",
        }
        
        for need, pattern in patterns.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                needs.append(need)
        
        # If no patterns matched, use key terms
        if not needs:
            needs = [f"information about {', '.join(key_terms[:3])}"]
        
        return needs
    
    def add_source(self, source: InformationSource) -> None:
        """Add a source to the database."""
        self.sources_db[source.id] = source
    
    def get_sources_by_type(self, source_type: SourceType) -> List[InformationSource]:
        """Get all sources of a specific type."""
        return [s for s in self.sources_db.values() if s.type == source_type]
    
    def synthesize_response(self, analysis: QueryAnalysis, 
                          available_sources: List[InformationSource]) -> SynthesizedResponse:
        """
        Synthesize a response from available sources.
        
        Args:
            analysis: Query analysis
            available_sources: Sources to use for synthesis
            
        Returns:
            SynthesizedResponse object
        """
        if not available_sources:
            # Fallback: generate basic response
            content = f"Based on your query about '{analysis.original_query}', "
            content += f"I can provide general information. Key aspects to consider: {', '.join(analysis.key_terms)}."
            
            return SynthesizedResponse(
                content=content,
                sources=[],
                confidence=0.3,
                recency=analysis.time_sensitivity
            )
        
        # Simple synthesis: combine source content
        combined_content = []
        for source in available_sources:
            if source.content:
                combined_content.append(source.content)
        
        # Identify contradictions (simplified)
        contradictions = []
        if len(available_sources) > 1:
            # Check for conflicting dates or facts
            dates = [s.date for s in available_sources if s.date]
            if dates and max(dates).year - min(dates).year > 10:
                contradictions.append("Sources span significantly different time periods")
        
        # Identify knowledge gaps
        knowledge_gaps = []
        for need in analysis.information_needs:
            covered = any(need in source.content.lower() for source in available_sources)
            if not covered:
                knowledge_gaps.append(f"Need: {need}")
        
        content = " ".join(combined_content[:3])  # Limit to first 3 sources
        
        # Calculate confidence based on source quality and recency
        confidence = self._calculate_confidence(available_sources, analysis)
        
        # Determine overall recency
        recency = self._determine_overall_recency(available_sources, analysis.time_sensitivity)
        
        return SynthesizedResponse(
            content=content,
            sources=available_sources,
            confidence=confidence,
            recency=recency,
            contradictions=contradictions,
            knowledge_gaps=knowledge_gaps
        )
    
    def _calculate_confidence(self, sources: List[InformationSource], 
                            analysis: QueryAnalysis) -> float:
        """Calculate confidence score for synthesized response."""
        if not sources:
            return 0.0
        
        # Base confidence on number and quality of sources
        avg_credibility = sum(s.credibility_score for s in sources) / len(sources)
        
        # Adjust for recency match
        recency_match = 1.0
        for source in sources:
            if source.date:
                current_year = datetime.datetime.now().year
                source_year = source.date.year
                age = current_year - source_year
                
                if analysis.time_sensitivity == InformationRecency.CURRENT and age > 2:
                    recency_match *= 0.7
                elif analysis.time_sensitivity == InformationRecency.RECENT and age > 5:
                    recency_match *= 0.8
        
        # Adjust for source type relevance
        type_relevance = 1.0
        relevant_types = set(analysis.potential_sources)
        source_types = set(s.type for s in sources)
        if relevant_types and not source_types.intersection(relevant_types):
            type_relevance = 0.6
        
        return min(1.0, avg_credibility * recency_match * type_relevance)
    
    def _determine_overall_recency(self, sources: List[InformationSource],
                                 query_recency: InformationRecency) -> InformationRecency:
        """Determine overall recency based on sources."""
        if not sources:
            return query_recency
        
        # Get dates from sources
        dates = [s.date for s in sources if s.date]
        if not dates:
            return query_recency
        
        # Find most recent date
        most_recent = max(dates)
        current_date = datetime.datetime.now()
        age_days = (current_date - most_recent).days
        
        if age_days <= 180:  # 6 months
            return InformationRecency.CURRENT
        elif age_days <= 730:  # 2 years
            return InformationRecency.RECENT
        else:
            return InformationRecency.HISTORICAL
    
    def get_response_with_citations(self, response: SynthesizedResponse) -> str:
        """Get response with formatted citations."""
        return response.with_citations()
    
    def save_analysis(self, filepath: str) -> None:
        """Save query history to file."""
        data = {
            "query_history": [q.to_dict() for q in self.query_history],
            "sources_count": len(self.sources_db),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_analysis(self, filepath: str) -> None:
        """Load query history from file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Note: This is simplified - would need proper deserialization
            print(f"Loaded {len(data.get('query_history', []))} queries from {filepath}")
        except FileNotFoundError:
            print(f"No analysis file found at {filepath}")


# Example usage
if __name__ == "__main__":
    pi = PerplexityInspired()
    
    # Example query
    query = "What are the latest developments in quantum computing?"
    analysis = pi.analyze_query(query)
    
    print(f"Query: {analysis.original_query}")
    print(f"Key terms: {analysis.key_terms}")
    print(f"Time sensitivity: {analysis.time_sensitivity}")
    print(f"Requires web search: {analysis.requires_web_search}")
    print(f"Information needs: {analysis.information_needs}")
    
    # Example sources (in real use, these would come from web search)
    source1 = InformationSource(
        id="src1",
        type=SourceType.WEB,
        content="Quantum computing has seen advances in error correction and qubit stability.",
        url="https://example.com/quantum-advances",
        title="Recent Advances in Quantum Computing",
        date=datetime.datetime(2025, 11, 15),
        credibility_score=0.8
    )
    
    source2 = InformationSource(
        id="src2",
        type=SourceType.NEWS,
        content="Major tech companies announced new quantum processors with 1000+ qubits.",
        url="https://example.com/quantum-news",
        title="Tech Giants Unveil Quantum Breakthroughs",
        date=datetime.datetime(2025, 12, 1),
        credibility_score=0.7
    )
    
    pi.add_source(source1)
    pi.add_source(source2)
    
    # Synthesize response
    response = pi.synthes