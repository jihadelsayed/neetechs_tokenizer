"""Fail-closed provenance manifest for an adjudicated held-out Arabic dataset."""
import argparse
import hashlib
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")


def verify_provenance(dataset_path, manifest_path):
    dataset_path, manifest_path = Path(dataset_path), Path(manifest_path)
    raw = dataset_path.read_bytes()
    dataset = json.loads(raw)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if dataset.get("schema_version") != 1 or not isinstance(dataset.get("cases"), list) or not dataset["cases"]:
        raise ValueError("Invalid or empty evaluation dataset")
    if dataset.get("metadata", {}).get("status") != "adjudicated_not_independently_verified":
        raise ValueError("Dataset must contain completed adjudication provenance")
    if not isinstance(dataset.get("audit"), dict):
        raise ValueError("Missing adjudication audit")
    commit = manifest.get("frozen_commit")
    if not isinstance(commit, str) or not SHA.fullmatch(commit):
        raise ValueError("Frozen commit must be a full 40-character Git SHA")
    if manifest.get("dataset_sha256") != hashlib.sha256(raw).hexdigest():
        raise ValueError("Dataset SHA-256 does not match frozen file")
    for key in ("source", "license", "language_variety", "collection_date",
                "reviewer_a", "reviewer_b", "adjudicator", "annotation_guide"):
        value = manifest.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing provenance field: {key}")
    if len({manifest[k] for k in ("reviewer_a", "reviewer_b", "adjudicator")}) != 3:
        raise ValueError("Reviewer identities must be distinct")
    if manifest.get("blind_review_confirmed") is not True:
        raise ValueError("Blind review has not been confirmed")
    if manifest.get("held_out_from_tuning_confirmed") is not True:
        raise ValueError("Holdout separation has not been confirmed")
    if manifest.get("frozen_code_verified") is not True:
        raise ValueError("Frozen source commit has not been independently checked")
    return {"manifest_valid": True, "dataset_sha256": manifest["dataset_sha256"],
            "frozen_commit": commit,
            "independent_accuracy_verified": False,
            "note": "Manifest declarations are not external proof of independence or quality."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_provenance(args.dataset, args.manifest), indent=2))


if __name__ == "__main__":
    main()
