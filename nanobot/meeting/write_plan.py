"""Build dry-run Lark write plans."""

from __future__ import annotations

import hashlib
import json

from nanobot.meeting.renderers import render_minutes_markdown, render_summary_message
from nanobot.meeting.schemas import (
    ApprovalStatus,
    ExecutionStatus,
    Meeting,
    MeetingMinutes,
    OperationType,
    WriteOperation,
    WritePlan,
)


class WritePlanBuilder:
    def build(
        self,
        *,
        run_id: str,
        meeting: Meeting,
        minutes: MeetingMinutes,
        create_doc: bool,
        create_tasks: bool,
        send_message: bool,
        chat_id: str | None = None,
    ) -> WritePlan:
        operations: list[WriteOperation] = []
        if create_doc:
            markdown = render_minutes_markdown(meeting, minutes)
            operations.append(
                WriteOperation(
                    operation_id="op-doc-1",
                    operation_type=OperationType.DOC_CREATE,
                    target={"folder_token": None},
                    dry_run_payload={"title": f"{minutes.title} 会议纪要", "markdown": markdown},
                    preview=f"创建飞书文档：{minutes.title} 会议纪要",
                    idempotency_key=_idempotency_key(
                        run_id,
                        "op-doc-1",
                        OperationType.DOC_CREATE,
                        {"title": f"{minutes.title} 会议纪要", "markdown": markdown},
                    ),
                    requires_approval=True,
                    approval_status=ApprovalStatus.PENDING,
                    execution_status=ExecutionStatus.PENDING,
                )
            )
        if create_tasks:
            for index, item in enumerate(minutes.action_items, start=1):
                operations.append(
                    self._task_operation(run_id, index, item)
                )
        if send_message:
            approval = ApprovalStatus.PENDING if chat_id else ApprovalStatus.MISSING_TARGET
            payload = {"chat_id": chat_id, "markdown": render_summary_message(minutes)}
            operations.append(
                WriteOperation(
                    operation_id="op-im-1",
                    operation_type=OperationType.IM_SEND,
                    target={"chat_id": chat_id},
                    dry_run_payload=payload,
                    preview="发送飞书群消息" if chat_id else "发送飞书群消息（缺少 chat_id，仅预览）",
                    idempotency_key=_idempotency_key(run_id, "op-im-1", OperationType.IM_SEND, payload),
                    requires_approval=True,
                    approval_status=approval,
                    execution_status=ExecutionStatus.PENDING,
                )
            )
        return WritePlan(run_id=run_id, operations=operations, status="approval_required" if operations else "completed")

    def _task_operation(self, run_id: str, index: int, item) -> WriteOperation:
        operation_id = f"op-task-{index}"
        payload = {
            "summary": item.task,
            "description": self._task_description(item),
            "due": item.due_date,
        }
        return WriteOperation(
            operation_id=operation_id,
            operation_type=OperationType.TASK_CREATE,
            target={"assignee": None},
            dry_run_payload=payload,
            preview=f"创建飞书任务：{item.task}",
            idempotency_key=_idempotency_key(run_id, operation_id, OperationType.TASK_CREATE, payload),
            requires_approval=True,
            approval_status=ApprovalStatus.PENDING,
            execution_status=ExecutionStatus.PENDING,
        )

    @staticmethod
    def _task_description(item) -> str:
        owner = item.owner or "unassigned"
        evidence = "\n".join(f"- {e.segment_id}: {e.quote}" for e in item.evidence_refs)
        return f"Owner: {owner}\n\nEvidence:\n{evidence}"


def _idempotency_key(run_id: str, operation_id: str, operation_type: OperationType, payload: dict) -> str:
    material = json.dumps(
        {
            "run_id": run_id,
            "operation_id": operation_id,
            "operation_type": operation_type.value,
            "payload": payload,
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
