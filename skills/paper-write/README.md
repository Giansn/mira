# Paper Write Skill

Academic writing assistant for FHNW BA/MA theses implementing FHNW citation rules (Wegleitung 2018), bibliography formatting, and style improvement to avoid AI-stiffness.

## Features

### 1. FHNW Citation Processing
- Converts raw citations to FHNW format: `(vgl. Autor Jahr: Seiten).`
- Handles page ranges with en dashes: `139–141` (not hyphens)
- Supports multiple citations: `(vgl. Autor1 Jahr: Seiten; Autor2 Jahr: Seiten).`
- Corrects common errors: missing pages, incorrect punctuation

### 2. Bibliography Generation
- Creates properly formatted bibliography entries:
  - Monographs: `Autor (Jahr). Titel. Ort: Verlag.`
  - Journal articles: `Autor (Jahr). Titel. In: Zeitschrift. Band. Jg. (Heft). S. Seiten.`
  - Chapters in edited volumes
  - Online sources with access dates
  - Reports and theses

### 3. Style Improvement
- Detects and fixes AI-stiff writing patterns:
  - Passive constructions → Active voice
  - Nominalizations → Verb forms
  - Hedging language → Direct statements
  - Empty phrases → Substantive content
- Provides analysis reports with recommendations

### 4. Chapter Templates
- BA Thesis structure: Introduction, Theoretical Framework, Methodology, Case Studies, Synthesis, Conclusion
- MA Thesis structure with greater depth
- FHNW-compliant formatting

## Installation

The skill is already installed in your OpenClaw workspace. To use it:

1. **Trigger the skill** with:
   - `paper.write` (primary trigger)
   - `thesis` (with writing/citation context)
   - `zitieren` / `literaturverzeichnis` / `fhnw`

2. **Or use command-line tools** directly:
   ```bash
   cd /home/ubuntu/.openclaw/workspace/skills/paper-write
   
   # Process citations
   python3 citation_processor.py --citation "Spivak 1988" --type paraphrase --pages "120-125"
   
   # Generate bibliography entry
   python3 bibliography_generator.py --type monograph --author "Ernst Engelke" --year "1992" \
     --title "Soziale Arbeit als Wissenschaft" --place "Freiburg" --publisher "Lambertus"
   
   # Improve style
   python3 style_improver.py --file your_text.md --improve --output improved.md
   ```

## Usage Examples

### Example 1: Citation Correction
```
User: "paper.write: korrigiere dieses Zitat: (Spivak 1988; Gramsci 1971)"
→ Returns: "(vgl. Spivak 1988: [Seiten]; Gramsci 1971: [Seiten])."
```

### Example 2: Bibliography Entry
```
User: "paper.write: erstelle bibliographie eintrag für Spivak 1988, Can the Subaltern Speak?, pages 120-125"
→ Returns: "Spivak, Gayatri Chakravorty (1988). Can the Subaltern Speak? In: Marxism and the Interpretation of Culture. Urbana: University of Illinois Press. S. 120–125."
```

### Example 3: Style Improvement
```
User: "paper.write: verbessere diesen satz: 'Es kann verstanden werden, dass postkoloniale Theorien helfen, westliche Wissensverhältnisse zu verstehen.'"
→ Returns: "Postkoloniale Theorien zeigen, wie westliche Wissensverhältnisse fortwirken – ein Mechanismus, der in der internationalen Sozialen Arbeit oft übersehen wird."
```

### Example 4: Full Chapter Review
```
User: "paper.write: analysiere und verbessere kapitel 1"
→ Returns: Style analysis report + improved text with FHNW-compliant citations
```

## Integration with BA Thesis

The skill works directly with your existing BA thesis files:

- `ba_thesis_chapter1_introduction.md`
- `ba_thesis_chapter2_theoretical_framework.md`
- `ba_thesis_chapter4_3_china_case.md`
- `writing/nz_empirical_analysis_week1.md`

To process an entire chapter:
```bash
cd /home/ubuntu/.openclaw/workspace
python3 skills/paper-write/citation_processor.py --file ba_thesis_chapter1.md --fix
python3 skills/paper-write/style_improver.py --file ba_thesis_chapter1.md --improve --output ba_thesis_chapter1_improved.md
```

## FHNW Citation Rules (Key Points)

### In-text Citations
- **Paraphrase:** `(vgl. Böhnisch 2001: 139).`
- **Direct quote:** `(Böhnisch 2001: 139).`
- **Page ranges:** Use en dashes: `139–141` (not hyphens)
- **Two pages:** `23f.` (no space)
- **Author in sentence:** `Böhnisch (2001: 139–141) argumentiert, dass …`
- **Repeated reference:** `(vgl. ebd.: 42)`

### Bibliography Examples

**Monograph:**
```
Engelke, Ernst (1992). Soziale Arbeit als Wissenschaft. Eine Orientierung. Freiburg: Lambertus.
```

**Journal Article:**
```
Schnurr, Stefan (2005). Evidenz ohne Reflexivität? – Zur Debatte um Evidenzbasierte Praxis in der Sozialen Arbeit. In: Zeitschrift Forschung & Wissenschaft Soziale Arbeit. 5. Jg. (2). S. 19–50.
```

**Chapter in Edited Volume:**
```
Duttweiler, Stefanie (2007). Beratung als Ort neoliberaler Subjektivierung. In: Anhorn, Roland/Bettinger, Frank/Stehr, Johannes (Hg.). Foucaults Machtanalytik und Soziale Arbeit. Eine kritische Einführung und Bestandesaufnahme. Wiesbaden: VS Verlag für Sozialwissenschaften. S. 261–275.
```

## Avoiding AI-Stiffness

### Problematic Patterns (to avoid):
- **Passive:** "Es kann verstanden werden" → **Better:** "Die Analyse zeigt"
- **Nominalizations:** "Die Durchführung einer Untersuchung" → **Better:** "Wir untersuchen"
- **Hedging:** "Möglicherweise könnte man argumentieren" → **Better:** "Argumentativ lässt sich zeigen"
- **Empty phrases:** "Es ist wichtig zu beachten" → **Better:** (omit, state directly)

### Good Academic Style:
- Active voice
- Direct statements
- Clear argument progression
- Varied sentence structure
- Precise terminology

## Dependencies

- Python 3.12+
- Standard library only (no external dependencies)

## Testing

Test the skill with sample files:
```bash
# Test citation processing
echo "(Spivak 1988; Gramsci 1971)" | python3 citation_processor.py --fix

# Test bibliography generation
python3 bibliography_generator.py --type monograph \
  --author "Gayatri Spivak" --year "1988" \
  --title "Can the Subaltern Speak?" \
  --place "Urbana" --publisher "University of Illinois Press"

# Test style improvement
echo "Es kann verstanden werden, dass postkoloniale Theorien helfen." | python3 style_improver.py --improve
```

## Troubleshooting

### Common Issues

1. **Missing page numbers:** The skill flags citations without pages: `[Seiten]`
2. **Incorrect dash usage:** Converts hyphens to en dashes automatically
3. **Missing "vgl.":** Added automatically for paraphrases
4. **AI-stiff language:** Detected and suggested improvements

### Error Messages
- `ERR_MISSING_PAGES`: Citation lacks page numbers
- `ERR_INVALID_FORMAT`: Citation doesn't match FHNW pattern
- `ERR_STIFF_LANGUAGE`: Text contains AI-typical constructions

## Future Development

Planned enhancements:
1. Auto-page lookup from digital libraries
2. Zotero/BibTeX integration
3. Overleaf/LaTeX template generation
4. Plagiarism similarity check
5. Deadline and progress tracking

## Academic Integrity Note

This skill assists with formatting and style improvement, but:
- All ideas and arguments must be your own
- Citations must accurately represent sources
- Plagiarism checks are still required
- Final responsibility lies with the author

Remember to declare AI usage in your thesis appendix:
```
Deklarierung der Verwendung von künstlicher Intelligenz

paper.write Skill      Zitierkorrektur, Stilverbesserung    Kapitel 1–6
```

## License

OpenClaw Skill - Free to use for academic purposes

## Author

OpenClaw Skill System
FHNW Wegleitung 2018 implementation
Based on Duygu Karadag MA thesis examples