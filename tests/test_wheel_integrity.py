import csv
import base64
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.check_wheel import REQUIRED, inspect_wheel


class WheelVerificationTests(unittest.TestCase):
    def make_wheel(self, destination, omit=None):
        omit = omit or set()
        files = {}
        for name in REQUIRED - omit:
            if name.endswith(".json"):
                files[name] = json.dumps({"schema_version": 1})
            else:
                files[name] = "# test fixture"
        files["neetechs_tokenizer-0.9.29.dist-info/METADATA"] = (
            "Metadata-Version: 2.1\nName: neetechs_tokenizer\nVersion: 0.9.29\n"
        )
        if "WHEEL" not in omit:
            files["neetechs_tokenizer-0.9.29.dist-info/WHEEL"] = (
                "Wheel-Version: 1.0\\nGenerator: test fixture\\nRoot-Is-Purelib: true\\nTag: py3-none-any\\n"
            )
        records = "neetechs_tokenizer-0.9.29.dist-info/RECORD"
        stream = io.StringIO()
        writer = csv.writer(stream)
        for name in sorted(files):
            payload = files[name].encode("utf-8")
            digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
            writer.writerow([name, "sha256=" + digest, str(len(payload))])
        writer.writerow([records, "", ""])
        files[records] = stream.getvalue()
        with ZipFile(destination, "w") as archive:
            for name, contents in files.items():
                archive.writestr(name, contents)

    def test_valid_wheel(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.whl"
            self.make_wheel(path)
            self.assertTrue(inspect_wheel(path)["valid"])

    def test_missing_wheel_metadata_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.whl"
            self.make_wheel(path, {"WHEEL"})
            with self.assertRaisesRegex(ValueError, "wheel_count=0"):
                inspect_wheel(path)

    def test_corrupted_wheel_member_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.whl"
            self.make_wheel(path)
            data = path.read_bytes()
            # ZIP_STORED fixture: alter file payload but leave its recorded CRC.
            self.assertIn(b"# test fixture", data)
            path.write_bytes(data.replace(b"# test fixture", b"! test fixture", 1))
            with self.assertRaisesRegex(ValueError, "Corrupted wheel"):
                inspect_wheel(path)

    def test_record_hash_mismatch_fails_even_with_valid_zip_crc(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.whl"
            self.make_wheel(path)
            with ZipFile(path) as archive:
                files = {name: archive.read(name) for name in archive.namelist()}
            # Rebuild the ZIP after tampering, so the ZIP CRC is correct but
            # the RECORD digest still describes the unmodified content.
            files["neetechs_tokenizer/morphology.py"] = b"# tampered fixture"
            with ZipFile(path, "w") as archive:
                for name, data in files.items():
                    archive.writestr(name, data)
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                inspect_wheel(path)

    def test_unrecorded_extra_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.whl"
            self.make_wheel(path)
            with ZipFile(path, "a") as archive:
                archive.writestr("neetechs_tokenizer/extra.py", "print('unexpected')")
            with self.assertRaisesRegex(ValueError, "file lists differ"):
                inspect_wheel(path)

    def test_duplicate_archive_member_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.whl"
            self.make_wheel(path)
            with ZipFile(path, "a") as archive:
                archive.writestr("neetechs_tokenizer/new.py", "one")
                archive.writestr("neetechs_tokenizer/new.py", "two")
            with self.assertRaisesRegex(ValueError, "duplicate archive"):
                inspect_wheel(path)

    def test_missing_bundled_lexicon_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.whl"
            self.make_wheel(path, {"neetechs_tokenizer/data/lexicon.json"})
            with self.assertRaisesRegex(ValueError, "lexicon.json"):
                inspect_wheel(path)


if __name__ == "__main__":
    unittest.main()
