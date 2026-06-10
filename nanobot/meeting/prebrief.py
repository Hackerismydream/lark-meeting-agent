"""Pre-meeting brief workflow."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.retrieval import MeetingRetrievalEngine
from nanobot.meeting.schemas import (
    Meeting,
    MeetingRefType,
    PreBrief,
    PreBriefInput,
    PreBriefSection,
    ProviderMode,
    QASource,
    RetrievalQuery,
)
from nanobot.meeting.trace import RunTraceWriter


class PreBriefWorkflow:
    def __init__(self, workspace: Path | str, provider_mode: str = "fake") -> None:
        self.workspace = Path(workspace)
        self.provider_mode = provider_mode
        self.memory = MeetingMemoryStore(self.workspace)
        self.retrieval = MeetingRetrievalEngine(self.memory)

    def generate(self, request: PreBriefInput) -> PreBrief:
        run_id = str(uuid.uuid4())
        trace = RunTraceWriter(self.workspace, run_id, "PreBriefWorkflow")
        trace.add("start", "prebrief requested", request.model_dump(mode="json"))

        adapter = self._adapter(request.provider_mode)
        agenda = adapter.execute(
            "calendar.agenda",
            {
                "query": request.meeting_ref.query or request.meeting_ref.value,
                "start": request.time_range.get("start"),
                "end": request.time_range.get("end"),
                "meeting_id": request.meeting_ref.value if request.meeting_ref.type == MeetingRefType.MEETING_ID else None,
            },
        )
        trace.add("lark_read", "calendar agenda read", {"items": len(_items(agenda))})
        meeting = _meeting_from_agenda(agenda, request)

        filters = {
            "project": request.project,
            "customer": request.customer,
            "person": request.participants[0] if request.participants else None,
        }
        retrieved = self.retrieval.retrieve(
            RetrievalQuery(
                question=" ".join(part for part in [request.project, request.customer, request.meeting_ref.query] if part),
                project=request.project,
                customer=request.customer,
                limit=8,
            )
        )
        open_actions = self.memory.open_action_items(filters)
        docs = adapter.execute("docs.search", {"query": request.project or request.customer or request.meeting_ref.query or ""})
        tasks = adapter.execute("task.search", {"query": request.project or request.customer or "", "status": "open"})
        trace.add(
            "context",
            "prebrief context collected",
            {"retrieval_items": len(retrieved.items), "open_actions": len(open_actions), "docs": len(_items(docs)), "tasks": len(_items(tasks))},
        )

        sections = [
            PreBriefSection(
                title="历史背景",
                bullets=[item.text for item in retrieved.items[:4]] or ["没有找到可引用的历史会议背景。"],
                sources=[item.source for item in retrieved.items[:4]],
            ),
            PreBriefSection(
                title="未关闭待办",
                bullets=[_task_text(item) for item in [*open_actions, *_items(tasks)][:6]] or ["没有找到相关未关闭待办。"],
                sources=[_source_from_action(item) for item in open_actions[:6]],
            ),
            PreBriefSection(
                title="相关资料",
                bullets=[str(item.get("title") or item.get("content") or item) for item in _items(docs)[:4]] or ["没有找到相关文档。"],
                sources=[QASource(meeting_id=meeting.meeting_id, kind="doc", text=str(item.get("title") or item)) for item in _items(docs)[:4]],
            ),
            PreBriefSection(
                title="风险与建议追问",
                bullets=_template_questions(request.meeting_type),
                sources=[],
            ),
        ]
        brief = PreBrief(
            run_id=run_id,
            meeting=meeting,
            meeting_type=request.meeting_type,
            goal=_goal_for(request, meeting),
            sections=sections,
            suggested_questions=_template_questions(request.meeting_type),
        )
        trace.add("complete", "prebrief generated", {"sections": len(sections), "suggested_questions": len(brief.suggested_questions)})
        brief.trace_path = str(trace.save())
        return brief

    def _adapter(self, mode: str | ProviderMode) -> LarkToolAdapter:
        if ProviderMode(mode) == ProviderMode.FAKE:
            return LarkToolAdapter.fake(self.workspace)
        if ProviderMode(mode) == ProviderMode.OAPI:
            return LarkToolAdapter.oapi(self.workspace)
        return LarkToolAdapter.cli(self.workspace)


def _items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("items", "meetings", "tasks", "docs"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    data = payload.get("data")
    if isinstance(data, dict):
        return _items(data)
    return []


def _meeting_from_agenda(payload: dict[str, Any], request: PreBriefInput) -> Meeting:
    item = (_items(payload) or [{}])[0]
    return Meeting(
        meeting_id=str(item.get("meeting_id") or request.meeting_ref.value or f"prebrief-{uuid.uuid4()}"),
        title=str(item.get("title") or item.get("summary") or request.meeting_ref.query or "会议"),
        start_time=item.get("start_time"),
        end_time=item.get("end_time"),
        source="calendar",
    )


def _goal_for(request: PreBriefInput, meeting: Meeting) -> str:
    target = request.customer or request.project or meeting.title
    return f"准备 {target} 的{request.meeting_type.value}上下文，确认历史结论、未关闭待办、风险和建议追问。"


def _task_text(item: dict[str, Any]) -> str:
    owner = item.get("owner") or "unassigned"
    due = item.get("due_date") or "no due date"
    return f"{item.get('summary') or item.get('task') or item.get('text')} owner={owner} due={due}"


def _source_from_action(item: dict[str, Any]) -> QASource:
    evidence = (item.get("evidence_refs") or [{}])[0]
    return QASource(
        meeting_id=str(evidence.get("meeting_id") or item.get("meeting_id") or ""),
        segment_id=evidence.get("segment_id"),
        kind="action_item",
        text=str(evidence.get("quote") or item.get("summary") or item.get("task") or item),
        speaker_name=evidence.get("speaker_name"),
        timestamp=evidence.get("timestamp"),
    )


def _template_questions(meeting_type) -> list[str]:
    templates = {
        "customer_meeting": ["客户上次最关心的问题是否关闭？", "这次需要确认哪些承诺和风险？"],
        "project_sync": ["上次决策是否执行？", "当前阻塞和下一步 owner 是谁？"],
        "requirement_review": ["需求边界是否明确？", "验收标准和风险是否有证据？"],
        "technical_review": ["关键技术取舍是什么？", "上线风险和回滚方案是否明确？"],
        "incident_review": ["根因证据是什么？", "修复 owner 和预防动作是否明确？"],
        "one_on_one": ["上次承诺是否完成？", "本次需要同步的风险是什么？"],
    }
    return templates.get(getattr(meeting_type, "value", str(meeting_type)), ["这次会议需要确认什么结论？", "哪些待办需要 owner 和截止时间？"])
