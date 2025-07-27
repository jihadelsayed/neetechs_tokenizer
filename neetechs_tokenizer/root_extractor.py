# neetechs_tokenizer/root_extractor.py

COMMON_ROOTS = {
    'كتب': ['كاتب', 'مكتوب', 'كتاب', 'كتابة', 'استكتب'],
    'علم': ['عالم', 'معلوم', 'تعليم', 'علم']
}

def extract_root(word: str) -> str or None:
    """
    Simple rule-based root extractor using a sample root dictionary.
    """
    for root, forms in COMMON_ROOTS.items():
        if word in forms or any(word.startswith(f) for f in forms):
            return root
    return None
