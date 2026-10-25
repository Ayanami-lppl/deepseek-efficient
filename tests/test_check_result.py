import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_result.py"
spec = importlib.util.spec_from_file_location("check_result", SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class CheckResultTests(unittest.TestCase):
    def test_long_log_retains_markers_before_buffered_noise_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "check.log"
            data = b"Ran 11 tests in 0.001s\n\nOK\n" + b"progress noise\n" * 20000
            log.write_bytes(data)
            result = helper.inspect_log(log, 0, temp)
            self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(result["bytes"], len(data))
            self.assertEqual(result["lines"], 20003)
            self.assertEqual([m["text"] for m in result["markers"]], ["Ran 11 tests in 0.001s", "OK"])
            self.assertLess(len(json.dumps(result)), 4000)
            self.assertTrue(result["output_omitted"])
            self.assertFalse(result["command_executed_by_helper"])
            self.assertEqual(log.read_bytes(), data)

    def test_failure_status_survives_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "check.log"
            log.write_text("FAILED (failures=1)\n", encoding="utf-8")
            run = subprocess.run([sys.executable, str(SCRIPT), str(log), "7", "--root", temp], capture_output=True, text=True)
            self.assertEqual(run.returncode, 7)
            result = json.loads(run.stdout)
            self.assertEqual(result["exit_code"], 7)
            self.assertIn("FAILED", result["markers"][0]["text"])

    def test_unicode_and_spaces(self):
        with tempfile.TemporaryDirectory(prefix="project space ") as temp:
            log = Path(temp) / "检查.log"
            log.write_text("中文内容\nOK\n", encoding="utf-8")
            result = helper.inspect_log(log, 0, temp)
            self.assertIn("中文内容", result["tail"])
            self.assertEqual(result["log"], "检查.log")

    def test_outside_project_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            log = Path(temp) / "outside.log"
            log.write_bytes(b"OK\n")
            with self.assertRaises(ValueError):
                helper.inspect_log(log, 0, root)

    def test_oversized_line_is_not_a_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "check.log"
            log.write_bytes(b"x" * 65536 + b"OK\n")
            result = helper.inspect_log(log, 0, temp)
            self.assertEqual(result["markers"], [])
            self.assertTrue(result["tail"].endswith("OK"))


if __name__ == "__main__":
    unittest.main()
