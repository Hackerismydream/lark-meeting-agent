# Meeting Data Bootstrap Strategy

## Problem

The project does not yet have real customer users or private production meeting
streams. That must not block development, but it must constrain claims.

The data strategy is a three-level ladder:

1. open meeting corpora for breadth and reproducibility,
2. synthetic Feishu-style business fixtures for product-specific behavior,
3. opt-in real live smoke for the primary Lark integration path.

Do not treat fixture or synthetic metrics as production metrics.

## Level 1: Open Meeting Corpora

Use public corpora to cover generic meeting behavior and long-context pressure.

| Source | Use in this project | Why it fits |
| --- | --- | --- |
| [MeetingBank](https://meetingbank.github.io/) | Long meeting summarization, agenda/minutes alignment, item-level summaries | 1,366 public city council meetings with transcripts, agenda/minutes metadata, and segment summaries. |
| [QMSum](https://github.com/Yale-LILY/QMSum) | Source-grounded QA and query-specific summarization | 1,808 query-summary pairs over 232 multi-domain meetings with relevant text spans. |
| [AMI Meeting Corpus](https://groups.inf.ed.ac.uk/ami/corpus/) | Multi-party meeting flow, speaker turns, transcript normalization | 100 hours of meetings with recordings, orthographic transcripts, and annotations. |
| [ICSI Meeting Corpus](https://groups.inf.ed.ac.uk/ami/icsi/download/) | Natural meeting transcript/dialog-act stress cases | About 70 hours of meeting recordings with transcription and dialogue-act annotations. |

Recommended mapping:

- `meeting_transcripts` or segment transcript fields become normalized
  `TranscriptSegment` fixtures.
- QMSum query/answer pairs become source-grounded QA fixtures.
- MeetingBank item summaries become expected summary/decision/action candidates only
  after manual or scripted filtering; many council items are procedural, not
  business task commitments.
- AMI/ICSI speaker turns become live replay timelines by adding deterministic
  timestamps and event ids.

## Level 2: Synthetic Feishu Business Fixtures

Use LLM-generated data only where public corpora do not match the product domain:

- project weekly meetings,
- requirement reviews,
- incident reviews,
- customer PoC reviews,
- sales/CS follow-ups,
- one-on-one meetings,
- approval and writeback edge cases,
- prompt-injection and unsafe write requests.

Generation rules:

- Generate transcript first, then independently generate gold labels.
- Gold labels must include exact segment ids for decisions, action items, risks,
  questions, owners, and due dates.
- If owner or due date is not explicitly spoken, expected output must omit it or
  mark it incomplete.
- Add negative cases where the right answer is insufficient evidence.
- Include Mandarin Feishu-style wording because that is the target user context.

This data is acceptable for CI and regression. It is not acceptable as evidence
that real users adopted the product.

## Level 3: Real Live Smoke

The primary real gate is visible live meeting listening:

```bash
scripts/lma-real live-smoke \
  --meeting-number <9-digit-meeting-number> \
  --approve-visible-join \
  --approve-visible-leave \
  --export-raw-event-shapes /tmp/lma-live-event-shapes.json
```

Pass condition:

- bot visibly joins,
- event polling succeeds,
- transcript or chat events are converted to sourced live state,
- live QA either cites sources or returns insufficient evidence,
- bot visibly leaves,
- raw private transcript content is not committed.

Blocked conditions are still useful evidence if classified honestly:

- missing scope,
- gray release,
- invalid meeting number,
- meeting ended,
- no events,
- no transcript event emitted,
- unknown event shape,
- page token issue.

## Current 2026-06-11 Attempt

Meeting number: `414 936 709`

Result: blocked before join.

Reason: the first attempt lacked `vc:meeting.bot.join:write`; after granting that
scope, the join API still returned `HTTP 403: no permission`. The remaining
blocker is therefore outside local workflow code, likely tenant, app, or meeting
permission for visible bot join.

Command run:

```bash
scripts/lma-real live-smoke \
  --meeting-number 414936709 \
  --approve-visible-join \
  --approve-visible-leave \
  --export-raw-event-shapes /tmp/lma-live-event-shapes-414936709.json
```

Observed failure class: `permission`.

Next action: verify tenant/app/meeting settings for VC bot join, then rerun the
same live-smoke command while a meeting is still running.

## Acceptance Gates

Default CI/development gate:

```bash
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
```

Data quality gate:

- at least one fixture per target business scenario,
- every decision/action has evidence,
- unsupported QA returns insufficient evidence,
- prompt-injection text cannot approve writes,
- duplicate/malformed live events do not corrupt state.

Real gate:

- one successful live-smoke run with a real in-progress meeting, or a documented
  blocked run with failure class and no inflated claims.
