# neetechs_tokenizer/tokenizer.py

from .utils import clean_text
from .clitic_handler import split_clitics
from .root_extractor import extract_root
from .pattern_matcher import match_pattern

def tokenize(text: str) -> list:
    """
    Tokenize Arabic sentence into meaningful units: clitics, roots, stems.
    """
    clean = clean_text(text)
    words = clean.split()

    tokens = []
    for word in words:
        clitic_parts = split_clitics(word)
        tokens.extend(clitic_parts)

    return tokens

def analyze_tokens(tokens: list) -> list:
    """
    Analyze tokens: root + pattern matching (optional).
    """
    analyzed = []
    for token in tokens:
        root = extract_root(token)
        pattern = match_pattern(token, root) if root else None
        analyzed.append({
            "token": token,
            "root": root,
            "pattern": pattern
        })
    return analyzed

# Optional test
if __name__ == "__main__":
    example = "استكتب المعلم الطالب الدرس"
    tokens = tokenize(example)
    print("Tokens:", tokens)

    analysis = analyze_tokens(tokens)
    for a in analysis:
        print(a)
