"""Offline release checks for this repository's skill, evidence and package."""

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_skill():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    parts = text.split("---", 2)
    require(len(parts) == 3 and parts[0] == "", "SKILL.md must start with YAML frontmatter")
    fields = {}
    for line in parts[1].strip().splitlines():
        key, separator, value = line.partition(":")
        require(bool(separator), "Unsupported frontmatter line")
        fields[key.strip()] = value.strip()
    require(fields.get("name") == "deepseek-efficient", "Unexpected skill name")
    require(bool(fields.get("description")), "Skill description is required")
    require(len(fields["description"]) <= 1024, "Skill description exceeds discovery budget")
    require(bool(parts[2].strip()), "Skill instructions are empty")
    print("Skill format: OK; body characters:", len(parts[2].strip()))


def check_history():
    result = json.loads((ROOT / "benchmarks" / "results.json").read_text(encoding="utf-8"))
    snapshot = ROOT / "benchmarks" / "prompts" / ("v" + result["skill_version"] + ".txt")
    require(digest(snapshot) == result["skill_sha256"], "Historical prompt hash mismatch")
    runs = result["runs"]
    require(len(runs) == 8, "Historical run count changed")
    for row in runs:
        usage = row["usage"]
        for key in ["inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens", "totalTokens"]:
            require(type(usage[key]) is int and usage[key] >= 0, "Invalid token count")
        require(usage["totalTokens"] == sum(usage[k] for k in ["inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens"]), "Token accounting mismatch")
        artifact = (ROOT / row["artifact"]).resolve()
        require(artifact.is_relative_to(ROOT), "Artifact escapes repository")
        require(digest(artifact) == row["artifact_sha256"], "Historical artifact hash mismatch")
        check = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "benchmarks" / "evaluate.py"), row["task"], str(artifact)], capture_output=True, text=True, encoding="utf-8", timeout=15)
        require(check.returncode == 0, "Historical artifact no longer passes: " + row["run"])
        grade = json.loads(check.stdout)
        require(grade["passed_cases"] == row["validation"]["passed_cases"], "Historical check count mismatch")
    for arm in ["baseline", "skill"]:
        rows = [r for r in runs if r["arm"] == arm]
        totals = result["totals"][arm]
        require(totals["total_tokens"] == sum(r["usage"]["totalTokens"] for r in rows), "Aggregate token mismatch")
        require(totals["output_tokens"] == sum(r["usage"]["outputTokens"] for r in rows), "Aggregate output mismatch")
        require(totals["tool_calls"] == sum(r["tool_calls"] for r in rows), "Aggregate tool count mismatch")
    for pair in result["pairs"]:
        a = next(r for r in runs if r["task"] == pair["task"] and r["repetition"] == pair["repetition"] and r["arm"] == "baseline")
        b = next(r for r in runs if r["task"] == pair["task"] and r["repetition"] == pair["repetition"] and r["arm"] == "skill")
        require(pair["baseline_tokens"] == a["usage"]["totalTokens"] and pair["skill_tokens"] == b["usage"]["totalTokens"], "Pair totals mismatch")
        reduction = 100 * (1 - pair["skill_tokens"] / pair["baseline_tokens"])
        require(math.isclose(reduction, pair["token_reduction_percent"], abs_tol=1e-9), "Pair percentage mismatch")
    print("Historical evidence and 1,716 checks: OK")


def check_negative_controls():
    tasks = json.loads((ROOT / "benchmarks" / "tasks.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="deepseek-negative-") as temp:
        base = Path(temp).resolve()
        require(base.parent == Path(tempfile.gettempdir()).resolve(), "Unexpected temporary directory")
        for task, definition in tasks.items():
            source = base / definition["filename"]
            source.write_text(definition["initial_code"], encoding="utf-8", newline="\n")
            check = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "benchmarks" / "evaluate.py"), task, str(source)], capture_output=True, text=True, encoding="utf-8", timeout=15)
            require(check.returncode == 1 and not json.loads(check.stdout)["passed"], "Original bug control unexpectedly passed")
    print("Original bug controls: rejected as expected")


def check_public_files():
    patterns = [
        re.compile(r"[A-Za-z]:[\\/]Users[\\/]", re.I),
        re.compile("/" + "Users" + "/"), re.compile(r"127\.0\.0\.1"),
        re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    ]
    excluded = {".git", "__pycache__", "dist", ".venv", ".pytest_cache"}
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in excluded for part in relative.parts) or not path.is_file():
            continue
        require(not path.is_symlink(), "Release must not contain links: " + relative.as_posix())
        require(path.suffix not in {".zstd", ".jsonl", ".log", ".pyc"}, "Raw/private artifact in source tree: " + relative.as_posix())
        data = path.read_text(encoding="utf-8")
        for index, pattern in enumerate(patterns):
            require(not pattern.search(data), "Potential private data: " + relative.as_posix() + " rule " + str(index))
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", data):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                candidate = (path.parent / target.split("#", 1)[0]).resolve()
                require(candidate.is_relative_to(ROOT) and candidate.exists(), "Broken local link: " + relative.as_posix() + " -> " + target)
    print("Local links and publication data scan: OK")


def check_extended():
    base = ROOT / "benchmarks" / "extended"
    results = json.loads((base / "results.json").read_text(encoding="utf-8"))
    plan = json.loads((base / "plan.json").read_text(encoding="utf-8"))
    require(digest(ROOT / "SKILL.md") == results["old_skill_sha256"], "Published runtime differs from retained original")
    for key, field in [("old", "old_skill_sha256"), ("candidate", "candidate_skill_sha256")]:
        require(digest(base / results["prompt_snapshots"][key]) == results[field], "Extended prompt hash mismatch")
    spec = importlib.util.spec_from_file_location("extended_fixture", base / "fixture.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    keys = ["inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens", "totalTokens"]
    rows = results["rows"]
    require(len(rows) == 12 and len({r["run"] for r in rows}) == 12, "Extended run count mismatch")
    for row, trial in zip(rows, plan["trials"]):
        require(row["run"] == trial["id"] and all(row[k] == trial[k] for k in ["task", "arm", "effort", "repetition"]), "Plan/run mismatch")
        definition, files = fixture.files_for(row["task"])
        for relative, expected in row["expected_frozen_hashes"].items():
            require(hashlib.sha256(files[relative].encode("utf-8")).hexdigest() == expected, "Frozen fixture mismatch")
        for usage in [row["usage"]] + [t["usage"] for t in row["per_turn"]]:
            require(all(type(usage[k]) is int and usage[k] >= 0 for k in keys), "Invalid extended usage")
            require(usage["totalTokens"] == sum(usage[k] for k in keys[:-1]), "Extended token accounting mismatch")
        require([t["turn"] for t in row["per_turn"]] == [1, 2], "Expected two user turns")
        for key in keys:
            require(row["usage"][key] == sum(t["usage"][key] for t in row["per_turn"]), "Per-turn usage mismatch")
        require(row["model_requests"] == sum(t["requests"] for t in row["per_turn"]), "Per-turn requests mismatch")
        require(row["tool_calls"] == sum(t["tool_calls"] for t in row["per_turn"]), "Per-turn tools mismatch")
        artifact = (base / row["artifact"]).resolve()
        require(artifact.is_relative_to(base) and digest(artifact) == row["artifact_sha256"], "Extended artifact hash mismatch")
        check = fixture.evaluate(row["task"], artifact)
        require(check.returncode == 0, "Extended artifact failed: " + row["run"] + "\n" + check.stderr)
        count = 9 if row["task"] == "reload" else 10
        require(row["test_methods"] == count and f"Ran {count} tests" in check.stderr, "Extended method count mismatch")
        observed_checks = ["unit_tests_passed", "requested_terminal_verification_executed_and_passed", "updated_rules_read_in_order", "handoff_did_not_modify_files", "route_correct"]
        require(row["all_checks_passed"] == (all(row[k] for k in observed_checks) and not row["protected_files_changed"]), "Observation summary mismatch")
    for arm in ["old_high", "new_high", "new_low"]:
        group = [r for r in rows if r["arm"] == arm]
        require({(r["task"], r["repetition"]) for r in group} == {(t, n) for t in ["cache", "reload"] for n in [1, 2]}, "Unbalanced extended design")
        total = results["totals"][arm]
        require(total["runs"] == len(group) and total["all_checks_passed"] == sum(r["all_checks_passed"] for r in group), "Extended count mismatch")
        require(all(total["usage"][k] == sum(r["usage"][k] for r in group) for k in keys), "Extended aggregate usage mismatch")
        require(total["requests"] == sum(r["model_requests"] for r in group) and total["tool_calls"] == sum(r["tool_calls"] for r in group), "Extended aggregate calls mismatch")
    totals = results["totals"]
    adopt = (totals["old_high"]["all_checks_passed"] == 4 and totals["new_high"]["all_checks_passed"] == 4 and totals["new_high"]["usage"]["totalTokens"] <= totals["old_high"]["usage"]["totalTokens"])
    require(results["candidate_adopted"] == adopt, "Predefined adoption decision mismatch")
    with tempfile.TemporaryDirectory(prefix="deepseek-extended-control-") as temporary:
        for task in ["reload", "cache"]:
            definition, files = fixture.files_for(task)
            source = Path(temporary) / (task + ".py")
            source.write_text(files[definition["editable"][0]], encoding="utf-8", newline="\n")
            require(fixture.evaluate(task, source).returncode != 0, "Extended original bug unexpectedly passed")
    print("Extended evidence, 114 unittest method executions and negative controls: OK")


def main():
    check_skill()
    check_history()
    check_negative_controls()
    check_extended()
    check_prompt_experiment("reasoning", ["graph", "ledger"])
    check_prompt_experiment("focused", ["join", "limiter", "patch", "paths"])
    angles = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "benchmarks" / "angles" / "check.py")], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=180)
    require(angles.returncode == 0, "Factorial evidence check failed:\n" + angles.stdout + angles.stderr)
    print(angles.stdout.strip())
    check_public_files()
    check = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT)
    require(check.returncode == 0, "Release package tests failed")
    print("All offline repository checks passed; no model/API calls were made.")


def check_prompt_experiment(directory, tasks):
    base = ROOT / "benchmarks" / directory
    result = json.loads((base / "results.json").read_text(encoding="utf-8"))
    plan = json.loads((base / "plan.json").read_text(encoding="utf-8"))
    snapshots = {arm: (base / name).resolve() for arm, name in result["prompt_snapshots"].items()}
    require(digest(snapshots["original"]) == result["old_sha256"] == plan["old_sha256"], "Prompt experiment original prompt hash mismatch")
    require(digest(snapshots["candidate"]) == result["candidate_sha256"] == plan["candidate_sha256"], "Prompt experiment candidate prompt hash mismatch")
    require(digest(ROOT / "SKILL.md") == result["old_sha256"], "Experimental prompt was promoted despite unmet criterion")
    spec = importlib.util.spec_from_file_location("reasoning_fixture", base / "fixture.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    rows = result["rows"]
    expected_runs = len(tasks) * 4
    require(len(rows) == len(plan["trials"]) == expected_runs and len({r["run"] for r in rows}) == expected_runs, "Prompt experiment run count mismatch")
    keys = ["inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens", "totalTokens"]
    for row, trial in zip(rows, plan["trials"]):
        require(row["run"] == trial["id"] and all(row[k] == trial[k] for k in ["task", "arm", "repetition", "effort"]), "Prompt experiment plan/run mismatch")
        require(all(type(row["usage"][k]) is int and row["usage"][k] >= 0 for k in keys), "Invalid reasoning usage")
        require(row["usage"]["totalTokens"] == sum(row["usage"][k] for k in keys[:-1]), "Prompt experiment token accounting mismatch")
        definition, files = fixture.files_for(row["task"])
        for relative, wanted in row["expected_frozen_hashes"].items():
            actual = digest(snapshots[row["arm"]]) if relative == ".agents/skills/deepseek-efficient/SKILL.md" else hashlib.sha256(files[relative].encode("utf-8")).hexdigest()
            require(actual == wanted, "Prompt experiment frozen fixture mismatch")
        artifact = (base / row["artifact"]).resolve()
        require(artifact.is_relative_to(base) and digest(artifact) == row["artifact_sha256"], "Prompt experiment artifact hash mismatch")
        check = fixture.evaluate(row["task"], artifact)
        count = definition["test_methods"]
        require(check.returncode == 0 and f"Ran {count} tests" in check.stderr and count == row["test_methods"], "Prompt experiment artifact failed: " + row["run"] + "\n" + check.stderr)
        quality = (row["transport_exit"] == 0 and not row["timed_out"] and row["has_final"] and row["unit_tests_passed"] and not row["protected_files_changed"] and row["terminal_verification_passed"] and row["route_correct"])
        require(row["all_checks_passed"] == quality, "Prompt experiment observation summary mismatch")
    for task in tasks:
        order = [[t["arm"] for t in plan["trials"] if t["task"] == task and t["repetition"] == n] for n in [1, 2]]
        require(set(order[0]) == {"original", "candidate"} and order[0] == list(reversed(order[1])), "Prompt experiment order balance mismatch")
    for arm in ["original", "candidate"]:
        group = [r for r in rows if r["arm"] == arm]
        total = result["totals"][arm]
        require({(r["task"], r["repetition"]) for r in group} == {(t, n) for t in tasks for n in [1, 2]}, "Prompt experiment design mismatch")
        require(total["runs"] == len(tasks) * 2 and total["all_checks_passed"] == sum(r["all_checks_passed"] for r in group), "Prompt experiment aggregate quality mismatch")
        require(all(total["usage"][k] == sum(r["usage"][k] for r in group) for k in keys), "Prompt experiment aggregate usage mismatch")
        require(all(total[k] == sum(r[k] for r in group) for k in ["model_requests", "tool_calls", "wall_ms"]), "Prompt experiment aggregate calls/time mismatch")
    require(len(result["pairs"]) == len(tasks) * 2 and len({(p["task"], p["repetition"]) for p in result["pairs"]}) == len(tasks) * 2, "Prompt experiment pair count mismatch")
    for pair in result["pairs"]:
        a = next(r for r in rows if r["task"] == pair["task"] and r["repetition"] == pair["repetition"] and r["arm"] == "original")
        b = next(r for r in rows if r["task"] == pair["task"] and r["repetition"] == pair["repetition"] and r["arm"] == "candidate")
        require(pair["original_tokens"] == a["usage"]["totalTokens"] and pair["candidate_tokens"] == b["usage"]["totalTokens"], "Prompt experiment pair usage mismatch")
        require(pair["candidate_wins"] == (pair["candidate_tokens"] < pair["original_tokens"]), "Prompt experiment pair winner mismatch")
        require(math.isclose(pair["reduction_percent"], 100 * (1 - pair["candidate_tokens"] / pair["original_tokens"]), abs_tol=1e-9), "Prompt experiment pair percentage mismatch")
    criterion = plan["adoption"]
    require(result["adoption_criterion"] == criterion, "Prompt experiment adoption criterion changed")
    adopt = (all(r["all_checks_passed"] for r in rows) and result["totals"]["candidate"]["usage"]["totalTokens"] / result["totals"]["original"]["usage"]["totalTokens"] <= criterion["candidate_total_ratio_max"] and sum(p["candidate_wins"] for p in result["pairs"]) >= criterion["candidate_pair_wins_min"])
    if "task_totals" in result:
        require(set(result["task_totals"]) == set(tasks), "Per-task summary keys mismatch")
        for task in tasks:
            groups = {arm: [r for r in rows if r["task"] == task and r["arm"] == arm] for arm in ["original", "candidate"]}
            a = sum(r["usage"]["totalTokens"] for r in groups["original"])
            b = sum(r["usage"]["totalTokens"] for r in groups["candidate"])
            total = result["task_totals"][task]
            require(total["original_runs"] == total["candidate_runs"] == 2, "Per-task run count mismatch")
            require(total["original_tokens"] == a and total["candidate_tokens"] == b and math.isclose(total["candidate_ratio"], b / a, abs_tol=1e-12), "Per-task tokens mismatch")
            wins = sum(p["candidate_wins"] for p in result["pairs"] if p["task"] == task)
            require(total["pair_wins"] == wins, "Per-task wins mismatch")
            if criterion.get("every_task_has_pair_win"):
                adopt = adopt and wins >= 1
            if "per_task_total_ratio_max" in criterion:
                adopt = adopt and b / a <= criterion["per_task_total_ratio_max"]
        for row in rows:
            require(all(type(row[k]) is int and row[k] >= 0 for k in ["native_read_calls", "native_read_steps", "discovery_calls", "write_or_edit_calls"]), "Invalid observed tool metric")
            require(row["native_read_steps"] <= row["native_read_calls"] <= row["tool_calls"], "Inconsistent native read counts")
    require(result["candidate_adopted"] == adopt, "Prompt experiment adoption decision mismatch")
    with tempfile.TemporaryDirectory(prefix="deepseek-reasoning-control-") as temporary:
        for task in tasks:
            definition, files = fixture.files_for(task)
            original = Path(temporary) / (task + ".py")
            original.write_text(files[definition["editable"][0]], encoding="utf-8", newline="\n")
            check = fixture.evaluate(task, original)
            require(check.returncode == 1 and "FAILED" in check.stderr, "Prompt experiment original bug control did not fail as expected")
    print(directory + " experiment:", sum(r["test_methods"] for r in rows), "unittest method executions and negative controls: OK")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        print("CHECK FAILED:", error, file=sys.stderr)
        sys.exit(1)
