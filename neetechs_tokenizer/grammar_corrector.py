# neetechs_tokenizer/grammar_corrector.py

CORRECTION_RULES = {
    "انا يحب": "أنا أحب",
    "هى": "هي",
    "فى": "في",
    "انتا": "أنتَ",
    "انتي": "أنتِ",
    "لمازا": "لماذا"
}

def correct_grammar(text: str, method: str = "offline") -> str:
    """
    Naive grammar correction using dictionary of known mistakes.
    """
    corrected = text
    for wrong, right in CORRECTION_RULES.items():
        corrected = corrected.replace(wrong, right)
    return corrected

# Optional test
if __name__ == "__main__":
    raw = "انا يحب الذكاء الاصطناعي"
    fixed = correct_grammar(raw)
    print("→", fixed)
