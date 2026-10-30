# Neetechs Tokenizer — Arabic Morphology Baseline

A small, transparent, **rule-based Arabic tokenizer and morphological analyzer** written in Python. It prioritizes validated analyses over aggressive stem stripping.

**Status: v0.3 prototype.** The starter lexicon is intentionally small. This is not yet a complete morphological, syntactic, semantic, diacritization, or AI model. Unknown words are retained instead of assigned invented roots.

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

- Only a **bundled and validated starter set** of sound triliteral stems (e.g. كتب, علم, درس) and a few clitic constructions are supported.
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

Expand the versioned lexicon, strengthen affix compatibility rules, add orthographic transformations, ambiguity evaluation, and corpus-backed regression tests before attempting ML-based token compression or language modeling. Keep tokenizer segmentation separate from root analysis and later semantic analysis.

Repository: https://github.com/jihadelsayed/neetechs_tokenizer · MIT License

## v0.4: experimental perfect-tense recognition

`analyze_perfect('كتبت')` yields multiple person/gender readings because short vowels are not written. `word_analyzer('فتحتم')` now also includes validated past-tense analyses. Only exact sound-triliteral and currently attested Form X perfect stems are considered; imperfect, imperative, weak roots, gemination, and most clitic interactions are **not** implemented. The analyzer does not infer grammatical context.

## v0.5: reviewed imperfect and imperative forms

`analyze_imperfect('يكتب')`, `analyze_imperfect('تكتبون')`, and `analyze_imperative('اكتب')` use explicitly reviewed Form I stem lists. Unvowelled ambiguity is retained, and these results are also available via `wordAnalyzer()`. This is not exhaustive: weak roots, Form II–X imperfect derivation, jussive/subjunctive, imperative plurals, and sentence-level interpretation are not yet supported. Affix compatibility remains limited.

## v0.6: candidate-first analysis

The analyzer generates reversible prefix/stem/suffix combinations with `priority_identifier()` and only validates stems found in the reviewed lexicon. Prefix/suffix compatibility is checked before root/template matching. Bare `س` on dictionary perfect verbs was removed to avoid false future-tense analyses. Scores are deterministic prioritization heuristics, not probabilities. Candidate generation does not imply every returned candidate is linguistically correct; only validated analyses are returned by `wordAnalyzer()`.
