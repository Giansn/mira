#!/usr/bin/env python3
"""
FHNW Citation Processor - Implements FHNW Wegleitung 2018 citation rules
"""

import re
import sys
from typing import List, Tuple, Dict, Optional

class FHNWCitationProcessor:
    """Process citations according to FHNW Wegleitung 2018"""
    
    def __init__(self):
        self.citation_patterns = {
            'simple': r'\(([^)]+)\)',  # Matches (Author Year: Pages)
            'author_in_text': r'([A-Z][a-z]+) \((\d{4}):',  # Matches Author (Year):
            'multiple': r'([A-Z][a-z]+ \d{4})',  # Matches Author Year
        }
        
    def process_citation(self, citation: str, citation_type: str = "paraphrase", pages: str = "") -> str:
        """
        Process a single citation to FHNW format.
        
        Args:
            citation: Raw citation string, e.g., "Spivak 1988"
            citation_type: "paraphrase" (indirect) or "quote" (direct)
            pages: Page numbers, e.g., "120-125" or "139"
            
        Returns:
            FHNW-formatted citation, e.g., "(vgl. Spivak 1988: 120–125)"
        """
        # Clean input
        citation = citation.strip()
        
        # Parse author and year
        parts = citation.split()
        if len(parts) < 2:
            return citation  # Return unchanged if can't parse
        
        author = parts[0]
        year = parts[1]
        
        # Format pages
        if pages:
            # Convert hyphens to en dashes
            pages = pages.replace('-', '–')
            # Handle "f." for two pages
            if pages.endswith('f'):
                pages = pages.replace('f', 'f.')
            # Add colon
            pages_str = f": {pages}"
        else:
            pages_str = ""
            
        # Determine prefix
        if citation_type == "paraphrase":
            prefix = "vgl. "
        elif citation_type == "quote":
            prefix = ""
        else:
            prefix = ""
            
        # Construct citation
        formatted = f"({prefix}{author} {year}{pages_str})"
        
        # Add period for paraphrases
        if citation_type == "paraphrase":
            formatted += "."
            
        return formatted
    
    def process_multiple_citations(self, citations: List[str], citation_types: List[str], pages_list: List[str]) -> str:
        """
        Process multiple citations in one parentheses.
        
        Args:
            citations: List of citation strings
            citation_types: List of types ("paraphrase" or "quote")
            pages_list: List of page strings
            
        Returns:
            Combined FHNW-formatted citations
        """
        processed = []
        for cite, ctype, pages in zip(citations, citation_types, pages_list):
            processed.append(self.process_citation(cite, ctype, pages))
        
        # Remove parentheses from individual citations
        cleaned = [c.strip('()') for c in processed]
        
        # Combine with semicolons
        combined = "; ".join(cleaned)
        
        # Add outer parentheses
        result = f"({combined})"
        
        # Add period if any are paraphrases
        if "paraphrase" in citation_types:
            result += "."
            
        return result
    
    def fix_existing_citation(self, text: str) -> str:
        """
        Fix an existing citation in text to FHNW format.
        
        Args:
            text: Text containing citation, e.g., "(Spivak 1988; Gramsci 1971)"
            
        Returns:
            Text with corrected citation
        """
        # Common patterns to fix
        patterns = [
            (r'\(([A-Z][a-z]+ \d{4})\)', r'(vgl. \1: [Seiten]).'),  # Single citation no pages
            (r'\(([A-Z][a-z]+ \d{4}); ([A-Z][a-z]+ \d{4})\)', r'(vgl. \1: [Seiten]; \2: [Seiten]).'),  # Multiple no pages
            (r'\(([A-Z][a-z]+ \d{4}): (\d+)\)', r'(vgl. \1: \2).'),  # With pages
            (r'\(([A-Z][a-z]+ \d{4}): (\d+)-(\d+)\)', r'(vgl. \1: \2–\3).'),  # With page range (hyphen)
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
            
        return text
    
    def extract_citations_from_text(self, text: str) -> List[Dict]:
        """
        Extract citations from text for processing.
        
        Args:
            text: Text to extract citations from
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Find all citation patterns
        patterns = [
            (r'\(([^)]+)\)', "parenthetical"),
            (r'([A-Z][a-z]+) \((\d{4}):? (\d+[–-]?\d*[f.]?)\)', "author_in_text"),
        ]
        
        for pattern, ctype in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if ctype == "parenthetical":
                    citation_text = match
                    # Parse components
                    if ":" in citation_text:
                        parts = citation_text.split(":")
                        author_year = parts[0].strip()
                        pages = parts[1].strip()
                    else:
                        author_year = citation_text
                        pages = ""
                        
                    citations.append({
                        "text": citation_text,
                        "author_year": author_year,
                        "pages": pages,
                        "type": ctype,
                        "needs_fix": "vgl." not in citation_text and pages == ""
                    })
                elif ctype == "author_in_text":
                    author, year, pages = match
                    citations.append({
                        "text": f"{author} ({year}: {pages})",
                        "author_year": f"{author} {year}",
                        "pages": pages,
                        "type": ctype,
                        "needs_fix": False
                    })
        
        return citations

def main():
    """Command-line interface for citation processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FHNW Citation Processor")
    parser.add_argument("--citation", help="Citation to process, e.g., 'Spivak 1988'")
    parser.add_argument("--type", choices=["paraphrase", "quote"], default="paraphrase", 
                       help="Citation type: paraphrase (indirect) or quote (direct)")
    parser.add_argument("--pages", help="Page numbers, e.g., '120-125' or '139'")
    parser.add_argument("--file", help="Process citations in a file")
    parser.add_argument("--fix", action="store_true", help="Fix existing citations in text")
    
    args = parser.parse_args()
    
    processor = FHNWCitationProcessor()
    
    if args.citation:
        result = processor.process_citation(args.citation, args.type, args.pages)
        print(result)
    
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if args.fix:
            fixed = processor.fix_existing_citation(content)
            print(fixed)
        else:
            citations = processor.extract_citations_from_text(content)
            for cite in citations:
                print(f"Found: {cite['text']}")
                if cite['needs_fix']:
                    fixed = processor.process_citation(cite['author_year'], "paraphrase", cite['pages'])
                    print(f"Fixed: {fixed}")
                print()
    
    else:
        # Interactive mode
        print("FHNW Citation Processor")
        print("Enter citations in format 'Author Year' (or 'quit' to exit)")
        
        while True:
            try:
                user_input = input("\nCitation: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                pages = input("Pages (optional): ").strip()
                ctype = input("Type (paraphrase/quote) [paraphrase]: ").strip() or "paraphrase"
                
                result = processor.process_citation(user_input, ctype, pages)
                print(f"Result: {result}")
                
            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()