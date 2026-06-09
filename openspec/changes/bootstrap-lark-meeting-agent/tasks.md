# Tasks: Bootstrap Lark Meeting Agent

## 1. Repository Context

- [ ] 1.1 Create `AGENTS.md` with project development rules.
- [ ] 1.2 Create `docs/PROJECT_BRIEF.md` with product positioning, MVP scope, architecture, and roadmap.
- [ ] 1.3 Ensure README references OpenSpec workflow and development commands.

## 2. OpenSpec Baseline

- [ ] 2.1 Create product delta spec.
- [ ] 2.2 Create lark-tools delta spec.
- [ ] 2.3 Create meeting-intelligence delta spec.
- [ ] 2.4 Create workflows delta spec.
- [ ] 2.5 Create memory delta spec.
- [ ] 2.6 Create safety delta spec.
- [ ] 2.7 Create API delta spec.
- [ ] 2.8 Create evaluation delta spec.
- [ ] 2.9 Run OpenSpec validation for the change.

## 3. Python Project Bootstrap

- [ ] 3.1 Create Python project structure under `app/`.
- [ ] 3.2 Configure `pyproject.toml`.
- [ ] 3.3 Add FastAPI dependency.
- [ ] 3.4 Add Pydantic v2 dependency.
- [ ] 3.5 Add pytest, ruff, and mypy.
- [ ] 3.6 Create `app/main.py`.
- [ ] 3.7 Implement `GET /health`.

## 4. Core Schemas

- [ ] 4.1 Add `Meeting` schema.
- [ ] 4.2 Add `TranscriptSegment` schema.
- [ ] 4.3 Add `EvidenceRef` schema.
- [ ] 4.4 Add `MeetingMinutes` schema.
- [ ] 4.5 Add `Decision` schema.
- [ ] 4.6 Add `ActionItem` schema.
- [ ] 4.7 Add `Risk` schema.
- [ ] 4.8 Add `OpenQuestion` schema.
- [ ] 4.9 Add `WritePlan` schema.
- [ ] 4.10 Add `WriteOperation` schema.
- [ ] 4.11 Add `Run` schema.

## 5. Core Infrastructure

- [ ] 5.1 Add configuration loader.
- [ ] 5.2 Add structured logging.
- [ ] 5.3 Add base error classes.
- [ ] 5.4 Add test fixtures directory.
- [ ] 5.5 Add sample transcript fixture.
- [ ] 5.6 Add fake Lark output fixture placeholders.

## 6. Tests

- [ ] 6.1 Add `/health` test.
- [ ] 6.2 Add schema validation tests.
- [ ] 6.3 Add evidence-required validation tests.
- [ ] 6.4 Add write operation approval schema tests.
- [ ] 6.5 Ensure tests run without real Lark credentials.

## 7. Validation

- [ ] 7.1 Run `ruff check .`.
- [ ] 7.2 Run `mypy app`.
- [ ] 7.3 Run `pytest`.
- [ ] 7.4 Document any bootstrap limitations.
