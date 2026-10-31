"""Smoke-test a locally built wheel in a fresh isolated Python environment."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

SMOKE = r'''
import importlib.metadata
import json
import os
from importlib.resources import files
import neetechs_tokenizer as n

assert os.path.abspath(n.__file__).startswith(os.path.abspath(os.environ["SMOKE_VENV_ROOT"])), n.__file__
assert n.get_root("مكتوب") == "كتب"
assert n.get_root("كلمةغيرمعروفة") is None
assert n.tokenize("والكاتب!") == ["و", "ال", "كاتب", "!"]
assert n.wordAnalyzer("استكتبوهم")["analyses"]
assert n.analyze_text("مكتوب!")[0]["token"] == "مكتوب"
for filename in ("lexicon.json", "regression.json"):
    with files("neetechs_tokenizer").joinpath("data", filename).open(encoding="utf-8") as f:
        assert json.load(f)["schema_version"] == 1
assert importlib.metadata.version("neetechs_tokenizer")
print("Installed-wheel smoke checks passed")
'''


def run_wheel_smoke(wheel, *, timeout=120):
    wheel = Path(wheel).resolve(strict=True)
    if wheel.suffix != ".whl":
        raise ValueError("Expected a .whl file")
    with tempfile.TemporaryDirectory(prefix="neetechs-wheel-") as location:
        environment = Path(location) / "venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment)
        python = (environment / "Scripts" / "python.exe"
                  if os.name == "nt" else environment / "bin" / "python")
        subprocess.run(
            [str(python), "-m", "pip", "install", "--no-index",
             "--no-deps", str(wheel)],
            check=True, timeout=timeout,
        )
        variables = dict(os.environ)
        variables["SMOKE_VENV_ROOT"] = str(environment)
        subprocess.run(
            [str(python), "-I", "-c", SMOKE],
            env=variables, check=True, timeout=timeout,
            cwd=environment,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    run_wheel_smoke(args.wheel)
    print(json.dumps({"wheel": str(args.wheel), "installed_smoke": "PASS"}))


if __name__ == "__main__":
    main()
