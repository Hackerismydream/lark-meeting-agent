from __future__ import annotations

from nanobot.meeting_data.feishu_wrapper import fixture_to_feishu_context
from tests.meeting_data.test_fixture_schema import valid_fixture


def test_fixture_to_feishu_context_contains_product_chain_fields() -> None:
    context = fixture_to_feishu_context(valid_fixture())

    assert context.calendar_event.title == "Test Meeting"
    assert context.agenda_doc
    assert context.participants
    assert context.transcript_stream
    assert context.output_targets.sandbox_only is True
    assert context.approval_policy == "dry_run_required"
