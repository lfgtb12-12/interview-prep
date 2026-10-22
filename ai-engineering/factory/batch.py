"""Batch lesson preview builder. No publication or implicit PR merge."""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

from batch_quality import inspect
from render import render
from validate import load

HERE = Path(__file__).resolve().parent
PUBLISHED = HERE.parent.resolve()


def build(paths, out, strict=False):
    """Validate a batch atomically before writing any preview."""
    paths = [Path(p).resolve() for p in paths]
    if not 1 <= len(paths) <= 3:
        raise ValueError("batch requires 1–3 lesson specifications")
    if len(set(paths)) != len(paths):
        raise ValueError("duplicate spec paths")
    target = Path(out).resolve()
    if target == PUBLISHED or PUBLISHED in target.parents:
        raise ValueError("preview output must be outside the published ai-engineering tree")
    if target == HERE.parent.parent.resolve() or target == HERE.parent.parent.resolve().parent:
        raise ValueError("refusing to write previews to a repository root")
    errors, warnings = inspect(paths)
    if errors or (strict and warnings):
        raise ValueError("; ".join(errors or warnings))
    lessons = [load(path) for path in paths]
    names = [lesson["id"].lower() + ".html" for lesson in lessons]
    if len(set(names)) != len(names):
        raise ValueError("duplicate output names")
    # Preflight existing outputs: no generated HTML or report is ever overwritten.
    for name in names + ["quality-report.json", "index.html"]:
        if (target / name).exists():
            raise FileExistsError(f"refusing to overwrite {target / name}")
    target.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "preview-only",
        "lesson_ids": [lesson["id"] for lesson in lessons],
        "specs": [str(path) for path in paths],
        "editorial_warnings": warnings,
        "structural_errors": [],
        "fact_checked": False,
        "labs_executed": False,
        "browser_tested": False,
    }
    for lesson, name in zip(lessons, names):
        (target / name).write_text(render(lesson), encoding="utf-8")
    links = "\n".join(f'<li><a href="{html.escape(name, quote=True)}">{html.escape(lesson["id"])}: {html.escape(lesson["title"])}</a></li>'
                      for lesson, name in zip(lessons, names))
    (target / "index.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>Draft lesson batch</title><h1>Draft previews — not published</h1><ul>'
        + links + '</ul></html>', encoding="utf-8")
    (target / "quality-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def propose_pr(branch, title, body, remote="origin"):
    """Optional explicit GitHub CLI operation; never auto-merge or alter main."""
    if not branch.startswith("factory/"):
        raise ValueError("PR head must be a factory/ branch")
    current = subprocess.run(["git", "branch", "--show-current"], check=True,
                             capture_output=True, text=True).stdout.strip()
    if current != branch:
        raise ValueError(f"checkout {branch} before creating its PR (currently {current})")
    dirty = subprocess.run(["git", "status", "--porcelain"], check=True,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        raise ValueError("working tree must be clean; commit reviewed factory changes first")
    # gh handles repository identity and authentication. Draft PR requires explicit promotion.
    subprocess.run(["git", "push", remote, branch], check=True)
    subprocess.run(["gh", "pr", "create", "--base", "main", "--head", branch,
                    "--draft", "--title", title, "--body", body], check=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate and stage up to three draft lessons")
    parser.add_argument("specs", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path,
                        help="new preview directory outside ai-engineering/")
    parser.add_argument("--strict-editorial", action="store_true")
    parser.add_argument("--create-pr", action="store_true",
                        help="explicitly push current factory branch and create a DRAFT PR using gh")
    parser.add_argument("--branch", help="required with --create-pr")
    args = parser.parse_args(argv)
    try:
        report = build(args.specs, args.out, args.strict_editorial)
        print(json.dumps(report, indent=2))
        if args.create_pr:
            if not args.branch:
                parser.error("--create-pr requires --branch")
            propose_pr(args.branch, "Factory: staged batch lesson previews",
                       "Staged validated lesson specifications. Draft only; "
                       "review factual claims, exercises, accessibility and browser behavior.")
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Batch failed: {exc}\n")


if __name__ == "__main__":
    main()
