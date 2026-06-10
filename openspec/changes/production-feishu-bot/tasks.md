## 1. Documentation-first OpenSpec

- [x] 1.1 Create `production-feishu-bot` change.
- [x] 1.2 Add proposal, design, task list, and specs for bot, security, storage, provider, approval, and deployment.
- [x] 1.3 Validate `openspec validate production-feishu-bot`.
- [x] 1.4 Commit documentation/spec artifacts.

## 2. Production Documentation

- [x] 2.1 Add `docs/PRODUCTION_FEISHU_BOT_DEPLOYMENT.md`.
- [x] 2.2 Add `docs/PRODUCTION_SECURITY_CHECKLIST.md`.
- [x] 2.3 Add `docs/PRODUCTION_RUNBOOK.md`.
- [x] 2.4 Add `docs/PRODUCTION_ENV.example.md`.
- [x] 2.5 Add `docs/REAL_TRANSCRIPT_GATE.md`.
- [x] 2.6 Add `docs/OAPI_PROVIDER_PLAN.md`.

## 3. Later Implementation Scope

- [ ] 3.1 Implement deterministic `/meeting` command parser.
- [ ] 3.2 Implement access policy and approver policy.
- [ ] 3.3 Implement approval prompt/reject protocol.
- [ ] 3.4 Add repository interfaces and SQLite backend.
- [ ] 3.5 Add production config validation.
- [ ] 3.6 Add fake tests and opt-in real smoke tests.

## 4. Explicit Non-goals

- [x] 4.1 Do not implement custom ASR in this change.
- [x] 4.2 Do not implement automatic meeting bot join in this change.
- [x] 4.3 Do not implement macOS app runtime in this change.
- [x] 4.4 Do not claim real production deployment without a real Feishu app smoke test.
