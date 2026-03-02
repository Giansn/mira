---
name: research
description: "Deep research skill - comprehensive information gathering and analysis using multi-model orchestration"
trigger: "research"
---

# Research Skill

## Overview

A comprehensive research skill that triggers when you say "research something" or similar phrases. Uses multi-model orchestration for deep, thorough information gathering and analysis.

## Trigger Phrases

The skill activates when messages contain:
- "research" (as a verb: "research X", "do research on Y")
- "look into"
- "investigate"
- "find information about"
- "analyze" (when combined with research intent)
- "study" (when research-focused)

## Architecture

### 1. Research Pipeline
```
Research Request → Query Analysis → Multi-Model Orchestration → Synthesis → Report
```

### 2. Model Coordination
- **Research Phase:** gemini-pro (research capability)
- **Analysis Phase:** claude-sonnet (reasoning + analysis)
- **Writing Phase:** gpt-4 (creativity + writing)
- **Review Phase:** claude-sonnet (review)

### 3. Information Sources
1. **Web search** (when Brave API available)
2. **Academic/scholarly sources**
3. **Current news** (time-sensitive topics)
4. **Official documentation**
5. **Memory system** (past research)

## Usage

### Basic Research
```
User: "research quantum computing applications"
→ Skill triggers
→ Multi-model orchestration executes
→ Returns comprehensive research report
```

### Complex Research
```
User: "research the impact of AI on social work education"
→ Skill triggers with complexity analysis
→ Parallel research on multiple aspects
→ Integrated analysis with citations
```

### Research with Constraints
```
User: "research renewable energy policies in Europe, focus on Germany"
→ Skill triggers with specific scope
→ Targeted research with geographic focus
→ Comparative analysis
```

## Implementation

### Core Components

1. **`research_skill.py`** - Main skill handler
2. **`research_pipeline.py`** - Multi-stage research workflow
3. **`query_analyzer.py`** - Parse research intent and scope
4. **`source_tracker.py`** - Track information sources and citations

### Integration Points

- **Multi-Model Orchestrator** - Coordinates AI models for research
- **Perplexity-Inspired Skill** - Query analysis and source citation
- **Async Agent Pattern** - Long-running research tasks
- **Memory System** - Store and retrieve research findings

## Research Methodology

### 1. Scope Definition
- Identify research question
- Determine breadth vs. depth
- Set time constraints (current vs. historical)
- Define required sources

### 2. Information Gathering
- Multi-source collection
- Source credibility assessment
- Time sensitivity consideration
- Cross-verification

### 3. Analysis & Synthesis
- Pattern identification
- Trend analysis
- Comparative evaluation
- Gap identification

### 4. Report Generation
- Structured format
- Source citations
- Key findings summary
- Recommendations/next steps

## Output Format

### Standard Research Report
```
# Research Report: [Topic]

## Executive Summary
Brief overview of key findings

## Research Methodology
- Scope definition
- Sources used
- Analysis approach

## Key Findings
1. Finding 1 with supporting evidence
2. Finding 2 with supporting evidence
3. Finding 3 with supporting evidence

## Analysis
- Trends and patterns
- Comparative insights
- Implications

## Sources
1. [Source 1] - Type, date, relevance
2. [Source 2] - Type, date, relevance
3. [Source 3] - Type, date, relevance

## Recommendations
- Further research areas
- Practical applications
- Limitations

## Research Metadata
- Date conducted: [timestamp]
- Models used: [list]
- Confidence score: [0.0-1.0]
- Time spent: [duration]
```

## Configuration

### Research Depth Levels
1. **Quick** - Surface-level, 1-2 models, <5 minutes
2. **Standard** - Comprehensive, 2-3 models, 5-15 minutes
3. **Deep** - Thorough, 3+ models, 15-30+ minutes
4. **Academic** - Scholarly, multiple sources, citations, peer-review style

### Source Priority
1. **Academic** - Peer-reviewed journals, conferences
2. **Official** - Government reports, organizational publications
3. **News** - Current events, recent developments
4. **Web** - General information, blogs, documentation

## Examples

### Example 1: Technology Research
```
User: "research blockchain scalability solutions"
→ Triggers research skill
→ Uses: gemini-pro (research) → claude-sonnet (analysis) → gpt-4 (writing)
→ Returns: Comprehensive report on Layer 2, sharding, consensus algorithms
```

### Example 2: Social Science Research
```
User: "research effects of social media on mental health in adolescents"
→ Triggers research skill
→ Uses: gemini-pro (academic sources) → claude-sonnet (analysis) → review
→ Returns: Research with academic citations, statistical analysis
```

### Example 3: Current Events Research
```
User: "research recent developments in quantum computing 2025"
→ Triggers research skill with time sensitivity
→ Prioritizes recent sources (<6 months)
→ Returns: Current state analysis with timeline
```

## Integration with Existing Workflow

### Heartbeat Integration
Research tasks can be scheduled via heartbeat for:
- Daily research briefings
- Weekly topic deep dives
- Ongoing research projects

### Memory Integration
- Store research findings in memory system
- Create research topic embeddings
- Enable semantic search across past research
- Build knowledge graph of research topics

### Project Integration
- Link research to thesis projects
- Track research progress
- Organize findings by project
- Generate literature reviews

## Quality Assurance

### Validation Methods
1. **Cross-model verification** - Multiple models analyze same data
2. **Source credibility scoring** - Rate sources by authority/recency
3. **Consistency checking** - Ensure findings are internally consistent
4. **Bias detection** - Identify potential biases in sources/analysis

### Confidence Scoring
- **High (0.8-1.0)** - Multiple reliable sources, consistent findings
- **Medium (0.5-0.8)** - Limited sources, some uncertainty
- **Low (0.0-0.5)** - Inconclusive, needs more research

## Limitations

### Current Constraints
1. **Web search dependency** - Requires Brave API for external research
2. **Model availability** - Limited to configured AI models
3. **Time constraints** - Deep research requires significant time
4. **Source access** - Some sources may be paywalled or restricted

### Mitigation Strategies
- Use memory system for past research
- Leverage multi-model analysis for depth
- Implement progressive disclosure (quick → deep)
- Cache research findings for similar queries

## Future Enhancements

### Planned Features
1. **Automated literature review** - Academic paper analysis
2. **Research topic tracking** - Monitor developments over time
3. **Comparative research** - Side-by-side analysis of multiple topics
4. **Visual research outputs** - Charts, graphs, timelines
5. **Collaborative research** - Share findings, peer review

### Integration Goals
1. **Thesis research assistant** - Specialized for academic research
2. **News monitoring** - Daily research briefings on selected topics
3. **Knowledge base builder** - Automatically expand memory system
4. **Research dashboard** - Track all research activities and findings

## Usage Notes

### Best Practices
1. **Be specific** - Clear research questions yield better results
2. **Set scope** - Define breadth/depth expectations
3. **Consider time** - Recent vs. historical information needs
4. **Review sources** - Always check source credibility

### Common Use Cases
- Academic research support
- Market/competitor analysis
- Technology evaluation
- Policy research
- Historical analysis
- Current events monitoring

## Quick Start

### Basic Usage
Just say "research [topic]" and the skill will automatically:
1. Analyze your query
2. Determine appropriate research depth
3. Coordinate multiple AI models
4. Return comprehensive findings

### Advanced Usage
For more control, specify:
- "deep research on [topic]" - More thorough analysis
- "quick research on [topic]" - Surface-level overview
- "academic research on [topic]" - Scholarly focus
- "current research on [topic]" - Recent developments only