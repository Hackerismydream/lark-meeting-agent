"""Repository interfaces and SQLite storage for production meeting bot state."""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator
from typing import Protocol

from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.schemas import EntityMemory, Run, ToolCallAuditEvent, WriteOperation

SCHEMA_VERSION = 1


class RunRepository(Protocol):
    def save_run(self, run: Run) -> None: ...

    def load_run(self, run_id: str) -> Run: ...


class WriteOperationRepository(Protocol):
    def list_write_operations(self, run_id: str) -> list[WriteOperation]: ...


class AuditRepository(Protocol):
    def save_audit_events(self, events: list[ToolCallAuditEvent]) -> None: ...


class MeetingRepository(RunRepository, WriteOperationRepository, AuditRepository, Protocol):
    pass


class MemoryRepository(Protocol):
    pass


class JsonlMeetingRepository:
    """Adapter over the existing JSONL memory store for local/dev use."""

    def __init__(self, workspace: Path | str) -> None:
        self.store = MeetingMemoryStore(workspace)

    def save_run(self, run: Run) -> None:
        self.store.persist_run(run)
        self.store.save_run_snapshot(run)

    def load_run(self, run_id: str) -> Run:
        return self.store.load_run_snapshot(run_id)

    def list_write_operations(self, run_id: str) -> list[WriteOperation]:
        run = self.load_run(run_id)
        return run.write_plan.operations if run.write_plan else []

    def save_audit_events(self, events: list[ToolCallAuditEvent]) -> None:
        self.store.persist_audit(events)


class SQLiteMeetingRepository:
    """SQLite production-MVP storage backend.

    Rows keep typed JSON snapshots as the source of truth while exposing
    normalized keys for query and operational inspection.
    """

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_schema()

    @contextmanager
    def approval_guard(self, run_id: str) -> Iterator[None]:
        del run_id
        with self._lock:
            yield

    def save_run(self, run: Run) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs(run_id, status, provider_mode, analyzer_mode, payload_json, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                  status=excluded.status,
                  provider_mode=excluded.provider_mode,
                  analyzer_mode=excluded.analyzer_mode,
                  payload_json=excluded.payload_json,
                  updated_at=excluded.updated_at
                """,
                (
                    run.run_id,
                    str(run.status.value if hasattr(run.status, "value") else run.status),
                    str(run.provider_mode.value if hasattr(run.provider_mode, "value") else run.provider_mode),
                    str(run.analyzer_mode.value if hasattr(run.analyzer_mode, "value") else run.analyzer_mode),
                    run.model_dump_json(),
                    run.created_at,
                    run.updated_at,
                ),
            )
            if run.meeting:
                conn.execute(
                    """
                    INSERT INTO meetings(meeting_id, title, payload_json)
                    VALUES(?, ?, ?)
                    ON CONFLICT(meeting_id) DO UPDATE SET title=excluded.title, payload_json=excluded.payload_json
                    """,
                    (run.meeting.meeting_id, run.meeting.title, run.meeting.model_dump_json()),
                )
            for segment in run.transcript_segments:
                conn.execute(
                    """
                    INSERT INTO transcript_segments(meeting_id, segment_id, payload_json)
                    VALUES(?, ?, ?)
                    ON CONFLICT(meeting_id, segment_id) DO UPDATE SET payload_json=excluded.payload_json
                    """,
                    (segment.meeting_id, segment.segment_id, segment.model_dump_json()),
                )
            if run.minutes:
                conn.execute(
                    """
                    INSERT INTO minutes(run_id, meeting_id, payload_json)
                    VALUES(?, ?, ?)
                    ON CONFLICT(run_id) DO UPDATE SET meeting_id=excluded.meeting_id, payload_json=excluded.payload_json
                    """,
                    (run.run_id, run.minutes.meeting_id, run.minutes.model_dump_json()),
                )
                for decision in run.minutes.decisions:
                    conn.execute(
                        """
                        INSERT INTO decisions(run_id, decision_id, payload_json)
                        VALUES(?, ?, ?)
                        ON CONFLICT(run_id, decision_id) DO UPDATE SET payload_json=excluded.payload_json
                        """,
                        (run.run_id, decision.decision_id, decision.model_dump_json()),
                    )
                for action in run.minutes.action_items:
                    conn.execute(
                        """
                        INSERT INTO action_items(run_id, action_id, status, payload_json)
                        VALUES(?, ?, ?, ?)
                        ON CONFLICT(run_id, action_id) DO UPDATE SET status=excluded.status, payload_json=excluded.payload_json
                        """,
                        (run.run_id, action.action_id, action.status, action.model_dump_json()),
                    )
                for risk in run.minutes.risks:
                    conn.execute(
                        """
                        INSERT INTO risks(run_id, risk_id, payload_json)
                        VALUES(?, ?, ?)
                        ON CONFLICT(run_id, risk_id) DO UPDATE SET payload_json=excluded.payload_json
                        """,
                        (run.run_id, risk.risk_id, risk.model_dump_json()),
                    )
                for question in run.minutes.open_questions:
                    conn.execute(
                        """
                        INSERT INTO open_questions(run_id, question_id, payload_json)
                        VALUES(?, ?, ?)
                        ON CONFLICT(run_id, question_id) DO UPDATE SET payload_json=excluded.payload_json
                        """,
                        (run.run_id, question.question_id, question.model_dump_json()),
                    )
            if run.write_plan:
                for operation in run.write_plan.operations:
                    conn.execute(
                        """
                        INSERT INTO write_operations(run_id, operation_id, operation_type, execution_status, approval_status, idempotency_key, payload_json)
                        VALUES(?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(run_id, operation_id) DO UPDATE SET
                          execution_status=excluded.execution_status,
                          approval_status=excluded.approval_status,
                          idempotency_key=excluded.idempotency_key,
                          payload_json=excluded.payload_json
                        """,
                        (
                            run.run_id,
                            operation.operation_id,
                            operation.operation_type.value,
                            operation.execution_status.value,
                            operation.approval_status.value,
                            operation.idempotency_key,
                            operation.model_dump_json(),
                        ),
                    )

    def load_run(self, run_id: str) -> Run:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT payload_json FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if not row:
            raise KeyError(f"run not found: {run_id}")
        return Run.model_validate(json.loads(row["payload_json"]))

    def list_write_operations(self, run_id: str) -> list[WriteOperation]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT payload_json FROM write_operations WHERE run_id = ? ORDER BY operation_id",
                (run_id,),
            ).fetchall()
        return [WriteOperation.model_validate(json.loads(row["payload_json"])) for row in rows]

    def save_audit_events(self, events: list[ToolCallAuditEvent]) -> None:
        with self._lock, self._connect() as conn:
            for event in events:
                conn.execute(
                    """
                    INSERT INTO audit_events(audit_id, operation_name, payload_json)
                    VALUES(?, ?, ?)
                    ON CONFLICT(audit_id) DO UPDATE SET payload_json=excluded.payload_json
                    """,
                    (event.audit_id, event.operation_name, event.model_dump_json()),
                )

    def save_entity_memory(self, memory: EntityMemory) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO entity_memories(entity_type, entity_id, payload_json)
                VALUES(?, ?, ?)
                ON CONFLICT(entity_type, entity_id) DO UPDATE SET payload_json=excluded.payload_json
                """,
                (memory.entity_type.value, memory.entity_id, memory.model_dump_json()),
            )

    def schema_version(self) -> int:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT value FROM schema_meta WHERE key = 'schema_version'").fetchone()
        return int(row["value"]) if row else 0

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    provider_mode TEXT NOT NULL,
                    analyzer_mode TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS meetings (
                    meeting_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS transcript_segments (
                    meeting_id TEXT NOT NULL,
                    segment_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(meeting_id, segment_id)
                );
                CREATE TABLE IF NOT EXISTS minutes (
                    run_id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS decisions (
                    run_id TEXT NOT NULL,
                    decision_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(run_id, decision_id)
                );
                CREATE TABLE IF NOT EXISTS action_items (
                    run_id TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(run_id, action_id)
                );
                CREATE TABLE IF NOT EXISTS risks (
                    run_id TEXT NOT NULL,
                    risk_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(run_id, risk_id)
                );
                CREATE TABLE IF NOT EXISTS open_questions (
                    run_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(run_id, question_id)
                );
                CREATE TABLE IF NOT EXISTS write_operations (
                    run_id TEXT NOT NULL,
                    operation_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    execution_status TEXT NOT NULL,
                    approval_status TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(run_id, operation_id)
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    audit_id TEXT PRIMARY KEY,
                    operation_name TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS entity_memories (
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(entity_type, entity_id)
                );
                CREATE TABLE IF NOT EXISTS schema_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                INSERT INTO schema_meta(key, value)
                VALUES('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (str(SCHEMA_VERSION),),
            )
