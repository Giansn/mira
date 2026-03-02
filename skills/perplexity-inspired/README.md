# Perplexity-Inspired Skill

Implements key features inspired by Perplexity AI's approach to information retrieval and synthesis.

## Overview

This skill provides a framework for:
- **Query analysis** - Understanding user information needs
- **Information synthesis** - Combining multiple sources
- **Source citation** - Tracking and citing information sources
- **Current information priority** - Focusing on up-to-date information

## Installation

```bash
# Clone or copy the skill to your OpenClaw workspace
cp -r skills/perplexity-inspired ~/.openclaw/workspace/skills/
```

## Usage

### Basic Usage

```python
from perplexity_inspired import PerplexityInspired

# Initialize
pi = PerplexityInspired()

# Analyze a query
query = "What are the latest developments in quantum computing?"
analysis = pi.analyze_query(query)

print(f"Key terms: {analysis.key_terms}")
print(f"Time sensitivity: {analysis.time_sensitivity}")
print(f"Requires web search: {analysis.requires_web_search}")

# Add sources (in real use, these would come from web search)
from perplexity_inspired import InformationSource, SourceType
import datetime

source = InformationSource(
    id="src1",
    type=SourceType.NEWS,
    content="Quantum computing breakthrough announced...",
    url="https://example.com/news",
    title="Quantum Breakthrough",
    date=datetime.datetime(2025, 11, 15),
    credibility_score=0.8
)

pi.add_source(source)

# Synthesize response
response = pi.synthesize_response(analysis, [source])

print(f"Response: {response.content}")
print(f"Confidence: {response.confidence:.2f}")
print(f"Recency: {response.recency}")

# Get response with citations
response_with_cites = pi.get_response_with_citations(response)
```

### Integration with OpenClaw

```python
# In an OpenClaw skill or agent
def handle_query(user_query: str):
    pi = PerplexityInspired()
    analysis = pi.analyze_query(user_query)
    
    # Use analysis to guide information gathering
    if analysis.requires_web_search:
        # Trigger web search when available
        print(f"Query requires web search for: {analysis.key_terms}")
    
    # Synthesize from available sources
    available_sources = get_available_sources(analysis)
    response = pi.synthesize_response(analysis, available_sources)
    
    return response.with_citations()
```

## Features

### 1. Query Analysis
- Extracts key terms from queries
- Determines time sensitivity (current, recent, historical, timeless)
- Identifies information needs (definition, how-to, comparison, etc.)
- Suggests appropriate source types (web, academic, news, official)

### 2. Information Synthesis
- Combines content from multiple sources
- Identifies contradictions between sources
- Highlights knowledge gaps
- Calculates confidence scores based on source quality and recency

### 3. Source Management
- Tracks information sources with metadata
- Supports different source types (web, academic, news, etc.)
- Provides citation formatting
- Includes credibility scoring

### 4. Recency Awareness
- Classifies information as current, recent, historical, or timeless
- Prioritizes recent sources for time-sensitive queries
- Flags potentially outdated information

## Architecture

### Core Classes

1. **`PerplexityInspired`** - Main class coordinating all features
2. **`QueryAnalysis`** - Analysis results of a user query
3. **`InformationSource`** - Represents a source with metadata
4. **`SynthesizedResponse`** - Response synthesized from multiple sources
5. **`SourceType`** - Enum of source types (web, academic, news, etc.)
6. **`InformationRecency`** - Enum of recency levels

### Data Flow

```
User Query → Query Analysis → Source Identification → Information Gathering → Synthesis → Response with Citations
```

## Integration Points

### Web Search Integration
When Brave API is configured, the skill can:
- Use query analysis to generate search terms
- Process search results into `InformationSource` objects
- Prioritize sources based on recency and credibility

### Memory Integration
- Store and retrieve previous query analyses
- Maintain source database across sessions
- Learn from past information synthesis patterns

### Real-time Updates
- Check source dates against current time
- Flag outdated information
- Suggest re-searching for time-sensitive topics

## Example Use Cases

### 1. Research Assistant
```python
# User asks about a technical topic
analysis = pi.analyze_query("Explain transformer architecture in AI")
# Identifies need for academic/web sources, technical explanation
```

### 2. News Summarization
```python
# User asks for current events
analysis = pi.analyze_query("Latest developments in climate policy")
# Prioritizes news sources, current information
```

### 3. Comparative Analysis
```python
# User asks for comparison
analysis = pi.analyze_query("Compare React and Vue.js")
# Identifies need for technical specs, pros/cons, use cases
```

## Configuration

### Source Credibility Weights
```python
# Customize how different source types are weighted
CREDIBILITY_WEIGHTS = {
    SourceType.ACADEMIC: 0.9,
    SourceType.OFFICIAL: 0.85,
    SourceType.NEWS: 0.7,
    SourceType.WEB: 0.6,
    SourceType.USER: 0.5,
}
```

### Time Sensitivity Thresholds
```python
# Adjust what counts as "current" vs "recent"
CURRENT_THRESHOLD_DAYS = 180  # 6 months
RECENT_THRESHOLD_DAYS = 730   # 2 years
```

## Limitations

1. **Web Search Dependency** - Full functionality requires web search API access
2. **Source Quality Assessment** - Automated credibility scoring is basic
3. **Language Understanding** - Query analysis uses simple pattern matching
4. **Real-time Updates** - Depends on source metadata accuracy

## Future Enhancements

1. **Multi-language Support** - Analyze queries in different languages
2. **Domain-specific Analysis** - Specialized handling for technical, medical, legal queries
3. **Source Network Analysis** - Track how sources reference each other
4. **Trend Detection** - Identify emerging topics and information gaps
5. **User Feedback Integration** - Learn from user corrections and preferences

## Inspired By

Perplexity AI's approach to:
- Real-time web search integration
- Source citation and transparency
- Current information prioritization
- Query understanding and synthesis

## License

OpenClaw Skill - Free to use and modify