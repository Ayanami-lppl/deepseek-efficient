"""Check archive content and reproducibility; no model or network calls."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("skill_release", ROOT / "scripts" / "build_release.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseTests(unittest.TestCase):
    def test_reproducible(self):
        first, first_meta = MODULE.build()
        second, second_meta = MODULE.build()
        self.assertEqual(first, second)
        self.assertEqual(first_meta, second_meta)

    def test_minimal_archive_and_checksums(self):
        data, meta = MODULE.build()
        self.assertEqual(hashlib.sha256(data).hexdigest(), meta["sha256"])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertEqual(set(archive.namelist()), {
                "deepseek-efficient/SKILL.md", "deepseek-efficient/LICENSE",
                "deepseek-efficient/README.md", "deepseek-efficient/manifest.json",
            })
            manifest = json.loads(archive.read("deepseek-efficient/manifest.json"))
            self.assertEqual(manifest["version"], meta["version"])
            for name, expected in manifest["files"].items():
                self.assertEqual(hashlib.sha256(archive.read("deepseek-efficient/" + name)).hexdigest(), expected)
            self.assertEqual(archive.read("deepseek-efficient/SKILL.md"), (ROOT / "SKILL.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
