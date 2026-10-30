# Neetechs Tokenizer — Arabic Morphology Baseline

A small, transparent, **rule-based Arabic tokenizer and morphological analyzer** written in Python. It prioritizes validated analyses over aggressive stem stripping.

**Status: v0.2 prototype.** The starter lexicon is intentionally small. This is not yet a complete morphological, syntactic, semantic, diacritization, or AI model. Unknown words are retained instead of assigned invented roots.

## Quick start

    python -m pip install -e .
    python -m unittest discover -s tests -v

Example Python:

    from neetechs_tokenizer import tokenize, wordAnalyzer, get_root
    print(tokenize("والكاتب استكتبوهم!"))
    # ['و', 'ال', 'كاتب', 'استكتب', 'و', 'هم', '!']
    result = wordAnalyzer("استكتبوهم")
    print(result["analyses"][0]["root"])      # كتب
    print(result["analyses"][0]["pattern"])   # استفعل
    print(get_root("مكتوب"))                  # كتب
    print(get_root("كلمةغيرمعروفة"))          # None

    print(tokenize("والكاتب!", split_clitics=False))  # ['والكاتب', '!']

## How it works

1. **Normalize without losing meaning**: remove optional harakat and tatweel; keep hamza, ta marbuta, and alif maqsura distinct by default.
2. **Generate candidates**: consider known combinations of conjunctions, definite article, prepositions, and a small set of subject/object suffixes.
3. **Match known stems**: check a curated starter lexicon, allowing more than one reading of a homograph.
4. **Validate patterns**: reconstruct each candidate from its root and Arabic template to reject false matches.
5. **Rank analyses**: sort verified candidates with a deterministic heuristic. Scores are ranking values, **not probabilities**.

The JSON-compatible word_analyzer(word) result contains word, normalized, and analyses. Each analysis has root, pattern, stem, part_of_speech, prefixes, suffixes, source, and score.

## Current limitations

- Only a **starter set** of sound triliteral stems (e.g. كتب, علم, درس) and a few clitic constructions are supported.
- No general root discovery, weak-root handling, quadriliteral roots, comprehensive POS tagging, or sentence syntax yet.
- Conjugation is only partially represented (e.g. وا and وهم); additional affix rules must be reviewed and tested.
- The existing restore_diacritics, correct_grammar, and translate utilities are illustrative dictionary lookups, not language models.
- Orthographic alternations and broader contexts need more than surface segmentation. Do not use this prototype as linguistic ground truth.

## Public API

- tokenize(text, split_clitics=True): word and punctuation tokenization; optional validated segmentation
- word_analyzer(word) / wordAnalyzer(word): candidate analyses with ranked results
- get_root(word) / extract_root(word): top validated root (or None)
- analyze_tokens(tokens): legacy-compatible token/root/pattern records
- match_pattern(word, root): validated template for a supplied root
- clean_text, normalize_arabic, remove_diacritics in neetechs_tokenizer.utils

## Next steps

Add a reviewed morphology lexicon (external data file), affix compatibility rules, orthographic transformations, ambiguity evaluation, and corpus-backed regression tests before attempting ML-based token compression or language modeling. Keep tokenizer segmentation separate from root analysis and later semantic analysis.

Repository: https://github.com/jihadelsayed/neetechs_tokenizer · MIT License
