from __future__ import annotations

import pytest
from pydantic import ValidationError

from nanobot.meeting.schemas import (
    ActionItem,
    ApprovalStatus,
    Decision,
    EvidenceRef,
    ExecutionStatus,
    OperationType,
    WriteOperation,
)


def evidence_ref(segment_id: str = "seg-0001") -> EvidenceRef:
    return EvidenceRef(
        evidence_id="ev-1",
        meeting_id="meeting-1",
        segment_id=segment_id,
        speaker_name="张三",
        timestamp="00:01:00",
        quote="本周先灰度上线",
    )


def test_decision_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        Decision(decision_id="dec-1", text="本周先灰度上线", evidence_refs=[])


def test_action_item_allows_unknown_owner_and_due_date_when_evidence_exists() -> None:
    item = ActionItem(
        action_id="act-1",
        task="补充接口文档",
        owner=None,
        due_date=None,
        evidence_refs=[evidence_ref()],
    )

    assert item.owner is None
    assert item.due_date is None


def test_write_operation_tracks_approval_and_execution_state() -> None:
    op = WriteOperation(
        operation_id="op-doc-1",
        operation_type=OperationType.DOC_CREATE,
        target={"folder_token": None},
        dry_run_payload={"title": "会议纪要", "markdown": "# 会议纪要"},
        preview="创建飞书文档：会议纪要",
        requires_approval=True,
        approval_status=ApprovalStatus.PENDING,
        execution_status=ExecutionStatus.PENDING,
    )

    assert op.requires_approval is True
    assert op.approval_status == ApprovalStatus.PENDING
    assert op.execution_status == ExecutionStatus.PENDING
