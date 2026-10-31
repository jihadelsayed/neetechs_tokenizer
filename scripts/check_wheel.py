"""Validate the contents of a built distribution wheel before publication."""
import argparse
import base64
import hashlib
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
        wheel_metadata = [name for name in names if name.endswith(".dist-info/WHEEL")]
        if missing or len(metadata_paths) != 1 or len(records) != 1 or len(wheel_metadata) != 1:
            raise ValueError(
                f"Invalid wheel: missing={missing}, "
                f"metadata_count={len(metadata_paths)}, record_count={len(records)}, wheel_count={len(wheel_metadata)}"
            )
        if any(path.rsplit("/", 1)[0] != metadata_paths[0].rsplit("/", 1)[0]
               for path in (records[0], wheel_metadata[0])):
            raise ValueError("Wheel metadata files must share the same dist-info directory")
        wheel_headers = archive.read(wheel_metadata[0]).decode("utf-8")
        if "Wheel-Version:" not in wheel_headers or "Tag:" not in wheel_headers:
            raise ValueError("Wheel is missing required WHEEL metadata headers")
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
        if len(archive.namelist()) != len(names):
            raise ValueError("Wheel contains duplicate archive members")
        record_names = [row[0] for row in record_rows if row]
        if len(record_names) != len(set(record_names)):
            raise ValueError("Wheel RECORD contains duplicate entries")
        if recorded != names:
            raise ValueError("Wheel archive and RECORD file lists differ")
        for row in record_rows:
            if len(row) != 3:
                raise ValueError("Malformed wheel RECORD row")
            name, digest, declared_size = row
            if name not in names:
                raise ValueError(f"Wheel RECORD refers to missing member: {name}")
            if name == records[0]:
                continue  # RECORD is intentionally unhashed by wheel conventions.
            if not digest.startswith("sha256="):
                raise ValueError(f"Missing SHA-256 digest for wheel member: {name}")
            payload = archive.read(name)
            expected = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
            if digest[7:] != expected:
                raise ValueError(f"Wheel RECORD hash mismatch: {name}")
            if not declared_size.isdecimal() or int(declared_size) != len(payload):
                raise ValueError(f"Wheel RECORD size mismatch: {name}")
        return {"wheel": str(wheel_path), "required_files": len(REQUIRED),
                "metadata_path": metadata_paths[0], "valid": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_wheel(args.wheel), indent=2))


if __name__ == "__main__":
    main()
