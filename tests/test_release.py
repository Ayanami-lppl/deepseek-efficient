"""Check archive content and reproducibility; no model or network calls."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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
                "deepseek-efficient/scripts/check_result.py", "deepseek-efficient/references/log-output.md",
            })
            manifest = json.loads(archive.read("deepseek-efficient/manifest.json"))
            self.assertEqual(manifest["version"], meta["version"])
            for name, expected in manifest["files"].items():
                self.assertEqual(hashlib.sha256(archive.read("deepseek-efficient/" + name)).hexdigest(), expected)
            self.assertEqual(archive.read("deepseek-efficient/SKILL.md"), (ROOT / "SKILL.md").read_bytes())


    def test_installed_helper_runs_without_repository_dependencies(self):
        data, _ = MODULE.build()
        with tempfile.TemporaryDirectory(prefix="installed skill ") as temporary:
            base = Path(temporary)
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                archive.extractall(base)
            log = base / "failure.txt"
            payload = b"Ran 3 tests in 0.001s\nFAILED (failures=1)\n"
            log.write_bytes(payload)
            command = [sys.executable, str(base / "deepseek-efficient/scripts/check_result.py"),
                       str(log), "1", "--root", str(base)]
            result = subprocess.run(command, cwd=base, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 1)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertFalse(summary["command_executed_by_helper"])
            self.assertEqual(log.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
