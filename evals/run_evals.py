"""
End-to-end evaluation suite for APIA.
Runs all test cases in golden_set.json against the live pipeline.

Requirements:
  - FastAPI running on localhost:8000
  - Ingestion pipeline completed (ChromaDB populated)

Usage:
  python -m evals.run_evals
  python -m evals.run_evals --test z4_eval_001        # run one test
  python -m evals.run_evals --category engine         # run by category
  python -m evals.run_evals --fast                    # skip slow tests
"""

import json
import time
import argparse
import requests
from datetime import datetime
from pathlib import Path

API_URL      = "http://localhost:8000"
GOLDEN_SET   = Path("evals/golden_set.json")
RESULTS_DIR  = Path("evals/results")
RESULTS_DIR.mkdir(exist_ok=True)


# ── Assertion checker ─────────────────────────────────────────────────────────

def check_assertions(data: dict, assertions: dict) -> tuple[list, list]:
    """
    Runs all assertions for a single test case.
    Returns (passed_list, failed_list).
    """
    passed = []
    failed = []

    classification = data.get("classification", {})
    report         = data.get("report", {})
    report_text    = json.dumps(report).lower()

    def ok(name):
        passed.append(name)

    def fail(name, reason=""):
        failed.append(f"{name}" + (f" ({reason})" if reason else ""))

    # Classification category match
    if "classification.defect_category" in assertions:
        expected = assertions["classification.defect_category"]
        actual   = classification.get("defect_category", "")
        if actual == expected:
            ok("defect_category")
        else:
            fail("defect_category", f"expected '{expected}', got '{actual}'")

    # Severity in allowed set
    if "classification.severity_in" in assertions:
        allowed = assertions["classification.severity_in"]
        actual  = classification.get("severity", "")
        if actual in allowed:
            ok("severity")
        else:
            fail("severity", f"expected one of {allowed}, got '{actual}'")

    # Report must contain these phrases
    for phrase in assertions.get("report_must_mention", []):
        if phrase.lower() in report_text:
            ok(f"mentions '{phrase}'")
        else:
            fail(f"mentions '{phrase}'", "phrase not found in report")

    # Report must NOT contain these phrases
    for phrase in assertions.get("report_must_not_mention", []):
        if phrase.lower() not in report_text:
            ok(f"avoids '{phrase}'")
        else:
            fail(f"avoids '{phrase}'", "phrase found but should not be")

    # Minimum sources retrieved
    if "min_research_sources" in assertions:
        sources    = report.get("sources", [])
        min_needed = assertions["min_research_sources"]
        if len(sources) >= min_needed:
            ok(f"min_sources ({len(sources)} >= {min_needed})")
        else:
            fail(f"min_sources", f"got {len(sources)}, need {min_needed}")

    # Escalation flag
    if "validation.requires_escalation" in assertions:
        expected   = assertions["validation.requires_escalation"]
        validation = data.get("validation", {})
        actual     = validation.get("requires_escalation", False)
        if actual == expected:
            ok("requires_escalation")
        else:
            fail("requires_escalation", f"expected {expected}, got {actual}")

    return passed, failed


# ── Single test runner ────────────────────────────────────────────────────────

def run_single_test(test_case: dict) -> dict:
    """
    Submits one defect, waits for the pipeline to complete,
    auto-approves, and runs assertions.
    Returns a result dict.
    """
    test_id    = test_case["id"]
    assertions = test_case["assertions"]
    max_lat    = assertions.get("max_latency_seconds", 120)

    result = {
        "id":        test_id,
        "passed":    [],
        "failed":    [],
        "error":     None,
        "latency_s": None,
        "cost_usd":  None
    }

    start = time.time()

    try:
        # 1. Submit defect — runs the full pipeline
        resp = requests.post(
            f"{API_URL}/submit-defect",
            json=test_case["input"],
            timeout=max_lat + 30
        )
        resp.raise_for_status()
        data = resp.json()

        latency = round(time.time() - start, 1)
        result["latency_s"] = latency

        # 2. Auto-approve so the graph completes
        report_id = data.get("report_id")
        if report_id:
            requests.post(
                f"{API_URL}/human-decision",
                json={"report_id": report_id, "approved": True, "feedback": ""},
                timeout=30
            )

        # 3. Latency assertion
        if latency <= max_lat:
            result["passed"].append(f"latency ({latency}s <= {max_lat}s)")
        else:
            result["failed"].append(f"latency ({latency}s > {max_lat}s)")

        # 4. Run all content assertions
        passed, failed = check_assertions(data, assertions)
        result["passed"].extend(passed)
        result["failed"].extend(failed)

    except requests.exceptions.Timeout:
        result["error"] = f"Request timed out after {max_lat + 30}s"
    except requests.exceptions.ConnectionError:
        result["error"] = "Cannot connect to API — is FastAPI running on port 8000?"
    except Exception as e:
        result["error"] = str(e)

    return result


# ── Main eval runner ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="APIA Evaluation Suite")
    parser.add_argument("--test",     help="Run a single test by ID, e.g. z4_eval_001")
    parser.add_argument("--category", help="Run only tests matching a defect category")
    parser.add_argument("--fast",     action="store_true", help="Skip tests with latency > 90s")
    args = parser.parse_args()

    # Load test cases
    with open(GOLDEN_SET) as f:
        all_tests = json.load(f)

    # Filter if flags provided
    if args.test:
        tests = [t for t in all_tests if t["id"] == args.test]
        if not tests:
            print(f"❌ Test '{args.test}' not found in golden_set.json")
            return
    elif args.category:
        tests = [
            t for t in all_tests
            if t["assertions"].get("classification.defect_category") == args.category
        ]
        if not tests:
            print(f"❌ No tests found for category '{args.category}'")
            return
    elif args.fast:
        tests = [t for t in all_tests if t["assertions"].get("max_latency_seconds", 120) <= 90]
    else:
        tests = all_tests

    print("\n" + "=" * 60)
    print(f"  APIA Evaluation Suite — {len(tests)} test(s)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Verify API is reachable before starting
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        health.raise_for_status()
        print(f"  ✅ API reachable at {API_URL}\n")
    except Exception:
        print(f"  ❌ Cannot reach API at {API_URL}")
        print("     Start the API first: uvicorn api.main:app --reload --port 8000")
        return

    all_results  = []
    total_passed = 0
    total_failed = 0
    total_errors = 0

    for i, test in enumerate(tests, 1):
        print(f"[{i:02d}/{len(tests):02d}] {test['id']}", end="  ", flush=True)

        result = run_single_test(test)
        all_results.append(result)

        if result["error"]:
            print(f"ERROR: {result['error']}")
            total_errors += 1
        else:
            n_pass = len(result["passed"])
            n_fail = len(result["failed"])
            total_passed += n_pass
            total_failed += n_fail

            status = "✅ PASS" if n_fail == 0 else f"❌ FAIL"
            lat    = f"{result['latency_s']}s" if result["latency_s"] else "?"
            print(f"{status} | {n_pass}/{n_pass + n_fail} assertions | {lat}")

            # Print failed assertions indented
            for fail_msg in result["failed"]:
                print(f"         ✗ {fail_msg}")

    # ── Summary ───────────────────────────────────────────────────────────────
    total_assertions = total_passed + total_failed
    tests_passed     = sum(1 for r in all_results if not r["error"] and not r["failed"])
    tests_failed     = len(tests) - tests_passed - total_errors
    avg_latency      = (
        sum(r["latency_s"] for r in all_results if r["latency_s"])
        / max(1, sum(1 for r in all_results if r["latency_s"]))
    )

    print("\n" + "=" * 60)
    print(f"  Test cases:  {tests_passed}/{len(tests)} passed")
    print(f"  Assertions:  {total_passed}/{total_assertions} passed")
    print(f"  Errors:      {total_errors}")
    print(f"  Avg latency: {avg_latency:.1f}s")
    if total_errors > 0:
        print(f"\n  ⚠ {total_errors} test(s) errored — check API logs for details")
    print("=" * 60)

    # ── Save results to file ──────────────────────────────────────────────────
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"eval_results_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump({
            "timestamp":       datetime.now().isoformat(),
            "total_tests":     len(tests),
            "tests_passed":    tests_passed,
            "total_assertions": total_assertions,
            "assertions_passed": total_passed,
            "avg_latency_s":   round(avg_latency, 1),
            "results":         all_results
        }, f, indent=2)

    print(f"\n  Results saved to: {output_file}")


if __name__ == "__main__":
    main()