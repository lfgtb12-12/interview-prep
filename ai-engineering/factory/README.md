# AI Textbook Factory — Phase 1

This directory prototypes an **additive** lesson pipeline. Existing four expanded lessons and the deployed site are not modified by Phase 1. **A generated lesson is a draft until editorial review.**

## Workflow

1. Write a JSON lesson specification conforming to `lesson.schema.json`, using `examples/M03-L05.json` as a starting point.
2. Validate it with `python ai-engineering/factory/validate.py ai-engineering/factory/examples/M03-L05.json`.
3. Render to an untracked staging folder with `python ai-engineering/factory/render.py ai-engineering/factory/examples/M03-L05.json --out /tmp/ai-textbook-preview`.
4. Open the staged HTML in a browser; check accessible interactions, mobile layout and link behavior. For local development, use a static server if fetch or imports are involved.
5. Propose content as a **draft PR** with a checklist and link to a preview. Factory-owned, non-draft PRs can be merged automatically after both CI suites pass, but only if every changed file is on the automation allowlist. Workflow changes, root content, and modifications to existing chapter HTML always require a separate manual merge. Never overwrite a published lesson automatically.

## Spec contract

Required: `id`, `module`, `title`, `summary`, `objectives`, `sections`, `quiz`, `interview`, `lab`. Each section has an `id`, `title`, `paragraphs`, and optional `diagram`. `diagram` supports `state-machine` and `sequence` using named nodes and edges (renderer currently supports node-transition simulations). Content is plain text, never raw HTML. Quiz questions must have four options, an answer index, and a non-empty explanation. IDs must be stable.

The renderer is intentionally dependency-free (Python 3.11+), writes only to a user-supplied staging directory, HTML-escapes text and uses stable quiz progress keys. It **does not** modify `curriculum.json`, `navigation.js`, the dashboard, or root files. Registration is a separate review step.

## Exit criteria for Phase 1

- Verify JSON rejects invalid structure and duplicate identifiers.
- Generate an accessible preview with a diagram and quiz.
- Run offline unit tests and manually verify a browser.
- Keep working lesson files unchanged.
- Confirm both CI checks pass. Eligible non-draft factory PRs can merge automatically; draft and out-of-scope PRs remain manual.

## Planned later phases

2. Replace hardcoded navigation routes with curriculum-driven paths and add regression tests for old progress keys.
3. Build an approved shared component library and design-system layer. Migrate one existing lesson only after visual baseline comparisons.
4. Generate 2–3 lesson specs per batch; lint factual claims, run link/lab/HTML and browser tests, create one draft PR per batch, and review accuracy, senior interview depth, accessibility and exercises.
5. Automate CI checks and batch PR creation with least-privilege GitHub Actions permissions; grant merge access only to the restricted privileged automation that never checks out PR code.

## Reusable components (Phase 3)

The renderer embeds `components.py`'s SVG state/sequence trace component into each staged HTML preview. Controls support Next, Previous and Reset; the active edge, destination node, step list and progress meter update in sync. Reduced-motion preferences disable animation. SVG labels are assigned with `textContent` rather than interpolated HTML. The factory quiz and browser-local completion format are unchanged.

Generated SVG traces are **instructional edge walkthroughs**, not an execution engine or automatic graph layout. A later batch can add fan-out timelines, retry simulations and interactive parameterized exercises, each with separate validation and browser tests. Existing published lessons are deliberately not converted.
