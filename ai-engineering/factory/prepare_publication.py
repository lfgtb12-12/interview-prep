"""Prepare reviewed chapter candidates outside the live site; never deploy implicitly.

Explicit promotion is a separate, human-approved PR containing published files.
"""
import argparse
import json
import re
from pathlib import Path

from batch_quality import inspect
from render import render
from validate import load

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.resolve()


def chapter_html(spec):
    """Convert a validated factory draft to a *candidate* handbook chapter."""
    data = load(spec)
    ident = data["id"]
    page = render(data)
    header = '<header><a href="../">← Handbook</a> · Generated preview · Not published</header>'
    if page.count(header) != 1:
        raise ValueError("renderer header contract changed")
    page = page.replace(header, '<header><a href="./">← Handbook dashboard</a> · Lesson candidate</header>')
    key = '"ai-textbook-factory-" + data.id + "-v1"'
    if page.count(key) != 1:
        raise ValueError("renderer storage contract changed")
    page = page.replace(key, '"ai-handbook-" + data.id.toLowerCase() + "-v1"')
    head = '</head>'
    if page.count(head) != 1:
        raise ValueError("renderer head contract changed")
    page = page.replace(head, '<link rel="stylesheet" href="navigation.css">' + head, 1)
    end = '</body>'
    if page.count(end) != 1:
        raise ValueError("renderer script contract changed")
    page = page.replace(end, '<script src="navigation.js" defer></script>' + end, 1)
    return page


def prepare(specs, output, curriculum):
    paths = [Path(p).resolve() for p in specs]
    if not 1 <= len(paths) <= 3:
        raise ValueError("expected 1–3 specs")
    errors, warnings = inspect(paths)
    if errors or warnings:
        raise ValueError("quality gate failed: " + "; ".join(errors + warnings))
    manifest = json.loads(Path(curriculum).read_text(encoding="utf-8"))
    existing = {lesson["id"] for module in manifest["modules"] for lesson in module["lessons"]}
    output = Path(output).resolve()
    if output == SITE or SITE in output.parents:
        raise ValueError("never write candidates into the deployed directory")
    chapter_files = {}
    for path in paths:
        data = load(path)
        if data["id"] in existing:
            raise ValueError(f"already published: {data['id']}")
        name = "chapter-" + data["id"].lower() + ".html"
        if name in chapter_files:
            raise ValueError("duplicate lesson identifier in batch")
        chapter_files[name] = chapter_html(path)
    for name in chapter_files:
        if (output / name).exists():
            raise FileExistsError(f"refusing to overwrite {name}")
    if (output / "promotion-report.json").exists():
        raise FileExistsError("refusing to overwrite promotion report")
    output.mkdir(parents=True, exist_ok=True)
    for name, page in chapter_files.items():
        (output / name).write_text(page, encoding="utf-8")
    report = {
        "status": "candidate-not-published",
        "files": list(chapter_files),
        "editorial_review_required": True,
        "browser_verification_required": True,
        "lab_reference_tests_required": True,
        "publication_requires_separate_approval": True,
        "curriculum_unchanged": True,
    }
    (output / "promotion-report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description="Prepare chapter candidates for separate publication PR")
    parser.add_argument("specs", nargs="+")
    parser.add_argument("--out", required=True)
    parser.add_argument("--curriculum", default=str(SITE / "curriculum.json"))
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.specs, args.out, args.curriculum), indent=2))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"Promotion preparation failed: {exc}\n")


if __name__ == "__main__":
    main()
