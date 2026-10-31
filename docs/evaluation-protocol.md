# Evaluation dataset protocol

The separate `data/evaluation_seed.json` contains **20 draft candidate examples**.
It is **not** an independently annotated dataset and must not be used to
advertise measured Arabic accuracy. Some labels may need correction.

## Independence requirements

1. Freeze a version of the analyzer, including its lexicon and rules.
2. Recruit two Arabic linguistics reviewers who do not see model predictions.
3. Have them annotate root(s), ambiguity and whether the expression is in scope.
   Use an agreed written annotation guide and preserve disagreements.
4. Resolve disputed examples with a third adjudicator; record provenance,
   language variety, license, date, and annotation agreement.
5. Keep the held-out evaluation dataset separate from test/regression data,
   training, root dictionaries, tuning, and code-review examples.
6. If cases or labels influence implementation, retire those cases from the
   held-out set and obtain replacements.

## Run as a diagnostic only

```bash
python -m unittest discover -s tests -v
python -m neetechs_tokenizer.benchmark data/evaluation_seed.json
```

The seed diagnostic can report coverage and root-ranking metrics, but do not
publish its figures as independently verified accuracy. For a meaningful
evaluation, report corpus size, dialect, annotation agreement, coverage,
top-one correctness, tie-aware correctness, abstentions and error categories
along with the exact immutable code and evaluation-set versions.

The seed intentionally contains forms that current implementation may not
support: that is useful for identifying vocabulary gaps, **not** grounds to
quietly add them to the model and then score on the same holdout.

## Diagnostic metrics (Step 5)

The benchmark preserves the earlier `coverage`, `top_one_root_accuracy`,
`root_recall_at_any_candidate`, `tie_aware_top_accuracy`, and
`unambiguous_top_root_accuracy` fields.

Additional metrics:
- `selective_coverage`: fraction of examples with exactly one highest-scoring
  distinct root. This excludes both abstentions and tied top roots.
- `selective_accuracy`: accepted-root correctness among those uniquely ranked
  examples; null if there are none.
- `case_results`: word-by-word expected roots, all predicted roots, highest
  ranked roots, top-one result, and diagnostic error labels.
- `error_category_counts`: counts of nonexclusive diagnostics.

Diagnostics can overlap. `abstained` means no analysis;
`wrong_top_root` means the deterministically selected top root was not
accepted; `ambiguous_top_root` means tied highest-ranked roots are not all
accepted; `expected_root_missing` means none of the predictions contains an
accepted root. Error category counts must **not** be summed as if they are
disjoint. Accuracy still refers exclusively to the supplied labels;
`data/evaluation_seed.json` is unreviewed and is **not** a verified test set.

## Frozen dataset provenance gate

The adjudicated dataset is not automatically a verified independent benchmark.
Store its SHA-256 digest, full frozen analyzer Git commit, source, license,
language variety, collection date, annotation guide and reviewer IDs in a
separate JSON manifest. The manifest must also contain explicit boolean
confirmations for blind review, held-out separation and frozen-code inspection.
Generate the hash from the final, immutable dataset file, not from a JSON
re-serialization. For example:

```powershell
(Get-FileHash data/held_out_adjudicated.json -Algorithm SHA256).Hash.ToLowerInvariant()
python scripts/verify_evaluation_provenance.py data/held_out_adjudicated.json data/held_out_manifest.json
```

Manifest keys: `dataset_sha256`, `frozen_commit`, `source`, `license`,
`language_variety`, `collection_date`, `annotation_guide`,
`reviewer_a`, `reviewer_b`, `adjudicator`,
`blind_review_confirmed`, `held_out_from_tuning_confirmed`, and
`frozen_code_verified`. Never mark a confirmation as true without evidence.
The checker validates declared metadata and file integrity, **not** reviewer
independence, source authenticity or the existence of a Git commit. Keep any
reviewer-private personal information out of the published manifest.
