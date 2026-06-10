"""Meeting analyzers."""

from __future__ import annotations

import json
import os
import re
from typing import Protocol

from pydantic import ValidationError

from nanobot.meeting.errors import AnalyzerValidationError
from nanobot.meeting.prompts import build_repair_prompt, build_system_prompt, build_user_prompt
from nanobot.meeting.schemas import (
    ActionItem,
    Chapter,
    Decision,
    EvidenceRef,
    MeetingMinutes,
    OpenQuestion,
    Risk,
    TranscriptSegment,
)


class MeetingAnalyzer(Protocol):
    def analyze(self, meeting_id: str, title: str, segments: list[TranscriptSegment]) -> MeetingMinutes:
        """Analyze normalized transcript segments."""


class FakeMeetingAnalyzer:
    """Deterministic analyzer for tests and offline demos."""

    def analyze(self, meeting_id: str, title: str, segments: list[TranscriptSegment]) -> MeetingMinutes:
        decisions: list[Decision] = []
        action_items: list[ActionItem] = []
        risks: list[Risk] = []
        questions: list[OpenQuestion] = []

        for segment in segments:
            evidence = self._evidence(segment)
            text = segment.text
            if "决定" in text:
                decisions.append(
                    Decision(
                        decision_id=f"dec-{len(decisions) + 1}",
                        text=self._after_marker(text, "决定"),
                        owner=segment.speaker_name,
                        evidence_refs=[evidence],
                    )
                )
            if self._looks_like_action(text):
                action_items.append(
                    ActionItem(
                        action_id=f"act-{len(action_items) + 1}",
                        task=self._action_text(text),
                        owner=segment.speaker_name or "unassigned",
                        due_date=self._due_date(text),
                        evidence_refs=[evidence],
                    )
                )
            if "风险" in text:
                risks.append(Risk(risk_id=f"risk-{len(risks) + 1}", text=text, evidence_refs=[evidence]))
            if "开放问题" in text or "是否" in text:
                questions.append(
                    OpenQuestion(
                        question_id=f"q-{len(questions) + 1}",
                        text=self._after_marker(text, "开放问题"),
                        evidence_refs=[evidence],
                    )
                )

        if not decisions and segments:
            first = segments[0]
            decisions.append(
                Decision(
                    decision_id="dec-1",
                    text="未发现明确决策；需要人工确认",
                    owner=None,
                    evidence_refs=[self._evidence(first)],
                )
            )
        summary = decisions[0].text if decisions else "会议已处理"
        return MeetingMinutes(
            meeting_id=meeting_id,
            title=title,
            one_sentence_summary=summary,
            detailed_summary="\n".join(segment.text for segment in segments),
            chapters=[
                Chapter(
                    title="会议讨论",
                    summary="; ".join(segment.text for segment in segments[:3]),
                    evidence_refs=[self._evidence(segments[0])] if segments else [],
                )
            ],
            decisions=decisions,
            action_items=action_items,
            risks=risks,
            open_questions=questions,
        )

    @staticmethod
    def _evidence(segment: TranscriptSegment) -> EvidenceRef:
        return EvidenceRef(
            evidence_id=f"ev-{segment.segment_id}",
            meeting_id=segment.meeting_id,
            segment_id=segment.segment_id,
            speaker_name=segment.speaker_name,
            timestamp=segment.start_time,
            quote=segment.text,
        )

    @staticmethod
    def _after_marker(text: str, marker: str) -> str:
        if marker not in text:
            return text
        remainder = text.split(marker, 1)[1].strip()
        remainder = re.sub(r"^[：:，,。\\s]+", "", remainder).strip()
        if remainder.startswith("是") and not remainder.startswith("是否"):
            remainder = remainder[1:].lstrip("：:，,。 ")
        return remainder or text

    @staticmethod
    def _looks_like_action(text: str) -> bool:
        if "开放问题" in text or text.startswith("风险"):
            return False
        return any(marker in text for marker in ("我", "负责", "待办", "补充", "确认", "完成")) and any(
            verb in text for verb in ("补充", "确认", "完成", "负责", "整理")
        )

    @staticmethod
    def _action_text(text: str) -> str:
        text = re.sub(r"^我", "", text).strip("：:，,。 ")
        return text or "未命名待办"

    @staticmethod
    def _due_date(text: str) -> str | None:
        if "周五" in text:
            return None
        if "明天" in text:
            return None
        return None


class OpenAICompatibleMeetingAnalyzer:
    """OpenAI-compatible analyzer, defaulting to DeepSeek environment variables."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("LMA_LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.environ.get("LMA_LLM_BASE_URL") or "https://api.deepseek.com"
        self.model = model or os.environ.get("LMA_LLM_MODEL") or "deepseek-v4-pro"

    def analyze(self, meeting_id: str, title: str, segments: list[TranscriptSegment]) -> MeetingMinutes:
        if not self.api_key:
            raise AnalyzerValidationError("LMA_LLM_API_KEY or DEEPSEEK_API_KEY is required")
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - dependency is installed in normal env
            raise AnalyzerValidationError("openai package is required for LLM analyzer") from exc

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        user_prompt = build_user_prompt(meeting_id, title, segments)
        content = self._complete(client, user_prompt)
        try:
            return self._parse_minutes(content)
        except AnalyzerValidationError:
            repaired = self._complete(client, build_repair_prompt(content), temperature=0)
            return self._parse_minutes(repaired)

    def _complete(self, client: object, prompt: str, temperature: float = 0.1) -> str:
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
            stream=False,
        )
        return response.choices[0].message.content or ""

    @staticmethod
    def _parse_minutes(content: str) -> MeetingMinutes:
        try:
            data = json.loads(_extract_json(content))
            return MeetingMinutes.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise AnalyzerValidationError(f"invalid analyzer output: {exc}") from exc


def _extract_json(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def create_analyzer(mode: str) -> MeetingAnalyzer:
    if mode == "fake":
        return FakeMeetingAnalyzer()
    if mode == "llm":
        return OpenAICompatibleMeetingAnalyzer()
    raise AnalyzerValidationError(f"unknown analyzer mode: {mode}")
