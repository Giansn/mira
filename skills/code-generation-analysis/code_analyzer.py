#!/usr/bin/env python3
"""
Code Analyzer - Static analysis, security scanning, and code review
"""

import re
import ast
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import hashlib


@dataclass
class CodeIssue:
    """Code issue found during analysis."""
    severity: str  # critical, high, medium, low, info
    category: str  # security, performance, style, bug, best_practice
    location: str  # file:line or function:line
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID


@dataclass
class CodeAnalysisResult:
    """Result of code analysis."""
    language: str
    lines_analyzed: int
    issues_found: int
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    issues: List[CodeIssue]
    summary: str
    confidence: float
    analysis_time: float


class CodeAnalyzer:
    """Analyze code for issues, security vulnerabilities, and best practices."""
    
    def __init__(self):
        # Security patterns to detect
        self.security_patterns = {
            'eval_usage': {
                'pattern': r'\beval\s*\(',
                'severity': 'critical',
                'category': 'security',
                'description': 'Use of eval() function',
                'recommendation': 'Avoid eval() as it can execute arbitrary code',
                'cwe_id': 'CWE-95'
            },
            'exec_usage': {
                'pattern': r'\bexec\s*\(',
                'severity': 'critical',
                'category': 'security',
                'description': 'Use of exec() function',
                'recommendation': 'Avoid exec() or sanitize inputs thoroughly',
                'cwe_id': 'CWE-78'
            },
            'sql_injection': {
                'pattern': r'f"?["\']\s*\+\s*\w+\s*\+\s*["\']',
                'severity': 'high',
                'category': 'security',
                'description': 'Potential SQL injection via string concatenation',
                'recommendation': 'Use parameterized queries or ORM',
                'cwe_id': 'CWE-89'
            },
            'hardcoded_password': {
                'pattern': r'password\s*=\s*["\'][^"\']+["\']',
                'severity': 'high',
                'category': 'security',
                'description': 'Hardcoded password in source code',
                'recommendation': 'Store passwords in environment variables or secure vault',
                'cwe_id': 'CWE-798'
            },
            'insecure_random': {
                'pattern': r'random\.(randint|choice|random)\(',
                'severity': 'medium',
                'category': 'security',
                'description': 'Use of insecure random for security purposes',
                'recommendation': 'Use secrets module for cryptographic randomness',
                'cwe_id': 'CWE-338'
            }
        }
        
        # Performance patterns
        self.performance_patterns = {
            'nested_loop': {
                'pattern': r'for\s+\w+\s+in\s+\w+:\s*\n\s*for\s+\w+\s+in\s+\w+:',
                'severity': 'medium',
                'category': 'performance',
                'description': 'Nested loops with O(n²) complexity',
                'recommendation': 'Consider using dictionaries or sets for O(1) lookups'
            },
            'string_concat_in_loop': {
                'pattern': r'for\s+\w+\s+in\s+\w+:\s*\n\s*\w+\s*\+=\s*\w+',
                'severity': 'medium',
                'category': 'performance',
                'description': 'String concatenation in loop',
                'recommendation': 'Use list comprehension with join()'
            },
            'unnecessary_computation': {
                'pattern': r'for\s+\w+\s+in\s+\w+:\s*\n\s*\w+\s*=\s*\w+\s*\.\s*(lower|upper|strip)\(\)',
                'severity': 'low',
                'category': 'performance',
                'description': 'Repeated computation in loop',
                'recommendation': 'Compute once outside loop'
            }
        }
        
        # Style and best practice patterns
        self.style_patterns = {
            'missing_docstring': {
                'pattern': r'def\s+\w+\s*\([^)]*\):\s*\n(?!\s*""")',
                'severity': 'low',
                'category': 'style',
                'description': 'Function missing docstring',
                'recommendation': 'Add docstring describing function purpose and parameters'
            },
            'long_function': {
                'pattern': r'(?s)def\s+\w+\s*\([^)]*\):\s*.*?(?=\n\s*def|\Z)',
                'severity': 'medium',
                'category': 'style',
                'description': 'Function longer than 50 lines',
                'recommendation': 'Break into smaller, focused functions'
            },
            'magic_number': {
                'pattern': r'\b\d{3,}\b',
                'severity': 'low',
                'category': 'style',
                'description': 'Magic number (hardcoded numeric literal)',
                'recommendation': 'Define as named constant with descriptive name'
            },
            'broad_except': {
                'pattern': r'except\s*(Exception|BaseException):',
                'severity': 'medium',
                'category': 'best_practice',
                'description': 'Catching overly broad exception',
                'recommendation': 'Catch specific exceptions or re-raise with context'
            }
        }
        
        # Bug patterns
        self.bug_patterns = {
            'uninitialized_variable': {
                'pattern': r'if\s+\w+:\s*\n\s*\w+\s*=\s*\w+\s*\nelse:\s*\n\s*#',
                'severity': 'medium',
                'category': 'bug',
                'description': 'Variable may be uninitialized in some code paths',
                'recommendation': 'Initialize variable before conditional branches'
            },
            'off_by_one': {
                'pattern': r'range\s*\(\s*len\s*\(\s*\w+\s*\)\s*\)',
                'severity': 'medium',
                'category': 'bug',
                'description': 'Potential off-by-one error with range(len())',
                'recommendation': 'Consider using enumerate() or range(len()-1) if appropriate'
            },
            'comparison_with_none': {
                'pattern': r'\w+\s*==\s*None',
                'severity': 'low',
                'category': 'bug',
                'description': 'Comparison with None using == instead of is',
                'recommendation': 'Use "is None" or "is not None" for identity comparison'
            }
        }
    
    def analyze_code(self, code: str, language: str = 'python') -> CodeAnalysisResult:
        """Analyze code for issues."""
        start_time = time.time()
        
        # Count lines
        lines = code.split('\n')
        lines_analyzed = len(lines)
        
        # Initialize issues
        issues = []
        
        # Run analysis based on language
        if language == 'python':
            issues.extend(self._analyze_python(code))
        elif language == 'javascript':
            issues.extend(self._analyze_javascript(code))
        else:
            # Generic analysis for other languages
            issues.extend(self._analyze_generic(code))
        
        # Categorize issues
        issues_by_severity = self._categorize_by_severity(issues)
        issues_by_category = self._categorize_by_category(issues)
        
        # Generate summary
        summary = self._generate_summary(issues, lines_analyzed)
        
        # Calculate confidence (simplified)
        confidence = min(0.95, 0.7 + (len(issues) / max(lines_analyzed, 1)) * 0.25)
        
        return CodeAnalysisResult(
            language=language,
            lines_analyzed=lines_analyzed,
            issues_found=len(issues),
            issues_by_severity=issues_by_severity,
            issues_by_category=issues_by_category,
            issues=issues,
            summary=summary,
            confidence=confidence,
            analysis_time=time.time() - start_time
        )
    
    def _analyze_python(self, code: str) -> List[CodeIssue]:
        """Analyze Python code."""
        issues = []
        
        try:
            # Parse AST for deeper analysis
            tree = ast.parse(code)
            
            # AST-based checks
            issues.extend(self._analyze_python_ast(tree, code))
            
        except SyntaxError as e:
            # Code has syntax errors
            issues.append(CodeIssue(
                severity='critical',
                category='bug',
                location=f'syntax:{e.lineno}',
                description=f'Syntax error: {e.msg}',
                recommendation='Fix syntax error before further analysis',
                code_snippet=code.split('\n')[e.lineno-1] if e.lineno else None
            ))
        
        # Pattern-based checks
        issues.extend(self._analyze_with_patterns(code, 'python'))
        
        return issues
    
    def _analyze_python_ast(self, tree: ast.AST, original_code: str) -> List[CodeIssue]:
        """Analyze Python AST for specific issues."""
        issues = []
        lines = original_code.split('\n')
        
        class Analyzer(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                self.current_function = None
            
            def visit_FunctionDef(self, node):
                # Check function length
                func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
                if func_lines > 50:
                    self.issues.append(CodeIssue(
                        severity='medium',
                        category='style',
                        location=f'{node.name}:{node.lineno}',
                        description=f'Function {node.name} is {func_lines} lines long',
                        recommendation='Break into smaller functions',
                        code_snippet='\n'.join(lines[node.lineno-1:min(node.end_lineno, node.lineno+5)])
                    ))
                
                # Check for docstring
                if not ast.get_docstring(node):
                    self.issues.append(CodeIssue(
                        severity='low',
                        category='style',
                        location=f'{node.name}:{node.lineno}',
                        description=f'Function {node.name} missing docstring',
                        recommendation='Add docstring describing purpose and parameters',
                        code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else None
                    ))
                
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = None
            
            def visit_ExceptHandler(self, node):
                # Check for bare except
                if node.type is None:
                    self.issues.append(CodeIssue(
                        severity='medium',
                        category='best_practice',
                        location=f'except:{node.lineno}',
                        description='Bare except clause catches all exceptions',
                        recommendation='Specify exception types or handle and re-raise',
                        code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else None
                    ))
                self.generic_visit(node)
        
        analyzer = Analyzer()
        analyzer.visit(tree)
        return analyzer.issues
    
    def _analyze_javascript(self, code: str) -> List[CodeIssue]:
        """Analyze JavaScript code."""
        issues = []
        
        # Pattern-based checks for JavaScript
        js_security_patterns = {
            'eval_js': {
                'pattern': r'\beval\s*\(',
                'severity': 'critical',
                'category': 'security',
                'description': 'Use of eval() in JavaScript',
                'recommendation': 'Avoid eval() - use JSON.parse() or Function constructor with caution',
                'cwe_id': 'CWE-95'
            },
            'inner_html': {
                'pattern': r'\.innerHTML\s*=',
                'severity': 'high',
                'category': 'security',
                'description': 'Direct assignment to innerHTML',
                'recommendation': 'Use textContent or sanitize inputs to prevent XSS',
                'cwe_id': 'CWE-79'
            },
            'console_log': {
                'pattern': r'console\.log\(',
                'severity': 'low',
                'category': 'best_practice',
                'description': 'Console.log in production code',
                'recommendation': 'Remove or wrap with environment check'
            }
        }
        
        for pattern_name, pattern_info in js_security_patterns.items():
            matches = re.finditer(pattern_info['pattern'], code, re.MULTILINE)
            for match in matches:
                line_no = code[:match.start()].count('\n') + 1
                issues.append(CodeIssue(
                    severity=pattern_info['severity'],
                    category=pattern_info['category'],
                    location=f'line:{line_no}',
                    description=pattern_info['description'],
                    recommendation=pattern_info['recommendation'],
                    code_snippet=self._get_line_at_position(code, match.start()),
                    cwe_id=pattern_info.get('cwe_id')
                ))
        
        return issues
    
    def _analyze_generic(self, code: str) -> List[CodeIssue]:
        """Generic code analysis for any language."""
        issues = []
        
        # Check for common issues
        lines = code.split('\n')
        
        # Check line length
        for i, line in enumerate(lines, 1):
            if len(line) > 100:  # Long line
                issues.append(CodeIssue(
                    severity='low',
                    category='style',
                    location=f'line:{i}',
                    description=f'Line {i} is {len(line)} characters long',
                    recommendation='Break into multiple lines for readability',
                    code_snippet=line[:100] + '...'
                ))
        
        # Check for TODO comments
        for i, line in enumerate(lines, 1):
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                issues.append(CodeIssue(
                    severity='low',
                    category='best_practice',
                    location=f'line:{i}',
                    description='TODO/FIXME comment found',
                    recommendation='Address TODO items before production deployment',
                    code_snippet=line
                ))
        
        return issues
    
    def _analyze_with_patterns(self, code: str, language: str) -> List[CodeIssue]:
        """Analyze code using pattern matching."""
        issues = []
        
        # Combine all patterns
        all_patterns = {}
        all_patterns.update(self.security_patterns)
        all_patterns.update(self.performance_patterns)
        all_patterns.update(self.style_patterns)
        all_patterns.update(self.bug_patterns)
        
        for pattern_name, pattern_info in all_patterns.items():
            matches = re.finditer(pattern_info['pattern'], code, re.MULTILINE | re.DOTALL)
            for match in matches:
                line_no = code[:match.start()].count('\n') + 1
                issues.append(CodeIssue(
                    severity=pattern_info['severity'],
                    category=pattern_info['category'],
                    location=f'line:{line_no}',
                    description=pattern_info['description'],
                    recommendation=pattern_info['recommendation'],
                    code_snippet=self._get_line_at_position(code, match.start()),
                    cwe_id=pattern_info.get('cwe_id')
                ))
        
        return issues
    
    def _get_line_at_position(self, code: str, position: int) -> str:
        """Get the line containing a specific position."""
        lines = code.split('\n')
        char_count = 0
        for i, line in enumerate(lines):
            char_count += len(line) + 1  # +1 for newline
            if char_count > position:
                return line
        return lines[-1] if lines else ""
    
    def _categorize_by_severity(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """Categorize issues by severity."""
        categories = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for issue in issues:
            categories[issue.severity] += 1
        return categories
    
    def _categorize_by_category(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """Categorize issues by category."""
        categories = {}
        for issue in issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1
        return categories
    
    def _generate_summary(self, issues: List[CodeIssue], lines_analyzed: int) -> str:
        """Generate analysis summary."""
        if not issues:
            return "No issues found. Code appears clean and follows best practices."
        
        # Count critical/high issues
        critical_high = sum(1 for i in issues if i.severity in ['critical', 'high'])
        
        if critical_high > 0:
            return f"Found {critical_high} critical/high priority issues that should be addressed immediately."
        elif len(issues) > 10:
            return f"Found {len(issues)} issues. Consider refactoring to improve code quality."
        else:
            return f"Found {len(issues)} minor issues. Code quality is acceptable."
    
    def generate_report(self, result: CodeAnalysisResult) -> str:
        """Generate formatted analysis report."""
        lines = []
        
        # Header
        lines.append("# Code Analysis Report")
        lines.append("")
        lines.append(f"**Language**: {result.language}")
        lines.append(f"**Lines analyzed**: {result.lines_analyzed}")
        lines.append(f"**Issues found**: {result.issues_found}")
        lines.append(f"**Analysis time**: {result.analysis_time:.2f}s")
        lines.append(f"**Confidence**: {result.confidence:.2f}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append(result.summary)
        lines.append("")
        
        # Statistics
        lines.append("## Statistics")
        lines.append("### By Severity")
        for severity, count in result.issues_by_severity.items():
            if count > 0:
                lines.append(f"- **{severity.title()}**: {count}")
        
        lines.append("")
        lines.append("### By Category")
        for category, count in result.issues_by_category.items():
            if count > 0:
                lines.append(f"- **{category.replace('_', ' ').title()}**: {count}")
        
        lines.append("")
        
        # Detailed Issues
        if result.issues:
            lines.append("## Detailed Issues")
            lines.append("")
            
            # Group by severity
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                severity_issues = [i for i in result.issues if i.severity == severity]
                if severity_issues:
                    lines.append(f"### {severity.title()} Priority Issues")
                    lines.append("")
                    
                    for i, issue in enumerate(severity_issues, 1):
                        lines.append(f"#### {i}. {issue.description}")
                        lines.append(f"- **Location**: {issue.location}")
                        lines.append(f"- **Category**: {issue.category}")
                        if issue.cwe_id:
                            lines.append(f"- **CWE**: {issue.cwe_id}")
                        lines.append(f"- **Recommendation**: {issue.recommendation}")
                        if issue.code_snippet:
                            lines.append(f"- **Code**: `{issue.code_snippet[:100]}{'...' if len(issue.code_snippet) > 100 else ''}`")
                        if issue.fix_suggestion:
                            lines.append(f"- **Fix suggestion**: {issue.fix_suggestion}")
                        lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        
        if result.issues_by_severity.get('critical', 0) > 0:
            lines.append("🚨 **Immediate Action Required**:")
            lines.append("1. Address all critical security issues first")
            lines.append("2. Review high-priority performance issues")
            lines.append("3. Test fixes thoroughly")
            lines.append("")
        
        if result.issues_by_severity.get('high', 0) > 0:
            lines.append("⚠️ **High Priority**:")
            lines.append("1. Fix security vulnerabilities")
            lines.append("2. Address performance bottlenecks")
            lines.append("3. Review and fix bugs")
            lines.append("")
        
        if result.issues_by_severity.get('medium', 0) > 0:
            lines.append("📝 **Medium Priority**:")
            lines.append("1. Improve code style and readability")
            lines.append("2. Add missing documentation")
            lines.append("3. Follow best practices")
            lines.append("")
        
        if result.issues_by_severity.get('low', 0) > 0:
            lines.append("💡 **Low Priority (Nice to have)**:")
            lines.append("1. Clean up TODO comments")
            lines.append("2. Optimize minor performance issues")
            lines.append("3. Improve code consistency")
            lines.append("")
        
        # Next Steps
        lines.append("## Next Steps")
        lines.append("1. **Prioritize fixes** by severity and impact")
        lines.append("2. **Test thoroughly** after each fix")
        lines.append("3. **Review changes** with team if applicable")
        lines.append("4. **Consider automated testing** to prevent regressions")
        lines.append("5. **Document decisions** for future reference")
        
        return "\n".join(lines)


# Example usage
def example():
    """Example of using the code analyzer."""
    analyzer = CodeAnalyzer()
    
    # Example Python code with issues
    python_code = '''
def process_data(user_input):
    # Security issue: eval
    result = eval(user_input)
    
    # Performance issue: nested loops
    data = []
    for i in range(100):
        for j in range(100):
            data.append(i * j)
    
    # Style issue: no docstring
    return result

# Bug: comparison with None
if process_data("1+1") == None:
    print("No result")
'''
    
    print("Analyzing Python code...")
    result = analyzer.analyze_code(python_code, 'python')
    report = analyzer.generate_report(result)
    print(report)
    
    # Example JavaScript code
    js_code = '''
function updateContent(userInput) {
    // Security issue: innerHTML
    document.getElementById("content").innerHTML = userInput;
    
    // Debug code left in
    console.log("Updated content:", userInput);
    
    return true;
}
'''
    
    print("\n" + "="*80 + "\n")
    print("Analyzing JavaScript code...")
    result = analyzer.analyze_code(js_code, 'javascript')
    report = analyzer.generate_report(result)
    print(report)


if __name__ == "__main__":
    example()