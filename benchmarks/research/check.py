"""Recheck research artifacts and accounting offline; never calls a model."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
KEYS = ["inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens", "totalTokens"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def valid_usage(value):
    return (all(type(value[k]) is int and value[k] >= 0 for k in KEYS)
            and value["totalTokens"] == sum(value[k] for k in KEYS[:-1]))


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def evaluate(definition, artifact=None):
    with tempfile.TemporaryDirectory(prefix="research-artifact-") as directory:
        work = Path(directory)
        for relative, content in definition["files"].items():
            target = work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
        if artifact:
            (work / definition["editable"][0]).write_bytes(artifact.read_bytes())
        return subprocess.run([sys.executable, "-X", "utf8", "verify.py"], cwd=work,
                              capture_output=True, text=True, encoding="utf-8", timeout=30)


def main():
    tasks = load("tasks.json")
    executions = 0
    for stage in ["prototype", "repaired"]:
        plan, result = load(stage + "-plan.json"), load(stage + "-results.json")
        require(result["complete"] and len(plan["trials"]) == len(result["rows"]) == 8, "Incomplete stage")
        require(result["adoption_criterion"] == plan["adoption"], "Criteria changed")
        snapshots = {arm: (BASE / relative).read_bytes() for arm, relative in result["prompt_snapshots"].items()}
        helper = (BASE / result["helper_snapshot"]).read_bytes()
        require(sha(helper) == plan["helper_sha256"] == result["helper_sha256"], "Helper hash mismatch")
        require(sha(snapshots["original"]) == plan["old_sha256"] == result["old_sha256"], "Original hash mismatch")
        require(sha(snapshots["candidate"]) == plan["candidate_sha256"] == result["candidate_sha256"], "Candidate hash mismatch")
        require((ROOT / "SKILL.md").read_bytes() == snapshots["original"], "Default skill changed without adoption")
        for row, trial in zip(result["rows"], plan["trials"]):
            require(all(row[k] == trial[k] for k in ["task", "arm", "repetition"]), "Trial mismatch")
            require(row["run"] == trial["id"], "Run mismatch")
            definition = tasks[row["task"]]
            require(row["expected_frozen_hashes"] == trial["frozen_hashes"], "Frozen control mismatch")
            for relative, wanted in trial["frozen_hashes"].items():
                actual = (snapshots[row["arm"]] if relative.endswith("SKILL.md") else
                          helper if relative.startswith(".agents/skills/") else
                          definition["files"][relative].encode("utf-8"))
                require(sha(actual) == wanted, "Frozen file changed: " + relative)
            usages = [r["usage"] for r in row["request_usage"]]
            require(valid_usage(row["usage"]) and all(valid_usage(u) for u in usages), "Invalid usage")
            require(row["model_requests"] == len(usages), "Request count mismatch")
            require(all(row["usage"][k] == sum(u[k] for u in usages) for k in KEYS), "Usage aggregation mismatch")
            quality = (row["transport_exit"] == 0 and not row["timed_out"] and row["has_final"]
                       and row["unit_tests_passed"] and not row["protected_files_changed"]
                       and row["requested_verification_passed"] and row["route_correct"])
            require(row["all_checks_passed"] == quality, "Quality summary mismatch")
            artifact = (BASE / row["artifact"]).resolve()
            require(artifact.is_relative_to(BASE) and sha(artifact.read_bytes()) == row["artifact_sha256"], "Artifact hash mismatch")
            grade = evaluate(definition, artifact)
            require(grade.returncode == 0 and f'Ran {row["test_methods"]} tests' in grade.stderr
                    and row["test_methods"] == definition["test_methods"], "Code artifact failed")
            executions += row["test_methods"]
            logs = row["retained_logs"]
            passed = any(r["hash_matches"] and r["size_matches"] and r["exit_code"] == 0
                         and r["test_count_matches"] and r["has_ok"] for r in logs)
            require(row["helper_evidence_passed"] == passed, "Helper evidence mismatch")
        rows = result["rows"]
        for task in tasks:
            orders = [[r["arm"] for r in rows if r["task"] == task and r["repetition"] == n] for n in [1, 2]]
            require(set(orders[0]) == {"candidate", "original"} and orders[1] == list(reversed(orders[0])), "Pair order mismatch")
        for arm in ["original", "candidate"]:
            group = [r for r in rows if r["arm"] == arm]
            total = result["totals"][arm]
            require(len(group) == total["runs"] == 4, "Group size mismatch")
            require(total["all_checks_passed"] == sum(r["all_checks_passed"] for r in group), "Quality aggregate mismatch")
            require(all(total["usage"][k] == sum(r["usage"][k] for r in group) for k in KEYS), "Token aggregate mismatch")
            require(all(total[k] == sum(r[k] for r in group) for k in
                        ["model_requests", "tool_calls", "tool_result_chars", "verification_result_chars", "wall_ms"]), "Counter aggregate mismatch")
        require(len(result["pairs"]) == 4 and len({(p["task"], p["repetition"]) for p in result["pairs"]}) == 4, "Pair count mismatch")
        for pair in result["pairs"]:
            group = {r["arm"]: r for r in rows if r["task"] == pair["task"] and r["repetition"] == pair["repetition"]}
            a, b = group["original"]["usage"]["totalTokens"], group["candidate"]["usage"]["totalTokens"]
            require(pair["original_tokens"] == a and pair["candidate_tokens"] == b
                    and pair["candidate_wins"] == (b < a), "Pair accounting mismatch")
        for task in tasks:
            total = result["task_totals"][task]
            for arm in ["original", "candidate"]:
                group = [r for r in rows if r["task"] == task and r["arm"] == arm]
                require(total[arm + "_runs"] == len(group) == 2, "Task cell count mismatch")
                require(total[arm + "_tokens"] == sum(r["usage"]["totalTokens"] for r in group), "Task token sum mismatch")
            require(math.isclose(total["candidate_ratio"], total["candidate_tokens"] / total["original_tokens"]), "Task ratio mismatch")
        verbose = [r for r in rows if r["task"] == "verbose" and r["arm"] == "candidate"]
        adherence = len(verbose) == 2 and all(r["helper_calls"] > 0 and r["helper_evidence_passed"] for r in verbose)
        require(result["helper_adherence"] == adherence, "Adherence mismatch")
        criterion = plan["adoption"]
        adopted = (all(r["all_checks_passed"] for r in rows)
                   and result["totals"]["candidate"]["usage"]["totalTokens"] / result["totals"]["original"]["usage"]["totalTokens"] <= criterion["candidate_total_ratio_max"]
                   and sum(p["candidate_wins"] for p in result["pairs"]) >= criterion["pair_wins_min"]
                   and result["task_totals"]["quiet"]["candidate_ratio"] <= criterion["quiet_total_ratio_max"]
                   and result["task_totals"]["verbose"]["candidate_ratio"] <= criterion["verbose_total_ratio_max"]
                   and adherence)
        require(result["candidate_adopted"] == adopted, "Adoption decision mismatch")
    for definition in tasks.values():
        negative = evaluate(definition)
        require(negative.returncode == 1 and "FAILED" in negative.stderr, "Bug control unexpectedly passed")
    print(f"Research evidence: 16 artifacts, {executions} unittest method executions, negative controls and both rejected candidates: OK")


if __name__ == "__main__":
    main()
