#!/usr/bin/env python3
"""
Research Pipeline - Multi-stage research workflow
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_skill import ResearchQuery, ResearchResult


@dataclass
class ResearchStage:
    """A stage in the research pipeline."""
    name: str
    description: str
    required_capabilities: List[str]
    timeout_seconds: int = 300
    dependencies: List[str] = field(default_factory=list)


@dataclass
class StageResult:
    """Result of a pipeline stage."""
    stage_name: str
    content: str
    execution_time: float
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResearchPipeline:
    """Multi-stage research pipeline."""
    
    def __init__(self):
        self.stages = self._define_stages()
    
    def _define_stages(self) -> Dict[str, ResearchStage]:
        """Define research pipeline stages."""
        return {
            'scope_definition': ResearchStage(
                name='scope_definition',
                description='Define research scope and methodology',
                required_capabilities=['planning', 'reasoning'],
                timeout_seconds=60
            ),
            'literature_review': ResearchStage(
                name='literature_review',
                description='Gather and review existing literature',
                required_capabilities=['research', 'analysis'],
                timeout_seconds=600,
                dependencies=['scope_definition']
            ),
            'data_collection': ResearchStage(
                name='data_collection',
                description='Collect primary and secondary data',
                required_capabilities=['research', 'specialist'],
                timeout_seconds=600,
                dependencies=['scope_definition']
            ),
            'analysis': ResearchStage(
                name='analysis',
                description='Analyze collected information',
                required_capabilities=['analysis', 'reasoning'],
                timeout_seconds=300,
                dependencies=['literature_review', 'data_collection']
            ),
            'synthesis': ResearchStage(
                name='synthesis',
                description='Synthesize findings into coherent insights',
                required_capabilities=['writing', 'creativity'],
                timeout_seconds=300,
                dependencies=['analysis']
            ),
            'validation': ResearchStage(
                name='validation',
                description='Validate findings and check consistency',
                required_capabilities=['review', 'analysis'],
                timeout_seconds=180,
                dependencies=['synthesis']
            ),
            'report_generation': ResearchStage(
                name='report_generation',
                description='Generate final research report',
                required_capabilities=['writing', 'creativity'],
                timeout_seconds=240,
                dependencies=['validation']
            )
        }
    
    async def execute_pipeline(self, query: ResearchQuery) -> Dict[str, StageResult]:
        """Execute the full research pipeline."""
        results = {}
        
        # Determine which stages to run based on depth
        stages_to_run = self._select_stages_for_depth(query.depth)
        
        print(f"Executing research pipeline with {len(stages_to_run)} stages")
        
        for stage_name in stages_to_run:
            stage = self.stages[stage_name]
            
            # Check dependencies
            deps_met = all(dep in results for dep in stage.dependencies)
            if not deps_met:
                print(f"Skipping {stage_name}: dependencies not met")
                continue
            
            print(f"Starting stage: {stage.name} - {stage.description}")
            
            try:
                result = await self._execute_stage(stage, query, results)
                results[stage_name] = result
                
                if result.success:
                    print(f"  ✓ Completed in {result.execution_time:.2f}s")
                else:
                    print(f"  ✗ Failed: {result.metadata.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ✗ Stage failed: {e}")
                results[stage_name] = StageResult(
                    stage_name=stage_name,
                    content=f"Stage failed: {str(e)}",
                    execution_time=0,
                    success=False,
                    metadata={'error': str(e)}
                )
        
        return results
    
    def _select_stages_for_depth(self, depth: str) -> List[str]:
        """Select pipeline stages based on research depth."""
        if depth == 'quick':
            return ['scope_definition', 'literature_review', 'report_generation']
        elif depth == 'standard':
            return ['scope_definition', 'literature_review', 'analysis', 'report_generation']
        elif depth == 'deep':
            return list(self.stages.keys())  # All stages
        elif depth == 'academic':
            # Academic research includes all stages with emphasis on validation
            return list(self.stages.keys())
        else:
            return ['scope_definition', 'literature_review', 'report_generation']
    
    async def _execute_stage(self, stage: ResearchStage, query: ResearchQuery, 
                           previous_results: Dict[str, StageResult]) -> StageResult:
        """Execute a single pipeline stage."""
        start_time = time.time()
        
        # Simulate stage execution (would integrate with actual AI models)
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Generate stage-specific content
        content = self._generate_stage_content(stage, query, previous_results)
        
        return StageResult(
            stage_name=stage.name,
            content=content,
            execution_time=time.time() - start_time,
            success=True,
            metadata={
                'capabilities_used': stage.required_capabilities,
                'timeout': stage.timeout_seconds
            }
        )
    
    def _generate_stage_content(self, stage: ResearchStage, query: ResearchQuery,
                              previous_results: Dict[str, StageResult]) -> str:
        """Generate content for a pipeline stage."""
        if stage.name == 'scope_definition':
            return self._generate_scope_definition(query)
        elif stage.name == 'literature_review':
            return self._generate_literature_review(query, previous_results)
        elif stage.name == 'data_collection':
            return self._generate_data_collection(query, previous_results)
        elif stage.name == 'analysis':
            return self._generate_analysis(query, previous_results)
        elif stage.name == 'synthesis':
            return self._generate_synthesis(query, previous_results)
        elif stage.name == 'validation':
            return self._generate_validation(query, previous_results)
        elif stage.name == 'report_generation':
            return self._generate_report(query, previous_results)
        else:
            return f"Stage: {stage.name}\nDescription: {stage.description}"
    
    def _generate_scope_definition(self, query: ResearchQuery) -> str:
        """Generate scope definition content."""
        return f"""
# Research Scope Definition

## Topic
{query.topic}

## Depth Level
{query.depth}

## Time Sensitivity
{query.time_sensitivity}

## Focus Areas
{', '.join(query.scope) if query.scope else 'Comprehensive coverage'}

## Constraints
{', '.join(query.constraints) if query.constraints else 'None specified'}

## Methodology
- Research approach: {query.depth} depth
- Time focus: {query.time_sensitivity}
- Source types: Multiple (academic, web, official, news)
- Analysis method: Multi-stage pipeline

## Expected Output
- Comprehensive research report
- {'With citations' if query.requires_citations else 'Without citations'}
- {'With analysis' if query.requires_analysis else 'Without analysis'}
- {'With recommendations' if query.requires_recommendations else 'Without recommendations'}
"""
    
    def _generate_literature_review(self, query: ResearchQuery, 
                                  previous_results: Dict[str, StageResult]) -> str:
        """Generate literature review content."""
        scope_content = previous_results.get('scope_definition', StageResult('', '', 0)).content
        
        return f"""
# Literature Review

## Research Topic
{query.topic}

## Scope Context
Based on scope definition, focusing on relevant literature.

## Key Sources Identified
1. **Academic papers** - Peer-reviewed research on related topics
2. **Industry reports** - Market analysis and trend reports
3. **Official publications** - Government and organizational reports
4. **News articles** - Current developments and coverage

## Literature Themes
- Theme 1: Foundational concepts and definitions
- Theme 2: Current state and recent developments
- Theme 3: Challenges and limitations
- Theme 4: Future directions and opportunities

## Gaps Identified
- Need for more recent data (if {query.time_sensitivity})
- Limited coverage of specific aspects
- Varying perspectives requiring synthesis

## Next Steps for Data Collection
- Gather additional sources based on identified gaps
- Focus on {query.time_sensitivity} information
- Prioritize sources relevant to focus areas
"""
    
    def _generate_data_collection(self, query: ResearchQuery,
                                previous_results: Dict[str, StageResult]) -> str:
        """Generate data collection content."""
        return f"""
# Data Collection

## Collection Strategy
- Source types: Multiple (based on literature review findings)
- Time period: {query.time_sensitivity} focus
- Geographic scope: Global (unless specified otherwise)

## Data Categories
1. **Quantitative data** - Statistics, metrics, measurements
2. **Qualitative data** - Case studies, expert opinions, narratives
3. **Comparative data** - Cross-sectional comparisons
4. **Historical data** - Timeline and evolution data

## Collection Methods
- Web scraping and API calls
- Database queries
- Manual research and compilation
- Expert consultations (simulated)

## Data Quality Assessment
- Source credibility evaluation
- Timeliness verification
- Relevance scoring
- Consistency checking

## Data Volume
- Multiple sources per category
- Cross-verified information
- Diverse perspectives included
"""
    
    def _generate_analysis(self, query: ResearchQuery,
                         previous_results: Dict[str, StageResult]) -> str:
        """Generate analysis content."""
        literature_content = previous_results.get('literature_review', StageResult('', '', 0)).content
        data_content = previous_results.get('data_collection', StageResult('', '', 0)).content
        
        return f"""
# Analysis

## Analytical Framework
- Comparative analysis across sources
- Trend identification
- Pattern recognition
- Gap analysis

## Key Findings
1. **Primary finding** - Most significant insight
2. **Secondary findings** - Supporting evidence
3. **Contradictory evidence** - Areas of disagreement
4. **Emerging patterns** - Trends and developments

## Statistical Insights
- Data correlations identified
- Significance levels assessed
- Confidence intervals calculated
- Predictive indicators noted

## Critical Evaluation
- Strengths of current understanding
- Limitations and constraints
- Biases and assumptions identified
- Reliability assessment

## Analytical Conclusions
- Summary of key insights
- Implications of findings
- Relationships between different aspects
- Overall assessment of state of knowledge
"""
    
    def _generate_synthesis(self, query: ResearchQuery,
                          previous_results: Dict[str, StageResult]) -> str:
        """Generate synthesis content."""
        analysis_content = previous_results.get('analysis', StageResult('', '', 0)).content
        
        return f"""
# Synthesis

## Integrated Understanding
Combining findings from literature review, data collection, and analysis into coherent understanding.

## Core Themes Synthesized
1. **Theme synthesis** - How different findings relate
2. **Contradiction resolution** - Reconciling conflicting evidence
3. **Pattern integration** - Connecting disparate patterns
4. **Insight combination** - Creating new understanding from parts

## Conceptual Framework
- Unified model of the topic
- Relationships between components
- Causal mechanisms identified
- Systemic understanding developed

## Novel Insights
- New perspectives emerging from synthesis
- Previously unrecognized connections
- Innovative approaches suggested
- Future research directions identified

## Synthesis Quality
- Coherence of integrated understanding
- Completeness of synthesis
- Originality of insights
- Practical applicability
"""
    
    def _generate_validation(self, query: ResearchQuery,
                           previous_results: Dict[str, StageResult]) -> str:
        """Generate validation content."""
        synthesis_content = previous_results.get('synthesis', StageResult('', '', 0)).content
        
        return f"""
# Validation

## Validation Methods
1. **Cross-verification** - Checking against original sources
2. **Consistency checking** - Internal coherence assessment
3. **Plausibility assessment** - Reasonableness evaluation
4. **Expert review simulation** - Critical examination

## Validation Results
- **Accuracy**: High (based on source verification)
- **Consistency**: Good (internal coherence maintained)
- **Completeness**: {query.depth} level achieved
- **Reliability**: Acceptable for {query.depth} research

## Issues Identified
- Minor inconsistencies noted
- Areas requiring clarification
- Limitations acknowledged
- Assumptions documented

## Validation Confidence
- Overall confidence level: High
- Key findings validated: Yes
- Methodology sound: Yes
- Conclusions supported: Yes

## Recommendations for Final Report
- Emphasize validated findings
- Acknowledge limitations
- Provide clear citations
- Include confidence assessments
"""
    
    def _generate_report(self, query: ResearchQuery,
                       previous_results: Dict[str, StageResult]) -> str:
        """Generate final report content."""
        # Collect content from all previous stages
        all_content = []
        for stage_name, result in previous_results.items():
            if result.success:
                all_content.append(f"## {stage_name.replace('_', ' ').title()}")
                all_content.append(result.content)
                all_content.append("")
        
        # Generate executive summary
        exec_summary = self._generate_executive_summary(query, previous_results)
        
        # Generate recommendations if requested
        recommendations = ""
        if query.requires_recommendations:
            recommendations = self._generate_recommendations(query, previous_results)
        
        # Generate sources section if requested
        sources = ""
        if query.requires_citations:
            sources = self._generate_sources_section(query)
        
        # Assemble final report
        report = [
            f"# Research Report: {query.topic}",
            f"*Depth: {query.depth} | Time focus: {query.time_sensitivity}*",
            "",
            "## Executive Summary",
            exec_summary,
            "",
            "## Detailed Findings",
            "\n".join(all_content),
            ""
        ]
        
        if recommendations:
            report.append("## Recommendations")
            report.append(recommendations)
            report.append("")
        
        if sources:
            report.append("## Sources")
            report.append(sources)
            report.append("")
        
        report.append("## Research Metadata")
        report.append(f"- Research depth: {query.depth}")
        report.append(f"- Time focus: {query.time_sensitivity}")
        report.append(f"- Stages completed: {len(previous_results)}")
        report.append(f"- Completion time: {time.ctime()}")
        report.append("")
        
        return "\n".join(report)
    
    def _generate_executive_summary(self, query: ResearchQuery,
                                  previous_results: Dict[str, StageResult]) -> str:
        """Generate executive summary."""
        return f"""
This research report provides {query.depth} analysis of {query.topic}. 
The research was conducted with a focus on {query.time_sensitivity} information 
and includes comprehensive coverage of key aspects.

Key findings include important insights relevant to the topic, with analysis 
supported by multiple sources and validated through systematic review.

The research methodology employed a multi-stage pipeline ensuring thorough 
investigation and reliable conclusions.
"""
    
    def _generate_recommendations(self, query: ResearchQuery,
                                previous_results: Dict[str, StageResult]) -> str:
        """Generate recommendations section."""
        return f"""
Based on the research findings, the following recommendations are proposed:

1. **Immediate actions** - Steps that can be taken now based on current understanding
2. **Further research** - Areas requiring additional investigation
3. **Monitoring** - Aspects to track for future developments
4. **Implementation** - Practical applications of research findings

These recommendations are tailored to the {query.depth} depth of research 
conducted and focus on {query.time_sensitivity} considerations.
"""
    
    def _generate_sources_section(self, query: ResearchQuery) -> str:
        """Generate sources section."""
        return f"""
The research drew upon multiple sources including:

1. **Academic literature** - Peer-reviewed papers and studies
2. **Industry reports** - Market analysis and trend data
3. **Official publications** - Government and organizational documents
4. **News media** - Current coverage and analysis
5. **Expert opinions** - Specialist perspectives and insights

Sources were selected based on relevance to {query.topic} with emphasis on 
{query.time_sensitivity} information and credibility assessment.
"""


# Example usage
async def example():
    """Example of using the research pipeline."""
    pipeline = ResearchPipeline()
    
    # Create a test query
    query = ResearchQuery(
        original_text="research quantum computing applications",
        topic="quantum computing applications",
        depth="standard",
        time_sensitivity="current",
        scope=[],
        constraints=[],
        requires_citations=True,
        requires_analysis=True,
        requires_recommendations=True
    )
    
    # Execute pipeline
    results = await pipeline.execute_pipeline(query)
    
    # Print results
    print(f"Pipeline completed with {len(results)} stages")
    for stage_name, result in results.items():
        print(f"\n{stage_name}: {result.execution_time:.2f}s")
        print(f"Success: {result.success}")
        if result.content:
            print(f"Content preview: {result.content[:100]}...")


if __name__ == "__main__":
    asyncio.run(example())