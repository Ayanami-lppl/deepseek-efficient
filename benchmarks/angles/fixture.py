"""Prepare skill/effort fixtures or validate trusted artifacts offline."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
ARMS = ["none_high", "skill_high", "none_low", "skill_low"]
TASKS = ["join", "limiter", "patch", "paths"]


def files_for(task):
    definition = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))[task]
    return definition, dict(definition["files"])


def populate(task, destination, arm=None):
    definition, files = files_for(task)
    destination.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    if arm and arm.startswith("skill_"):
        target = destination / ".agents/skills/deepseek-efficient/SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_bytes((ROOT.parent / "prompts/v0.1.0.txt").read_bytes())
    return definition


def evaluate(task, artifact):
    artifact = artifact.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="deepseek-angles-") as temporary:
        work = Path(temporary).resolve()
        if work.parent != Path(tempfile.gettempdir()).resolve():
            raise ValueError("Unexpected temporary directory")
        definition = populate(task, work)
        (work / definition["editable"][0]).write_bytes(artifact.read_bytes())
        return subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "unittest", "-v"],
            cwd=work, capture_output=True, text=True, encoding="utf-8", timeout=20,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("task", choices=TASKS)
    prepare.add_argument("arm", choices=ARMS)
    prepare.add_argument("destination", type=Path)
    check = commands.add_parser("evaluate")
    check.add_argument("task", choices=TASKS)
    check.add_argument("artifact", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        destination = args.destination.resolve()
        destination.mkdir(parents=True, exist_ok=False)
        populate(args.task, destination, args.arm)
        print("Prepared synthetic fixture:", destination)
        print("Set the host effort separately:", args.arm.split("_")[1])
        return 0
    result = evaluate(args.task, args.artifact)
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    return 0 if result.returncode == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print("Fixture error:", error, file=sys.stderr)
        sys.exit(2)
