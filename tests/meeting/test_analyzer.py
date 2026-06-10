from __future__ import annotations

from pathlib import Path

from nanobot.meeting.analyzer import FakeMeetingAnalyzer, OpenAICompatibleMeetingAnalyzer
from nanobot.meeting.normalizer import TranscriptNormalizer

FIXTURE = Path("tests/fixtures/meeting/transcripts/sample_project_sync.txt")


def test_fake_analyzer_extracts_schema_valid_outputs_with_evidence() -> None:
    segments = TranscriptNormalizer().normalize_text("meeting-1", FIXTURE.read_text())
    minutes = FakeMeetingAnalyzer().analyze(
        meeting_id="meeting-1",
        title="项目例会",
        segments=segments,
    )

    assert minutes.decisions
    assert minutes.action_items
    assert all(d.evidence_refs for d in minutes.decisions)
    assert all(a.evidence_refs for a in minutes.action_items)
    assert minutes.action_items[0].owner in {"张三", "李四", "unassigned", None}
    assert minutes.open_questions[0].text == "是否需要客户确认验收标准。"


def test_llm_parser_normalizes_common_alias_fields_and_extra_metadata() -> None:
    content = """
    {
      "meeting_id": "meeting-1",
      "title": "项目例会",
      "meeting_date": null,
      "participants": [],
      "one_sentence_summary": "完成灰度上线安排。",
      "detailed_summary": "会议讨论了上线安排。",
      "chapters": [
        {
          "chapter_id": "ch-1",
          "title": "讨论",
          "summary": "同步上线安排",
          "start_time": "00:00",
          "end_time": "02:30",
          "evidence_refs": ["seg-0001"]
        }
      ],
      "decisions": [
        {
          "decision_id": "dec-1",
          "text": "本周先灰度上线。",
          "owner": "张三",
          "rationale": null,
          "evidence_refs": [
            {
              "evidence_id": "ev-seg-0001",
              "meeting_id": "meeting-1",
              "segment_id": "seg-0001",
              "speaker_name": "张三",
              "timestamp": "00:00",
              "quote": "我们决定本周先灰度上线。"
            }
          ]
        }
      ],
      "action_items": [
        {
          "action_item_id": "act-1",
          "text": "补充接口文档",
          "owner": "张三",
          "due_date": null,
          "evidence_refs": ["seg-0002"]
        }
      ],
      "risks": [
        {"risk_id": "risk-1", "text": "后端排期可能延迟。", "raised_by": "王五", "evidence_refs": []}
      ],
      "open_questions": [
        {"text": "是否需要客户确认？", "raised_by": "李四", "evidence_refs": []}
      ]
    }
    """

    segments = TranscriptNormalizer().normalize_text(
        "meeting-1",
        "[00:00] 张三: 我们决定本周先灰度上线。\n[01:00] 张三: 我周五前补充接口文档。",
    )
    minutes = OpenAICompatibleMeetingAnalyzer._parse_minutes(content, segments)

    assert minutes.action_items[0].action_id == "act-1"
    assert minutes.action_items[0].task == "补充接口文档"
    assert minutes.chapters[0].title == "讨论"
    assert minutes.chapters[0].summary == "同步上线安排"
    assert minutes.open_questions[0].question_id == "q-1"
    assert minutes.action_items[0].evidence_refs[0].quote == "我周五前补充接口文档。"
