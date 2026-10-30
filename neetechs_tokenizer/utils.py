"""Unicode utilities that preserve morphologically significant Arabic letters."""
import re
import unicodedata

DIACRITICS_PATTERN = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
ARABIC_LETTERS = re.compile(r"^[\u0621-\u063A\u0641-\u064A\u0671-\u06D3]+$")


def remove_diacritics(text: str) -> str:
    return DIACRITICS_PATTERN.sub("", text)


def normalize_arabic(text: str, *, fold_hamza: bool = False) -> str:
    """Normalize Unicode without collapsing ة/ه or ى/ي.

    Set fold_hamza=True only for fuzzy lookup, not linguistic analysis.
    """
    text = unicodedata.normalize("NFKC", text).replace("ـ", "")
    if fold_hamza:
        text = re.sub(r"[إأآٱ]", "ا", text)
    return text


def is_arabic_word(word: str) -> bool:
    return bool(word) and bool(ARABIC_LETTERS.fullmatch(remove_diacritics(word)))


def clean_text(text: str) -> str:
    return remove_diacritics(normalize_arabic(text)).strip()
