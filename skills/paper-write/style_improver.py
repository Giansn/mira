#!/usr/bin/env python3
"""
FHNW Style Improver - Detects and improves AI-stiff academic writing
"""

import re
from typing import List, Tuple, Dict

class StyleImprover:
    """Improve academic writing style by removing AI-stiffness"""
    
    def __init__(self):
        # Patterns of AI-stiff writing with improvements
        self.patterns = [
            # Passive constructions
            (r'Es kann (?:festgestellt|gesehen|verstanden) werden, dass', 
             'Die Analyse zeigt, dass'),
            (r'Es lässt sich (?:feststellen|zeigen|beobachten), dass',
             'Untersuchungen zeigen, dass'),
            (r'Es ist (?:zu beachten|wichtig|notwendig), dass',
             '(omit or state directly)'),
            (r'Es wurde (?:gezeigt|festgestellt|nachgewiesen), dass',
             'Die Studie zeigt, dass'),
            
            # Nominalizations
            (r'Die Durchführung (?:einer|der) (?:Untersuchung|Analyse|Studie)',
             'Wir untersuchen'),
            (r'Die Anwendung (?:von|der) (?:Methode|Theorie)',
             'Die Methode/Theorie anwenden'),
            (r'Die Berücksichtigung (?:von|der)',
             'Berücksichtigen wir'),
            
            # Hedging language
            (r'Möglicherweise könnte man (?:argumentieren|sagen|feststellen), dass',
             'Argumentativ lässt sich zeigen, dass'),
            (r'In gewissem Sinne (?:könnte|kann) man (?:sagen|behaupten), dass',
             'Es zeigt sich, dass'),
            (r'Es scheint, als ob|Es scheint, dass',
             'Die Evidenz deutet darauf hin, dass'),
            
            # Empty phrases
            (r'Es ist (?:interessant|wichtig|bemerkenswert) zu (?:bemerken|erwähnen|betonen), dass',
             '(omit, state directly)'),
            (r'An dieser Stelle (?:soll|muss|kann) (?:erwähnt|betont|festgehalten) werden, dass',
             '(omit, state directly)'),
            (r'Wie bereits (?:erwähnt|gesagt|festgestellt)',
             '(omit or refer specifically)'),
            
            # Overly complex
            (r'Im Rahmen (?:der|dieser) (?:Untersuchung|Studie|Arbeit)',
             'In dieser Arbeit'),
            (r'Auf der Grundlage (?:der|von) (?:vorliegenden|bereits erwähnten)',
             'Basierend auf'),
            (r'Im Hinblick auf (?:die|das)',
             'Hinsichtlich'),
            
            # AI-typical sentence starters
            (r'Zusammenfassend lässt sich sagen, dass',
             'Zusammenfassend zeigt sich, dass'),
            (r'Abschliessend kann (?:festgehalten|gesagt) werden, dass',
             'Abschliessend lässt sich konstatieren, dass'),
            (r'In diesem Zusammenhang (?:ist|sind)',
             'Damit verbunden sind'),
        ]
        
        # Positive patterns to encourage
        self.good_patterns = [
            r'Die Analyse zeigt, dass',
            r'Untersuchungen belegen, dass',
            r'Argumentativ lässt sich zeigen, dass',
            r'Es zeigt sich, dass',
            r'Die Evidenz deutet darauf hin, dass',
            r'Konkret bedeutet dies, dass',
            r'Daraus folgt, dass',
            r'Im Gegensatz dazu',
            r'Vergleichsweise betrachtet',
            r'Dies verweist auf',
        ]
    
    def improve_sentence(self, sentence: str) -> str:
        """Improve a single sentence by removing AI-stiffness"""
        original = sentence
        improved = sentence
        
        # Apply pattern replacements
        for pattern, replacement in self.patterns:
            if re.search(pattern, improved, re.IGNORECASE):
                improved = re.sub(pattern, replacement, improved, flags=re.IGNORECASE)
        
        # Check for remaining issues
        issues = self.detect_issues(improved)
        
        return improved, issues
    
    def detect_issues(self, text: str) -> List[Dict]:
        """Detect style issues in text"""
        issues = []
        
        # Check for passive voice
        passive_patterns = [
            r'Es kann .* werden',
            r'Es lässt sich .*',
            r'Es wurde .*',
            r'Es sind .*',
        ]
        
        for pattern in passive_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': 'passive_construction',
                    'text': match.group(),
                    'suggestion': 'Aktive Formulierung verwenden',
                    'severity': 'medium'
                })
        
        # Check for nominalizations
        nominalization_patterns = [
            r'Die \w+ung (?:von|der)',
            r'Das \w+en (?:von|der)',
            r'Eine \w+ung (?:von|der)',
        ]
        
        for pattern in nominalization_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': 'nominalization',
                    'text': match.group(),
                    'suggestion': 'Verbform verwenden',
                    'severity': 'low'
                })
        
        # Check for hedging
        hedging_patterns = [
            r'Möglicherweise',
            r'Vielleicht',
            r'Eventuell',
            r'In gewissem Sinne',
            r'Gewissermassen',
        ]
        
        for pattern in hedging_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': 'hedging',
                    'text': match.group(),
                    'suggestion': 'Direkter Ausdruck',
                    'severity': 'low'
                })
        
        # Check sentence length
        sentences = re.split(r'[.!?]', text)
        for i, sentence in enumerate(sentences):
            words = sentence.split()
            if len(words) > 35:
                issues.append({
                    'type': 'long_sentence',
                    'text': sentence[:50] + '...',
                    'suggestion': 'Satz in zwei kürzere Sätze teilen',
                    'severity': 'high'
                })
        
        return issues
    
    def analyze_text(self, text: str) -> Dict:
        """Complete style analysis of text"""
        sentences = re.split(r'[.!?]', text)
        
        results = {
            'total_sentences': len(sentences),
            'improved_sentences': [],
            'issues': [],
            'stats': {
                'passive_count': 0,
                'nominalization_count': 0,
                'hedging_count': 0,
                'long_sentence_count': 0,
                'ai_pattern_count': 0,
            }
        }
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            improved, issues = self.improve_sentence(sentence)
            
            results['improved_sentences'].append({
                'original': sentence.strip(),
                'improved': improved.strip(),
                'changed': sentence.strip() != improved.strip()
            })
            
            results['issues'].extend(issues)
            
            # Update stats
            for issue in issues:
                results['stats'][f"{issue['type']}_count"] += 1
                if issue['type'] in ['passive_construction', 'nominalization', 'hedging']:
                    results['stats']['ai_pattern_count'] += 1
        
        return results
    
    def generate_improvement_report(self, analysis: Dict) -> str:
        """Generate a human-readable improvement report"""
        report = []
        
        report.append("STYLE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Total sentences: {analysis['total_sentences']}")
        report.append(f"Sentences with issues: {len([s for s in analysis['improved_sentences'] if s['changed']])}")
        report.append("")
        
        # Statistics
        report.append("STATISTICS:")
        for key, value in analysis['stats'].items():
            if value > 0:
                report.append(f"  {key}: {value}")
        
        # Issues by severity
        high_issues = [i for i in analysis['issues'] if i['severity'] == 'high']
        medium_issues = [i for i in analysis['issues'] if i['severity'] == 'medium']
        low_issues = [i for i in analysis['issues'] if i['severity'] == 'low']
        
        report.append("")
        report.append("ISSUES BY SEVERITY:")
        report.append(f"  High: {len(high_issues)}")
        report.append(f"  Medium: {len(medium_issues)}")
        report.append(f"  Low: {len(low_issues)}")
        
        # Example improvements
        changed_sentences = [s for s in analysis['improved_sentences'] if s['changed']]
        if changed_sentences:
            report.append("")
            report.append("EXAMPLE IMPROVEMENTS:")
            for i, sentence in enumerate(changed_sentences[:3]):  # Show first 3
                report.append(f"  {i+1}. Original: {sentence['original'][:60]}...")
                report.append(f"     Improved: {sentence['improved'][:60]}...")
                report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        if analysis['stats']['passive_count'] > 0:
            report.append("  • Aktive statt passive Formulierungen verwenden")
        if analysis['stats']['nominalization_count'] > 0:
            report.append("  • Nominalisierungen durch Verben ersetzen")
        if analysis['stats']['hedging_count'] > 0:
            report.append("  • Direkte Aussagen statt vorsichtiger Formulierungen")
        if analysis['stats']['long_sentence_count'] > 0:
            report.append("  • Lange Sätze in kürzere teilen")
        
        report.append("")
        report.append("GENERAL TIPS:")
        report.append("  • Klare, direkte Aussagen bevorzugen")
        report.append("  • Aktiv statt Passiv verwenden")
        report.append("  • Konkrete Beispiele einfügen")
        report.append("  • Argumentationslinie deutlich machen")
        report.append("  • Fachbegriffe erklären, wo nötig")
        
        return "\n".join(report)
    
    def improve_full_text(self, text: str) -> str:
        """Improve entire text while preserving structure"""
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        improved_paragraphs = []
        
        for paragraph in paragraphs:
            # Split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            improved_sentences = []
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                    
                improved, _ = self.improve_sentence(sentence)
                improved_sentences.append(improved)
            
            improved_paragraphs.append(' '.join(improved_sentences))
        
        return '\n\n'.join(improved_paragraphs)

def main():
    """Command-line interface for style improver"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FHNW Style Improver")
    parser.add_argument("--text", help="Text to improve")
    parser.add_argument("--file", help="File to improve")
    parser.add_argument("--analyze", action="store_true", help="Analyze without improving")
    parser.add_argument("--improve", action="store_true", help="Improve text")
    parser.add_argument("--report", action="store_true", help="Generate analysis report")
    parser.add_argument("--output", help="Output file")
    
    args = parser.parse_args()
    
    improver = StyleImprover()
    
    # Get input text
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        # Interactive mode
        print("Enter text to analyze (Ctrl+D to finish):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        text = '\n'.join(lines)
    
    if args.analyze:
        # Analyze only
        analysis = improver.analyze_text(text)
        
        if args.report:
            report = improver.generate_improvement_report(analysis)
            print(report)
        else:
            print(f"Found {len(analysis['issues'])} issues:")
            for issue in analysis['issues']:
                print(f"  [{issue['severity'].upper()}] {issue['type']}: {issue['text'][:50]}...")
                print(f"      Suggestion: {issue['suggestion']}")
    
    elif args.improve:
        # Improve text
        improved = improver.improve_full_text(text)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(improved)
            print(f"Improved text saved to {args.output}")
        else:
            print("IMPROVED TEXT:")
            print("=" * 50)
            print(improved)
    
    else:
        # Default: analyze and improve
        analysis = improver.analyze_text(text)
        improved = improver.improve_full_text(text)
        
        print("ANALYSIS REPORT:")
        print("=" * 50)
        print(improver.generate_improvement_report(analysis))
        
        print("\n\nIMPROVED TEXT:")
        print("=" * 50)
        print(improved)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write("ANALYSIS REPORT:\n")
                f.write("=" * 50 + "\n")
                f.write(improver.generate_improvement_report(analysis))
                f.write("\n\nIMPROVED TEXT:\n")
                f.write("=" * 50 + "\n")
                f.write(improved)
            print(f"\nFull report saved to {args.output}")

if __name__ == "__main__":
    main()