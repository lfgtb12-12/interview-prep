## Milestone 2026-10-22: M03-L02 lesson added

- Confirmed repository access and write permission on `main`.
- Added `chapter-tool-contracts.html`: complete lesson on allowlists, exact schema validation, trusted actor authorization, approval gating, prompt injection and UNKNOWN outcomes. Includes animated five-node SVG validation trace, six selectable scenarios, runnable stdlib Python 3.11+ lab with negative tests, two exercises, senior design tradeoffs, five graded local-storage quiz questions, and per-lesson completion.
- Shared navigation (`navigation.js`) now recognizes both chapters and links both in the M03 section.
- `curriculum.json` at v0.2 tracks M03-L01 and M03-L02; dashboard includes link to lesson 02; README updated.
- Git commits: lesson `2ec77bb`, navigation `4d618c1`, curriculum `cf9b334`, README `0641c8a`, dashboard `18eeaf2`.
- Verified through GitHub connector that lesson and navigation files exist on main. GitHub Pages URL could not be independently fetched from this environment; browser verification remains pending.
- Follow-up: build M03-L03 bounded loops and deadlines; integrate per-lesson completion into the dashboard progress export/import (M03-L02 currently stores its own browser-local key `ai-handbook-m03-l02-v1`); test mobile nav and browser animation.
- Preserve root `index.html`, root flashcards and illustrated notebook.

# AI Engineering Handbook handoff

Date: 2026-10-22

Goal: prepare for mid-level and senior-level Applied AI Engineering roles.

Repository: https://github.com/lfgtb12-12/interview-prep
Target: https://lfgtb12-12.github.io/interview-prep/ai-engineering/

Deployment policy: add files under ai-engineering/ only; preserve current homepage, notebook and flashcards.

Study order: module M03 first; connect prerequisite M01/M02, evaluation M05 and durability M06. Four tracks Learn, Build, Interview, Get Hired.

Initial deliverable: interactive M03-L01 lesson, bounded-loop walkthrough, Python lab, mid/senior prompts, 5-question quiz, 6 flashcards, local progress export/import, 12-module roadmap.

Important: progress uses per-browser localStorage. Export before switching devices; import explicitly. No cloud sync. Progress completion represents self-reported study, not independently assessed mastery.

Next session: fetch curriculum.json, README.md, HANDOFF.md; inspect existing site before editing; add M03-L02 with runnable pytest exercise and answers, and build a lesson-content directory with a manifest-driven renderer. Confirm website health and links.

## Deployment verification, 2026-10-22

- GitHub connector access: repository metadata confirmed admin/push permissions.
- Published compact adaptation to `ai-engineering/index.html`, commit `155cdb64f1e44545c61bd5620286d06b38333334`.
- Original source archive `ai-engineering-handbook-v0.1.zip` in ChatGPT Library was inspected, but original `site/styles.css`, `site/content.js`, and `site/app.js` were NOT uploaded verbatim. The deployed page is a standalone adaptation; replacing it with the fully modular original archive is future work.
- The four new paths were read back successfully via GitHub connector. Root `index.html` blob remained `42c8975af2ef570a781f29400bc5d1e5af1f7395`.
- Public website could not be fetched by the web verification service in this session. Do not claim a passed browser UI test until verified in a browser.
- Test checklist: homepage renders; first lesson; five walkthrough steps; Python code; quiz explanations/score; six flashcards; local progress and export/import; small-screen layout; old homepage/notebook/flashcards still work.
- Progress JSON schema of deployed adaptation uses `done`, `answers`, `notes`; this differs from the original ZIP's proposed format. Maintain backward compatibility or add an explicit migration before changing live progress data.

## Shared navigation update — 2026-10-22

- Added `navigation.js` and `navigation.css` as shared curriculum navigation used by dashboard and expanded M03-L01 chapter.
- Both HTML pages now reference the same relative shared assets. The JS builds a collapsible module tree from `curriculum.json` (with fallback module titles), direct navigation to available lesson, quiz, flashcards and roadmap.
- Responsive drawer on narrow screens; current chapter link highlighted; completion marker reads existing `ai-handbook-progress-v1` localStorage. No progress migration or destructive changes made.
- Preserve sidebar component and lesson IDs when adding chapters. Add new lesson entries in curriculum manifest and update navigation link resolver for additional routes.
- Readback from GitHub connector must verify new asset paths and references. Live GitHub Pages browser testing remains separate; remote web access is restricted in this environment.
