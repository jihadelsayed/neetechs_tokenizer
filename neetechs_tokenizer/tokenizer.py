"""Arabic-aware word tokenization with optional validated clitic segmentation."""
import re
import unicodedata
from .morphology import word_analyzer
from .utils import clean_text, is_arabic_word, normalize_arabic, remove_diacritics

WORD_RE = re.compile(r"[\u0621-\u063A\u0641-\u064A\u0671-\u06D3]+|[A-Za-z]+(?:'[A-Za-z]+)?|[0-9\u0660-\u0669\u06F0-\u06F9]+(?:[.,\u066B\u066C][0-9\u0660-\u0669\u06F0-\u06F9]+)*|[^\s]", re.UNICODE)


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



def _original_offset_map(text: str, normalized: str) -> list[tuple[int, int]] | None:
    """Map normalized character positions to original spans by combining cluster.

    Returns None if normalization crosses a cluster boundary in a way that
    prevents reliable alignment (for example, some cross-character forms).
    """
    clusters = []
    for index, char in enumerate(text):
        if clusters and unicodedata.combining(char):
            previous, start, _ = clusters[-1]
            clusters[-1] = (previous + char, start, index + 1)
        else:
            clusters.append((char, index, index + 1))
    expanded = []
    for value, start, end in clusters:
        rendered = remove_diacritics(normalize_arabic(value))
        expanded.extend((ch, start, end) for ch in rendered)
    while expanded and expanded[0][0].isspace():
        expanded.pop(0)
    while expanded and expanded[-1][0].isspace():
        expanded.pop()
    return expanded if "".join(ch for ch, _, _ in expanded) == normalized else None

def analyze_text(text: str, *, include_segments: bool = False, include_original_offsets: bool = False) -> list[dict]:
    """Analyze a normalized sentence token-by-token without destructive splitting.

    Each result preserves the surface token and all available morphology
    candidates. Punctuation, non-Arabic and unknown words remain visible
    with an empty analyses list. Optional segments are lossless.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    normalized = clean_text(text)
    results = []
    source_map = _original_offset_map(text, normalized) if include_original_offsets else None
    for match in WORD_RE.finditer(normalized):
        token = match.group()
        analyses = word_analyzer(token)["analyses"] if is_arabic_word(token) else []
        record = {
            "token": token,
            "start": match.start(),
            "end": match.end(),
            "analyses": analyses,
        }
        if include_original_offsets:
            if source_map is None:
                record["original_start"] = None
                record["original_end"] = None
            else:
                record["original_start"] = source_map[match.start()][1]
                record["original_end"] = source_map[match.end() - 1][2]
        if include_segments:
            if analyses:
                best = analyses[0]
                pieces = (list(best["prefixes"]) + [best["stem"]]
                          + [s["surface"] for s in best["suffixes"]])
                record["segments"] = pieces if all(pieces) and "".join(pieces) == token else [token]
            else:
                record["segments"] = [token]
        results.append(record)
    return results
