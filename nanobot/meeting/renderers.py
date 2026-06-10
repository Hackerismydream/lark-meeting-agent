"""Render meeting outputs into human-readable payloads."""

from __future__ import annotations

from nanobot.meeting.schemas import Meeting, MeetingMinutes


def render_minutes_markdown(meeting: Meeting, minutes: MeetingMinutes) -> str:
    lines = [
        f"# {minutes.title}",
        "",
        "## 基本信息",
        f"- Meeting ID: `{meeting.meeting_id}`",
    ]
    if meeting.start_time:
        lines.append(f"- Start: {meeting.start_time}")
    if meeting.end_time:
        lines.append(f"- End: {meeting.end_time}")
    if meeting.attendees:
        lines.append("- Attendees: " + ", ".join(a.name for a in meeting.attendees))

    lines.extend(["", "## 一句话总结", minutes.one_sentence_summary, "", "## 详细总结", minutes.detailed_summary])

    if minutes.decisions:
        lines.extend(["", "## 决策"])
        for decision in minutes.decisions:
            lines.append(f"- {decision.text}")
            lines.extend(_evidence_lines(decision.evidence_refs))

    if minutes.action_items:
        lines.extend(["", "## 待办"])
        for item in minutes.action_items:
            owner = item.owner or "unassigned"
            due = item.due_date or "未指定"
            lines.append(f"- {item.task} Owner: {owner} Due: {due}")
            lines.extend(_evidence_lines(item.evidence_refs))

    if minutes.risks:
        lines.extend(["", "## 风险"])
        lines.extend(f"- {risk.text}" for risk in minutes.risks)

    if minutes.open_questions:
        lines.extend(["", "## 开放问题"])
        lines.extend(f"- {question.text}" for question in minutes.open_questions)

    lines.extend(["", "## Evidence"])
    for item in [*minutes.decisions, *minutes.action_items, *minutes.risks, *minutes.open_questions]:
        for evidence in item.evidence_refs:
            lines.append(f"- `{evidence.segment_id}` {evidence.speaker_name or ''}: {evidence.quote}")

    return "\n".join(lines).strip() + "\n"


def render_summary_message(minutes: MeetingMinutes) -> str:
    parts = [f"会议纪要：{minutes.title}", minutes.one_sentence_summary]
    if minutes.decisions:
        parts.append("决策：" + "；".join(decision.text for decision in minutes.decisions))
    if minutes.action_items:
        parts.append("待办：" + "；".join(item.task for item in minutes.action_items))
    return "\n".join(parts)


def _evidence_lines(evidence_refs: list) -> list[str]:
    return [f"  - Evidence `{e.segment_id}`: {e.quote}" for e in evidence_refs]
