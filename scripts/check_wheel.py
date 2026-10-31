"""Validate the contents of a built distribution wheel before publication."""
import argparse
import csv
import io
import json
from pathlib import Path
from zipfile import ZipFile

REQUIRED = {
    "neetechs_tokenizer/__init__.py",
    "neetechs_tokenizer/morphology.py",
    "neetechs_tokenizer/tokenizer.py",
    "neetechs_tokenizer/validation.py",
    "neetechs_tokenizer/data/lexicon.json",
    "neetechs_tokenizer/data/regression.json",
}


def inspect_wheel(wheel_path):
    with ZipFile(wheel_path) as archive:
        corrupted = archive.testzip()
        if corrupted is not None:
            raise ValueError(f"Corrupted wheel archive member: {corrupted}")
        names = set(archive.namelist())
        missing = sorted(REQUIRED - names)
        metadata_paths = [name for name in names
                          if name.endswith(".dist-info/METADATA")]
        records = [name for name in names if name.endswith(".dist-info/RECORD")]
        if missing or len(metadata_paths) != 1 or len(records) != 1:
            raise ValueError(
                f"Invalid wheel: missing={missing}, "
                f"metadata_count={len(metadata_paths)}, record_count={len(records)}"
            )
        metadata = archive.read(metadata_paths[0]).decode("utf-8")
        if "Name: neetechs_tokenizer" not in metadata and "Name: neetechs-tokenizer" not in metadata:
            raise ValueError("Wheel contains unexpected distribution metadata")
        for path in ("neetechs_tokenizer/data/lexicon.json",
                     "neetechs_tokenizer/data/regression.json"):
            data = json.loads(archive.read(path))
            if data.get("schema_version") != 1:
                raise ValueError(f"Unexpected schema in {path}")
        record_rows = list(csv.reader(io.StringIO(
            archive.read(records[0]).decode("utf-8"))))
        recorded = {row[0] for row in record_rows if row}
        if not REQUIRED <= recorded:
            raise ValueError("Wheel RECORD omits required package files")
        return {"wheel": str(wheel_path), "required_files": len(REQUIRED),
                "metadata_path": metadata_paths[0], "valid": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_wheel(args.wheel), indent=2))


if __name__ == "__main__":
    main()
