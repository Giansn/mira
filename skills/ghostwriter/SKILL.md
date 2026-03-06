---
name: ghostwriter
description: "Academic ghostwriting assistant for FHNW BA/MA theses - FHNW citation rules, style emulation, chapter writing, research synthesis"
trigger: "ghostwriter / ghostwriting / ghostwrite / ma-kooperation / ghost"
---

# Ghostwriter Skill

## Overview

Specialized academic ghostwriting assistant for FHNW Hochschule für Soziale Arbeit (HSA) theses and papers. Focuses on emulating human academic style (avoiding AI stiffness), implementing FHNW citation rules (Wegleitung 2018), and providing substantive content for BA/MA theses while maintaining academic integrity through proper citation and transparent AI use declaration.

## Trigger Phrases

The skill activates when messages contain:
- `ghostwriter` (primary trigger)
- `ghostwriting` / `ghostwrite`
- `ma-kooperation` (specific MA collaboration context)
- `ghost` (when combined with writing/academic context)
- `schreibe für mich` / `write for me` (with academic intent)
- `kapitel verfassen` / `chapter writing`
- `akademisches ghostwriting`

## Core Principles

### 1. Academic Integrity & Transparency
- **Always cite sources** using FHNW rules
- **Declare AI assistance** in appendix (KI-Deklaration)
- **Never plagiarize** - all content must be original or properly cited
- **Maintain author voice** - enhance, don't replace human thought
- **Transparent about limitations** - admit when something requires human expertise

### 2. FHNW Compliance
- Follow "Wegleitung zur Gestaltung wissenschaftlicher Arbeiten an der Hochschule für Soziale Arbeit FHNW" (31.08.2018)
- Implement citation rules: `(vgl. Autor Jahr: Seiten).` for paraphrases, en dashes for page ranges
- Use proper bibliography formatting
- Adhere to FHNW structure requirements

### 3. Style Emulation (Avoiding AI Stiffness)
- **Active voice preferred** over passive
- **Direct statements** instead of hedging
- **Varied sentence structure** (not repetitive patterns)
- **Academic precision** without jargon overload
- **Human-like flow** - logical progression, natural transitions
- **SOUL.md alignment** - direct, helpful, no filler words

## Architecture

### 1. Style Detection & Emulation
- Analyze existing user writing samples
- Extract stylistic patterns (sentence length, vocabulary, transition words)
- Emulate detected style while improving clarity
- Avoid generic AI phrasing

### 2. Citation Integration
- Use `paper.write` skill for FHNW-compliant citations
- Automatic page number tracking (when available)
- Bibliography generation
- Cross-reference checking

### 3. Content Development
- Thesis structure templates
- Argument development frameworks
- Evidence integration strategies
- Critical analysis techniques

### 4. Quality Assurance
- Plagiarism avoidance checks
- Citation completeness verification
- Style consistency monitoring
- Academic tone maintenance

## Usage Scenarios

### Scenario 1: BA Thesis Chapter Writing
```
User: "ghostwriter: schreibe kapitel 2.1 postkoloniale theorie für ba-thesis"
→ Skill triggers
→ Checks existing thesis structure and style
→ Writes section with FHNW citations, emulating user's academic voice
→ Provides KI-Deklaration text for appendix
```

### Scenario 2: MA Collaboration Content
```
User: "ghostwriter: ma-kooperation konzeptentwicklung"
→ Skill triggers with MA-level depth
→ Accesses existing MA02_LNW_Duygu_Karadag.pdf as style reference
→ Develops conceptual framework with advanced theoretical integration
→ Maintains FHNW compliance
```

### Scenario 3: Style-Specific Writing
```
User: "ghostwriter: schreibe einleitung im stil von duygu karadag"
→ Skill analyzes MA thesis writing style
→ Emulates: direct statements, theoretical integration, citation density
→ Produces introduction with similar voice but original content
```

### Scenario 4: Citation & Style Fix
```
User: "ghostwriter: korrigiere zitate und stil in kapitel 3"
→ Skill processes entire chapter
→ Fixes citations to FHNW format
→ Improves style (removes AI stiffness)
→ Returns cleaned version with change log
```

## Integration with Existing Work

### BA Thesis Files
The skill can directly work with:
- `ba_thesis_chapter1_introduction.md`
- `ba_thesis_chapter2_theoretical_framework.md`
- `ba_thesis_chapter4_3_china_case.md`
- `writing/nz_empirical_analysis_week1.md`

### MA Collaboration
- References `MA02_LNW_Duygu_Karadag.pdf` for style emulation
- Uses `PROJECT.md` for project context
- Integrates with `memory/` system for continuity

### paper.write Skill Integration
- Citation processing via `citation_processor.py`
- Bibliography generation via `bibliography_generator.py`
- Style improvement via `style_improver.py`

## FHNW Ghostwriting Protocols

### 1. Pre-Writing Checklist
- [ ] Confirm thesis structure alignment
- [ ] Identify existing writing samples for style analysis
- [ ] Gather required sources and citations
- [ ] Determine appropriate depth (BA vs. MA)
- [ ] Plan KI-Deklaration wording

### 2. Writing Process
1. **Outline Development**: Logical structure, argument flow
2. **Draft Creation**: Content generation with placeholder citations
3. **Citation Integration**: Add FHNW-compliant citations with page numbers
4. **Style Refinement**: Remove AI stiffness, improve flow
5. **Quality Check**: Verify citations, check for plagiarism patterns

### 3. Post-Writing
- Generate bibliography entries
- Create KI-Deklaration text
- Provide style analysis report
- Suggest further development areas

## Style Emulation Techniques

### Analyzing User Style
```python
# Example style metrics to analyze
style_metrics = {
    "avg_sentence_length": 18,  # words
    "passive_ratio": 0.15,  # 15% passive constructions
    "citation_density": 2.1,  # citations per paragraph
    "transition_words": ["darüber hinaus", "hingegen", "folglich"],
    "theoretical_integration": "high",  # low/medium/high
    "vocabulary_level": "academic"  # casual/academic/technical
}
```

### Emulation Strategies
1. **Vocabulary matching**: Use similar terminology level
2. **Sentence structure**: Match complexity and length patterns
3. **Citation patterns**: Similar frequency and integration style
4. **Theoretical depth**: Align with user's typical analysis level
5. **Transition style**: Use similar connecting phrases

### Avoiding Detection as AI
- Vary sentence openings
- Mix short and long sentences naturally
- Include occasional minor imperfections (human-like)
- Use discipline-specific phrasing
- Maintain consistent voice throughout

## Examples

### Example 1: BA Thesis Introduction (Improved)
**Before (AI-stiff):**
```
Es kann festgestellt werden, dass die internationale Soziale Arbeit vor Herausforderungen steht. Möglicherweise könnte man argumentieren, dass postkoloniale Theorien helfen, diese zu verstehen.
```

**After (Ghostwriter-improved):**
```
Die internationale Soziale Arbeit steht vor der Herausforderung, universelle normative Ansprüche mit lokalen Praxiskontexten zu vermitteln. Postkoloniale Theorien (vgl. Razack 2012: 707–710) bieten hierfür einen analytischen Rahmen, der epistemische Machtverhältnisse sichtbar macht.
```

### Example 2: Theoretical Framework Section
**Ghostwriter Output:**
```
Die Hegemonietheorie Antonio Gramscis (1971) analysiert, wie dominante Gruppen Konsens über kulturelle und ideologische Mittel herstellen, nicht allein durch Zwang. In der internationalen Sozialen Arbeit manifestiert sich dies in der Naturalisierung westlicher Wissenssysteme als universelle Standards (vgl. Gray/Fook 2004: 625–644). Diese hegemoniale Naturalisierung erzeugt, wie Santos (2014: 38–55) zeigt, einen „Epistemizid" – die systematische Auslöschung nicht-westlicher Wissensformen.
```

### Example 3: KI-Deklaration Template
```
Deklarierung der Verwendung von künstlicher Intelligenz

Ghostwriter Skill      Inhaltsentwicklung, Stilemulation      Kapitel 2.1–2.3
paper.write Skill      Zitierkorrektur, Literaturverzeichnis  Gesamte Arbeit
```

## Ethical Guidelines

### What Ghostwriter Does
- Assists with structure and organization
- Improves academic style and clarity
- Ensures proper citation formatting
- Helps develop arguments coherently
- Provides templates and frameworks

### What Ghostwriter Doesn't Do
- Replace original human thought
- Write complete theses without user input
- Guarantee grades or acceptance
- Bypass academic integrity requirements
- Create content without proper citation

### Transparency Requirements
1. **Always declare** AI assistance in appendix
2. **Cite all sources** used in content generation
3. **Acknowledge limitations** of AI-generated content
4. **Maintain human oversight** throughout process
5. **Take final responsibility** as author

## Quality Metrics

### Content Quality
- **Argument coherence**: Logical flow between paragraphs
- **Theoretical integration**: Appropriate use of concepts
- **Evidence support**: Sufficient citation density
- **Originality**: Avoidance of plagiarism patterns
- **Depth**: Appropriate for BA/MA level

### Technical Quality
- **Citation compliance**: 100% FHNW format
- **Bibliography completeness**: All cited sources included
- **Style consistency**: No AI-stiffness patterns
- **Structure adherence**: Follows thesis guidelines
- **Language precision**: Academic German correctness

### Ethical Quality
- **Transparency**: Clear AI use declaration
- **Integrity**: No plagiarism, proper attribution
- **Responsibility**: Human author maintains control
- **Appropriateness**: Content matches assignment requirements

## Troubleshooting

### Common Issues

#### 1. Style Mismatch
```
Problem: Content doesn't match user's writing style
Solution: Provide writing sample for analysis, use style_improver.py
```

#### 2. Citation Errors
```
Problem: Citations not FHNW-compliant
Solution: Run through citation_processor.py, check page numbers
```

#### 3. AI-Stiffness Persists
```
Problem: Text still sounds robotic
Solution: Manual review, vary sentence structure, add human imperfections
```

#### 4. Theoretical Depth Issues
```
Problem: Content too shallow/deep for BA/MA level
Solution: Adjust based on thesis type, consult existing examples
```

### Error Messages
- `ERR_STYLE_MISMATCH`: Cannot emulate requested style
- `ERR_CITATION_INCOMPLETE`: Missing page numbers or sources
- `ERR_ACADEMIC_LEVEL`: Content doesn't match BA/MA requirements
- `ERR_ETHICAL_CONCERN`: Potential academic integrity issue detected

## Advanced Features

### 1. Multi-Model Orchestration
For complex tasks, coordinate:
- **Research phase**: gemini-pro (source finding)
- **Analysis phase**: claude-sonnet (critical thinking)
- **Writing phase**: ghostwriter (style emulation)
- **Review phase**: human + AI collaboration

### 2. Progressive Disclosure
- **Level 1**: Structure and outline assistance
- **Level 2**: Content development with citations
- **Level 3**: Full style emulation and refinement
- **Level 4**: Complete chapter with quality assurance

### 3. Style Library
Store and recall writing styles:
- **Duygu Karadag MA style**: Theoretical integration, direct statements
- **BA thesis style**: Structured, citation-dense, clear arguments
- **User custom style**: Learned from provided samples

## Implementation Commands

### Basic Usage
```bash
# Analyze writing style from sample
ghostwriter --analyze-style --file user_writing_sample.md

# Write section with style emulation
ghostwriter --write --section "2.1 Postkoloniale Theorie" --emulate-style user

# Fix existing chapter
ghostwriter --fix --chapter ba_thesis_chapter2.md --output chapter2_fixed.md

# Generate KI-Deklaration
ghostwriter --generate-declaration --tools "ghostwriter, paper.write" --chapters "1-6"
```

### Integration with paper.write
```bash
# Full processing pipeline
ghostwriter --write --section "3.2 Methodik" | \
paper.write --fix-citations | \
paper.write --improve-style --output methodik_final.md
```

## Configuration

### Style Preferences
- **Formality level**: academic/professional/casual
- **Citation density**: high/medium/low
- **Theoretical depth**: BA/MA/PhD level
- **Language**: German/English/bilingual

### Output Format
- **Markdown**: `.md` for editing
- **Word**: `.docx` via pandoc
- **PDF**: Final formatted version
- **HTML**: Web publication

### Quality Settings
- **Plagiarism check**: strict/standard/lenient
- **Citation verification**: automatic/manual
- **Style enforcement**: strict/flexible
- **Human review required**: yes/no

## Examples from Current Projects

### BA Thesis Integration
```bash
# Process existing chapter
ghostwriter --fix --file ba_thesis_chapter1.md --output chapter1_improved.md

# Write new section
ghostwriter --write --section "4.2 Schweiz-Fallstudie" \
  --based-on writing/nz_empirical_analysis_week1.md \
  --output writing/ch_empirical_analysis_week2.md
```

### MA Collaboration
```bash
# Emulate Duygu Karadag style
ghostwriter --write --section "Konzeptentwicklung" \
  --emulate-style ma02_duygu \
  --references MA02_LNW_Duygu_Karadag.pdf \
  --output ma_kooperation_konzept.md
```

## Best Practices

### For Users
1. **Provide writing samples** for better style emulation
2. **Review all AI-generated content** before submission
3. **Verify citations** match your actual sources
4. **Customize KI-Deklaration** to reflect actual use
5. **Maintain academic integrity** - AI assists, doesn't replace

### For Skill
1. **Always cite** - no uncited content
2. **Emulate, don't copy** - avoid plagiarism
3. **Be transparent** about AI assistance
4. **Respect academic levels** - BA vs. MA differences
5. **Maintain human voice** - enhance individuality

## Future Development

### Planned Features
1. **Style transfer learning**: AI learns user style from few samples
2. **Plagiarism detection**: Integrated similarity checking
3. **Citation auto-completion**: Fetch page numbers from libraries
4. **Multi-language support**: German/English seamless switching
5. **Peer-review simulation**: Generate constructive feedback

### Integration Goals
1. **Zotero/BibTeX sync**: Automatic bibliography updates
2. **Overleaf integration**: LaTeX template compatibility
3. **FHNW submission system**: Direct formatting for submission
4. **Academic database access**: JSTOR, SpringerLink integration

## Quick Start

### Immediate Use
Just say `ghostwriter` followed by your request:
- `ghostwriter schreibe einleitung für ba-thesis`
- `ghostwriter korrigiere stil in kapitel 3`
- `ghostwriter erstelle ki-deklaration`
- `ghostwriter analysiere schreibstil aus dieser probe`

### For Best Results
1. Provide a writing sample for style analysis
2. Specify thesis type (BA/MA) and chapter
3. List key sources to be cited
4. Indicate preferred theoretical depth
5. Review output and provide feedback

## Notes

### Academic Context
This skill is designed for **assistance**, not replacement. It follows FHNW guidelines and maintains academic integrity through:
- Proper citation of all sources
- Transparent AI use declaration
- Human oversight requirement
- Original content generation

### Legal & Ethical Compliance
- Complies with FHNW academic integrity policies
- Requires human author responsibility
- Transparent about AI assistance level
- No guarantee of grades or acceptance
- Educational use intended

### Skill Limitations
- Cannot access paid academic databases
- Limited to provided source materials
- Style emulation requires user samples
- Theoretical depth constrained by training data
- Human review always recommended

## Support

For issues or questions:
1. Check `paper.write` skill for citation problems
2. Review SOUL.md for style guidance
3. Consult FHNW Wegleitung for formatting rules
4. Contact through OpenClaw system for technical issues

---

**Remember**: Ghostwriting assists, but you're the author. Your voice, your ideas, your responsibility.