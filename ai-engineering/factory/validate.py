"""Dependency-free lesson spec checks. Python 3.11+."""
import json
import re
import sys
from pathlib import Path

FIELDS = {"id", "module", "title", "summary", "objectives", "sections", "quiz", "interview", "lab"}
SECTION = {"id", "title", "paragraphs", "diagram", "interactive"}
QUESTION = {"prompt", "options", "answer", "explanation"}
LAB = {"title", "instructions", "expected"}
DIAGRAM = {"type", "nodes", "edges"}


def check_text(value, path, minimum=1):
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ValueError(f"{path}: expected text with at least {minimum} characters")


def check_strings(value, path, minimum=1, count=1):
    if not isinstance(value, list) or len(value) < count:
        raise ValueError(f"{path}: expected at least {count} strings")
    for i, item in enumerate(value):
        check_text(item, f"{path}[{i}]", minimum)


def keys(value, path, required, allowed=None):
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    allowed = allowed or required
    missing = required - value.keys()
    extra = value.keys() - allowed
    if missing or extra:
        raise ValueError(f"{path}: missing={sorted(missing)} unexpected={sorted(extra)}")


def validate(data):
    keys(data, "lesson", FIELDS)
    if not isinstance(data["id"], str) or not re.fullmatch(r"M[0-9]{2}-L[0-9]{2}", data["id"]):
        raise ValueError("lesson.id: expected Mxx-Lxx")
    if not isinstance(data["module"], str) or data["module"] != data["id"].split("-")[0]:
        raise ValueError("lesson.module: does not match lesson.id")
    check_text(data["title"], "title", 8)
    check_text(data["summary"], "summary", 40)
    check_strings(data["objectives"], "objectives", 10, 2)
    check_strings(data["interview"], "interview", 20, 2)
    sections = data["sections"]
    if not isinstance(sections, list) or len(sections) < 2:
        raise ValueError("sections: expected at least two")
    ids = set()
    for i, section in enumerate(sections):
        p = f"sections[{i}]"
        keys(section, p, SECTION - {"diagram", "interactive"}, SECTION)
        sid = section["id"]
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", sid) or sid in ids:
            raise ValueError(f"{p}.id: invalid or duplicate")
        ids.add(sid)
        check_text(section["title"], f"{p}.title", 5)
        check_strings(section["paragraphs"], f"{p}.paragraphs", 30)
        if "interactive" in section:
            w = section["interactive"]
            if not isinstance(w, dict) or w.get("type") not in ("timeline", "retry", "parameter"):
                raise ValueError(f"{p}.interactive: unknown widget type")
            kind = w["type"]
            required = {
                "timeline": {"type", "tasks"},
                "retry": {"type", "maxAttempts", "failuresBeforeSuccess", "outcome"},
                "parameter": {"type", "parameter", "minimum", "maximum", "base", "factor", "target", "explanation"},
            }[kind]
            keys(w, f"{p}.interactive", required)
            if kind == "timeline":
                tasks = w["tasks"]
                if not isinstance(tasks, list) or not 2 <= len(tasks) <= 8:
                    raise ValueError(f"{p}.interactive.tasks: expected 2–8 tasks")
                names = set()
                for task in tasks:
                    keys(task, f"{p}.task", {"name", "start", "duration"})
                    check_text(task["name"], f"{p}.task.name")
                    if task["name"] in names:
                        raise ValueError(f"{p}.interactive.tasks: duplicate name")
                    names.add(task["name"])
                    for key in ("start", "duration"):
                        if type(task[key]) not in (int, float) or not 0 <= task[key] <= 1000 or (key == "duration" and task[key] == 0):
                            raise ValueError(f"{p}.task.{key}: invalid duration")
            elif kind == "retry":
                if type(w["maxAttempts"]) is not int or not 1 <= w["maxAttempts"] <= 10:
                    raise ValueError(f"{p}.interactive.maxAttempts: invalid")
                if type(w["failuresBeforeSuccess"]) is not int or not 0 <= w["failuresBeforeSuccess"] < w["maxAttempts"]:
                    raise ValueError(f"{p}.interactive.failuresBeforeSuccess: invalid")
                if w["outcome"] not in ("transient", "unknown"):
                    raise ValueError(f"{p}.interactive.outcome: invalid")
            else:
                check_text(w["parameter"], f"{p}.interactive.parameter")
                check_text(w["explanation"], f"{p}.interactive.explanation", 20)
                for key in ("minimum", "maximum", "base", "factor", "target"):
                    if type(w[key]) not in (int, float) or not -100000 <= w[key] <= 100000:
                        raise ValueError(f"{p}.interactive.{key}: invalid numeric value")
                if not w["minimum"] < w["maximum"] or w["maximum"] - w["minimum"] > 1000:
                    raise ValueError(f"{p}.interactive: invalid input range")
        if "diagram" in section:
            d = section["diagram"]
            keys(d, f"{p}.diagram", DIAGRAM)
            if d["type"] not in ("state-machine", "sequence"):
                raise ValueError(f"{p}.diagram.type: unsupported")
            check_strings(d["nodes"], f"{p}.diagram.nodes", count=2)
            if len(set(d["nodes"])) != len(d["nodes"]):
                raise ValueError(f"{p}.diagram.nodes: duplicates")
            if not isinstance(d["edges"], list) or not d["edges"]:
                raise ValueError(f"{p}.diagram.edges: empty")
            for edge in d["edges"]:
                if not isinstance(edge, list) or len(edge) != 2 or any(
                    not isinstance(v, str) or v not in d["nodes"] for v in edge
                ):
                    raise ValueError(f"{p}.diagram.edges: references unknown node")
    questions = data["quiz"]
    if not isinstance(questions, list) or len(questions) < 3:
        raise ValueError("quiz: expected at least three questions")
    for i, q in enumerate(questions):
        p = f"quiz[{i}]"
        keys(q, p, QUESTION)
        check_text(q["prompt"], f"{p}.prompt", 15)
        check_strings(q["options"], f"{p}.options", 2, 4)
        if len(q["options"]) != 4 or len(set(q["options"])) != 4:
            raise ValueError(f"{p}.options: four distinct options required")
        if type(q["answer"]) is not int or not 0 <= q["answer"] <= 3:
            raise ValueError(f"{p}.answer: expected integer 0..3")
        check_text(q["explanation"], f"{p}.explanation", 20)
    lab = data["lab"]
    keys(lab, "lab", LAB)
    check_text(lab["title"], "lab.title", 5)
    check_strings(lab["instructions"], "lab.instructions", 10, 2)
    check_text(lab["expected"], "lab.expected", 15)
    return data


def load(path):
    with Path(path).open(encoding="utf-8") as f:
        return validate(json.load(f))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python validate.py <lesson.json> [more.json ...]")
    try:
        for name in sys.argv[1:]:
            lesson = load(name)
            print(f"VALID {lesson['id']}: {name}")
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        sys.exit(f"INVALID: {exc}")
