# neetechs_tokenizer/pattern_matcher.py

PATTERNS = {
    'فاعل': lambda w: len(w) == 4,
    'مفعول': lambda w: len(w) == 5 and w.startswith('م'),
    'افتعل': lambda w: len(w) >= 6 and w.startswith('است'),
}

def match_pattern(word: str, root: str) -> str or None:
    """
    Naive pattern matching based on surface form.
    """
    for pattern, rule in PATTERNS.items():
        if rule(word):
            return pattern
    return None
