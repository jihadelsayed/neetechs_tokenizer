# neetechs_tokenizer/translator.py

# Optional: use OpenAI or Google Translate API later
# from transformers import MarianMTModel, MarianTokenizer

BASIC_TRANSLATION_DICT = {
    "أنا": "I",
    "أحب": "love",
    "الذكاء": "intelligence",
    "الاصطناعي": "artificial",
    "كتب": "wrote",
    "طالب": "student",
    "معلم": "teacher",
    "الدرس": "the lesson",
    "استكتب": "made someone write"
}

def translate(text: str, method: str = "offline") -> str:
    """
    Translate Arabic to English using a dictionary-based method (default).
    Future support: method='openai', 'transformers', etc.
    """
    words = text.split()
    translated = []
    for word in words:
        t = BASIC_TRANSLATION_DICT.get(word, f"[{word}]")
        translated.append(t)
    return ' '.join(translated)

# Optional test
if __name__ == "__main__":
    a = "أنا أحب الذكاء الاصطناعي"
    print("→", translate(a))
