"""Inspect a retained check log without executing commands or changing the file.

The caller must capture the original command's exit code immediately. Markers
are navigation aids, not independent evidence that a command or test passed.
Python 3.10+; standard library only.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
MARKER = re.compile(r"^(?:Ran \d+ tests? in .+|OK(?: \(.*\))?|FAILED\b.*|ERROR\b.*|FAIL\b.*)$")


def inspect_log(log, exit_code, root, tail_lines=6, tail_bytes=2048):
    root = Path(root).resolve(strict=True)
    log = (root / log).resolve(strict=True)
    if not root.is_dir() or not log.is_file() or not log.is_relative_to(root):
        raise ValueError("Log must be a file inside the project root")
    if type(exit_code) is not int or not 1 <= tail_lines <= 200 or not 256 <= tail_bytes <= 65536:
        raise ValueError("Invalid exit code or output limit")
    digest = hashlib.sha256()
    size = breaks = 0
    window = b""
    with log.open("rb") as saved:
        for chunk in iter(lambda: saved.read(65536), b""):
            digest.update(chunk)
            size += len(chunk)
            breaks += chunk.count(b"\n")
            window = (window + chunk)[-tail_bytes:]
    markers = []
    # Skip fragments of oversized lines; a trailing OK is not a full marker.
    line_number = 1
    fragmented = False
    with log.open("rb") as saved:
        for raw in iter(lambda: saved.readline(65536), b""):
            complete = raw.endswith(b"\n") or len(raw) < 65536
            if complete and not fragmented:
                value = ANSI.sub("", raw.decode("utf-8", errors="replace")).strip()
                if MARKER.fullmatch(value):
                    markers.append({"line": line_number, "text": value[:240]})
                    markers = markers[-6:]
            if complete:
                line_number += 1
                fragmented = False
            else:
                fragmented = True
    selected = window.decode("utf-8", errors="replace").splitlines()[-tail_lines:]
    lines = breaks + int(bool(size) and not window.endswith(b"\n"))
    return {
        "schema_version": 1,
        "command_executed_by_helper": False,
        "exit_code": exit_code,
        "exit_code_source": "caller; capture immediately after the original command",
        "log": log.relative_to(root).as_posix(),
        "sha256": digest.hexdigest(),
        "bytes": size,
        "lines": lines,
        "markers": markers,
        "tail": "\n".join(selected),
        "output_omitted": size > len(window) or lines > len(selected),
        "interpretation": "Caller-supplied exit code; markers are log navigation aids, not independent pass proof. Inspect failures in the retained log.",
    }


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("exit_code", type=int)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--tail-lines", type=int, default=6)
    parser.add_argument("--tail-bytes", type=int, default=2048)
    args = parser.parse_args()
    try:
        result = inspect_log(args.log, args.exit_code, args.root, args.tail_lines, args.tail_bytes)
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return args.exit_code


if __name__ == "__main__":
    sys.exit(main())
