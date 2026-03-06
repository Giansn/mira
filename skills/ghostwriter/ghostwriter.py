#!/usr/bin/env python3
"""
Ghostwriter Skill - Main interface for FHNW academic ghostwriting
"""

import sys
import os
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Try to import paper.write modules
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'paper-write'))
    from citation_processor import FHNWCitationProcessor
    from style_improver import StyleImprover
    PAPER_WRITE_AVAILABLE = True
except ImportError:
    PAPER_WRITE_AVAILABLE = False
    print("Warning: paper.write modules not available")

class Ghostwriter:
    """FHNW Academic Ghostwriting Assistant"""
    
    def __init__(self):
        self.style_metrics = {}
        self.user_samples = []
        
        if PAPER_WRITE_AVAILABLE:
            self.citation_processor = FHNWCitationProcessor()
            self.style_improver = StyleImprover()
        else:
            self.citation_processor = None
            self.style_improver = None
    
    def analyze_writing_style(self, text: str) -> Dict:
        """Analyze writing style from text sample"""
        # Basic style metrics
        sentences = re.split(r'[.!?]', text)
        words = re.findall(r'\b\w+\b', text)
        
        # Calculate metrics
        metrics = {
            'avg_sentence_length': len(words) / max(len(sentences), 1),
            'total_sentences': len(sentences),
            'total_words': len(words),
            'passive_ratio': self._calculate_passive_ratio(text),
            'citation_density': self._count_citations(text) / max(len(sentences), 1),
            'transition_words': self._extract_transition_words(text),
            'vocabulary_level': self._assess_vocabulary_level(text),
            'theoretical_references': self._extract_theoretical_references(text),
        }
        
        self.style_metrics = metrics
        return metrics
    
    def _calculate_passive_ratio(self, text: str) -> float:
        """Calculate ratio of passive constructions"""
        passive_patterns = [
            r'Es kann .* werden',
            r'Es lässt sich .*',
            r'Es wurde .*',
            r'Es sind .*',
            r'Es wird .*',
            r'Es waren .*',
        ]
        
        sentences = re.split(r'[.!?]', text)
        passive_count = 0
        
        for sentence in sentences:
            for pattern in passive_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_count += 1
                    break
        
        return passive_count / max(len(sentences), 1)
    
    def _count_citations(self, text: str) -> int:
        """Count citations in text"""
        citation_patterns = [
            r'\([^)]+\)',  # Parenthetical citations
            r'[A-Z][a-z]+ \(\d{4}',  # Author-year citations
        ]
        
        total = 0
        for pattern in citation_patterns:
            total += len(re.findall(pattern, text))
        
        return total
    
    def _extract_transition_words(self, text: str) -> List[str]:
        """Extract common transition words"""
        transition_words = [
            'darüber hinaus', 'hingegen', 'folglich', 'deshalb', 
            'zudem', 'außerdem', 'dennoch', 'jedoch', 'allerdings',
            'zusammenfassend', 'abschießend', 'einerseits', 'andererseits',
            'vergleichend', 'konkret', 'generell', 'speziell',
        ]
        
        found = []
        text_lower = text.lower()
        for word in transition_words:
            if word in text_lower:
                found.append(word)
        
        return found
    
    def _assess_vocabulary_level(self, text: str) -> str:
        """Assess vocabulary level (casual/academic/technical)"""
        # Academic German words
        academic_words = [
            'diskurs', 'hegemonie', 'epistemisch', 'postkolonial',
            'theoretisch', 'empirisch', 'methodisch', 'konzeptionell',
            'analytisch', 'kritisch', 'reflexiv', 'normativ',
        ]
        
        # Technical social work terms
        technical_words = [
            'sozialarbeit', 'profession', 'kompetenz', 'intervention',
            'fallarbeit', 'beratung', 'supervision', 'qualifikation',
            'standards', 'richtlinien', 'ethik', 'autonomie',
        ]
        
        words = re.findall(r'\b\w+\b', text.lower())
        academic_count = sum(1 for w in words if w in academic_words)
        technical_count = sum(1 for w in words if w in technical_words)
        
        total_words = len(words)
        
        if total_words == 0:
            return "unknown"
        
        academic_ratio = academic_count / total_words
        technical_ratio = technical_count / total_words
        
        if technical_ratio > 0.1:
            return "technical"
        elif academic_ratio > 0.05:
            return "academic"
        else:
            return "casual"
    
    def _extract_theoretical_references(self, text: str) -> List[str]:
        """Extract theoretical references from text"""
        # Common theorists in social work
        theorists = [
            'gramsci', 'foucault', 'bourdieu', 'habermas',
            'razack', 'santos', 'mignolo', 'spivak',
            'fricker', 'sen', 'nussbaum', 'butler',
        ]
        
        found = []
        text_lower = text.lower()
        for theorist in theorists:
            if theorist in text_lower:
                found.append(theorist)
        
        return found
    
    def emulate_style(self, content: str, target_style: Dict) -> str:
        """Emulate target style in content"""
        # This is a simplified version - real implementation would be more complex
        improved = content
        
        # Apply basic style adjustments based on metrics
        if target_style.get('passive_ratio', 0) < 0.1:
            # Target prefers active voice
            improved = self._reduce_passive_voice(improved)
        
        if target_style.get('citation_density', 0) > 1.5:
            # Target is citation-dense
            improved = self._increase_citation_integration(improved)
        
        # Use target's transition words
        transition_words = target_style.get('transition_words', [])
        if transition_words:
            improved = self._incorporate_transition_words(improved, transition_words)
        
        return improved
    
    def _reduce_passive_voice(self, text: str) -> str:
        """Reduce passive voice constructions"""
        replacements = [
            (r'Es kann (?:festgestellt|gesehen|verstanden) werden, dass', 
             'Die Analyse zeigt, dass'),
            (r'Es lässt sich (?:feststellen|zeigen|beobachten), dass',
             'Untersuchungen zeigen, dass'),
            (r'Es wurde (?:gezeigt|festgestellt|nachgewiesen), dass',
             'Die Studie zeigt, dass'),
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _increase_citation_integration(self, text: str) -> str:
        """Increase citation integration in text"""
        # This would normally integrate more citations
        # For now, just ensure citations are properly formatted
        if self.citation_processor:
            text = self.citation_processor.fix_existing_citation(text)
        
        return text
    
    def _incorporate_transition_words(self, text: str, transition_words: List[str]) -> str:
        """Incorporate target transition words"""
        # Simple implementation: add transition words at paragraph starts
        paragraphs = text.split('\n\n')
        enhanced_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            if i > 0 and transition_words:
                # Use a transition word from the list (cycling)
                transition = transition_words[i % len(transition_words)]
                paragraph = f"{transition.capitalize()} {paragraph[0].lower()}{paragraph[1:]}"
            
            enhanced_paragraphs.append(paragraph)
        
        return '\n\n'.join(enhanced_paragraphs)
    
    def generate_ki_declaration(self, tools_used: List[str], chapters_used: str) -> str:
        """Generate KI-Deklaration for thesis appendix"""
        declaration = """Deklarierung der Verwendung von künstlicher Intelligenz

"""
        
        for tool in tools_used:
            if tool == "ghostwriter":
                declaration += "Ghostwriter Skill      Inhaltsentwicklung, Stilemulation      "
            elif tool == "paper.write":
                declaration += "paper.write Skill      Zitierkorrektur, Literaturverzeichnis  "
            else:
                declaration += f"{tool}                    Verwendung nicht spezifiziert        "
            
            declaration += f"{chapters_used}\n"
        
        declaration += f"""
Ich bestätige, dass ich die oben genannten KI-Assistenzsysteme zur Unterstützung bei der Erstellung dieser Arbeit verwendet habe. Die inhaltliche Verantwortung für die Arbeit liegt ausschließlich bei mir. Alle verwendeten Quellen wurden gemäss den Zitierregeln der FHNW HSA korrekt angegeben.

Datum: {datetime.now().strftime('%d.%m.%Y')}
"""
        
        return declaration
    
    def write_section(self, section_title: str, style_reference: Optional[str] = None) -> str:
        """Write a thesis section with optional style emulation"""
        # Template-based section writing
        templates = {
            "Einleitung": self._introduction_template(),
            "Theoretischer Rahmen": self._theoretical_framework_template(),
            "Methodik": self._methodology_template(),
            "Fallstudie": self._case_study_template(),
            "Diskussion": self._discussion_template(),
            "Schlussfolgerung": self._conclusion_template(),
        }
        
        # Get template or default
        template = templates.get(section_title, self._generic_section_template())
        
        # Apply style emulation if reference provided
        if style_reference and self.style_metrics:
            template = self.emulate_style(template, self.style_metrics)
        
        return template
    
    def _introduction_template(self) -> str:
        """Introduction section template"""
        return """## 1 Einleitung

### 1.1 Ausgangslage
Die internationale Soziale Arbeit operiert im Spannungsfeld zwischen universalistischen normativen Ansprüchen und lokalen Praxiskontexten. Während die International Federation of Social Workers (IFSW) und die International Association of Schools of Social Work (IASSW) globale Standards für Bildung und Praxis formulieren (IFSW/IASSW 2004, 2018), zeigen empirische Studien erhebliche Diskrepanzen in der Umsetzung dieser Standards in unterschiedlichen politischen und kulturellen Kontexten.

### 1.2 Fragestellung
Die vorliegende Arbeit untersucht folgende Forschungsfragen:
1. Wie reflektieren sich die IFSW/IASSW-Leitlinien in der Praxis der internationalen Sozialen Arbeit in den Fallländern Neuseeland, Schweiz und China?
2. Welche Spannungen zwischen universalistischem Anspruch und lokaler Realität werden sichtbar?
3. Was bedeuten diese Befunde für die professionelle Kohärenz der internationalen Sozialen Arbeit?

### 1.3 Zielsetzung
Ziel der Arbeit ist es, eine kritische Analyse der normativen Grundlagen internationaler Sozialer Arbeit im Bildungskontext vorzulegen, die sowohl theoretische Implikationen postkolonialer und hegemoniekritischer Ansätze berücksichtigt als auch empirische Realitäten in drei unterschiedlichen Ländern einbezieht.

### 1.4 Aufbau der Arbeit
Kapitel 2 legt den theoretischen Rahmen dar. Kapitel 3 analysiert die IFSW/IASSW-Leitlinien. Kapitel 4 präsentiert die Fallstudien zu Neuseeland, Schweiz und China. Kapitel 5 diskutiert die vergleichenden Ergebnisse, bevor Kapitel 6 die Schlussfolgerungen zieht."""
    
    def _theoretical_framework_template(self) -> str:
        """Theoretical framework template"""
        return """## 2 Theoretischer Rahmen

### 2.1 Postkoloniale Theorie
Postkoloniale Theorien (vgl. Razack 2012: 707–710; Santos 2014: 38–55) analysieren die Fortwirkung kolonialer Macht- und Wissensverhältnisse auch nach dem formalen Ende kolonialer Herrschaft. Narda Razack beschreibt die internationale Soziale Arbeit als "contested terrain" – ein umkämpftes Terrain zwischen Solidarität und Dominanz. Boaventura de Sousa Santos' Konzept der "Epistemologien des Südens" kritisiert den "Epistemizid", die systematische Auslöschung nicht-westlicher Wissensformen durch eurozentrische Wissenssysteme.

### 2.2 Hegemoniekritik
Die Hegemonietheorie Antonio Gramscis (1971) untersucht, wie dominante Gruppen Konsens über kulturelle und ideologische Mittel herstellen, nicht allein durch Zwang. In der internationalen Sozialen Arbeit manifestiert sich dies in der Naturalisierung westlicher Wissenssysteme als universelle Standards (vgl. Gray/Fook 2004: 625–644). Diese hegemoniale Naturalisierung marginalisiert lokale Praxen und Wissensformen.

### 2.3 Epistemische Gerechtigkeit
Miranda Frickers (2023) Konzept der epistemischen Ungerechtigkeit unterscheidet zwischen testimonialer Ungerechtigkeit (Glaubwürdigkeitsdefizit aufgrund von Vorurteilen) und hermeneutischer Ungerechtigkeit (fehlende begriffliche Ressourcen zur Artikulation von Erfahrungen). In der internationalen Sozialen Arbeit führt dies zur systematischen Unterrepräsentation nicht-westlicher Wissensformen in globalen Diskursen.

### 2.4 Synthese: Drei-Linsen-Analyse
Die integrierte Anwendung dieser drei theoretischen Perspektiven – postkoloniale Kritik, Hegemonietheorie und epistemische Gerechtigkeit – ermöglicht eine mehrdimensionale Analyse der Spannungen in der internationalen Sozialen Arbeit. Dieser theoretische Rahmen leitet die nachfolgende Analyse der Fallstudien."""
    
    def _methodology_template(self) -> str:
        """Methodology section template"""
        return """## 3 Methodik

### 3.1 Forschungsdesign
Die Arbeit folgt einem theoriegeleiteten Literaturreview mit vergleichender Fallstudienanalyse. Der vergleichende Ansatz ermöglicht die Identifikation von Gemeinsamkeiten und Unterschieden in der Umsetzung internationaler Standards in unterschiedlichen Kontexten.

### 3.2 Fallauswahl
Die Fallländer Neuseeland, Schweiz und China wurden aufgrund ihrer unterschiedlichen Positionierung im globalen Bildungskontext ausgewählt:
- Neuseeland: Postkolonialer Kontext mit indigener Selbstbestimmung
- Schweiz: Westlicher Kontext mit multilingualer und föderaler Struktur  
- China: Autoritärer Kontext mit staatlicher Kontrolle von Bildung

### 3.3 Datenbasis
Die Analyse stützt sich auf:
- Primärdokumente: IFSW/IASSW-Leitlinien (2004, 2018)
- Sekundärliteratur: Fachpublikationen zur internationalen Sozialen Arbeit
- Menschenrechtsberichte: Human Rights Watch (2021) für China
- Curriculardokumente: Ausbildungsprogramme in den Fallländern

### 3.4 Analyseverfahren
Die Dokumentenanalyse folgt einem qualitativ-inhaltsanalytischen Ansatz nach Mayring (2008). Die Auswertung erfolgt entlang der theoretischen Kategorien des Drei-Linsen-Rahmens."""
    
    def _case_study_template(self) -> str:
        """Case study template"""
        return """## 4.X [Land]: [Titel der Fallstudie]

### 4.X.1 Kontextualisierung
[Geografischer, historischer, politischer Kontext des Landes]

### 4.X.2 Datenbasis
[Verwendete Dokumente, Interviews, Sekundärliteratur für diesen Fall]

### 4.X.3 Analyse nach drei Linsen
1. **Postkoloniale Perspektive:** [Wie manifestieren sich postkoloniale Machtverhältnisse in diesem Kontext?]
2. **Hegemonietheorie:** [Welche hegemonialen Strukturen prägen die Soziale Arbeit in diesem Land?]
3. **Epistemische Gerechtigkeit:** [Werden nicht-westliche Wissensformen anerkannt und integriert?]

### 4.X.4 Konsequenzen für professionelle Kohärenz
[Auswirkungen der analysierten Spannungen auf die professionelle Identität und Praxis der Sozialen Arbeit in diesem Kontext]"""
    
    def _discussion_template(self) -> str:
        """Discussion section template"""
        return """## 5 Diskussion

### 5.1 Beantwortung der Forschungsfragen
[Zusammenfassung der zentralen Befunde zu jeder Forschungsfrage]

### 5.2 Theoretische Implikationen
[Was die Ergebnisse für postkoloniale Theorie, Hegemoniekritik und epistemische Gerechtigkeit bedeuten]

### 5.3 Praktische Konsequenzen
[Handlungsempfehlungen für Ausbildung, Praxis und Politik der internationalen Sozialen Arbeit]

### 5.4 Limitationen der Studie
[Eingeschränkte Generalisierbarkeit, methodische Beschränkungen, Datenverfügbarkeit]"""
    
    def _conclusion_template(self) -> str:
        """Conclusion section template"""
        return """## 6 Schlussfolgerung

### 6.1 Zusammenfassung der Ergebnisse
[Prägnante Zusammenfassung der zentralen Erkenntnisse der Arbeit]

### 6.2 Ausblick
[Weiterführende Forschungsfragen, Entwicklungsmöglichkeiten für das Feld der internationalen Sozialen Arbeit]

### 6.3 Abschließende Bemerkung
[Konkludierende Reflexion zur Bedeutung der Ergebnisse für die Profession der Sozialen Arbeit im globalen Kontext]"""
    
    def _generic_section_template(self) -> str:
        """Generic section template"""
        return f"""## [Section Title]

### [Subsection 1]
[Content for first subsection]

### [Subsection 2]  
[Content for second subsection]

### [Subsection 3]
[Content for third subsection]

**Zusammenfassung:** [Brief summary of section content]"""

def main():
    """Command-line interface for ghostwriter skill"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FHNW Ghostwriter Skill")
    
    # Main commands
    parser.add_argument("--analyze-style", help="Analyze writing style from file")
    parser.add_argument("--write-section", help="Write a thesis section")
    parser.add_argument("--emulate-style", help="Emulate style from reference file")
    parser.add_argument("--generate-declaration", action="store_true", help="Generate KI-Deklaration")
    parser.add_argument("--fix", help="Fix style and citations in file")
    
    # Arguments
    parser.add_argument("--tools", help="Tools used for KI-Deklaration (comma-separated)")
    parser.add_argument("--chapters", help="Chapters where tools were used")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--style-reference", help="File to use as style reference")
    
    args = parser.parse_args()
    
    ghostwriter = Ghostwriter()
    
    if args.analyze_style:
        with open(args.analyze_style, 'r', encoding='utf-8') as f:
            text = f.read()
        
        metrics = ghostwriter.analyze_writing_style(text)
        
        print("WRITING STYLE ANALYSIS:")
        print("=" * 50)
        for key, value in metrics.items():
            if isinstance(value, list):
                print(f"{key}: {', '.join(value[:5])}{'...' if len(value) > 5 else ''}")
            else:
                print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
    
    elif args.write_section:
        style_ref = None
        if args.style_reference:
            with open(args.style_reference, 'r', encoding='utf-8') as f:
                style_text = f.read()
                ghostwriter.analyze_writing_style(style_text)
                style_ref = args.style_reference
        
        section = ghostwriter.write_section(args.write_section, style_ref)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(section)
            print(f"Section written to {args.output}")
        else:
            print(section)
    
    elif args.generate_declaration:
        if not args.tools or not args.chapters:
            print("Error: --tools and --chapters required for KI-Deklaration")
            return
        
        tools = [t.strip() for t in args.tools.split(',')]
        declaration = ghostwriter.generate_ki_declaration(tools, args.chapters)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(declaration)
            print(f"KI-Deklaration written to {args.output}")
        else:
            print(declaration)
    
    elif args.fix:
        with open(args.fix, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Apply style improvement if available
        if ghostwriter.style_improver:
            text = ghostwriter.style_improver.improve_full_text(text)
        
        # Apply citation fixing if available
        if ghostwriter.citation_processor:
            text = ghostwriter.citation_processor.fix_existing_citation(text)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Fixed file written to {args.output}")
        else:
            print(text)
    
    else:
        # Show help
        print("""
FHNW Ghostwriter Skill - Academic Ghostwriting Assistant

Commands:
  --analyze-style FILE      Analyze writing style from file
  --write-section SECTION   Write thesis section (e.g., "Einleitung")
  --emulate-style FILE      Use file as style reference
  --generate-declaration    Generate KI-Deklaration (requires --tools and --chapters)
  --fix FILE                Fix style and citations in file

Examples:
  ghostwriter --analyze-style user_writing.md
  ghostwriter --write-section "Theoretischer Rahmen" --output theoretical.md
  ghostwriter --generate-declaration --tools "ghostwriter,paper.write" --chapters "1-6"
  ghostwriter --fix chapter1.md --output chapter1_fixed.md

Style Emulation:
  Provide a writing sample with --style-reference for best results
  The skill analyzes: sentence length, passive ratio, citation density, vocabulary level
""")

if __name__ == "__main__":
    main()