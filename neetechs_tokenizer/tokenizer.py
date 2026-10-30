"""Arabic-aware word tokenization with optional validated clitic segmentation."""
import re
from .morphology import word_analyzer
from .utils import clean_text, is_arabic_word

WORD_RE = re.compile(r"[\u0621-\u063A\u0641-\u064A\u0671-\u06D3]+|[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+(?:[.,][0-9]+)*|[^\s]", re.UNICODE)


def tokenize(text: str, *, split_clitics: bool = True) -> list[str]:
    """Tokenize Arabic, keeping unknown words intact instead of guessing cuts."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    tokens = WORD_RE.findall(clean_text(text))
    if not split_clitics:
        return tokens
    segmented = []
    for token in tokens:
        if not is_arabic_word(token):
            segmented.append(token)
            continue
        analyses = word_analyzer(token)["analyses"]
        if analyses:
            best = analyses[0]
            pieces = (list(best["prefixes"]) + [best["stem"]]
                      + [s["surface"] for s in best["suffixes"]])
            # Never emit pieces if an analysis loses/changes surface letters.
            # Future orthographic transforms need an explicit alignment layer.
            if all(pieces) and "".join(pieces) == token:
                segmented.extend(pieces)
            else:
                segmented.append(token)
        else:
            segmented.append(token)
    return segmented


def analyze_tokens(tokens: list[str]) -> list[dict]:
    """Retain the original lightweight output shape for existing callers."""
    analyzed = []
    for token in tokens:
        result = word_analyzer(token)
        best = result["analyses"][0] if result["analyses"] else None
        analyzed.append({"token": token, "root": best["root"] if best else None,
                         "pattern": best["pattern"] if best else None})
    return analyzed
