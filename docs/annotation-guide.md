# Arabic root annotation guide — pilot v0.1

**Purpose:** independently annotate Arabic word forms for a *held-out* root-extraction benchmark. This document is a pilot guide, not a claim of linguistic validation. Agree on the rules and freeze the input list *before* annotation.

## Reviewer instructions

- Work independently. Do not use the Neetechs Tokenizer, its source code, output, regression data, evaluation seed, or other reviewer labels.
- Work from the **supplied linguistic context** where available. If none is provided, record all defensible roots for the unvowelled form rather than guessing one interpretation.
- Record root consonants in standard Arabic orthography. For weak/hamzated words, note disagreements over root representation rather than silently normalizing them.
- Root is **not** the surface stem, prefix, pronoun, grammatical pattern, or general meaning. Separate the root from attached clitics and inflection.
- If a word is a proper noun, foreign word, broken plural, or a form you cannot confidently analyze, mark `in_scope: false` or `uncertain: true` with a reason rather than inventing a root.
- When a form supports more than one defensible root, list **all** acceptable roots; never resolve ambiguity using an analyzer prediction.
- Do not add labels for words outside the frozen assignment. Preserve each input `word` unchanged.
- Each reviewer must maintain a private copy until both submissions are locked. An adjudicator receives the two sets *after* submission and records every decision.

## Input and submission contract

Input contains `schema_version: 1` and `cases`, each with a `word` and optionally `context`. Submit `cases` in the same word set with `roots: ["..."]` for every in-scope word. For an in-scope form, submit `roots: ["..."]`. For an uncertain or out-of-scope form, submit `status: "uncertain"` or `status: "out_of_scope"` with a nonempty `reason` and no roots. The comparison workflow preserves exclusions and the adjudication workflow records the included and excluded case counts. Do not interpret root-only benchmark accuracy as covering excluded forms. Reviewer identities and provenance belong in an access-controlled manifest, not in public evaluation examples.

## Reviewer checklist

1. Confirm the exact frozen input list and language variety.
2. Perform blind annotation without access to software predictions or other annotations.
3. Record every unclear item, unsupported form, and context ambiguity in the exclusion log.
4. Freeze both reviews; compare agreement with `scripts/review_agreement.py`.
5. Send disagreements to a qualified third adjudicator with reasoning.
6. Preserve disagreement history and exclude unresolved examples.
7. Complete independent provenance inspection before reporting any benchmark score.

**Important limitation:** The existing evaluation seed is unreviewed and must **not** be promoted to independent ground truth. Examples of roots in this guide are intentionally omitted to reduce anchoring.
