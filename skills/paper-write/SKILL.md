---
name: paper-write
description: "Academic writing assistant for FHNW BA/MA theses - FHNW citation rules, bibliography formatting, style improvement, chapter templates"
trigger: "paper.write / thesis / zitieren / literaturverzeichnis / fhnw"
---

# Paper Write Skill

## Overview

A specialized academic writing assistant for FHNW (Hochschule für Soziale Arbeit) theses and papers. Implements FHNW citation rules (Wegleitung 2018), bibliography formatting, style improvement to avoid AI-stiffness, and provides chapter templates for BA/MA theses.

## Trigger Phrases

The skill activates when messages contain:
- `paper.write` (primary trigger)
- `thesis` (when combined with writing/citation intent)
- `zitieren` / `zitation` / `zitierweise`
- `literaturverzeichnis` / `bibliographie`
- `fhnw` (when combined with writing/formatting)
- `academic writing` / `wissenschaftliches schreiben`
- `ba-thesis` / `ma-thesis` (with writing/citation context)

## FHNW Citation Rules (Wegleitung 2018)

### 1. In-text Citations

#### **Paraphrase (sinngemäße Wiedergabe):**
```
(vgl. Böhnisch 2001: 139).
```
- Use `vgl.` for indirect citations
- Page numbers required
- Period after closing parenthesis

#### **Direct Quote (wörtliches Zitat):**
```
(Böhnisch 2001: 139).
```
- No `vgl.` for direct quotes
- Page numbers required

#### **Page Ranges:**
- Single page: `139`
- Two pages: `23f.` (no space)
- Multiple pages: `139–141` (en dash, not hyphen)

#### **Author in Sentence Flow:**
```
Böhnisch (2001: 139–141) argumentiert, dass …
```

#### **Repeated Reference:**
```
(vgl. ebd.: 42)  # same source, different page
```

#### **Multiple Authors:**
- Two authors: `(Müller/Overbye 2010: 47)`
- Three+ authors: `(Arbeitsgruppe Schulforschung 1980, Bourdieu 1982 sowie Collins 1979)`

#### **Qualifiers:**
```
(z.B. Müller 2006: 25)
(siehe auch Müller 2006: 25)
(siehe aber Müller 2006: 25)
```

### 2. Bibliography Formatting

#### **Monograph:**
```
Engelke, Ernst (1992). Soziale Arbeit als Wissenschaft. Eine Orientierung. Freiburg: Lambertus.
```

#### **Journal Article:**
```
Schnurr, Stefan (2005). Evidenz ohne Reflexivität? – Zur Debatte um Evidenzbasierte Praxis in der Sozialen Arbeit. In: Zeitschrift Forschung & Wissenschaft Soziale Arbeit. 5. Jg. (2). S. 19–50.
```

#### **Chapter in Edited Volume:**
```
Duttweiler, Stefanie (2007). Beratung als Ort neoliberaler Subjektivierung. In: Anhorn, Roland/Bettinger, Frank/Stehr, Johannes (Hg.). Foucaults Machtanalytik und Soziale Arbeit. Eine kritische Einführung und Bestandesaufnahme. Wiesbaden: VS Verlag für Sozialwissenschaften. S. 261–275.
```

#### **Online Source:**
```
Titel. URL: https://example.com [Zugriff: 06.03.2026].
```

#### **Multiple Authors/Editors:**
```
Galuske, Michael/Thole, Werner (Hg.) (2006). Vom Fall zum Management. Neue Methoden der Sozialen Arbeit. Wiesbaden: VS Verlag.
```

### 3. Style Guidelines (Avoiding AI Stiffness)

#### **Problematic AI Patterns to Avoid:**
- **Passive constructions:** "Es kann verstanden werden" → "Die Analyse zeigt"
- **Nominalizations:** "Die Durchführung einer Untersuchung" → "Wir untersuchen"
- **Hedging language:** "Möglicherweise könnte man argumentieren" → "Argumentativ lässt sich zeigen"
- **Empty phrases:** "Es ist wichtig zu beachten" → (omit, state directly)
- **Overly complex sentences:** Break into clear, direct statements

#### **Human Academic Style:**
- Direct, active voice
- Clear argument progression
- Precise terminology without jargon
- Varied sentence structure
- Natural academic flow (not robotic)

## Architecture

### 1. Citation Processor
- **Input:** Raw citation `(Spivak 1988; Gramsci 1971)`
- **Processing:** Add page numbers, `vgl.` for paraphrases, en dashes for ranges
- **Output:** FHNW-compliant `(vgl. Spivak 1988: 120–125; Gramsci 1971: 45–50)`

### 2. Bibliography Generator
- **Input:** Source metadata (author, year, title, etc.)
- **Processing:** Format according to FHNW rules
- **Output:** Properly formatted bibliography entry

### 3. Style Improver
- **Input:** Text passage
- **Processing:** Detect AI-stiff patterns, suggest human alternatives
- **Output:** Improved text with academic flow

### 4. Chapter Templates
- **BA Thesis Structure:** Introduction, Theoretical Framework, Methodology, Case Studies (NZ, CH, CN), Synthesis, Conclusion
- **MA Thesis Structure:** Adapted for greater depth and specialization

## Usage Examples

### Example 1: Citation Correction
```
User: "paper.write: korrigiere dieses Zitat: (Spivak 1988; Gramsci 1971)"
→ Skill triggers
→ Returns: "(vgl. Spivak 1988: 120–125; Gramsci 1971: 45–50)"
→ Explanation: Added page numbers and 'vgl.' for paraphrase
```

### Example 2: Bibliography Entry
```
User: "paper.write: erstelle bibliographie eintrag für Spivak 1988, Can the Subaltern Speak?, pages 120-125"
→ Skill triggers
→ Returns: "Spivak, Gayatri Chakravorty (1988). Can the Subaltern Speak? In: Marxism and the Interpretation of Culture. Urbana: University of Illinois Press. S. 120–125."
```

### Example 3: Style Improvement
```
User: "paper.write: verbessere diesen satz: 'Es kann verstanden werden, dass postkoloniale Theorien helfen, westliche Wissensverhältnisse zu verstehen.'"
→ Skill triggers
→ Returns: "Postkoloniale Theorien zeigen, wie westliche Wissensverhältnisse fortwirken – ein Mechanismus, der in der internationalen Sozialen Arbeit oft übersehen wird."
```

### Example 4: Chapter Writing
```
User: "paper.write: schweiz fallstudie kapitel für ba-thesis"
→ Skill triggers
→ Returns: Chapter template with structure, key questions, and FHNW citation examples
```

## Integration with Existing Work

### BA Thesis Files
The skill can directly read and modify:
- `ba_thesis_chapter1_introduction.md`
- `ba_thesis_chapter2_theoretical_framework.md`
- `ba_thesis_chapter4_3_china_case.md`
- `writing/nz_empirical_analysis_week1.md`

### Memory System
- Store corrected citations in memory
- Track bibliography entries across chapters
- Maintain style improvement patterns

### Project Structure
- Aligns with Arjun.lol portfolio categories (`writing/`, `notes/`, etc.)
- Maintains European date format in text (`dd-mm-YYYY`)
- Uses ISO date format for filenames (`YYYY-MM-DD`)

## Implementation Commands

### 1. Citation Processing
```bash
# Process a single citation
paper.write --cite "Spivak 1988; Gramsci 1971" --pages "120-125;45-50" --type paraphrase

# Batch process a file
paper.write --file ba_thesis_chapter1.md --fix-citations
```

### 2. Bibliography Generation
```bash
# Generate bibliography from citations in file
paper.write --file ba_thesis_chapter1.md --generate-bib

# Create standalone bibliography entry
paper.write --bib-entry "author=Spivak;year=1988;title=Can the Subaltern Speak?;type=chapter"
```

### 3. Style Improvement
```bash
# Improve style of a text file
paper.write --file draft.md --improve-style

# Check for AI-stiffness patterns
paper.write --file draft.md --check-style
```

### 4. Chapter Templates
```bash
# Generate Switzerland case study template
paper.write --template case-study --country switzerland

# Generate theoretical framework template
paper.write --template theoretical-framework
```

## Configuration

### Citation Style
- **Default:** FHNW Wegleitung 2018
- **Alternative:** APA, Chicago (if needed for specific requirements)
- **Custom:** User-defined rules

### Language Settings
- **Primary:** German (FHNW requirements)
- **Secondary:** English (for international references)
- **Translation:** Mark translated quotes with `[Übersetzung durch den/die Verf.]`

### Output Format
- **Markdown:** `.md` files for editing
- **Word:** `.docx` export (via pandoc)
- **PDF:** Final formatting

## Quality Assurance

### Citation Validation
1. **Page numbers present:** All citations must have page numbers
2. **`vgl.` usage:** Correct for paraphrases, omitted for direct quotes
3. **En dashes:** `139–141` not `139-141`
4. **Period placement:** After closing parenthesis for paraphrases

### Style Validation
1. **Active voice preferred:** ≥80% active constructions
2. **Sentence complexity:** Avg. sentence length 15-25 words
3. **Jargon reduction:** Technical terms explained where needed
4. **Flow:** Logical progression between paragraphs

### Bibliography Validation
1. **Complete metadata:** All required fields present
2. **Format consistency:** Uniform formatting across all entries
3. **Alphabetical order:** Sorted by author last name
4. **Date format:** `[Zugriff: TT.MM.JJJJ]` for online sources

## Examples from Duygu Karadag MA Thesis

### Good Examples (to emulate):
```
"Laut Narda Razack (2012) gilt in den globalen Entwicklungsdiskursen Bildung als Schlüssel zu Fortschritt und Gleichheit, zugleich ist sie jedoch durch historische Machtstrukturen geformt, welche koloniale und ökonomische Abhängigkeiten reproduzieren (vgl. Razack 2012: 707)."

"Aus postkolonialer Perspektive versteht Razack die internationale Soziale Arbeit als ein «contested terrain», ein umkämpftes Terrain zwischen Solidarität und Dominanz (vgl. Razack 2012: 707)."
```

### Style Characteristics:
- **Direct:** Clear subject-verb-object structure
- **Precise:** Specific page numbers, not just years
- **Integrated:** Citations flow naturally in sentences
- **Academic:** Formal but not stiff

## Troubleshooting

### Common Issues

#### 1. Missing Page Numbers
```
Input: (Spivak 1988)
Fix: Add estimated pages or flag for manual addition
Output: (vgl. Spivak 1988: [Seiten])
```

#### 2. Incorrect Dash Usage
```
Input: (Böhnisch 2001: 139-141)
Fix: Replace hyphen with en dash
Output: (Böhnisch 2001: 139–141)
```

#### 3. Missing "vgl." for Paraphrase
```
Input: (Böhnisch 2001: 139)
Fix: Add "vgl." if not direct quote
Output: (vgl. Böhnisch 2001: 139)
```

#### 4. AI-Stiff Language
```
Input: "Es kann festgestellt werden, dass ..."
Fix: "Die Analyse zeigt, dass ..."
```

### Error Messages
- `ERR_MISSING_PAGES`: Citation lacks page numbers
- `ERR_INVALID_FORMAT`: Citation doesn't match FHNW pattern
- `ERR_STIFF_LANGUAGE`: Text contains AI-typical constructions
- `ERR_BIB_FORMAT`: Bibliography entry malformed

## Future Enhancements

### Planned Features
1. **Auto-page lookup:** Fetch page numbers from digital libraries
2. **Plagiarism check:** Basic similarity detection
3. **Word count tracking:** Per chapter and total
4. **Deadline management:** Progress tracking against thesis deadline
5. **Peer-review simulation:** Generate constructive feedback

### Integration Goals
1. **Zotero/BibTeX sync:** Import existing bibliographies
2. **Overleaf integration:** LaTeX template generation
3. **FHNW template compliance:** Automatic formatting checks
4. **Multi-language support:** English thesis option

## Quick Start

### Basic Usage
Just say `paper.write` followed by your request:
- `paper.write korrigiere dieses zitat: (Spivak 1988)`
- `paper.write erstelle literaturverzeichnis für kapitel 1`
- `paper.write verbessere stil dieses absatzes: [text]`
- `paper.write schweiz fallstudie vorlage`

### Advanced Usage
For specific operations:
- `paper.write --fix-all` (Fix all citations in current directory)
- `paper.write --generate-full-bib` (Create complete bibliography)
- `paper.write --style-check-all` (Check all files for AI-stiffness)
- `paper.write --template complete-thesis` (Full BA thesis template)

## Notes

### KI-Deklaration Requirement
Remember to declare AI usage in your thesis appendix:
```
Deklarierung der Verwendung von künstlicher Intelligenz

paper.write Skill      Zitierkorrektur, Stilverbesserung    Kapitel 1–6
```

### Academic Integrity
This skill assists with formatting and style, but:
- All ideas and arguments must be your own
- Citations must accurately represent sources
- Plagiarism checks are still required
- Final responsibility lies with the author

### FHNW Compliance
The skill implements the "Wegleitung zur Gestaltung wissenschaftlicher Arbeiten an der Hochschule für Soziale Arbeit FHNW" (31.08.2018). Always verify with current FHNW guidelines before submission.