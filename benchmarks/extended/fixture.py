"""Prepare synthetic fixtures or validate a supplied artifact; no model calls.

Validation executes the supplied Python code. Use only artifacts you trust.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def files_for(task):
    definition = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))[task]
    plan = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
    files = dict(definition["files"])
    files["TASK.md"] = definition["contract"] + "\n"
    files["AGENTS.md"] = plan["agents"]
    if task == "cache":
        for number in range(30):
            files[f"docs/archive/note-{number:02d}.md"] = (
                f"Synthetic note {number}\n" +
                "Archive data for an unrelated demonstration module. Record fields: sample, batch, tag, count. No cache API is described here.\n" * 9
            )
    return definition, files


def populate(task, destination, arm=None):
    definition, files = files_for(task)
    destination.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    if arm:
        filename = "v0.1.0.txt" if arm == "old_high" else "candidate-no-reload.txt"
        skill = destination / ".agents/skills/deepseek-efficient/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_bytes((ROOT.parent / "prompts" / filename).read_bytes())
    return definition


def evaluate(task, artifact):
    # Each artifact runs in a fresh fixture, with the published tests unchanged.
    artifact = artifact.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="deepseek-extended-") as temporary:
        work = Path(temporary).resolve()
        if work.parent != Path(tempfile.gettempdir()).resolve():
            raise ValueError("Unexpected temporary directory")
        definition = populate(task, work)
        (work / definition["editable"][0]).write_bytes(artifact.read_bytes())
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "unittest", "-v"],
            cwd=work, capture_output=True, text=True, encoding="utf-8", timeout=20,
        )
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("task", choices=["reload", "cache"])
    prepare.add_argument("arm", choices=["old_high", "new_high", "new_low"])
    prepare.add_argument("destination", type=Path)
    check = commands.add_parser("evaluate")
    check.add_argument("task", choices=["reload", "cache"])
    check.add_argument("artifact", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        destination = args.destination.resolve()
        destination.mkdir(parents=True, exist_ok=False)
        populate(args.task, destination, args.arm)
        print("Prepared synthetic fixture:", destination)
        print("Set the host effort separately:", "low" if args.arm == "new_low" else "high")
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
