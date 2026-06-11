# Processed Meeting Fixtures

Processed fixtures are canonical `MeetingFixture` JSON files generated from public datasets.

Expected directories:

```text
data/processed/meeting_fixtures/meetingbank/tiny10/
data/processed/meeting_fixtures/qmsum/tiny10/
data/processed/meeting_fixtures/vcsum/tiny10/
```

Generate them with:

```bash
uv run python scripts/data/prepare_meetingbank.py
uv run python scripts/data/prepare_qmsum.py
uv run python scripts/data/prepare_vcsum.py
```
