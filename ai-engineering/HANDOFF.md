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
