# Neetechs Tokenizer — Arabic Morphology Baseline

A small, transparent, **rule-based Arabic tokenizer and morphological analyzer** written in Python. It prioritizes validated analyses over aggressive stem stripping.

**Status: v0.9.17 prototype.** The starter lexicon is intentionally small. This is not yet a complete morphological, syntactic, semantic, diacritization, or AI model. Unknown words are retained instead of assigned invented roots.

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

## v0.7: quality baseline

The bundled `data/regression.json` corpus contains 20 small, manually selected positive and negative cases. `tests/test_regression.py` checks these expected roots, forms, surface segmentations, unknown-word behavior, preserved ambiguity, and duplicate analysis removal. This is **not** a statistical evaluation dataset; coverage is deliberately narrow. Run `python -m unittest discover -s tests -v` before releasing. The quality gate does not claim support for words outside these reviewed examples.

## v0.8: first weak-root forms

`analyze_weak_verb()` recognizes a small set of **attested** hollow and defective verbs, for example قال/يقول/قل (قول), باع/يبيع/بع (بيع), and دعا/يدعو/ادع (دعو). The mappings are lexeme-specific, not productive rules. Unknown weak verbs remain unsupported and must not be assigned guessed roots. Full diacritics, weak-root inflection, and context-based disambiguation remain future work.

## v0.9: expanded reviewed weak-verb paradigms

The weak-form table now includes additional plural, dual, singular, and imperfect
surfaces for قول, بيع, and دعو. Ambiguous undiacritized forms such as تقول
retain multiple readings. All mappings remain explicit and lexical; this is not
a generic inflection generator. Test with `python -m unittest discover -s tests -v`.

## v0.9.1 quality gate (not a stable v1.0 release)

Run the full library tests:

```bash
python -m unittest discover -s tests -v
```

Run the separate, machine-readable regression check:

```bash
python -m neetechs_tokenizer.evaluate
```

A nonzero exit status means an expected lexical, tense or tokenization case failed.
`pass_rate` summarizes only the **30 curated in-sample examples**, not
real-world root extraction accuracy, recall, or precision. Before 1.0, execute
the full suite, add independently annotated corpus tests, and examine ambiguity.

## v0.9.2 article–possessive compatibility fix

For recognized nouns, the analyzer rejects combining the definite article (ال) with an attached possessive pronoun. Unrecognized words stay intact in tokenization. Runtime verification is still required before declaring a stable release.

## v0.9.3 tokenizer invariants

`tokenize()` only emits a split when the concatenated components exactly reproduce the normalized input word. Added regression tests for reversible segmentation, unknown-word preservation, punctuation, and mixed Arabic/English text. The full suite must still be executed before a v1.0 release.

## Local release check (v0.9.x)

Run `python scripts/verify_release.py` from anywhere inside your checkout. It runs the full unit tests and the bundled morphology regression command, then writes `release-check-results.json`. Exit status is nonzero if either check fails. A green result only verifies curated regression cases, not full linguistic accuracy. Do not commit the generated report.

## v0.9.4 evaluation terminology

The legacy `negative` and `correct_negative` fields mean **expected-unsupported cases**, not true negatives. Some forms such as `قاموا` are valid Arabic but outside the current lexicon. The report also provides `supported_case_coverage` and `unsupported_case_rejection`; these are in-sample checks, not real-world accuracy metrics. Three noun-article-possessive incompatibility examples were added.

## v0.9.5 full-surface analysis invariant

Every analysis returned by `word_analyzer()` must reconstruct its complete
normalized word by concatenating prefixes, stem, and suffix surfaces.
Incomplete parses are discarded. This is a structural safety property and
does not prove that a morphologically plausible analysis is linguistically
correct. Added public-API contract tests; runtime validation remains required.

## v0.9.6 independent evaluation interface

Use `python -m neetechs_tokenizer.benchmark annotations.json` with separately annotated JSON labels, following `docs/benchmark-schema.json`. Outputs candidate-root recall and coverage. **The included JSON file is an input-format example, not an independent gold-standard corpus.** Root ambiguity means this metric must not be read as top-1 accuracy. Evaluation of a genuine independent dataset remains outstanding.

## v0.9.7 top-ranked root evaluation

The external benchmark now reports `top_one_root_accuracy` separately from `root_recall_at_any_candidate`. This distinguishes whether the expected root is returned at all from whether it is ranked first. Both are meaningful only when evaluated on independently annotated held-out inputs. Existing result fields are preserved.

## v0.9.8 uncertainty-aware ranking evaluation

The benchmark now identifies tied top-scoring **distinct roots** instead of pretending that alphabetical tie-breaking is linguistic evidence. `ambiguous_top_root_cases` counts unresolved root ties. `unambiguous_top_root_accuracy` measures top-root correctness only where no distinct-root tie occurred. Grammatical ambiguity (e.g., person/gender readings sharing one root) does not count as a root tie. No score calibration or new ranking weights are claimed.

## v0.9.9 benchmark denominator correction

`unambiguous_top_root_accuracy` now excludes both root ties and abstentions (words without any analysis). New counts `uniquely_ranked_cases` and `abstained_cases` expose the denominator and missing coverage explicitly. This prevents unsupported inputs from silently lowering the accuracy metric for uniquely ranked predictions. No new linguistic ranking weights were introduced.

## v0.9.10 conservative root lookup

Use `get_root(word, require_unique=True)` to return `None` when different top-scoring roots are tied. The default `get_root(word)` behavior stays unchanged. This protects callers from treating alphabetical tie breaks as linguistic evidence. Strict lookup is not a correctness guarantee; it only detects tied root scores.

## v0.9.11 accepted root sets

Evaluation inputs support either a legacy `root` string or a nonempty `roots` array when multiple analyses are accepted by independent annotators. A prediction counts as correct when its root belongs to that set; annotations are validated to prevent empty, duplicated, or mixed schemas. This avoids marking an acceptable root as a false prediction simply because a gold label was ambiguous. The benchmark remains unverified against independent data.

## v0.9.12 benchmark fix

Fixed the unambiguous top-root accuracy calculation for cases using a `roots` array. It now checks the accepted root set, consistent with candidate recall and top-one scoring. Expanded the regression assertion to cover this field.

## v0.9.13 benchmark tie detection

The benchmark finds top-scoring root ties using the maximum score across all returned analyses, rather than assuming the first analysis has the highest score. This makes the ambiguity count robust to analysis ordering. Added a synthetic order-independence regression test. The full suite still requires runtime verification.

## v0.9.14 benchmark order independence

Top-1 root selection now uses the maximum observed score, with deterministic lexical tie-breaking. The separate root-tie count remains essential: alphabetical tie selection is not linguistic confidence. Added tests for unsorted predictions and reordering. Full-suite verification and independent corpus evaluation are still pending.

## v0.9.15 tie-aware evaluation

The benchmark adds `tie_aware_top_accuracy`: a tied top prediction earns credit only when all its equal-score roots are in the set of accepted roots. `top_one_root_accuracy` is retained for backward compatibility, but its alphabetical tie-break is not linguistic evidence. The test suite and independent benchmark still require full execution.

## v0.9.16 release gate

A successful unittest exit code must also contain a test summary reporting at least one executed test. Zero-test or missing-summary runs fail the release gate. Full package verification is still pending.

## v0.9.17 verified release-gate reporting

Release check output now reflects the actual computed passed status, including no-test failures. Added four targeted tests, exercised locally against an isolated copy of the checker (4/4 pass). Full repository unit tests and linguistic benchmark remain unverified.
