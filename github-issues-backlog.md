# GitHub Issues Backlog: Skeptical Student Flow V2

This file contains copy-ready issue drafts. Create issues in order unless noted.

## Issue 1
Title: Enforce structured student evaluation decisions
Labels: enhancement, workflow, quality
Priority: P0
Depends on: none

Problem
The current decision flow can rely on free-form language. This creates brittle pass or fail logic.

Scope
- Define a strict decision payload for student evaluation outputs.
- Include: status, reason_code, summary, follow_up_questions.
- Update prompts so the student always returns that payload.

Acceptance Criteria
- Level 1 and Level 2 student evaluation outputs are machine-parseable.
- status is always one of approved or rejected.
- reason_code is always present.

Test Checklist
- [ ] Unit test: valid approved payload parses.
- [ ] Unit test: valid rejected payload parses.
- [ ] Unit test: malformed payload triggers safe fallback.

---

## Issue 2
Title: Replace keyword-based rejection checks with structured parser
Labels: enhancement, reliability
Priority: P0
Depends on: Issue 1

Problem
Keyword matching for rejection can miss real failures or misclassify outputs.

Scope
- Replace keyword checks with structured status parsing.
- Keep conservative fallback behavior when parsing fails.

Acceptance Criteria
- Retry logic uses decision status only.
- No keyword matching remains in rejection gate.

Test Checklist
- [ ] Integration test: rejected status triggers retry.
- [ ] Integration test: approved status exits retry loop.
- [ ] Regression test: malformed response does not pass silently.

---

## Issue 3
Title: Add document validation gate before write and index update
Labels: enhancement, data-quality
Priority: P0
Depends on: Issue 1

Problem
Malformed docs can be written and indexed, polluting the knowledge base.

Scope
- Validate archivist output against required template sections.
- Block write and index update when validation fails.
- Return actionable error details for retry.

Acceptance Criteria
- Invalid documents are never persisted.
- Index file updates only happen after successful validation and write.

Test Checklist
- [ ] Unit test: missing required section fails validation.
- [ ] Integration test: failed validation does not update index.
- [ ] Integration test: valid document is written and indexed.

---

## Issue 4
Title: Add explicit task context chaining for research to skeptic to student
Labels: enhancement, orchestration
Priority: P1
Depends on: Issue 1

Problem
Downstream tasks may operate on loosely reconstructed context rather than explicit upstream outputs.

Scope
- Ensure skeptic receives researcher output explicitly.
- Ensure student receives skeptic output explicitly.
- Remove implicit context assumptions where possible.

Acceptance Criteria
- Skeptic and student tasks consume explicit upstream outputs.
- End-to-end flow remains deterministic under retries.

Test Checklist
- [ ] Integration test: skeptic input contains exact researcher report.
- [ ] Integration test: student input contains exact skeptic review.

---

## Issue 5
Title: Make Level 2 retry context structured and bounded
Labels: enhancement, reliability
Priority: P1
Depends on: Issue 2, Issue 4

Problem
Free-form follow-up context can grow noisy and reduce retry quality.

Scope
- Convert follow-up context into structured fields.
- Pass only bounded, relevant fields to the next retry attempt.

Acceptance Criteria
- Retry prompts include reason_code and targeted follow-up questions.
- Context size is bounded by policy.

Test Checklist
- [ ] Integration test: retry uses structured context.
- [ ] Integration test: context truncation policy is enforced.

---

## Issue 6
Title: Persist evaluation outcomes as append-only run log
Labels: enhancement, observability
Priority: P1
Depends on: Issue 2

Problem
Rejections are transient; the system does not learn from repeated failure patterns.

Scope
- Append each evaluation outcome to jsonl log.
- Include concept, attempt, status, reason_code, timestamp.

Acceptance Criteria
- Every run produces an evaluation log record.
- Records are append-only and parseable.

Test Checklist
- [ ] Unit test: log record schema is valid.
- [ ] Integration test: rejection and approval both logged.

---

## Issue 7
Title: Add pre-run failure pattern summary for student guidance
Labels: enhancement, quality
Priority: P2
Depends on: Issue 6

Problem
The orchestrator does not use historical failures to improve future prompts.

Scope
- Summarize top recurring reason codes before each run.
- Feed concise pattern hints into the student orchestration context.

Acceptance Criteria
- Summary step runs before topic selection.
- Student receives at least top 3 recurring failure reasons when present.

Test Checklist
- [ ] Integration test: empty history path behaves safely.
- [ ] Integration test: non-empty history injects summary context.

---

## Issue 8
Title: Add structured workflow telemetry (duration, retries, outcomes)
Labels: enhancement, observability
Priority: P2
Depends on: none

Problem
Print logs do not provide actionable metrics for performance and quality tuning.

Scope
- Add jsonl telemetry for stage start and end.
- Record durations, retry count, final outcome.

Acceptance Criteria
- A telemetry record exists for each major stage.
- Retry count and final status are queryable from logs.

Test Checklist
- [ ] Unit test: telemetry records follow schema.
- [ ] Integration test: end-to-end run emits stage records.

---

## Issue 9
Title: Convert verification protocol to scored acceptance checklist
Labels: enhancement, science-rigor
Priority: P1
Depends on: Issue 1

Problem
Verification criteria are prose-only and can be applied inconsistently.

Scope
- Add checklist with explicit criterion pass flags.
- Add numeric score and pass threshold.
- Require theoretical flag when empirical evidence is absent.

Acceptance Criteria
- Skeptic output includes criterion flags and score.
- Student blocks approval below threshold.

Test Checklist
- [ ] Unit test: score parser handles expected formats.
- [ ] Integration test: below-threshold concepts are rejected.

---

## Issue 10
Title: Enforce prerequisite-aware topic selection for Level 2
Labels: enhancement, curriculum
Priority: P2
Depends on: Issue 3

Problem
Advanced topics can be selected before foundation concepts are covered.

Scope
- Define prerequisite map for advanced topics.
- Block Level 2 selection when prerequisites are missing.

Acceptance Criteria
- Topic selector does not choose blocked Level 2 concepts.
- Fallback topic selection remains deterministic.

Test Checklist
- [ ] Unit test: missing prerequisite blocks topic.
- [ ] Integration test: satisfied prerequisite allows topic.

---

## Issue 11
Title: Add checkpoint and resume support for long workflows
Labels: enhancement, resilience
Priority: P3
Depends on: Issue 4

Problem
Interrupted runs restart from scratch and waste tokens and time.

Scope
- Save checkpoint at stage boundaries.
- Resume from last completed stage for a concept run.

Acceptance Criteria
- Interrupted run resumes without re-running completed stages.
- Checkpoint corruption is handled safely.

Test Checklist
- [ ] Integration test: simulate interruption and resume.
- [ ] Integration test: corrupted checkpoint triggers safe recovery.

---

## Issue 12
Title: Harden image generation with ordered model fallback policy
Labels: enhancement, resilience
Priority: P3
Depends on: none

Problem
Single-model dependency increases failure rate in visual generation.

Scope
- Use ordered fallback model list from config.
- Record failure reason per model attempt.

Acceptance Criteria
- On first model failure, fallback attempts next model.
- Tool output clearly indicates final model used or full failure reason.

Test Checklist
- [ ] Integration test: first model fails, second succeeds.
- [ ] Integration test: all models fail and error is actionable.

---

## Suggested Milestones

Milestone A (Critical Path)
- Issue 1
- Issue 2
- Issue 3

Milestone B (Flow Quality)
- Issue 4
- Issue 5
- Issue 9

Milestone C (Learning and Ops)
- Issue 6
- Issue 7
- Issue 8
- Issue 10
- Issue 11
- Issue 12
