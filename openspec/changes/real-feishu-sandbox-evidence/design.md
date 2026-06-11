# Design: Real Feishu Sandbox Evidence

## Scenarios

1. `scenario_01_prebrief`: real Feishu calendar agenda read, sanitized local calendar evidence, public fixture context, prebrief artifact.
2. `scenario_02_postmeeting_writeback`: public transcript fixture, post-meeting workflow, dry-run WritePlan, optional sandbox approval.
3. `scenario_03_qa`: public fixture memory seed, source-grounded QA rows, optional sandbox chat message.

## Safety Gates

- `LMA_DEMO_ENABLE_REAL_WRITES` defaults to `0`.
- Real writes require `LMA_DEMO_ENABLE_REAL_WRITES=1` plus `--approve`.
- Missing `LMA_DEMO_CHAT_ID` marks IM operations as `missing_target`.
- Evidence packs are sanitized before writing Lark outputs.
- Raw private Lark JSON, tokens, cookies, secrets, and screenshots are not committed.

## Boundary

This stage proves sandbox product-chain integration. It does not prove live meeting listening; live meeting join/listen remains a separate smoke boundary.
