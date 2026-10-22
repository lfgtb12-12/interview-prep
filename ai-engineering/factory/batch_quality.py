"""Batch quality gate for staged textbook specifications.

Runs local structural validation plus clearly labeled editorial heuristics.
Never claims to verify factual accuracy or execute learner lab instructions.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def check_spec(spec, source):
    """Return (errors, warnings). Errors block rendering; warnings need editorial review."""
    errors, warnings = [], []
    ident = spec.get("id", source.name)
    sections = spec.get("sections", [])
    paragraphs = [p for section in sections for p in section.get("paragraphs", [])]
    if len(sections) < 4:
        warnings.append(f"{ident}: fewer than four teaching sections")
    if sum(len(p.split()) for p in paragraphs) < 500:
        warnings.append(f"{ident}: fewer than 500 words in section paragraphs")
    if len(spec.get("quiz", [])) < 5:
        warnings.append(f"{ident}: fewer than five questions")
    if not any(section.get("diagram") or section.get("widgets") for section in sections):
        warnings.append(f"{ident}: no interactive diagram/widget declared in sections")
    if len(spec.get("interview", [])) < 3:
        warnings.append(f"{ident}: fewer than three interview prompts")
    if not spec.get("lab", {}).get("expected", "").strip():
        errors.append(f"{ident}: lab lacks expected outcome")
    for i, section in enumerate(sections, 1):
        for j, paragraph in enumerate(section.get("paragraphs", []), 1):
            if re.search(r"\b(TODO|TBD|FIXME)\b", paragraph, re.I):
                warnings.append(f"{ident}: placeholder in section {i}, paragraph {j}")
    return errors, warnings


def inspect(paths):
    errors, warnings, ids = [], [], set()
    for path in paths:
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: cannot read JSON: {exc}")
            continue
        if not isinstance(spec, dict):
            errors.append(f"{path}: root must be an object")
            continue
        ident = spec.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"M\d{2}-L\d{2}", ident):
            errors.append(f"{path}: invalid lesson id")
        elif ident in ids:
            errors.append(f"{path}: duplicate lesson id {ident}")
        else:
            ids.add(ident)
        if isinstance(ident, str) and spec.get("module") != ident.split("-")[0]:
            errors.append(f"{path}: module does not match lesson id")
        if not isinstance(spec.get("sections"), list) or not isinstance(spec.get("quiz"), list):
            errors.append(f"{path}: missing sections or quiz list")
            continue
        if any(not isinstance(s, dict) or not isinstance(s.get("paragraphs"), list) for s in spec["sections"]):
            errors.append(f"{path}: malformed section")
            continue
        if not isinstance(spec.get("lab"), dict):
            errors.append(f"{path}: malformed lab")
            continue
        extra_errors, extra_warnings = check_spec(spec, path)
        errors.extend(extra_errors)
        warnings.extend(extra_warnings)
        # The authoritative validator checks the complete spec contract.
        result = subprocess.run(
            [sys.executable, str(HERE / "validate.py"), str(path)],
            text=True, capture_output=True, check=False,
        )
        if result.returncode:
            errors.append(f"{path}: schema validation failed: {(result.stderr or result.stdout).strip()[:500]}")
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Batch structural and editorial heuristic gate")
    parser.add_argument("specs", nargs="+", type=Path)
    parser.add_argument("--strict-editorial", action="store_true", help="Treat editorial warnings as failures")
    args = parser.parse_args(argv)
    errors, warnings = inspect(args.specs)
    for message in errors:
        print("ERROR:", message)
    for message in warnings:
        print("REVIEW:", message)
    print(f"Checked {len(args.specs)} lesson spec(s); {len(errors)} errors; {len(warnings)} editorial warnings")
    return 1 if errors or (args.strict_editorial and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
