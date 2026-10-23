# M05 — Evaluation & Experimentation

Recurring case study: a production internal support assistant that answers runbook questions, uses RAG and occasionally calls tools. Evaluation separates *did we retrieve the right evidence?*, *did we answer correctly and safely?*, and *did the system meet operational targets?* Each chapter uses judged examples, realistic failure cases, conversational interview answers, and a runnable Python exercise.

| ID | Lesson | Practical result |
|---|---|---|
| M05-L01 | Evaluation Foundations: Datasets, Metrics & Failure Taxonomy | Build a labeled holdout and compare selective answer thresholds, coverage and risk |
| M05-L02 | Retrieval and Grounded-Answer Evaluation | Compute recall@k, MRR, nDCG, claim support and correct abstention |
| M05-L03 | LLM-as-Judge, Rubrics & Human Calibration | Design judge prompts, detect position bias, calibrate against adjudicated labels |
| M05-L04 | Experiment Design, A/B Tests & Statistical Reasoning | Define hypotheses, randomization units, confidence intervals and guardrails |
| M05-L05 | Agent & Tool-Use Evals | Test tool selection, argument validity, recovery paths, side effects and security |
| M05-L06 | CI Evaluation Gates, Regression & Production Monitoring | Build repeatable golden sets, slice gates, traces, cost and latency budgets |
| M05-L07 | Evaluation System Design Capstone | Design an evidence-based launch decision with offline, shadow and online phases |

## Editorial & correctness contract

Plain English first. Treat model/evaluator scores as uncalibrated unless calibrated. Explicitly define positive labels, denominators, abstentions, and unit of analysis; never conflate accuracy on answered items with overall quality. Handle empty denominators, stratified coverage, contamination, nonrepresentative samples, uncertainty and segment regressions. Never use illustrative toy numbers as empirical guarantees. Distinguish deterministic gates (ACL/JSON/schema) from semantic judgments, and offline from production safety. Each new lesson contains a meaningful interactive scenario, runnable dependency-free Python, deterministic tests, at least six explained quiz questions, and conversational spoken mid/senior answers. Preserve historical localStorage keys and navigation.
