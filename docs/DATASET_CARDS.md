# Dataset Cards

## MeetingBank

- Source: https://meetingbank.github.io/
- Raw download: Zenodo MeetingBank.zip
- Contents: 1,366 public city-council meetings with transcripts, agendas, minutes, metadata, and long meeting videos.
- Project use: long meeting handling, agenda/minutes alignment, segment-level and full-meeting summarization fixtures.
- Not used for: production Feishu metrics.

## QMSum

- Source: https://github.com/Yale-LILY/QMSum
- Contents: 232 meetings and 1,808 query-summary pairs.
- Project use: source-grounded QA, query-focused summarization, locate-then-answer evaluation.
- Not used for: action item production precision claims.

## VCSum

- Source: https://github.com/hahahawu/VCSum
- Contents: 239 real Chinese meetings with topic segmentation, headlines, segment summaries, overall summaries, and salient sentences.
- Project use: Chinese meeting summarization, topic segmentation, salient evidence extraction.
- Not used for: real Feishu tenant performance claims.

## Governance

- Raw datasets stay under `data/raw/` and are not committed.
- Processed tiny fixtures are reproducible from documented commands.
- Public corpus metrics must be labeled as development/evaluation metrics.
