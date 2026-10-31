import csv
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
        records = "neetechs_tokenizer-0.9.29.dist-info/RECORD"
        stream = io.StringIO()
        writer = csv.writer(stream)
        for name in sorted(files):
            writer.writerow([name, "", ""])
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

    def test_missing_bundled_lexicon_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.whl"
            self.make_wheel(path, {"neetechs_tokenizer/data/lexicon.json"})
            with self.assertRaisesRegex(ValueError, "lexicon.json"):
                inspect_wheel(path)


if __name__ == "__main__":
    unittest.main()
