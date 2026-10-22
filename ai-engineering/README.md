# AI Engineering Handbook

Version 0.4 — 2026-10-22

## Purpose
Prepare for mid-level and senior-level Applied AI Engineering interviews. This is a separate addition to the interview-prep site; do not replace root index.html, notebooks, or flashcards.

## Learning sequence
Start with Module 03, AI Agents & Tool Calling, while filling in prerequisites from Modules 01 and 02. Parallel tracks: Learn, Build, Interview, Get Hired.

## Maintenance
- `curriculum.json` is the planned module/lesson catalog.
- `index.html` is the browser-only interactive study app and first lesson. New lessons should become separate versioned content files rather than extending a monolithic document indefinitely.
- Browser `localStorage` is device-specific; use Export/Import on the site to transfer learning progress between browsers. Exports include M03-L02, M03-L03 and M03-L04 quiz/completion data under `lessons.M03-L02`, `lessons.M03-L03`, and `lessons.M03-L04`; old backups without the `lessons` field remain importable and preserve any existing M03-L02 progress. Avoid storing private answers or secrets in notes.
- Keep `HANDOFF.md` current after each milestone; include GitHub commit and verification evidence.
- Review API-specific guidance against vendor documentation as APIs change.

## Next content
M03-L02: tool contracts and authorization. M03-L03: implemented bounded controller, deadline, retry and UNKNOWN-outcome lessons, animated scenario simulator, Python controller lab with three tests, quizzes and interviews. M03-L04: implemented dependency-aware orchestration, state, checkpoints, animated simulation, offline Python lab and unit tests. Next: M03-L05; M05 evaluation; M06 durable execution. Include Python lab, tests, failure modes, mid-level exercise, senior design prompt, quizzes and spaced recall.

## Origin
Content direction and initial lesson based on the AI Engineering Handbook v0.1 archive in the user's Library. This deployed implementation is a compact single-page adaptation, not a byte-for-byte unpacking of the ZIP's original four site assets.

## Orchestration lab
Run `python ai-engineering/orchestration_lab.py` and `cd ai-engineering && python -m unittest -v test_orchestration.py` (Python 3.11+). The in-memory store is illustrative, **not** crash durable; tests are offline only.
