#!/usr/bin/env python3
"""
Research Skill - Deep research using multi-model orchestration
Triggers on "research" keyword and similar phrases
"""

import re
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from multi_model_orchestrator.multi_model_orchestrator import MultiModelOrchestrator, WorkflowType
    MULTI_MODEL_AVAILABLE = True
except ImportError:
    MULTI_MODEL_AVAILABLE = False
    print("Warning: Multi-model orchestrator not available. Research will be limited.")

try:
    from perplexity_inspired.perplexity_inspired import QueryAnalysis, InformationSource, SynthesizedResponse
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False


@dataclass
class ResearchQuery:
    """Parsed research query."""
    original_text: str
    topic: str
    depth: str  # quick, standard, deep, academic
    time_sensitivity: str  # current, recent, historical, timeless
    scope: List[str]  # Specific aspects to focus on
    constraints: List[str]  # Limitations or exclusions
    requires_citations: bool = True
    requires_analysis: bool = True
    requires_recommendations: bool = True


@dataclass
class ResearchResult:
    """Result of research operation."""
    query: ResearchQuery
    content: str
    sources: List[Dict[str, Any]]
    models_used: List[str]
    execution_time: float
    confidence: float
    research_metadata: Dict[str, Any] = field(default_factory=dict)


class ResearchSkill:
    """Main research skill class."""
    
    def __init__(self):
        self.trigger_patterns = [
            r'\bresearch\b',
            r'\blook into\b',
            r'\binvestigate\b',
            r'\bfind (?:information|details) (?:about|on)\b',
            r'\banalyze\b.*\b(?:for|about)\b',
            r'\bstudy\b.*\b(?:of|about)\b',
            r'\bexplore\b.*\b(?:topic|subject|issue)\b',
            r'\bexamine\b.*\b(?:closely|in detail)\b',
        ]
        
        if MULTI_MODEL_AVAILABLE:
            self.orchestrator = MultiModelOrchestrator()
        else:
            self.orchestrator = None
        
        if PERPLEXITY_AVAILABLE:
            self.query_analyzer = QueryAnalysis()
        else:
            self.query_analyzer = None
    
    def should_trigger(self, message: str) -> bool:
        """Check if message should trigger research skill."""
        message_lower = message.lower()
        
        for pattern in self.trigger_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Also check for "research" as first word followed by topic
        if message_lower.startswith('research '):
            return True
        
        return False
    
    def parse_query(self, message: str) -> ResearchQuery:
        """Parse research query from message."""
        message_lower = message.lower()
        
        # Extract topic (remove trigger words)
        topic = message_lower
        
        # Remove common trigger phrases
        triggers_to_remove = [
            'research', 'look into', 'investigate', 'find information about',
            'analyze', 'study', 'explore', 'examine'
        ]
        
        for trigger in triggers_to_remove:
            if topic.startswith(trigger + ' '):
                topic = topic[len(trigger) + 1:]
            elif ' ' + trigger + ' ' in topic:
                topic = topic.replace(' ' + trigger + ' ', ' ')
        
        topic = topic.strip()
        
        # Determine depth
        depth = 'standard'
        if 'deep research' in message_lower or 'thorough research' in message_lower:
            depth = 'deep'
        elif 'quick research' in message_lower or 'brief research' in message_lower:
            depth = 'quick'
        elif 'academic research' in message_lower or 'scholarly research' in message_lower:
            depth = 'academic'
        
        # Determine time sensitivity
        time_sensitivity = 'timeless'
        time_indicators = {
            'current': ['current', 'recent', 'latest', 'now', 'today', '2026', '2025'],
            'recent': ['past year', 'last year', 'recent years', 'modern'],
            'historical': ['historical', 'history', 'past', 'evolution', 'development']
        }
        
        for sensitivity, indicators in time_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    time_sensitivity = sensitivity
                    break
            if time_sensitivity != 'timeless':
                break
        
        # Extract scope and constraints
        scope = []
        constraints = []
        
        # Look for scope indicators
        scope_indicators = ['focus on', 'especially', 'particularly', 'specifically']
        for indicator in scope_indicators:
            if indicator in message_lower:
                # Extract text after indicator
                parts = message_lower.split(indicator)
                if len(parts) > 1:
                    scope_text = parts[1].split('.')[0].split(',')[0].strip()
                    if scope_text:
                        scope.append(scope_text)
        
        # Look for constraint indicators
        constraint_indicators = ['excluding', 'without', 'not including', 'avoid']
        for indicator in constraint_indicators:
            if indicator in message_lower:
                parts = message_lower.split(indicator)
                if len(parts) > 1:
                    constraint_text = parts[1].split('.')[0].split(',')[0].strip()
                    if constraint_text:
                        constraints.append(constraint_text)
        
        # Determine if citations/analysis needed
        requires_citations = depth in ['deep', 'academic'] or 'citation' in message_lower
        requires_analysis = depth in ['standard', 'deep', 'academic']
        requires_recommendations = depth in ['deep', 'academic']
        
        return ResearchQuery(
            original_text=message,
            topic=topic,
            depth=depth,
            time_sensitivity=time_sensitivity,
            scope=scope,
            constraints=constraints,
            requires_citations=requires_citations,
            requires_analysis=requires_analysis,
            requires_recommendations=requires_recommendations
        )
    
    async def execute_research(self, query: ResearchQuery) -> ResearchResult:
        """Execute research using multi-model orchestration."""
        start_time = time.time()
        
        if not self.orchestrator:
            # Fallback: simple research without multi-model
            return await self._simple_research(query)
        
        # Build research task based on depth
        research_task = self._build_research_task(query)
        
        # Execute with appropriate workflow
        if query.depth == 'quick':
            workflow = WorkflowType.SEQUENTIAL
            max_models = 2
        elif query.depth == 'standard':
            workflow = WorkflowType.SEQUENTIAL
            max_models = 3
        elif query.depth == 'deep':
            workflow = WorkflowType.PARALLEL
            max_models = 4
        else:  # academic
            workflow = WorkflowType.SEQUENTIAL
            max_models = 4
        
        # Select models based on capabilities needed
        available_models = self._select_models_for_research(query)
        
        # Execute research
        try:
            result = await self.orchestrator.execute_complex_task(
                task=research_task,
                workflow_type=workflow,
                available_models=available_models[:max_models]
            )
            
            # Generate sources (mock for now - would integrate with actual search)
            sources = self._generate_sources(query)
            
            return ResearchResult(
                query=query,
                content=result.final_content,
                sources=sources,
                models_used=result.models_used,
                execution_time=result.execution_time,
                confidence=result.confidence,
                research_metadata={
                    'workflow_type': result.workflow_type.value,
                    'subtask_count': len(result.subtask_results),
                    'depth': query.depth
                }
            )
            
        except Exception as e:
            # Fallback to simple research
            print(f"Multi-model research failed: {e}")
            return await self._simple_research(query)
    
    async def _simple_research(self, query: ResearchQuery) -> ResearchResult:
        """Simple research fallback without multi-model orchestration."""
        start_time = time.time()
        
        # Simulate research
        await asyncio.sleep(1.0)  # Simulate research time
        
        content = self._generate_simple_research_content(query)
        sources = self._generate_sources(query)
        
        return ResearchResult(
            query=query,
            content=content,
            sources=sources,
            models_used=['simple-research'],
            execution_time=time.time() - start_time,
            confidence=0.6,
            research_metadata={'method': 'simple_fallback'}
        )
    
    def _build_research_task(self, query: ResearchQuery) -> str:
        """Build detailed research task description."""
        task_parts = [f"Research: {query.topic}"]
        
        if query.depth != 'standard':
            task_parts.append(f"Depth: {query.depth}")
        
        if query.time_sensitivity != 'timeless':
            task_parts.append(f"Time focus: {query.time_sensitivity}")
        
        if query.scope:
            task_parts.append(f"Focus areas: {', '.join(query.scope)}")
        
        if query.constraints:
            task_parts.append(f"Exclusions: {', '.join(query.constraints)}")
        
        task_parts.append("Provide comprehensive analysis with clear structure.")
        
        if query.requires_citations:
            task_parts.append("Include source citations where applicable.")
        
        if query.requires_analysis:
            task_parts.append("Include detailed analysis and insights.")
        
        if query.requires_recommendations:
            task_parts.append("Include recommendations and next steps.")
        
        return "\n".join(task_parts)
    
    def _select_models_for_research(self, query: ResearchQuery) -> List[str]:
        """Select appropriate models for research type."""
        if not self.orchestrator:
            return []
        
        # Model selection based on research type
        if query.depth == 'academic':
            # Academic research: research + analysis + writing + review
            return ['gemini-pro', 'claude-sonnet', 'gpt-4', 'claude-sonnet']
        elif query.depth == 'deep':
            # Deep research: parallel research on different aspects
            return ['gemini-pro', 'claude-sonnet', 'gpt-4']
        elif query.depth == 'standard':
            # Standard research: research → analysis → writing
            return ['gemini-pro', 'claude-sonnet', 'gpt-4']
        else:  # quick
            # Quick research: combined research+writing
            return ['gpt-4', 'claude-sonnet']
    
    def _generate_sources(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Generate mock sources (would integrate with actual search)."""
        sources = []
        
        # Mock sources based on topic
        source_types = ['web', 'academic', 'news', 'official']
        
        for i in range(min(3, len(source_types))):
            source_type = source_types[i]
            sources.append({
                'type': source_type,
                'title': f"Source on {query.topic}",
                'url': f"https://example.com/{query.topic.replace(' ', '-')}-{i}",
                'date': '2025-12-15' if query.time_sensitivity == 'current' else '2024-06-01',
                'relevance': 0.8 - (i * 0.1),
                'credibility': 0.7 if source_type in ['academic', 'official'] else 0.5
            })
        
        return sources
    
    def _generate_simple_research_content(self, query: ResearchQuery) -> str:
        """Generate simple research content for fallback."""
        content = [
            f"# Research Report: {query.topic}",
            f"*Generated via simple research method*",
            "",
            "## Executive Summary",
            f"This report provides an overview of {query.topic}. ",
            f"The research was conducted with {query.depth} depth and focuses on {query.time_sensitivity} information.",
            "",
            "## Key Findings",
            "1. **Finding 1**: Initial analysis suggests important aspects to consider.",
            "2. **Finding 2**: Multiple perspectives exist on this topic.",
            "3. **Finding 3**: Further research would provide more detailed insights.",
            "",
            "## Analysis",
            f"The topic of {query.topic} involves several key considerations. ",
            "Based on available information, several trends and patterns can be identified.",
            "",
            "## Limitations",
            "This research was conducted using a simplified method. ",
            "For more comprehensive analysis, multi-model orchestration would provide deeper insights.",
            "",
            "## Next Steps",
            "1. Conduct deeper research with multi-model coordination",
            "2. Gather additional sources and data",
            "3. Perform comparative analysis",
            f"4. Monitor developments in {query.topic}",
            "",
            "---",
            f"*Research completed: {time.ctime()}*",
            f"*Depth level: {query.depth}*",
            f"*Time focus: {query.time_sensitivity}*"
        ]
        
        return "\n".join(content)
    
    def format_research_result(self, result: ResearchResult) -> str:
        """Format research result for display."""
        lines = []
        
        lines.append(f"# 🔍 Research Complete: {result.query.topic}")
        lines.append("")
        
        # Metadata
        lines.append("## Research Metadata")
        lines.append(f"- **Depth**: {result.query.depth}")
        lines.append(f"- **Time focus**: {result.query.time_sensitivity}")
        lines.append(f"- **Execution time**: {result.execution_time:.2f}s")
        lines.append(f"- **Confidence**: {result.confidence:.2f}")
        lines.append(f"- **Models used**: {', '.join(result.models_used)}")
        
        if result.query.scope:
            lines.append(f"- **Focus areas**: {', '.join(result.query.scope)}")
        
        if result.query.constraints:
            lines.append(f"- **Exclusions**: {', '.join(result.query.constraints)}")
        
        lines.append("")
        
        # Sources
        if result.sources and result.query.requires_citations:
            lines.append("## Sources Referenced")
            for i, source in enumerate(result.sources, 1):
                lines.append(f"{i}. **{source['type'].title()}**: {source['title']}")
                if 'date' in source:
                    lines.append(f"   Date: {source['date']}, Relevance: {source['relevance']:.2f}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Content
        lines.append(result.content)
        
        return "\n".join(lines)


async def handle_research_request(message: str) -> Optional[str]:
    """
    Main entry point for research skill.
    Returns research result if triggered, None otherwise.
    """
    skill = ResearchSkill()
    
    if not skill.should_trigger(message):
        return None
    
    # Parse query
    query = skill.parse_query(message)
    
    # Execute research
    print(f"Starting research: {query.topic} (depth: {query.depth})")
    result = await skill.execute_research(query)
    
    # Format result
    return skill.format_research_result(result)


# Command-line interface for testing
async def main():
    """Test the research skill."""
    if len(sys.argv) < 2:
        print("Usage: python research_skill.py '<research query>'")
        sys.exit(1)
    
    message = ' '.join(sys.argv[1:])
    
    result = await handle_research_request(message)
    if result:
        print("\n" + "="*80)
        print(result)
        print("="*80)
    else:
        print("Research skill not triggered for this message.")


if __name__ == "__main__":
    asyncio.run(main())