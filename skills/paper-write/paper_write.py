#!/usr/bin/env python3
"""
Paper Write - Main interface for FHNW academic writing assistant
"""

import sys
import os
import argparse
from typing import Dict, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from citation_processor import FHNWCitationProcessor
    from bibliography_generator import FHNWBibliographyGenerator
    from style_improver import StyleImprover
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all module files are in the same directory.")
    IMPORT_SUCCESS = False

class PaperWrite:
    """Main interface for paper.write skill"""
    
    def __init__(self):
        if IMPORT_SUCCESS:
            self.citation_processor = FHNWCitationProcessor()
            self.bibliography_generator = FHNWBibliographyGenerator()
            self.style_improver = StyleImprover()
        else:
            print("Warning: Some modules failed to load")
    
    def process_command(self, command: str, args: Dict) -> str:
        """Process a paper.write command"""
        command = command.lower().strip()
        
        if command.startswith("korrigiere") or command.startswith("fix"):
            return self.handle_correction(args)
        
        elif command.startswith("zitat") or command.startswith("cite"):
            return self.handle_citation(args)
        
        elif command.startswith("bibliographie") or command.startswith("bib"):
            return self.handle_bibliography(args)
        
        elif command.startswith("literaturverzeichnis"):
            return self.handle_literature(args)
        
        elif command.startswith("verbessere") or command.startswith("improve"):
            return self.handle_improvement(args)
        
        elif command.startswith("analysiere") or command.startswith("analyze"):
            return self.handle_analysis(args)
        
        elif command.startswith("vorlage") or command.startswith("template"):
            return self.handle_template(args)
        
        else:
            return self.show_help()
    
    def handle_correction(self, args: Dict) -> str:
        """Handle citation correction"""
        if 'text' in args:
            text = args['text']
            fixed = self.citation_processor.fix_existing_citation(text)
            return f"Korrigiert: {fixed}"
        else:
            return "Bitte geben Sie das zu korrigierende Zitat an."
    
    def handle_citation(self, args: Dict) -> str:
        """Handle new citation creation"""
        required = ['author', 'year', 'pages']
        if all(k in args for k in required):
            citation = f"{args['author']} {args['year']}"
            ctype = args.get('type', 'paraphrase')
            pages = args['pages']
            
            result = self.citation_processor.process_citation(citation, ctype, pages)
            return f"Zitat: {result}"
        else:
            return f"Fehlende Informationen. Benötigt: {', '.join(required)}"
    
    def handle_bibliography(self, args: Dict) -> str:
        """Handle bibliography entry creation"""
        # Try to determine source type
        source_type = args.get('type', 'monograph')
        
        if source_type == 'monograph':
            required = ['author', 'year', 'title', 'place', 'publisher']
            if all(k in args for k in required):
                entry = self.bibliography_generator.generate_monograph(
                    args['author'], args['year'], args['title'],
                    args['place'], args['publisher']
                )
                return f"Bibliographieeintrag:\n{entry}"
        
        elif source_type == 'journal':
            required = ['author', 'year', 'title', 'journal', 'volume', 'issue', 'pages']
            if all(k in args for k in required):
                entry = self.bibliography_generator.generate_journal_article(
                    args['author'], args['year'], args['title'],
                    args['journal'], args['volume'], args['issue'], args['pages']
                )
                return f"Bibliographieeintrag:\n{entry}"
        
        return f"Unvollständige Informationen für {source_type}."
    
    def handle_literature(self, args: Dict) -> str:
        """Handle literature list generation"""
        if 'file' in args:
            # Generate from file
            with open(args['file'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract citations and generate entries
            import re
            citations = re.findall(r'\([^)]+\)', content)
            
            entries = []
            for citation in citations[:10]:  # Limit to first 10
                try:
                    entry = self.bibliography_generator.generate_from_citation(
                        citation, 'monograph'
                    )
                    entries.append(entry)
                except:
                    pass
            
            if entries:
                return "Literaturverzeichnis (Auszug):\n\n" + "\n\n".join(entries)
        
        return "Bitte geben Sie eine Datei mit --file an."
    
    def handle_improvement(self, args: Dict) -> str:
        """Handle style improvement"""
        if 'text' in args:
            text = args['text']
            improved = self.style_improver.improve_full_text(text)
            
            # Also analyze
            analysis = self.style_improver.analyze_text(text)
            changed = len([s for s in analysis['improved_sentences'] if s['changed']])
            
            return f"Verbessert ({changed} Sätze geändert):\n\n{improved}"
        
        elif 'file' in args:
            with open(args['file'], 'r', encoding='utf-8') as f:
                text = f.read()
            
            improved = self.style_improver.improve_full_text(text)
            
            if 'output' in args:
                with open(args['output'], 'w', encoding='utf-8') as f:
                    f.write(improved)
                return f"Verbesserter Text gespeichert in {args['output']}"
            else:
                return f"Verbesserter Text:\n\n{improved}"
        
        return "Bitte geben Sie Text oder eine Datei an."
    
    def handle_analysis(self, args: Dict) -> str:
        """Handle style analysis"""
        if 'text' in args:
            text = args['text']
        elif 'file' in args:
            with open(args['file'], 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            return "Bitte geben Sie Text oder eine Datei an."
        
        analysis = self.style_improver.analyze_text(text)
        report = self.style_improver.generate_improvement_report(analysis)
        
        return f"Analysebericht:\n\n{report}"
    
    def handle_template(self, args: Dict) -> str:
        """Handle template generation"""
        template_type = args.get('template_type', 'ba_thesis')
        
        templates = {
            'ba_thesis': self.ba_thesis_template(),
            'introduction': self.introduction_template(),
            'theoretical': self.theoretical_template(),
            'case_study': self.case_study_template(),
            'synthesis': self.synthesis_template(),
        }
        
        if template_type in templates:
            return templates[template_type]
        else:
            return f"Verfügbare Vorlagen: {', '.join(templates.keys())}"
    
    def ba_thesis_template(self) -> str:
        """BA Thesis template"""
        return """# BA Thesis Structure (FHNW HSA)

## 1 Einleitung
### 1.1 Ausgangslage
### 1.2 Fragestellung
### 1.3 Zielsetzung und Adressat*innenschaft
### 1.4 Methodik und Aufbau der Arbeit

## 2 Theoretischer Rahmen
### 2.1 Postkoloniale Theorie
### 2.2 Hegemoniekritik
### 2.3 Epistemologien des Südens
### 2.4 Synthese: Drei-Linsen-Analyse

## 3 Methodik
### 3.1 Forschungsdesign
### 3.2 Fallauswahl (Neuseeland, Schweiz, China)
### 3.3 Datenbasis und -analyse
### 3.4 Ethische Überlegungen

## 4 Empirische Analyse
### 4.1 Neuseeland: Postkolonialer Kontext
### 4.2 Schweiz: Hegemoniale Normen
### 4.3 China: Epistemische Gewalt
### 4.4 Vergleichende Synthese

## 5 Diskussion
### 5.1 Beantwortung der Forschungsfragen
### 5.2 Implikationen für die ISA
### 5.3 Limitationen der Studie

## 6 Schlussfolgerung
### 6.1 Zusammenfassung der Ergebnisse
### 6.2 Ausblick und weiterführende Forschung

## Literaturverzeichnis

## Anhang
- Interviewleitfäden
- Transkripte (anonymisiert)
- Kodierschema
- KI-Deklaration"""
    
    def introduction_template(self) -> str:
        """Introduction chapter template"""
        return """## 1 Einleitung

### 1.1 Ausgangslage
[Kontext des Forschungsproblems, Relevanz für die Soziale Arbeit]

### 1.2 Fragestellung
1. [Forschungsfrage 1]
2. [Forschungsfrage 2] 
3. [Forschungsfrage 3]

### 1.3 Zielsetzung und Adressat*innenschaft
[Was soll erreicht werden, wer profitiert von der Arbeit]

### 1.4 Methodik und Aufbau der Arbeit
[Kurzer Überblick über Vorgehen und Struktur]"""
    
    def theoretical_template(self) -> str:
        """Theoretical framework template"""
        return """## 2 Theoretischer Rahmen

### 2.1 Postkoloniale Theorie
[Kernkonzepte nach Razack (2012), Santos (2014), Mignolo (2011)]

### 2.2 Hegemoniekritik
[Gramsci (1971), Konzept der kulturellen Hegemonie]

### 2.3 Epistemologien des Südens
[Epistemizid, Ökologie der Wissensformen nach Santos (2014)]

### 2.4 Synthese: Drei-Linsen-Analyse
[Integration der Perspektiven für die Fallanalyse]"""
    
    def case_study_template(self) -> str:
        """Case study template"""
        return """## 4.X [Land]: [Titel der Fallstudie]

### 4.X.1 Kontextualisierung
[Geografischer, historischer, politischer Kontext]

### 4.X.2 Datenbasis
[Verwendete Dokumente, Interviews, Sekundärliteratur]

### 4.X.3 Analyse nach drei Linsen
1. **Postkoloniale Perspektive:** [Befunde]
2. **Hegemonietheorie:** [Befunde]  
3. **Epistemische Gerechtigkeit:** [Befunde]

### 4.X.4 Konsequenzen für professionelle Kohärenz
[Auswirkungen auf die ISA im jeweiligen Kontext]"""
    
    def synthesis_template(self) -> str:
        """Synthesis chapter template"""
        return """## 5 Vergleichende Synthese

### 5.1 Ländervergleich
[Gemeinsamkeiten und Unterschiede zwischen Neuseeland, Schweiz, China]

### 5.2 Theoretische Implikationen
[Was die Befunde für postkoloniale Theorie, Hegemoniekritik, epistemische Gerechtigkeit bedeuten]

### 5.3 Praktische Konsequenzen für die ISA
[Handlungsempfehlungen für Ausbildung, Praxis, Politik]

### 5.4 Offene Fragen und Forschungsperspektiven
[Was noch untersucht werden müsste]"""
    
    def show_help(self) -> str:
        """Show help information"""
        return """Paper Write Skill - FHNW Academic Writing Assistant

Verfügbare Befehle:

1. Zitate korrigieren:
   paper.write korrigiere "(Spivak 1988)"
   
2. Zitat erstellen:
   paper.write zitat --author "Spivak" --year "1988" --pages "120-125"
   
3. Bibliographieeintrag:
   paper.write bibliographie --type monograph --author "Engelke" --year "1992" --title "Soziale Arbeit als Wissenschaft" --place "Freiburg" --publisher "Lambertus"
   
4. Literaturverzeichnis generieren:
   paper.write literaturverzeichnis --file kapitel1.md
   
5. Stil verbessern:
   paper.write verbessere --text "Es kann verstanden werden..."
   paper.write verbessere --file draft.md --output improved.md
   
6. Stil analysieren:
   paper.write analysiere --file draft.md
   
7. Vorlage erstellen:
   paper.write vorlage --type ba_thesis
   paper.write vorlage --type introduction
   paper.write vorlage --type theoretical
   paper.write vorlage --type case_study
   paper.write vorlage --type synthesis

Beispiel aus der BA-Thesis:
paper.write korrigiere "(Spivak 1988; Gramsci 1971)"
→ "(vgl. Spivak 1988: [Seiten]; Gramsci 1971: [Seiten])."

FHNW Zitierregeln:
- Paraphrase: (vgl. Böhnisch 2001: 139).
- Direktes Zitat: (Böhnisch 2001: 139).
- Seitenbereich: 139–141 (en dash)
- Zwei Seiten: 23f. (kein Leerzeichen)"""

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description="Paper Write Skill")
    
    # Main command
    parser.add_argument("command", nargs="?", help="Command to execute")
    
    # Common arguments
    parser.add_argument("--text", help="Text to process")
    parser.add_argument("--file", help="File to process")
    parser.add_argument("--output", help="Output file")
    
    # Citation arguments
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--year", help="Publication year")
    parser.add_argument("--pages", help="Page numbers")
    parser.add_argument("--type", help="Citation type or source type")
    
    # Bibliography arguments
    parser.add_argument("--title", help="Title")
    parser.add_argument("--place", help="Place of publication")
    parser.add_argument("--publisher", help="Publisher")
    parser.add_argument("--journal", help="Journal name")
    parser.add_argument("--volume", help="Volume")
    parser.add_argument("--issue", help="Issue")
    
    # Template arguments
    parser.add_argument("--template-type", help="Type of template")
    
    args = parser.parse_args()
    
    # Convert args to dict
    args_dict = vars(args)
    
    # Create processor
    processor = PaperWrite()
    
    if args.command:
        result = processor.process_command(args.command, args_dict)
        print(result)
    else:
        # Show help
        print(processor.show_help())

if __name__ == "__main__":
    main()