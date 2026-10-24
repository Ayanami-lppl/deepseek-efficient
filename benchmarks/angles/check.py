"""Validate frozen factorial evidence and trusted artifacts without model calls."""

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
KEYS = ["inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens", "totalTokens"]
ARMS = ["none_high", "skill_high", "none_low", "skill_low"]
TASKS = ["join", "limiter", "patch", "paths"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def usage_valid(usage):
    return (all(type(usage[k]) is int and usage[k] >= 0 for k in KEYS)
            and usage["totalTokens"] == sum(usage[k] for k in KEYS[:-1]))


def main():
    result, plan = load(BASE / "results.json"), load(BASE / "plan.json")
    require(result["profile_control"]["patches_equal_after_reasoningEffort_normalization"] and result["profile_control"]["fields_changed"] == ["reasoningEffort"], "Effort profile control not confirmed")
    snapshot = (BASE / result["prompt_snapshot"]).resolve()
    require(snapshot.is_relative_to(ROOT) and sha(snapshot) == plan["skill_sha256"] == result["skill_sha256"], "Frozen skill hash mismatch")
    require(sha(ROOT / "SKILL.md") == result["skill_sha256"], "Runtime skill unexpectedly changed")
    spec = importlib.util.spec_from_file_location("angles_fixture", BASE / "fixture.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    rows = result["rows"]
    require(result["complete"] and result["completed"] == result["planned"] == plan["max_trials"] == len(rows) == 32, "Factorial run count mismatch")
    require(len({r["run"] for r in rows}) == 32, "Duplicate factorial run")
    for row, trial in zip(rows, plan["trials"]):
        require(row["run"] == trial["id"] and all(row[k] == trial[k] for k in ["task", "arm", "effort", "repetition", "skill_expected"]), "Plan/run mismatch")
        require(row["skill_expected"] == row["arm"].startswith("skill_") and row["effort"] == row["arm"].split("_")[1], "Factor assignment mismatch")
        definition, files = fixture.files_for(row["task"])
        frozen = row["expected_frozen_hashes"]
        require((".agents/skills/deepseek-efficient/SKILL.md" in frozen) == row["skill_expected"], "Skill fixture assignment mismatch")
        for relative, expected in frozen.items():
            actual = sha(snapshot) if relative.endswith("SKILL.md") else hashlib.sha256(files[relative].encode("utf-8")).hexdigest()
            require(actual == expected, "Frozen file mismatch: " + relative)
        usages = [r["usage"] for r in row["request_usage"]]
        require(all(usage_valid(u) for u in usages) and usage_valid(row["usage"]), "Invalid request usage")
        require(all(row["usage"][k] == sum(u[k] for u in usages) for k in KEYS), "Request/aggregate usage mismatch")
        require(row["model_requests"] == len(usages), "Request count mismatch")
        require(row["first_request_input_tokens"] == usages[0]["inputTokens"] + usages[0]["cacheReadTokens"], "Initial input mismatch")
        require(row["treatment_adherence"] == (row["skill_loaded"] == row["skill_expected"]), "Adherence mismatch")
        require(row["skill_loaded"] == (row["skill_load_calls"] > 0), "Skill load count mismatch")
        quality = (row["transport_exit"] == 0 and not row["timed_out"] and row["has_final"] and row["unit_tests_passed"] and not row["protected_files_changed"] and row["terminal_verification_passed"] and row["route_correct"])
        require(row["quality_passed"] == quality and row["all_checks_passed"] == (quality and row["treatment_adherence"]), "Quality summary mismatch")
        for key in ["tool_calls", "tool_errors", "native_write_unread_errors", "native_read_calls", "inspect_read_calls", "failed_skill_lookups", "post_success_test_tool_calls", "tool_count", "tool_schema_json_chars", "wall_ms"]:
            require(type(row[key]) is int and row[key] >= 0, "Invalid observed counter")
        require(row["native_write_unread_errors"] <= row["tool_errors"] <= row["tool_calls"], "Inconsistent tool error counts")
        artifact = (BASE / row["artifact"]).resolve()
        require(artifact.is_relative_to(BASE) and sha(artifact) == row["artifact_sha256"], "Artifact hash mismatch")
        grade = fixture.evaluate(row["task"], artifact)
        count = definition["test_methods"]
        require(grade.returncode == 0 and f"Ran {count} tests" in grade.stderr and count == row["test_methods"], "Artifact failed: " + row["run"] + "\n" + grade.stderr)
    for task in TASKS:
        orders = [[t["arm"] for t in plan["trials"] if t["task"] == task and t["repetition"] == n] for n in [1, 2]]
        require(set(orders[0]) == set(ARMS) and len(orders[0]) == 4 and orders[1] == list(reversed(orders[0])), "Four-arm order balance mismatch")
    for arm in ARMS:
        group = [r for r in rows if r["arm"] == arm]
        total = result["totals"][arm]
        require({(r["task"], r["repetition"]) for r in group} == {(t, n) for t in TASKS for n in [1, 2]}, "Factorial cells unbalanced")
        require(total["runs"] == len(group) == 8, "Cell run count mismatch")
        for key, field in [("quality_passed", "quality_passed"), ("adherence_passed", "treatment_adherence"), ("all_checks_passed", "all_checks_passed")]:
            require(total[key] == sum(r[field] for r in group), "Cell quality mismatch")
        require(all(total["usage"][k] == sum(r["usage"][k] for r in group) for k in KEYS), "Cell token aggregate mismatch")
        require(all(total[k] == sum(r[k] for r in group) for k in ["model_requests", "tool_calls", "wall_ms"]), "Cell count/time aggregate mismatch")
    require([(c["baseline"], c["candidate"]) for c in result["comparisons"]] == [tuple(c) for c in plan["analysis"]["comparisons"]], "Predefined comparisons changed")
    criterion = plan["analysis"]["recommendation_criterion"]
    for comparison in result["comparisons"]:
        a, b = comparison["baseline"], comparison["candidate"]
        ratio = result["totals"][b]["usage"]["totalTokens"] / result["totals"][a]["usage"]["totalTokens"]
        require(math.isclose(comparison["ratio"], ratio, abs_tol=1e-12), "Comparison ratio mismatch")
        require(len(comparison["pairs"]) == 8 and {(p["task"], p["repetition"]) for p in comparison["pairs"]} == {(t, n) for t in TASKS for n in [1, 2]}, "Comparison pair coverage mismatch")
        for pair in comparison["pairs"]:
            aa = next(r for r in rows if r["arm"] == a and r["task"] == pair["task"] and r["repetition"] == pair["repetition"])
            bb = next(r for r in rows if r["arm"] == b and r["task"] == pair["task"] and r["repetition"] == pair["repetition"])
            require(pair["baseline_tokens"] == aa["usage"]["totalTokens"] and pair["candidate_tokens"] == bb["usage"]["totalTokens"], "Pair token mismatch")
            require(pair["candidate_wins"] == (pair["candidate_tokens"] < pair["baseline_tokens"]), "Pair winner mismatch")
        wins = sum(p["candidate_wins"] for p in comparison["pairs"])
        quality = result["totals"][a]["all_checks_passed"] == result["totals"][b]["all_checks_passed"] == 8
        require(comparison["wins"] == wins and comparison["all_quality_and_adherence"] == quality, "Comparison quality/wins mismatch")
        eligible = quality and ratio <= criterion["candidate_total_ratio_max"] and wins >= criterion["pair_wins_min"]
        for task in TASKS:
            totals = comparison["task_totals"][task]
            group_a = [r for r in rows if r["arm"] == a and r["task"] == task]
            group_b = [r for r in rows if r["arm"] == b and r["task"] == task]
            ta, tb = (sum(r["usage"]["totalTokens"] for r in group) for group in [group_a, group_b])
            tw = sum(p["candidate_wins"] for p in comparison["pairs"] if p["task"] == task)
            require(totals["baseline_runs"] == totals["candidate_runs"] == 2 and totals["baseline_tokens"] == ta and totals["candidate_tokens"] == tb and math.isclose(totals["ratio"], tb / ta, abs_tol=1e-12) and totals["wins"] == tw, "Per-task comparison mismatch")
            eligible = eligible and tw >= 1 and tb / ta <= criterion["per_task_total_ratio_max"]
        require(comparison["meets_predefined_recommendation"] == eligible, "Predefined recommendation decision mismatch")
    probe = load(BASE / "read-guard/results.json")
    require(probe["complete"] and len(probe["rows"]) == 4, "Probe count mismatch")
    expected_arms = ["inspect", "read", "read", "inspect"]
    outcomes = []
    for row, arm in zip(probe["rows"], expected_arms):
        require(row["arm"] == arm and usage_valid(row["usage"]), "Probe assignment/usage mismatch")
        expected = (row["first_read"] == "ops_inspect_local_file" and row["first_native_write_rejected_as_unread"] and row["native_read_fallback"] and row["native_write_calls"] == 2) if arm == "inspect" else (row["first_read"] == "read" and not row["first_native_write_rejected_as_unread"] and row["native_write_calls"] == 1)
        require(row["hypothesis_observed"] == expected, "Probe interpretation mismatch")
        outcomes.append(expected and row["marker_and_protected_files_passed"] and not row["forbidden_shell_or_edit_calls"])
    require(probe["all_hypotheses_observed"] == all(outcomes), "Probe aggregate mismatch")
    with tempfile.TemporaryDirectory(prefix="deepseek-angles-control-") as temporary:
        for task in TASKS:
            definition, files = fixture.files_for(task)
            initial = Path(temporary) / (task + ".py")
            initial.write_text(files[definition["editable"][0]], encoding="utf-8", newline="\n")
            grade = fixture.evaluate(task, initial)
            require(grade.returncode == 1 and "FAILED" in grade.stderr, "Initial bug control not rejected")
    print("Factorial evidence: 32 artifacts / 336 unittest method executions; 4 controls; 4 recorded read-guard probes consistent.")


if __name__ == "__main__":
    main()
