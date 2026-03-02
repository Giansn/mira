---
name: perplexity-inspired
description: Implements Perplexity AI-inspired features: query analysis, information synthesis, source citation, and current information priority.
user-invocable: true
---

# Perplexity-Inspired Skill

Implements key features inspired by Perplexity AI's approach to information retrieval and synthesis.

## Features

### 1. Query Analysis
- Breaks down complex queries into searchable components
- Identifies information needs and knowledge gaps
- Determines optimal search strategies

### 2. Information Synthesis  
- Combines information from multiple sources
- Creates coherent, comprehensive responses
- Identifies contradictions and consensus

### 3. Source Citation
- Tracks information sources
- Provides citations for key facts
- Evaluates source credibility

### 4. Current Information Priority
- Flags outdated information
- Prioritizes recent sources
- Identifies time-sensitive queries

## Usage

```python
from perplexity_inspired import PerplexityInspired

# Initialize
pi = PerplexityInspired()

# Analyze query
analysis = pi.analyze_query("What are the latest developments in quantum computing?")

# Get synthesized response (when web access available)
response = pi.get_synthesized_response(analysis)

# With citations
response_with_citations = pi.get_response_with_citations(response)
```

## Integration Points

1. **Web Search**: When Brave API is configured, uses real-time web search
2. **Memory System**: Integrates with OpenClaw memory for context
3. **Source Database**: Maintains citation database for reference
4. **Time Awareness**: Uses current date/time for recency evaluation

## Inspired By

Perplexity AI's approach to:
- Real-time web search integration
- Source citation and transparency  
- Current information prioritization
- Query understanding and synthesis

## Limitations

- Web search requires Brave API key configuration
- Source tracking depends on available metadata
- Real-time updates limited by API access

## Future Enhancements

1. **Multi-source aggregation**: Combine web, memory, and local knowledge
2. **Credibility scoring**: Rate sources based on reliability
3. **Trend detection**: Identify emerging topics and patterns
4. **Query optimization**: Improve search strategy based on results