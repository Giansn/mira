"""
Filler phrase stripper for dense token output.
Run: python3 filler_stripper.py
"""

import re

# Simple string replacements (faster, more predictable)
FILLER_REPLACEMENTS = [
    # Start-of-response fillers
    "Great question! ",
    "I'd be happy to help you with that. ",
    "I'd love to help you with that. ",
    "I am happy to help you. ",
    "Happy to help! ",
    "Sure thing. ",
    "Of course. ",
    "Certainly. ",
    
    # Sentence-start fillers (with comma/space)
    "Now, ",
    "So, ",
    "Basically, ",
    "Actually, ",
    "Honestly, ",
    "Simply, ",
    "Just, ",
    "Anyway, ",
    
    # Phrase fillers
    "The answer is that ",
    "To answer your question, ",
    "As I mentioned earlier, ",
    "As I said before, ",
    "Here is the answer: ",
    "Here is the solution: ",
    "As you can see, ",
    "Let me explain, ",
    "Let me clarify, ",
    
    # End-of-response fillers
    " Let me know if you need more details!",
    " Hope this helps!",
    " Feel free to ask if you have more questions.",
    " Any questions?",
    "!",
]

def strip_filler(text: str) -> str:
    """Remove filler phrases from text."""
    result = text
    
    # First normalize: replace newlines with spaces
    result = re.sub(r'\n+', ' ', result)
    
    # Apply each replacement
    for filler in FILLER_REPLACEMENTS:
        result = result.replace(filler, '')
        # Also try lowercase version
        result = result.replace(filler.lower(), '')
    
    # Clean up artifacts
    result = re.sub(r'\s+', ' ', result).strip()
    
    # Capitalize if needed
    if result and result[0].islower():
        result = result[0].upper() + result[1:]
    
    # Clean up leading punctuation
    result = re.sub(r'^[,\.\s]+', '', result)
    
    return result


if __name__ == '__main__':
    # Demo
    BEFORE = """Great question! I'd be happy to help you with that.

Sure, let me explain how photosynthesis works. Basically, plants convert 
sunlight into energy through a process called photosynthesis.

The answer is that chlorophyll in the leaves absorbs light energy. This is 
then used to convert carbon dioxide and water into glucose and oxygen.

As you can see, this process is essential for plant life. Actually, it's 
fundamental for most ecosystems on Earth.

So the key points are: sunlight + chlorophyll + CO2 + water = glucose + oxygen. 
Anyway, let me know if you need more details!"""

    AFTER = strip_filler(BEFORE)
    
    print("=" * 50)
    print("BEFORE (filler included):")
    print("=" * 50)
    print(BEFORE)
    
    print("\n" + "=" * 50)
    print("AFTER (filler stripped):")
    print("=" * 50)
    print(AFTER)
    
    # Token count (approximate: 1 token ≈ 0.75 words)
    w_before = len(BEFORE.split())
    w_after = len(AFTER.split())
    t_before = int(w_before * 1.3)
    t_after = int(w_after * 1.3)
    
    print("\n" + "=" * 50)
    print("TOKEN COUNT:")
    print("=" * 50)
    print(f"Words before: {w_before} → ~{t_before} tokens")
    print(f"Words after:  {w_after} → ~{t_after} tokens")
    print(f"Reduction:    {t_before - t_after} tokens ({100*(t_before-t_after)/t_before:.1f}%)")
