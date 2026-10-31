"""Shared checks for conservative, lossless Arabic morphological analyses."""


def compatible_affixes(prefixes, suffix_labels, part_of_speech):
    """Reject impossible article/possessive combinations without guessing roots."""
    if part_of_speech not in {"noun", "verb"}:
        return False
    if "ال" in prefixes:
        if part_of_speech != "noun":
            return False
        if any(label.startswith(("possessive-or-object:", "possessive:"))
               for label in suffix_labels):
            return False
    return True


def reconstructs_surface(surface, prefixes, stem, suffix_surfaces):
    """Require every character of the normalized word to be accounted for."""
    return bool(stem) and (
        "".join(prefixes) + stem + "".join(suffix_surfaces) == surface
    )


def valid_analysis(surface, analysis):
    """Validate the surface and compatibility of an assembled analysis."""
    prefixes = analysis["prefixes"]
    suffixes = analysis["suffixes"]
    return (
        reconstructs_surface(surface, prefixes, analysis["stem"],
                             [item["surface"] for item in suffixes])
        and compatible_affixes(prefixes,
                               [item["function"] for item in suffixes],
                               analysis["part_of_speech"])
    )
