## Current continuation — 2026-10-23: M05-L06

- L05 PR #29 merged to main at `81a0530`; GitHub Pages workflow succeeded for that commit. Separate live-browser verification was not run in this session.
- Feature branch `m05-l06-ci-gates-monitoring` adds `chapter-m05-l06.html`, `m05_ci_gates_lab.py`, `test_m05_ci_gates_lab.py`, and `test_m05_l06_browser.py`; curriculum v0.19.
- Main fixture has six common and four rare support tasks, paired reference/candidate labels, explicit missing-observation coverage, slice floors, paired losses, independent safety and trace gates, and latency/cost budgets. Interactive simulator calculates gate decisions; eight explained quizzes and mid/senior spoken answers.
- Teaching fixtures are not production confidence bounds or safety guarantees. CI must be verified at the final feature head, merged only if sound, then Pages deployment and live browser tests verified separately. L07 capstone remains afterward.

## Current continuation — 2026-10-23: M05-L05 (feature branch)

- Feature branch `m05-l05-agent-tool-evals` from verified `main` at `3ad9f0a`. Root and Factory AGENTS.md were not present.
- Added `chapter-m05-l05.html`, `m05_agent_tool_eval_lab.py`, 16 deterministic tests in `test_m05_agent_tool_eval_lab.py`, and five Playwright tests in `test_m05_l05_browser.py`. Curriculum v0.18 registers L05.
- Twelve authored scenarios cover alternate safe trajectories, tool/argument/authorization gates, ambiguous side effects, blind retry, repeat invocation, escalation and adversarial attempts. The fixture explicitly does not assert actual duplicate external writes based only on calls.
- Interactive UI reports task outcome and mandatory gate results separately, offers exact-trace grading as an intentionally brittle comparison, and provides eight explained quiz items plus conversational mid/senior answers.
- Pending verification: run offline + browser tests, check final PR-head CI, merge, verify GitHub Pages deployment and live browser behavior. None of those are implied by branch commits. After L05, build M05-L06 and L07.

## Current continuation — 2026-10-23: M05-L04

- M05-L02 and L03 were merged, CI/Pages passed, all 13 live browser tests passed, and the user confirmed both pages.
- M05-L04 adds `chapter-m05-l04.html`, `m05_experiment_lab.py`, 20 deterministic lab tests and seven browser tests. Curriculum v0.17 registers the lesson.
- Content distinguishes paired offline evaluations from online randomization, assignment/analysis units and clustering, absolute versus relative lift, normal-approximation intervals and practical margins, MDE/power, stopping and multiplicity, allocation integrity and rare-risk bounds.
- Interactive experiment fixture compares independent-user intervals with invalid copied-row intervals; changing copies cannot change the valid result. Sample size, scenario, preselected confidence, margin, SRM and opportunistic-stopping controls change calculated results and the decision. A separate MDE control computes a simplified planning size.
- Method limits are explicit: no clustered/sequential/multiple-comparison inference, no universal normal-interval guarantee, no zero-risk inference from zero events, and planning against zero differs from requiring an interval above a practical margin. All scenarios are authored fixtures.
- Seven browser tests include Python/JS agreement over 240 experiment configurations, guardrail/integrity precedence, plot and policy behavior, MDE/risk arithmetic, eight explained quizzes, saved progress and mobile navigation. Existing workflow discovery runs L04 without workflow edits.
- Next: verify the L04 PR, CI and Pages state and run live browser checks before claiming publication. Then build M05-L05 — Agent & Tool-Use Evals, following `M05-OUTLINE.md`. Inspect the current repo and tests first; prioritize semantic quality, meaningful interactions and natural interview answers. L06 and L07 remain after L05.

## Current continuation — 2026-10-23: M05-L03

- M05-L02 merged via PR #26 (`55cdbbac9d6b12529542626ba60e8f93d7e4dae6`); both final-head CI checks and Pages deployment succeeded. All seven L02 browser tests passed against the public site, including 192 calculation configurations, quizzes, persistence, navigation and mobile layout.
- M05-L03 adds `chapter-m05-l03.html`, `m05_judge_calibration_lab.py`, 13 deterministic lab tests and six browser tests. Curriculum v0.16 registers it. Topics: explicit mandatory rubrics, independent human adjudication, confusion counts and automation coverage, calibration versus probability, output validation, bias perturbations, review routing and judge drift.
- Interactive judge calibration uses twelve authored cases and two hypothetical rating profiles. Threshold/review changes recalculate actual counts. A separate order-swap widget distinguishes identity-mapped consistency from agreement with humans. No live judge service is called and no rating is claimed to be a calibrated probability.
- Browser tests compare Python and JavaScript across 40 policy configurations, exercise controls and pairwise reversal, check eight explained quizzes and saved progress, and verify mobile curriculum navigation. The existing Factory test discovery includes L03 without another workflow change.
- Next: check L03 PR/CI/Pages state and run its live browser tests before claiming publication. Then build M05-L04 — Experiment Design, A/B Tests & Statistical Reasoning, using `M05-OUTLINE.md`. Inspect the repository/tests first. Maintain natural interview answers, meaningful calculations, standalone Python labs and deterministic tests.

## Current continuation — 2026-10-23: M05-L02

- M04 has seven registered lessons; M05-L01 was verified on live GitHub Pages in Chromium (threshold calculations, eight quizzes, sidebar navigation and completion persistence).
- M05-L02: `chapter-m05-l02.html`; curriculum v0.15. Covers recall@k, RR/MRR, exponential-gain nDCG, final-context recall, passage relevance, faithfulness, link-based citation precision, citation coverage, required-fact completeness and correct/false abstention.
- Interactive fixture separates ranking/cutoff, dropped context, answer content, citation attribution and corpus answerability. Undefined denominators display N/A. Semantic support labels are reviewed fixtures, not automated truth detection; joint-evidence entailment is an explicit extension exercise.
- Lab: `m05_rag_evaluation_lab.py`; 22 deterministic unit tests. `test_m05_l02_browser.py` has seven browser tests, including Python/JS agreement over 192 configurations, eight explained quizzes, persistence, old-key preservation, navigation and mobile layout. Set `M05_SITE_URL` to the public ai-engineering URL to run against deployment.
- Factory workflow now discovers M05 lab/browser tests, ensuring L02 is exercised in CI. Existing lesson files, navigation and storage keys are preserved.
- Next: verify the L02 PR merge and Pages deployment from GitHub Actions and run live browser tests; then build M05-L03 using `M05-OUTLINE.md`. Inspect current repository/tests first. Prioritize plain-English teaching, calibrated judge rubrics and human adjudication; no unrelated Factory refactoring.

## Milestone 2026-10-22: M03-L04 orchestration and state

- Added `chapter-orchestration.html`: dependency DAG animation, sequential/parallel timeline, read failure, checkpoint/recovery and ambiguous publication scenarios; exercises, architecture discussion, five saved quiz items.
- Added `orchestration_lab.py` and `test_orchestration.py`, standard-library offline executor and deterministic unit tests. In-memory state is not crash-durable and cannot guarantee atomic cross-service writes; code is educational.
- Registered lesson 04 in curriculum manifest and shared sidebar; preserved existing storage keys, and extended dashboard progress backup for `lessons.M03-L04`.
- Public GitHub Pages browser animations and actual CLI test execution require independent verification; do not equate GitHub readback with browser tests.
- Follow-up: validate all unit tests, import atomicity for invalid backup payloads, mobile drawer, and actual UI interaction; build M03-L05 next.

## Milestone 2026-10-22: M03-L03 bounded loops and recovery

- Added `chapter-bounded-loops.html` with five animated scenarios, visual time/step/cost budgets, typed retry decisions, standard-library Python controller and three illustrative tests, mid-level exercises, senior-scale architecture prompts and five locally saved quiz questions.
- Registered M03-L03 in `curriculum.json` version 0.3, added a sidebar link, extended dashboard chapter links and included M03-L03 in local progress export/import without changing earlier keys.
- New lesson commit `f0ef1b87064f65664cc068b1f41a6a3f2a388da6`; manifest `f0dac9896527870a4ff1e7297cb76f7c5804ff61`; navigation `f8a56702d1d195ac14bd0367c6e75054af6f4f9c`; dashboard `7e8425081b20b410d63541396d87c2ec6e9d18ce`.
- Scope: deterministic educational simulator, not a production provider integration. JavaScript animations and local-storage transfer still require live browser/manual verification; verify Python example execution separately.
- Root interview-prep homepage and existing lesson files unchanged.

## Follow-up 2026-10-22: Chapter 2 progress backup integration

- Inspected `chapter-tool-contracts.html`, curriculum, shared sidebar, dashboard, README and prior handoff. M03-L02 already existed on `main` (file SHA `fe3d7146b313ae2b5708a9d869f879a3caa57c78`); no duplicate chapter created.
- Updated dashboard export to include M03-L02 completion and quiz answers in `lessons.M03-L02`. Import accepts both old backups (without `lessons`, preserving existing Chapter 2 state) and new backups. No localStorage key was renamed.
- Commit for dashboard integration: `175653d5c7cf4f85b26d1fd492f4789dfcd85055`.
- Browser interaction tests remain unverified until independently tested. Next step: consider manifest-driven navigation and a runnable external test harness.

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
