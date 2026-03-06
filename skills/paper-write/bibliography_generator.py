#!/usr/bin/env python3
"""
FHNW Bibliography Generator - Creates bibliography entries according to FHNW Wegleitung 2018
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

class FHNWBibliographyGenerator:
    """Generate bibliography entries following FHNW Wegleitung 2018"""
    
    def __init__(self):
        self.templates = {
            "monograph": "{author} ({year}). {title}. {place}: {publisher}.",
            "journal_article": "{author} ({year}). {title}. In: {journal}. {volume}. Jg. ({issue}). S. {pages}.",
            "chapter": "{author} ({year}). {title}. In: {editors} (Hg.). {book_title}. {place}: {publisher}. S. {pages}.",
            "online": "{title}. URL: {url} [Zugriff: {access_date}].",
            "report": "{author} ({year}). {title}. {place}: {institution}.",
            "thesis": "{author} ({year}). {title}. {type}. {institution}.",
        }
        
    def format_author(self, author: str) -> str:
        """Format author name: Lastname, Firstname"""
        parts = author.split()
        if len(parts) >= 2:
            # Assume "First Last" or "First Middle Last"
            last = parts[-1]
            first = " ".join(parts[:-1])
            return f"{last}, {first}"
        else:
            return author
    
    def format_multiple_authors(self, authors: List[str]) -> str:
        """Format multiple authors with slashes"""
        formatted = [self.format_author(a) for a in authors]
        return "/".join(formatted)
    
    def format_editors(self, editors: List[str]) -> str:
        """Format editors with (Hg.)"""
        formatted = self.format_multiple_authors(editors)
        return f"{formatted} (Hg.)"
    
    def generate_monograph(self, author: str, year: str, title: str, 
                          place: str, publisher: str) -> str:
        """Generate monograph entry"""
        formatted_author = self.format_author(author)
        return self.templates["monograph"].format(
            author=formatted_author,
            year=year,
            title=title,
            place=place,
            publisher=publisher
        )
    
    def generate_journal_article(self, author: str, year: str, title: str,
                               journal: str, volume: str, issue: str, 
                               pages: str) -> str:
        """Generate journal article entry"""
        formatted_author = self.format_author(author)
        return self.templates["journal_article"].format(
            author=formatted_author,
            year=year,
            title=title,
            journal=journal,
            volume=volume,
            issue=issue,
            pages=pages
        )
    
    def generate_chapter(self, author: str, year: str, title: str,
                        editors: List[str], book_title: str, place: str,
                        publisher: str, pages: str) -> str:
        """Generate chapter in edited volume entry"""
        formatted_author = self.format_author(author)
        formatted_editors = self.format_multiple_authors(editors)
        
        return self.templates["chapter"].format(
            author=formatted_author,
            year=year,
            title=title,
            editors=formatted_editors,
            book_title=book_title,
            place=place,
            publisher=publisher,
            pages=pages
        )
    
    def generate_online_source(self, title: str, url: str, 
                             access_date: Optional[str] = None) -> str:
        """Generate online source entry"""
        if not access_date:
            access_date = datetime.now().strftime("%d.%m.%Y")
            
        return self.templates["online"].format(
            title=title,
            url=url,
            access_date=access_date
        )
    
    def generate_report(self, author: str, year: str, title: str,
                       place: str, institution: str) -> str:
        """Generate report entry"""
        formatted_author = self.format_author(author)
        return self.templates["report"].format(
            author=formatted_author,
            year=year,
            title=title,
            place=place,
            institution=institution
        )
    
    def generate_thesis(self, author: str, year: str, title: str,
                       thesis_type: str, institution: str) -> str:
        """Generate thesis entry (BA, MA, PhD)"""
        formatted_author = self.format_author(author)
        return self.templates["thesis"].format(
            author=formatted_author,
            year=year,
            title=title,
            type=thesis_type,
            institution=institution
        )
    
    def parse_citation_to_bib(self, citation: str) -> Dict:
        """
        Parse a citation string to extract bibliography information.
        
        Args:
            citation: FHNW citation, e.g., "(vgl. Spivak 1988: 120–125)"
            
        Returns:
            Dictionary with parsed information
        """
        # Remove parentheses and vgl.
        clean = citation.strip('()').replace('vgl. ', '')
        
        # Parse pattern: Author Year: Pages
        pattern = r'([A-Za-z]+) (\d{4}): (\d+[–]?\d*[f.]?)'
        match = re.match(pattern, clean)
        
        if match:
            author, year, pages = match.groups()
            return {
                "author": author,
                "year": year,
                "pages": pages,
                "type": "unknown",  # Need more info to determine type
            }
        
        return {}
    
    def generate_from_citation(self, citation: str, 
                             source_type: str = "monograph",
                             **kwargs) -> str:
        """
        Generate bibliography entry from citation with additional info.
        
        Args:
            citation: FHNW citation string
            source_type: Type of source (monograph, journal, chapter, etc.)
            **kwargs: Additional information needed for the specific type
            
        Returns:
            Bibliography entry
        """
        parsed = self.parse_citation_to_bib(citation)
        if not parsed:
            return f"Could not parse citation: {citation}"
        
        # Add parsed info to kwargs
        kwargs.update(parsed)
        
        # Generate based on type
        if source_type == "monograph":
            required = ["author", "year", "title", "place", "publisher"]
            if all(k in kwargs for k in required):
                return self.generate_monograph(
                    kwargs["author"], kwargs["year"], kwargs["title"],
                    kwargs["place"], kwargs["publisher"]
                )
                
        elif source_type == "journal_article":
            required = ["author", "year", "title", "journal", "volume", "issue", "pages"]
            if all(k in kwargs for k in required):
                return self.generate_journal_article(
                    kwargs["author"], kwargs["year"], kwargs["title"],
                    kwargs["journal"], kwargs["volume"], kwargs["issue"], kwargs["pages"]
                )
                
        elif source_type == "chapter":
            required = ["author", "year", "title", "editors", "book_title", "place", "publisher", "pages"]
            if all(k in kwargs for k in required):
                return self.generate_chapter(
                    kwargs["author"], kwargs["year"], kwargs["title"],
                    kwargs["editors"], kwargs["book_title"], kwargs["place"],
                    kwargs["publisher"], kwargs["pages"]
                )
        
        return f"Incomplete information for {source_type}. Required fields: {required}"

def main():
    """Command-line interface for bibliography generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FHNW Bibliography Generator")
    
    # Source type selection
    parser.add_argument("--type", choices=["monograph", "journal", "chapter", "online", "report", "thesis"],
                       default="monograph", help="Type of source")
    
    # Common arguments
    parser.add_argument("--author", help="Author name(s)")
    parser.add_argument("--year", help="Publication year")
    parser.add_argument("--title", help="Title")
    
    # Type-specific arguments
    parser.add_argument("--place", help="Place of publication (for monograph/chapter)")
    parser.add_argument("--publisher", help="Publisher (for monograph/chapter)")
    parser.add_argument("--journal", help="Journal name (for journal article)")
    parser.add_argument("--volume", help="Volume (for journal article)")
    parser.add_argument("--issue", help="Issue number (for journal article)")
    parser.add_argument("--pages", help="Page numbers")
    parser.add_argument("--editors", help="Editors (comma-separated, for chapter)")
    parser.add_argument("--book-title", help="Book title (for chapter)")
    parser.add_argument("--url", help="URL (for online source)")
    parser.add_argument("--access-date", help="Access date (for online source)")
    parser.add_argument("--institution", help="Institution (for report/thesis)")
    parser.add_argument("--thesis-type", help="Thesis type (BA, MA, PhD)")
    
    # File mode
    parser.add_argument("--file", help="Generate bibliography from citations in file")
    parser.add_argument("--output", help="Output file for bibliography")
    
    args = parser.parse_args()
    
    generator = FHNWBibliographyGenerator()
    
    if args.file:
        # Process file
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract citations (simplified)
        citations = re.findall(r'\([^)]+\)', content)
        
        entries = []
        for citation in citations:
            # Try to generate entry
            entry = generator.generate_from_citation(citation, args.type, **vars(args))
            entries.append(entry)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entries = []
        for entry in entries:
            if entry not in seen:
                seen.add(entry)
                unique_entries.append(entry)
        
        # Output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                for entry in unique_entries:
                    f.write(entry + "\n\n")
            print(f"Generated {len(unique_entries)} entries to {args.output}")
        else:
            for entry in unique_entries:
                print(entry + "\n")
    
    else:
        # Generate single entry
        if args.type == "monograph":
            if not all([args.author, args.year, args.title, args.place, args.publisher]):
                print("Error: Missing required fields for monograph")
                print("Required: --author, --year, --title, --place, --publisher")
                return
            
            entry = generator.generate_monograph(
                args.author, args.year, args.title,
                args.place, args.publisher
            )
            
        elif args.type == "journal":
            if not all([args.author, args.year, args.title, args.journal, args.volume, args.issue, args.pages]):
                print("Error: Missing required fields for journal article")
                print("Required: --author, --year, --title, --journal, --volume, --issue, --pages")
                return
            
            entry = generator.generate_journal_article(
                args.author, args.year, args.title,
                args.journal, args.volume, args.issue, args.pages
            )
            
        elif args.type == "chapter":
            if not all([args.author, args.year, args.title, args.editors, args.book_title, args.place, args.publisher, args.pages]):
                print("Error: Missing required fields for chapter")
                print("Required: --author, --year, --title, --editors, --book-title, --place, --publisher, --pages")
                return
            
            editors = [e.strip() for e in args.editors.split(",")]
            entry = generator.generate_chapter(
                args.author, args.year, args.title,
                editors, args.book_title, args.place,
                args.publisher, args.pages
            )
            
        elif args.type == "online":
            if not all([args.title, args.url]):
                print("Error: Missing required fields for online source")
                print("Required: --title, --url")
                return
            
            entry = generator.generate_online_source(
                args.title, args.url, args.access_date
            )
            
        elif args.type == "report":
            if not all([args.author, args.year, args.title, args.place, args.institution]):
                print("Error: Missing required fields for report")
                print("Required: --author, --year, --title, --place, --institution")
                return
            
            entry = generator.generate_report(
                args.author, args.year, args.title,
                args.place, args.institution
            )
            
        elif args.type == "thesis":
            if not all([args.author, args.year, args.title, args.thesis_type, args.institution]):
                print("Error: Missing required fields for thesis")
                print("Required: --author, --year, --title, --thesis-type, --institution")
                return
            
            entry = generator.generate_thesis(
                args.author, args.year, args.title,
                args.thesis_type, args.institution
            )
        
        else:
            print(f"Unknown source type: {args.type}")
            return
        
        print(entry)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(entry + "\n")
            print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()