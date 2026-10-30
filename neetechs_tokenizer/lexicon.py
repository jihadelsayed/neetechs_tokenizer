"""Bundled, versioned morphological lexicon with strict validation."""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files


def generate_form(root: str, pattern: str) -> str:
    """Substitute a sound triliteral root into an unvowelled template."""
    if len(root) != 3:
        raise ValueError("Only triliteral roots are supported")
    return "".join(dict(zip("فعل", root)).get(c, c) for c in pattern)


def validate_lexicon(payload: dict) -> dict[str, tuple[tuple[str, str, str], ...]]:
    """Validate lexical data before use; reject inconsistent patterns."""
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Unsupported lexicon schema")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Lexicon entries must be a list")
    by_surface: dict[str, list[tuple[str, str, str]]] = {}
    seen = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"surface", "root", "pattern", "pos"}:
            raise ValueError(f"Invalid lexicon entry {index}")
        surface, root, pattern, pos = (entry[k] for k in ("surface", "root", "pattern", "pos"))
        if not all(isinstance(v, str) and v for v in (surface, root, pattern, pos)):
            raise ValueError(f"Empty lexicon field in entry {index}")
        if pos not in {"noun", "verb"} or generate_form(root, pattern) != surface:
            raise ValueError(f"Invalid root, pattern or POS in entry {index}: {surface}")
        item = (root, pattern, pos)
        if (surface, item) in seen:
            raise ValueError(f"Duplicate lexicon entry {index}: {surface}")
        seen.add((surface, item))
        by_surface.setdefault(surface, []).append(item)
    return {surface: tuple(entries) for surface, entries in by_surface.items()}


@lru_cache(maxsize=1)
def load_lexicon() -> dict[str, tuple[tuple[str, str, str], ...]]:
    """Load bundled UTF-8 data (also works in installed wheels)."""
    resource = files("neetechs_tokenizer").joinpath("data/lexicon.json")
    with resource.open("r", encoding="utf-8") as stream:
        return validate_lexicon(json.load(stream))
