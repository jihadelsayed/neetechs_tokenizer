# neetechs_tokenizer/clitic_handler.py

CLITICS = ['و', 'ف', 'ب', 'ك', 'ل', 'س', 'ال']

def split_clitics(word: str) -> list:
    """
    Separate common Arabic clitics (e.g., و،ف،ب،ك،ل،س،ال) from the word.
    """
    parts = []
    while word:
        matched = False
        for clitic in sorted(CLITICS, key=len, reverse=True):
            if word.startswith(clitic) and len(word) > len(clitic):
                parts.append(clitic)
                word = word[len(clitic):]
                matched = True
                break
        if not matched:
            parts.append(word)
            break
    return parts
