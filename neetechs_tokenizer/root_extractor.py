"""Backwards-compatible root extraction API."""
from .morphology import get_root


def extract_root(word: str) -> str | None:
    return get_root(word)
