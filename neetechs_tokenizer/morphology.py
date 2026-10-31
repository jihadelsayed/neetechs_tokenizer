"""Conservative root-pattern and candidate-based morphological analyzer."""
from __future__ import annotations

from .utils import clean_text
from .candidates import priority_identifier
from .lexicon import generate_form, load_lexicon
from .conjugation import analyze_perfect
from .verb_forms import analyze_imperfect, analyze_imperative
from .weak_forms import analyze_weak_verb
from .validation import compatible_affixes, valid_analysis


def _ranking(analysis: dict) -> tuple:
    """Prefer validated explicit morph boundaries; retain ambiguous readings."""
    return (-analysis["score"], analysis["root"], analysis["stem"],
            analysis.get("source", ""), str(analysis.get("person", "")))


def word_analyzer(word: str) -> dict:
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    normalized = clean_text(word)
    if not normalized or any(ch.isspace() for ch in normalized):
        return {"word": word, "normalized": normalized, "analyses": []}

    analyses = []
    lexicon = load_lexicon()
    for candidate in priority_identifier(normalized):
        for root, pattern, pos in lexicon.get(candidate.stem, ()):
            if pos not in candidate.allowed_pos:
                continue
            # Standard Arabic does not combine noun definite article
            # with an attached possessive pronoun.
            if not compatible_affixes(candidate.prefixes, candidate.labels, pos):
                continue
            if generate_form(root, pattern) != candidate.stem:
                continue
            # Literal subject وا is applicable to reviewed perfect verbs;
            # the object-pronoun construction remains a starter heuristic.
            suffixes = [
                {"surface": p, "function": label}
                for p, label in zip(candidate.suffixes, candidate.labels)
            ]
            analyses.append({
                "root": root, "pattern": pattern, "stem": candidate.stem,
                "part_of_speech": pos, "prefixes": list(candidate.prefixes),
                "suffixes": suffixes, "source": "bundled_lexicon_v1",
                "score": round(min(0.98, 0.90 + candidate.priority * 0.01), 2),
            })
    # Keep full conjugation candidates instead of stripping their affixes
    # and losing grammatical person/number.
    analyses.extend(analyze_perfect(normalized))
    analyses.extend(analyze_imperfect(normalized))
    analyses.extend(analyze_imperative(normalized))
    analyses.extend(analyze_weak_verb(normalized))
    # Collapse identical analyses caused by overlapping lexical/rule paths,
    # but preserve genuinely different grammatical interpretations.
    unique = {}
    for analysis in analyses:
        signature = (
            analysis["root"], analysis["pattern"], analysis["stem"],
            analysis["part_of_speech"], tuple(analysis["prefixes"]),
            tuple((s["surface"], s["function"]) for s in analysis["suffixes"]),
            analysis.get("tense"), analysis.get("person"),
            analysis.get("number"), analysis.get("gender")
        )
        if signature not in unique or analysis["score"] > unique[signature]["score"]:
            unique[signature] = analysis
    # Every exposed analysis must account for the complete normalized
    # surface. Preserve unknown words rather than returning partial parses.
    analyses = [a for a in unique.values()
                if valid_analysis(normalized, a)]
    analyses.sort(key=_ranking)
    return {"word": word, "normalized": normalized, "analyses": analyses}


def wordAnalyzer(word: str) -> dict:
    return word_analyzer(word)


def get_root(word: str, *, require_unique: bool = False) -> str | None:
    """Return top root, or abstain on top-score root ties in strict mode.

    Strict mode handles only *ties* between different roots. It does not
    certify that a unique top-ranked root is linguistically correct.
    """
    matches = word_analyzer(word)["analyses"]
    if not matches:
        return None
    if require_unique:
        best_score = matches[0]["score"]
        roots = {a["root"] for a in matches if a["score"] == best_score}
        if len(roots) > 1:
            return None
    return matches[0]["root"]
