"""Conservative splitting: only split words with a validated lexical analysis."""
from .morphology import word_analyzer


def split_clitics(word: str) -> list[str]:
    analyses = word_analyzer(word)["analyses"]
    if not analyses:
        return [word]
    best = analyses[0]
    return best["prefixes"] + [best["stem"]] + [s["surface"] for s in best["suffixes"]]
