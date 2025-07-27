# neetechs_tokenizer/diacritics.py

BASIC_DIACRITIC_DICT = {
    "احب": "أُحِبُّ",
    "الذكاء": "ٱلذَّكَاءَ",
    "الاصطناعي": "ٱلِصْطِنَاعِيَّ",
    "الدرس": "ٱلدَّرْسَ",
    "كتب": "كَتَبَ"
}

def restore_diacritics(text: str, method: str = "offline") -> str:
    """
    Restore missing Arabic diacritics (tashkeel) using basic dictionary.
    """
    words = text.split()
    restored = []
    for word in words:
        restored.append(BASIC_DIACRITIC_DICT.get(word, word))
    return ' '.join(restored)

# Optional test
if __name__ == "__main__":
    plain = "احب الذكاء الاصطناعي"
    print("→", restore_diacritics(plain))
