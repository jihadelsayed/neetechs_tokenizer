"""Reviewed surface affix combinations and lightweight compatibility constraints.

Segmentation is conservative: only known lexical stems are accepted.
These are unvowelled surface candidates, not a general clitic grammar.
"""
PREFIXES = (
    ("", (), ("noun", "verb")),
    ("و", ("و",), ("noun", "verb")),
    ("ف", ("ف",), ("noun", "verb")),
    ("ال", ("ال",), ("noun",)),
    ("وال", ("و", "ال"), ("noun",)),
    ("فال", ("ف", "ال"), ("noun",)),
    ("ب", ("ب",), ("noun",)),
    ("ل", ("ل",), ("noun",)),
    ("ك", ("ك",), ("noun",)),
    ("بال", ("ب", "ال"), ("noun",)),
    ("كال", ("ك", "ال"), ("noun",)),
    ("س", ("س",), ("verb",)),
    ("وس", ("و", "س"), ("verb",)),
)
SUFFIXES = (
    ("", (), ("noun", "verb"), ()),
    ("وا", ("وا",), ("verb",), ("subject:3mp",)),
    ("وهم", ("و", "هم"), ("verb",), ("subject:3mp", "object:3mp")),
    ("هم", ("هم",), ("noun", "verb"), ("possessive-or-object:3mp",)),
    ("ها", ("ها",), ("noun", "verb"), ("possessive-or-object:3fs",)),
)
