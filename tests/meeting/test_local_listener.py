from __future__ import annotations

import json
from pathlib import Path

from nanobot.meeting.cli import main
from nanobot.meeting.local_listener import LocalTranscriptLiveRunner
from nanobot.meeting.schemas import RunStatus


def test_local_transcript_live_runner_updates_state_and_qa(tmp_path: Path) -> None:
    transcript = tmp_path / "live.txt"
    transcript.write_text("", encoding="utf-8")
    runner = LocalTranscriptLiveRunner(tmp_path)
    session = runner.start(transcript_file=transcript, meeting_id="local-live-1", title="本地会议")

    empty = runner.poll(session)
    transcript.write_text("[00:01] Alice: 决定先做本地监听。\n", encoding="utf-8")
    first = runner.poll(empty.session)
    duplicate = runner.poll(first.session)
    transcript.write_text(
        "[00:01] Alice: 决定先做本地监听。\n[00:02] Bob: 我负责补充风险清单。\n",
        encoding="utf-8",
    )
    second = runner.poll(duplicate.session)
    answer = runner.qa(second.session, "目前有哪些结论和待办？")

    assert empty.ingested_event_count == 0
    assert first.ingested_event_count == 1
    assert duplicate.ingested_event_count == 0
    assert second.ingested_event_count == 1
    assert len(second.live_state.transcript_segments) == 2
    assert second.live_state.decision_candidates
    assert second.live_state.action_candidates
    assert answer.sufficient is True
    assert answer.sources


def test_local_transcript_live_runner_returns_insufficient_evidence(tmp_path: Path) -> None:
    transcript = tmp_path / "live.txt"
    transcript.write_text("[00:01] Alice: 只是闲聊。", encoding="utf-8")
    runner = LocalTranscriptLiveRunner(tmp_path)
    session = runner.start(transcript_file=transcript, meeting_id="local-live-2")
    polled = runner.poll(session)

    answer = runner.qa(polled.session, "完全不存在的事项？")

    assert answer.sufficient is False
    assert "insufficient evidence" in answer.answer


def test_local_transcript_live_runner_stop_and_finalize_dry_run(tmp_path: Path) -> None:
    transcript = tmp_path / "live.txt"
    transcript.write_text(
        "[00:01] Alice: 决定采用本地 transcript live。\n[00:02] Bob: 我负责完成测试。\n",
        encoding="utf-8",
    )
    runner = LocalTranscriptLiveRunner(tmp_path)
    session = runner.start(transcript_file=transcript, meeting_id="local-live-3", title="本地 Transcript Live")
    polled = runner.poll(session)
    stopped = runner.stop(polled.session)
    result = runner.finalize(stopped, create_doc=True, create_tasks=True)

    assert stopped.provider_session.status == "stopped"
    assert result.status == RunStatus.APPROVAL_REQUIRED
    assert result.write_plan is not None
    assert result.write_plan.operations
    assert all(operation.execution_status == "pending" for operation in result.write_plan.operations)


def test_local_transcript_live_cli_can_finalize_and_answer(tmp_path: Path, capsys) -> None:
    transcript = tmp_path / "live.txt"
    transcript.write_text(
        "[00:01] Alice: 决定采用本地 transcript live。\n[00:02] Bob: 我负责完成测试。\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--workspace",
            str(tmp_path),
            "local-transcript-live",
            "--transcript-file",
            str(transcript),
            "--meeting-id",
            "local-live-cli",
            "--title",
            "本地 CLI 会议",
            "--question",
            "目前有哪些结论和待办？",
            "--finalize",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["ingested_event_count"] == 2
    assert output["qa_answer"]["sufficient"] is True
    assert output["postmeeting_result"]["status"] == "approval_required"
    assert output["postmeeting_result"]["write_plan"]["operations"]
