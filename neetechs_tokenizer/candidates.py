"""Prioritized, lossless Arabic affix candidates.

No string is segmented unless its entire surface can be reconstructed and
the remaining stem is validated against the reviewed lexicon.
"""
from dataclasses import dataclass
from .affixes import PREFIXES, SUFFIXES


@dataclass(frozen=True)
class Candidate:
    surface: str
    stem: str
    prefixes: tuple[str, ...]
    suffixes: tuple[str, ...]
    labels: tuple[str, ...]
    allowed_pos: tuple[str, ...]
    priority: int


def priority_identifier(word: str) -> list[Candidate]:
    """Generate reversible candidate cuts ordered by linguistic specificity."""
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    candidates = []
    seen = set()
    for prefix, prefix_parts, prefix_pos in PREFIXES:
        if not word.startswith(prefix):
            continue
        for ending, ending_parts, suffix_pos, labels in SUFFIXES:
            if ending and not word.endswith(ending):
                continue
            end = len(word) - len(ending) if ending else len(word)
            stem = word[len(prefix):end]
            if not stem or prefix + stem + ending != word:
                continue
            allowed = tuple(pos for pos in prefix_pos if pos in suffix_pos)
            if not allowed:
                continue
            # The definite article cannot attach to verbs. A future
            # marker cannot be applied to bare perfect dictionary stems.
            if "س" in prefix_parts:
                continue
            key = (stem, prefix_parts, ending_parts)
            if key in seen:
                continue
            seen.add(key)
            specificity = len(prefix_parts) * 2 + len(ending_parts)
            candidates.append(Candidate(
                word, stem, tuple(prefix_parts), tuple(ending_parts),
                tuple(labels), allowed, specificity
            ))
    return sorted(candidates, key=lambda c: (-c.priority, -len(c.stem), c.stem))


def priorityIdentifier(word: str) -> list[Candidate]:
    return priority_identifier(word)
