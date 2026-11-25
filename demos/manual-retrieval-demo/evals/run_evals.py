#!/usr/bin/env python3
"""Eval harness for the manual + run-time retrieval demo.

Runs retrieve.py as a subprocess for each case in cases.json and asserts:
  - the exact manual-section selection for the task type,
  - the number of rows retrieved at run time,
  - the computed values in the grounded answer (percent changes, prices),
  - guardrail behavior: a card with no rows yields the no-data answer and
    no invented price anywhere in the answer.

Prints PASS/FAIL per case and exits non-zero if any case fails.
Python 3 standard library only.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = Path(__file__).resolve().parent / "cases.json"
RETRIEVE = ROOT / "retrieve.py"
ANSWER_MARKER = "GROUNDED ANSWER"


def parse_sections(stdout):
    match = re.search(r"^Sections selected: (.+)$", stdout, re.MULTILINE)
    if not match:
        return None
    return [s.strip() for s in match.group(1).split("|")]


def parse_rows(stdout):
    match = re.search(r"^Rows retrieved: (\d+)$", stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def answer_part(stdout):
    idx = stdout.find(ANSWER_MARKER)
    return stdout[idx:] if idx >= 0 else ""


def run_case(case):
    failures = []
    proc = subprocess.run(
        [sys.executable, str(RETRIEVE), *case["args"]],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return [f"retrieve.py exited {proc.returncode}: {proc.stderr.strip()}"]
    out = proc.stdout
    expect = case["expect"]

    expected_sections = expect.get("sections_exact")
    if expected_sections is not None:
        actual_sections = parse_sections(out)
        if actual_sections != expected_sections:
            failures.append(
                f"sections: expected {expected_sections}, got {actual_sections}"
            )

    expected_rows = expect.get("rows_retrieved")
    if expected_rows is not None:
        actual_rows = parse_rows(out)
        if actual_rows != expected_rows:
            failures.append(f"rows: expected {expected_rows}, got {actual_rows}")

    for needle in expect.get("contains", []):
        if needle not in out:
            failures.append(f"missing expected text: {needle!r}")

    answer = answer_part(out)
    for needle in expect.get("answer_not_contains", []):
        if needle in answer:
            failures.append(f"answer must not contain {needle!r} (guardrail)")

    return failures


def main():
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    passed = 0
    for case in cases:
        failures = run_case(case)
        if failures:
            print(f"FAIL {case['id']}")
            for failure in failures:
                print(f"     - {failure}")
        else:
            print(f"PASS {case['id']}")
            passed += 1
    print(f"EVAL SUMMARY: {passed}/{len(cases)} PASS")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
