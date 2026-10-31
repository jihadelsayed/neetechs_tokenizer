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
