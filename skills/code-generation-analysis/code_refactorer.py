#!/usr/bin/env python3
"""
Code Refactorer - Code optimization, restructuring, and improvement
"""

import re
import ast
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class RefactoringSuggestion:
    """Suggestion for code refactoring."""
    type: str  # extract_method, rename_variable, simplify_logic, etc.
    location: str  # file:line or function:line
    description: str
    current_code: str
    suggested_code: str
    benefits: List[str]
    complexity_change: str  # reduced, increased, same


@dataclass
class RefactoringResult:
    """Result of code refactoring analysis."""
    original_code: str
    refactored_code: str
    suggestions: List[RefactoringSuggestion]
    improvements: Dict[str, Any]
    confidence: float
    refactoring_time: float


class CodeRefactorer:
    """Refactor code for better structure, performance, and maintainability."""
    
    def __init__(self):
        self.refactoring_patterns = {
            'extract_method': {
                'description': 'Extract repeated code into method',
                'min_lines': 3,
                'min_occurrences': 2
            },
            'rename_variable': {
                'description': 'Rename unclear variable name',
                'pattern': r'\b([a-z]{1,2}|[xy]|[ij])\b(?=\s*=)',
                'exceptions': ['i', 'j', 'x', 'y', 'z']  # Common loop variables
            },
            'simplify_conditional': {
                'description': 'Simplify complex conditional logic',
                'pattern': r'if\s+.*?\s*and\s+.*?\s*and\s+.*?:',
                'max_conditions': 2
            },
            'remove_dead_code': {
                'description': 'Remove unused code',
                'pattern': r'^\s*(def|class)\s+\w+\s*\([^)]*\):\s*\n(?:\s+.*\n)*?(?=\n\s*(?:def|class|\Z))',
                'check_usage': True
            },
            'optimize_loop': {
                'description': 'Optimize loop performance',
                'patterns': [
                    r'for\s+\w+\s+in\s+range\(len\(\w+\)\):',
                    r'for\s+\w+\s+in\s+\w+\.keys\(\):',
                    r'for\s+\w+\s+in\s+\w+\.values\(\):'
                ]
            },
            'improve_error_handling': {
                'description': 'Improve error handling',
                'pattern': r'try:\s*\n\s*.*?\s*\nexcept\s+(Exception|BaseException):',
                'suggestion': 'Catch specific exceptions'
            }
        }
    
    def analyze_for_refactoring(self, code: str, language: str = 'python') -> RefactoringResult:
        """Analyze code for refactoring opportunities."""
        start_time = time.time()
        
        suggestions = []
        
        if language == 'python':
            suggestions.extend(self._analyze_python_refactoring(code))
        elif language == 'javascript':
            suggestions.extend(self._analyze_javascript_refactoring(code))
        else:
            suggestions.extend(self._analyze_generic_refactoring(code))
        
        # Apply refactorings to generate improved code
        refactored_code = self._apply_refactorings(code, suggestions)
        
        # Calculate improvements
        improvements = self._calculate_improvements(code, refactored_code, suggestions)
        
        # Calculate confidence
        confidence = self._calculate_confidence(suggestions, improvements)
        
        return RefactoringResult(
            original_code=code,
            refactored_code=refactored_code,
            suggestions=suggestions,
            improvements=improvements,
            confidence=confidence,
            refactoring_time=time.time() - start_time
        )
    
    def _analyze_python_refactoring(self, code: str) -> List[RefactoringSuggestion]:
        """Analyze Python code for refactoring opportunities."""
        suggestions = []
        lines = code.split('\n')
        
        try:
            tree = ast.parse(code)
            
            # Find long functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
                    if func_lines > 30:
                        # Extract function body for analysis
                        func_code = '\n'.join(lines[node.lineno:node.end_lineno])
                        
                        # Check for repeated patterns
                        repeated_patterns = self._find_repeated_patterns(func_code)
                        if repeated_patterns:
                            suggestions.append(RefactoringSuggestion(
                                type='extract_method',
                                location=f'{node.name}:{node.lineno}',
                                description=f'Function {node.name} contains repeated code patterns',
                                current_code=func_code[:200] + '...' if len(func_code) > 200 else func_code,
                                suggested_code='# Extract repeated patterns into helper methods',
                                benefits=['Reduced duplication', 'Easier maintenance', 'Better testability'],
                                complexity_change='reduced'
                            ))
            
            # Find complex conditionals
            for i, line in enumerate(lines, 1):
                if ' and ' in line and line.count(' and ') >= 2:
                    suggestions.append(RefactoringSuggestion(
                        type='simplify_conditional',
                        location=f'line:{i}',
                        description='Complex conditional with multiple AND operators',
                        current_code=line,
                        suggested_code='# Consider extracting conditions into variables or methods',
                        benefits=['Improved readability', 'Easier debugging'],
                        complexity_change='reduced'
                    ))
            
            # Find poor variable names
            for i, line in enumerate(lines, 1):
                # Look for single-letter variable assignments (excluding common ones)
                matches = re.finditer(r'\b([a-df-hk-oq-w])\b\s*=', line)
                for match in matches:
                    var_name = match.group(1)
                    suggestions.append(RefactoringSuggestion(
                        type='rename_variable',
                        location=f'line:{i}',
                        description=f'Unclear variable name: {var_name}',
                        current_code=line,
                        suggested_code=f'# Rename {var_name} to descriptive name',
                        benefits=['Better understanding', 'Easier maintenance'],
                        complexity_change='same'
                    ))
        
        except SyntaxError:
            # Can't parse, skip AST analysis
            pass
        
        return suggestions
    
    def _analyze_javascript_refactoring(self, code: str) -> List[RefactoringSuggestion]:
        """Analyze JavaScript code for refactoring opportunities."""
        suggestions = []
        lines = code.split('\n')
        
        # Check for callback hell (nested callbacks)
        indent_level = 0
        for i, line in enumerate(lines, 1):
            # Count indentation
            current_indent = len(line) - len(line.lstrip())
            
            # Look for function calls with callbacks
            if '.then(' in line or '.catch(' in line or 'function(' in line:
                indent_level = current_indent // 4  # Assuming 4-space indentation
            
            # If we have deep nesting
            if indent_level > 3:
                suggestions.append(RefactoringSuggestion(
                    type='reduce_nesting',
                    location=f'line:{i}',
                    description='Deep callback nesting (callback hell)',
                    current_code=line,
                    suggested_code='# Consider using async/await or Promise chains',
                    benefits=['Better readability', 'Easier error handling'],
                    complexity_change='reduced'
                ))
        
        # Check for var usage (prefer let/const)
        for i, line in enumerate(lines, 1):
            if ' var ' in line:
                suggestions.append(RefactoringSuggestion(
                    type='modernize_declaration',
                    location=f'line:{i}',
                    description='Using var instead of let/const',
                    current_code=line,
                    suggested_code=line.replace(' var ', ' const ') if not line.strip().endswith('=') else line.replace(' var ', ' let '),
                    benefits=['Better scoping', 'Modern JavaScript'],
                    complexity_change='same'
                ))
        
        return suggestions
    
    def _analyze_generic_refactoring(self, code: str) -> List[RefactoringSuggestion]:
        """Generic refactoring analysis."""
        suggestions = []
        lines = code.split('\n')
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                suggestions.append(RefactoringSuggestion(
                    type='split_long_line',
                    location=f'line:{i}',
                    description=f'Line {i} is {len(line)} characters long',
                    current_code=line,
                    suggested_code='# Split into multiple lines for readability',
                    benefits=['Better readability', 'Easier code review'],
                    complexity_change='same'
                ))
        
        # Check for magic numbers
        for i, line in enumerate(lines, 1):
            # Look for numbers that aren't 0, 1, or common values
            numbers = re.findall(r'\b([2-9]\d*|1[0-9]+)\b', line)
            for num in numbers:
                suggestions.append(RefactoringSuggestion(
                    type='replace_magic_number',
                    location=f'line:{i}',
                    description=f'Magic number: {num}',
                    current_code=line,
                    suggested_code=f'# Define constant for {num} with descriptive name',
                    benefits=['Better understanding', 'Easier maintenance'],
                    complexity_change='same'
                ))
        
        return suggestions
    
    def _find_repeated_patterns(self, code: str) -> List[str]:
        """Find repeated code patterns."""
        lines = code.split('\n')
        patterns = {}
        
        # Simple pattern detection: identical lines
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                patterns[stripped] = patterns.get(stripped, 0) + 1
        
        # Return patterns that appear multiple times
        return [pattern for pattern, count in patterns.items() if count >= 2]
    
    def _apply_refactorings(self, code: str, suggestions: List[RefactoringSuggestion]) -> str:
        """Apply refactoring suggestions to code."""
        if not suggestions:
            return code
        
        lines = code.split('\n')
        
        # For demonstration, we'll just mark suggestions in comments
        # In a real implementation, this would actually transform the code
        for suggestion in suggestions:
            if suggestion.type == 'rename_variable':
                # Mark the line with a comment
                line_num = int(suggestion.location.split(':')[1]) - 1
                if line_num < len(lines):
                    lines[line_num] = f'{lines[line_num]}  # TODO: {suggestion.description}'
        
        return '\n'.join(lines)
    
    def _calculate_improvements(self, original: str, refactored: str, 
                               suggestions: List[RefactoringSuggestion]) -> Dict[str, Any]:
        """Calculate improvements from refactoring."""
        orig_lines = original.split('\n')
        refac_lines = refactored.split('\n')
        
        improvements = {
            'lines_changed': len([i for i in range(min(len(orig_lines), len(refac_lines))) 
                                 if orig_lines[i] != refac_lines[i]]),
            'suggestions_applied': len(suggestions),
            'complexity_reduction': sum(1 for s in suggestions if s.complexity_change == 'reduced'),
            'readability_improvement': len([s for s in suggestions if s.type in 
                                           ['rename_variable', 'simplify_conditional', 'split_long_line']]),
            'maintainability_improvement': len([s for s in suggestions if s.type in 
                                               ['extract_method', 'remove_dead_code']])
        }
        
        # Calculate estimated benefits
        total_benefits = sum(len(s.benefits) for s in suggestions)
        improvements['total_benefits'] = total_benefits
        
        return improvements
    
    def _calculate_confidence(self, suggestions: List[RefactoringSuggestion], 
                             improvements: Dict[str, Any]) -> float:
        """Calculate confidence score for refactoring suggestions."""
        if not suggestions:
            return 0.8  # High confidence if no issues found
        
        # Base confidence
        confidence = 0.6
        
        # Adjust based on suggestion types
        critical_suggestions = ['extract_method', 'simplify_conditional', 'improve_error_handling']
        for suggestion in suggestions:
            if suggestion.type in critical_suggestions:
                confidence += 0.05
            else:
                confidence += 0.02
        
        # Cap at 0.95
        return min(0.95, confidence)
    
    def generate_refactoring_report(self, result: RefactoringResult) -> str:
        """Generate formatted refactoring report."""
        lines = []
        
        # Header
        lines.append("# Code Refactoring Analysis")
        lines.append("")
        lines.append(f"**Original lines**: {len(result.original_code.split('\\n'))}")
        lines.append(f"**Suggestions found**: {len(result.suggestions)}")
        lines.append(f"**Analysis time**: {result.refactoring_time:.2f}s")
        lines.append(f"**Confidence**: {result.confidence:.2f}")
        lines.append("")
        
        # Improvements summary
        lines.append("## Improvements Summary")
        lines.append(f"- **Lines to change**: {result.improvements['lines_changed']}")
        lines.append(f"- **Complexity reduction opportunities**: {result.improvements['complexity_reduction']}")
        lines.append(f"- **Readability improvements**: {result.improvements['readability_improvement']}")
        lines.append(f"- **Maintainability improvements**: {result.improvements['maintainability_improvement']}")
        lines.append(f"- **Total benefits identified**: {result.improvements['total_benefits']}")
        lines.append("")
        
        # Detailed suggestions
        if result.suggestions:
            lines.append("## Refactoring Suggestions")
            lines.append("")
            
            # Group by type
            suggestions_by_type = {}
            for suggestion in result.suggestions:
                suggestions_by_type.setdefault(suggestion.type, []).append(suggestion)
            
            for refactor_type, type_suggestions in suggestions_by_type.items():
                lines.append(f"### {refactor_type.replace('_', ' ').title()}")
                lines.append("")
                
                for i, suggestion in enumerate(type_suggestions, 1):
                    lines.append(f"#### Suggestion {i}: {suggestion.location}")
                    lines.append(f"- **Description**: {suggestion.description}")
                    lines.append(f"- **Current code**: `{suggestion.current_code[:80]}{'...' if len(suggestion.current_code) > 80 else ''}`")
                    lines.append(f"- **Suggested change**: {suggestion.suggested_code}")
                    lines.append(f"- **Benefits**: {', '.join(suggestion.benefits)}")
                    lines.append(f"- **Complexity**: {suggestion.complexity_change}")
                    lines.append("")
        
        # Refactored code preview
        lines.append("## Refactored Code Preview")
        lines.append("")
        lines.append("```")
        # Show first 20 lines of refactored code
        refac_lines = result.refactored_code.split('\n')
        preview_lines = refac_lines[:20]
        lines.extend(preview_lines)
        if len(refac_lines) > 20:
            lines.append("...")
        lines.append("```")
        lines.append("")
        
        # Implementation plan
        lines.append("## Implementation Plan")
        lines.append("")
        lines.append("1. **Start with high-impact changes**:")
        lines.append("   - Extract repeated methods first")
        lines.append("   - Simplify complex conditionals")
        lines.append("   - Improve error handling")
        lines.append("")
        lines.append("2. **Then improve readability**:")
        lines.append("   - Rename unclear variables")
        lines.append("   - Split long lines")
        lines.append("   - Replace magic numbers")
        lines.append("")
        lines.append("3. **Finally, clean up**:")
        lines.append("   - Remove dead code")
        lines.append("   - Add documentation")
        lines.append("   - Run tests after each change")
        lines.append("")
        lines.append("4. **Testing strategy**:")
        lines.append("   - Run existing tests after each refactoring")
        lines.append("   - Add new tests for extracted methods")
        lines.append("   - Verify behavior remains unchanged")
        
        return "\n".join(lines)


# Example usage
def example():
    """Example of using the code refactorer."""
    refactorer = CodeRefactorer()
    
    # Example Python code needing refactoring
    python_code = '''
def calculate(data):
    # Complex conditional
    if data and data.get("value") and data.get("value") > 0 and data.get("type") == "positive":
        result = data["value"] * 2
    
    # Repeated pattern
    x = 1
    y = 2
    z = x + y
    
    a = 3
    b = 4
    c = a + b
    
    # Long line
    long_variable_name_with_many_characters = "this is a very long string that should probably be split into multiple lines for better readability"
    
    return result
'''
    
    print("Analyzing Python code for refactoring...")
    result = refactorer.analyze_for_refactoring(python_code, 'python')
    report = refactorer.generate_refactoring_report(result)
    print(report)
    
    # Example JavaScript code
    js_code = '''
function processData(data) {
    var result = 0;
    
    // Callback hell pattern
    getData(function(err, data1) {
        if (err) {
            processMore(data1