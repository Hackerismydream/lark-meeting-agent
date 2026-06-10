from __future__ import annotations

import sqlite3
from pathlib import Path

from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.repository import JsonlMeetingRepository, SQLiteMeetingRepository
from nanobot.meeting.workflow import PostMeetingWorkflow

FIXTURE = Path("tests/fixtures/meeting/transcripts/sample_project_sync.txt")


def test_sqlite_repository_creates_required_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "meeting.db"
    SQLiteMeetingRepository(db_path)

    with sqlite3.connect(db_path) as conn:
        table_names = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }

    assert {
        "runs",
        "meetings",
        "transcript_segments",
        "minutes",
        "decisions",
        "action_items",
        "risks",
        "open_questions",
        "write_operations",
        "audit_events",
        "entity_memories",
    }.issubset(table_names)


def test_sqlite_repository_round_trips_run_and_write_operations(tmp_path: Path) -> None:
    result = PostMeetingWorkflow(tmp_path, provider_mode="fake", analyzer_mode="fake").process_transcript_file(
        FIXTURE,
        create_doc=True,
        create_tasks=True,
        dry_run=True,
    )
    run = MeetingMemoryStore(tmp_path).load_run_snapshot(result.run_id)
    repository = SQLiteMeetingRepository(tmp_path / "meeting.db")

    repository.save_run(run)

    loaded = repository.load_run(result.run_id)
    operations = repository.list_write_operations(result.run_id)
    assert loaded.run_id == result.run_id
    assert loaded.meeting is not None
    assert loaded.minutes is not None
    assert len(operations) == len(result.write_plan.operations)
    assert all(operation.idempotency_key for operation in operations)


def test_jsonl_repository_preserves_local_dev_backend(tmp_path: Path) -> None:
    result = PostMeetingWorkflow(tmp_path, provider_mode="fake", analyzer_mode="fake").process_transcript_file(
        FIXTURE,
        create_doc=True,
        create_tasks=False,
        dry_run=True,
    )
    run = MeetingMemoryStore(tmp_path).load_run_snapshot(result.run_id)
    repository = JsonlMeetingRepository(tmp_path)

    repository.save_run(run)

    assert repository.load_run(result.run_id).run_id == result.run_id
    assert repository.list_write_operations(result.run_id)
