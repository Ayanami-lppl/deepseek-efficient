"""Create four fresh canary projects; does not start Harness or call a model."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    plan = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    for trial in plan["trials"]:
        target = destination / trial["id"]
        if not target.resolve().is_relative_to(destination):
            raise ValueError("Canary project escapes destination")
        target.mkdir()
        for name in ["marker.txt", "AGENTS.md"]:
            (target / name).write_text(plan["fixture"]["files"][name], encoding="utf-8", newline="\n")
        for name, expected in trial["frozen_hashes"].items():
            if hashlib.sha256((target / name).read_bytes()).hexdigest() != expected:
                raise ValueError("Canary fixture hash mismatch")
        print(trial["id"], trial["arm"], str(target))
    print("Open each project in a fresh Harness session and use its prompt from plan.json.")


if __name__ == "__main__":
    main()
