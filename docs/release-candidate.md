# Release candidate packaging (not a v1.0 approval)

The package stays at version `0.9.29` until tests pass and the limited
linguistic scope is documented. No PyPI publication is automated.

From the repository root, with Python 3.10+ and setuptools installed:

```powershell
python -m pip install --upgrade pip setuptools wheel
python scripts/verify_release.py
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
python scripts/check_wheel.py (Get-ChildItem dist/*.whl | Select-Object -First 1).FullName
```

A wheel integrity check confirms source modules, the lexicon, regression data,
wheel metadata, and the wheel file list are present. This is **not** a substitute
for installed-wheel smoke testing on a clean Python environment, linguistic
validation, or the full release checks. Do not publish a stable release if any
gate fails. Python test output is saved in `release-check-results.json`.
