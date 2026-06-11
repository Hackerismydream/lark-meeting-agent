# V1 Resume and Interview Notes

Truthful positioning:

Lark Meeting Agent is a Feishu/Lark meeting lifecycle agent with deterministic workflow orchestration, controlled tool calling, evidence-grounded extraction, approval-gated writeback, local/SQLite run state, and source-grounded QA. It is fixture-tested and fake-provider-tested; production deployment is not claimed.

Resume-safe bullets:

1. Designed a meeting lifecycle agent covering pre-brief, live event listening, post-meeting minutes, write-plan approval, memory, and QA across 4 workflow stages.
2. Implemented `LarkToolAdapter` as the only Lark boundary with allowlisted operations, dry-run previews, approval checks, audit events, and secret redaction.
3. Built evidence-grounded meeting extraction where decisions/action items require source references and unsupported QA returns insufficient evidence.
4. Added SQLite run recovery so status/approve/reject can resume after restart; duplicate approvals do not duplicate completed writes.
5. Built deterministic regression coverage: 31 lifecycle cases and 8 live scenarios; live replay action precision 93.75%, recall 100%, evidence coverage 100%, QA source accuracy 100%.
6. Added security and governance checks for admin config, separated permissions, prompt injection, direct tool bypass, and redaction.

Avoid saying:

- deployed in production,
- custom audio transcription exists,
- native macOS app exists,
- real Feishu channel was verified,
- real live meeting smoke succeeded,
- real LLM benchmark passed.

Interview framing:

The core technical choice is deterministic workflow plus controlled adapter instead of free-form autonomous tool calling. This is deliberate because enterprise collaboration writes need reviewability, idempotency, audit, and explicit approval.
