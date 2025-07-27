# Placeholder
# neetechs_tokenizer/utils.py

import re

# Arabic diacritics regex pattern
DIACRITICS_PATTERN = re.compile(r'[\u064B-\u0652]')

def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritics (tashkeel) from text."""
    return DIACRITICS_PATTERN.sub('', text)

def normalize_arabic(text: str) -> str:
    """Normalize common Arabic letter variants."""
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'[ى]', 'ي', text)
    text = re.sub(r'[ؤئ]', 'ء', text)
    text = re.sub(r'ة', 'ه', text)
    return text

def is_arabic_word(word: str) -> bool:
    """Check if a word consists only of Arabic letters."""
    return all('\u0600' <= c <= '\u06FF' or c == ' ' for c in word)

def clean_text(text: str) -> str:
    """Strip diacritics, normalize letters, and trim whitespace."""
    text = remove_diacritics(text)
    text = normalize_arabic(text)
    return text.strip()

# Optional: test run
if __name__ == "__main__":
    raw = "أُحِبُّ التَّعَلُّمَ وَالتَّطْوِيرَ"
    print("Cleaned:", clean_text(raw))
