# Ghostwriter Skill

Academic ghostwriting assistant for FHNW BA/MA theses with FHNW citation compliance, style emulation, and academic integrity transparency.

## Features

### 1. Style Emulation & Analysis
- Analyze writing style from samples (sentence length, passive ratio, citation density, vocabulary level)
- Emulate user's academic voice while improving clarity
- Avoid AI-stiffness patterns common in generated text

### 2. FHNW Academic Compliance
- Integrates with `paper.write` skill for citation formatting
- Follows "Wegleitung zur Gestaltung wissenschaftlicher Arbeiten" (FHNW 2018)
- Generates proper KI-Deklaration (AI use declaration) for thesis appendix

### 3. Thesis Section Templates
- BA/MA thesis structure templates
- Theoretical framework development
- Case study analysis templates
- Methodology and discussion sections

### 4. Ethical Ghostwriting
- Transparent about AI assistance
- Requires human oversight and responsibility
- Maintains academic integrity through proper citation
- Assists but doesn't replace original thought

## Installation

The skill is installed in your OpenClaw workspace. To use it:

1. **Trigger the skill** with:
   - `ghostwriter` (primary trigger)
   - `ghostwriting` / `ghostwrite`
   - `ma-kooperation` (MA collaboration context)
   - `schreibe für mich` (with academic intent)

2. **Or use command-line tools** directly:
   ```bash
   cd /home/ubuntu/.openclaw/workspace/skills/ghostwriter
   
   # Analyze writing style
   python3 ghostwriter.py --analyze-style user_writing_sample.md
   
   # Write thesis section
   python3 ghostwriter.py --write-section "Theoretischer Rahmen" --output theoretical.md
   
   # Generate KI-Deklaration
   python3 ghostwriter.py --generate-declaration \
     --tools "ghostwriter,paper.write" \
     --chapters "2.1-2.3, gesamte Arbeit" \
     --output ki_deklaration.md
   
   # Fix style and citations
   python3 ghostwriter.py --fix chapter1.md --output chapter1_fixed.md
   ```

## Usage Examples

### Example 1: Style Analysis
```
User: "ghostwriter: analysiere meinen schreibstil aus dieser probe"
→ Skill analyzes writing sample
→ Returns metrics: sentence length, passive ratio, citation density, vocabulary level
→ Provides style improvement suggestions
```

### Example 2: Section Writing
```
User: "ghostwriter: schreibe kapitel 2.1 postkoloniale theorie"
→ Skill writes theoretical section with FHNW citations
→ Emulates academic style (if reference provided)
→ Includes placeholder citations for user to fill with actual sources
```

### Example 3: MA Collaboration
```
User: "ghostwriter: ma-kooperation konzeptentwicklung im stil von duygu karadag"
→ Skill references MA02_LNW_Duygu_Karadag.pdf for style
→ Develops conceptual framework with theoretical integration
→ Maintains FHNW compliance and generates KI-Deklaration
```

### Example 4: Full Chapter Improvement
```
User: "ghostwriter: verbessere kapitel 3 stil und zitate"
→ Skill processes entire chapter
→ Fixes citations to FHNW format via paper.write integration
→ Improves style (removes AI-stiffness, improves flow)
→ Returns cleaned version with change log
```

## Integration with paper.write Skill

The ghostwriter skill integrates seamlessly with `paper.write`:

```bash
# Full pipeline: Write → Fix citations → Improve style
ghostwriter --write-section "Methodik" \
  | paper.write --fix-citations \
  | paper.write --improve-style \
  > methodik_final.md
```

### Shared Components:
- **Citation processing**: Uses `citation_processor.py` from paper.write
- **Style improvement**: Uses `style_improver.py` from paper.write  
- **Bibliography generation**: Can trigger `bibliography_generator.py`

## FHNW Compliance Features

### Citation Formatting
- Converts `(Spivak 1988)` → `(vgl. Spivak 1988: [Seiten]).`
- Uses en dashes for page ranges: `139–141`
- Proper handling of multiple authors: `(Müller/Overbye 2010: 47)`
- Supports `vgl.` for paraphrases, direct quotes without `vgl.`

### KI-Deklaration Generation
- Generates proper AI use declaration for thesis appendix
- Multiple templates (minimal, standard, detailed)
- BA/MA-specific variations
- Includes date and responsibility statement

### Academic Style
- Active voice preferred over passive
- Direct statements instead of hedging
- Varied sentence structure
- Discipline-specific terminology
- Logical argument progression

## Ethical Guidelines

### What This Skill Does
- Assists with structure and organization
- Improves academic style and clarity
- Ensures proper citation formatting
- Helps develop arguments coherently
- Provides templates and frameworks

### What This Skill Doesn't Do
- Replace original human thought
- Write complete theses without user input
- Guarantee grades or acceptance
- Bypass academic integrity requirements
- Create content without proper citation

### Transparency Requirements
1. **Always declare** AI assistance in appendix using generated KI-Deklaration
2. **Cite all sources** used in content generation
3. **Acknowledge limitations** of AI-generated content
4. **Maintain human oversight** throughout process
5. **Take final responsibility** as author

## Templates Included

### BA Thesis Structure
- Introduction with research questions
- Theoretical framework (postcolonial, hegemony, epistemic justice)
- Methodology (comparative case study)
- Case studies (NZ, CH, CN templates)
- Discussion and conclusion

### MA Thesis Enhancements
- Deeper theoretical integration
- Complex argument development
- Advanced methodology justification
- Critical reflection sections
- Detailed KI-Deklaration with reflection

### Section-Specific Templates
- `Einleitung`: Context, research questions, objectives
- `Theoretischer Rahmen`: Theoretical synthesis
- `Methodik`: Research design, case selection, analysis
- `Fallstudie`: Contextualization, three-lens analysis
- `Diskussion`: Answering research questions, implications
- `Schlussfolgerung`: Summary, outlook, final remarks

## Testing

### Quick Tests
```bash
# Test style analysis
echo "Die internationale Soziale Arbeit steht vor Herausforderungen." > test.txt
python3 ghostwriter.py --analyze-style test.txt

# Test section writing
python3 ghostwriter.py --write-section "Einleitung" --output test_einleitung.md

# Test KI-Deklaration generation
python3 ghostwriter.py --generate-declaration \
  --tools "ghostwriter" \
  --chapters "2.1-2.3" \
  --output test_deklaration.md
```

### Integration Test
```bash
# Full pipeline test
python3 ghostwriter.py --write-section "Methodik" --output test_methodik.md
python3 ../paper-write/citation_processor.py --file test_methodik.md --fix
python3 ../paper-write/style_improver.py --file test_methodik.md --improve --output test_methodik_final.md
```

## Configuration

### Style Preferences
Set in `ghostwriter.py` or via command line:
- `--style-reference FILE`: Use file as writing style reference
- `--emulate-style TYPE`: academic/technical/casual
- `--citation-density LEVEL`: high/medium/low
- `--theoretical-depth LEVEL`: BA/MA/PhD

### Output Options
- Markdown (`.md`) for editing
- Word (`.docx`) via pandoc integration
- PDF for final submission
- HTML for web publication

### Quality Settings
- Plagiarism pattern avoidance
- Citation completeness verification
- Style consistency enforcement
- Academic level appropriateness

## Best Practices

### For Optimal Results
1. **Provide writing samples** for better style emulation
2. **Review all AI-generated content** before submission
3. **Verify citations** match your actual sources
4. **Customize KI-Deklaration** to reflect actual use
5. **Maintain academic integrity** - AI assists, doesn't replace

### Workflow Recommendation
```
1. Provide writing sample for style analysis
2. Use ghostwriter for structure and draft
3. Fill in your own research and sources
4. Run through paper.write for citation fixing
5. Review and edit final version
6. Generate KI-Deklaration for appendix
7. Submit with transparent AI use declaration
```

## Troubleshooting

### Common Issues

#### Style Mismatch
```
Problem: Content doesn't match user's writing style
Solution: Provide better writing sample, use --style-reference
```

#### Citation Format Errors
```
Problem: Citations not FHNW-compliant
Solution: Run through paper.write citation processor
```

#### AI-Stiffness Persists
```
Problem: Text still sounds robotic
Solution: Manual editing, vary sentence structure, add human elements
```

#### Integration Issues
```
Problem: paper.write modules not found
Solution: Ensure paper-write skill is installed in sibling directory
```

### Error Messages
- `ERR_STYLE_MISMATCH`: Cannot emulate requested style
- `ERR_NO_SAMPLE`: No writing sample provided for analysis
- `ERR_CITATION_FORMAT`: Citation formatting failed
- `ERR_ACADEMIC_LEVEL`: Content doesn't match required level

## Examples from Current Projects

### BA Thesis Integration
```bash
# Process existing chapter
python3 ghostwriter.py --fix ba_thesis_chapter1.md --output chapter1_improved.md

# Write new section based on existing style
python3 ghostwriter.py --write-section "4.2 Schweiz-Fallstudie" \
  --style-reference writing/nz_empirical_analysis_week1.md \
  --output writing/ch_empirical_analysis_week2.md
```

### MA Collaboration Example
```bash
# Emulate Duygu Karadag MA style
python3 ghostwriter.py --write-section "Konzeptentwicklung" \
  --style-reference ../media/inbound/MA02_LNW_Duygu_Karadag.pdf \
  --output ma_kooperation_konzept.md
```

## Future Development

### Planned Features
1. **Style transfer learning**: AI learns user style from few samples
2. **Plagiarism detection**: Integrated similarity checking
3. **Citation auto-completion**: Fetch page numbers from digital libraries
4. **Multi-language support**: German/English seamless switching
5. **Peer-review simulation**: Generate constructive feedback

### Integration Goals
1. **Zotero/BibTeX sync**: Automatic bibliography updates
2. **Overleaf integration**: LaTeX template compatibility
3. **FHNW submission system**: Direct formatting for submission
4. **Academic database access**: JSTOR, SpringerLink integration

## Support

For issues or questions:
1. Check `paper.write` skill for citation problems
2. Review SOUL.md for overall style guidance
3. Consult FHNW Wegleitung for formatting rules
4. Contact through OpenClaw system for technical issues

## Legal & Ethical Compliance

- Complies with FHNW academic integrity policies
- Requires human author responsibility
- Transparent about AI assistance level
- No guarantee of grades or acceptance
- Educational use intended

---

**Remember**: This skill assists, but you're the author. Your voice, your ideas, your responsibility.