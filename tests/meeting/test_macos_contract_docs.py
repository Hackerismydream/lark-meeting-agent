from __future__ import annotations

from pathlib import Path


def test_macos_contract_doc_defines_companion_boundary() -> None:
    text = Path("docs/MACOS_COMPANION_APP.md").read_text()

    assert "not a second Agent runtime" in text
    assert "must not" in text
    assert "call Lark APIs directly" in text
    assert "LarkToolAdapter" in text
    assert "Keychain" in text


def test_macos_contract_doc_lists_companion_api_endpoints() -> None:
    text = Path("docs/MACOS_COMPANION_APP.md").read_text()

    for endpoint in [
        "GET  /v1/agent/status",
        "GET  /v1/runs/{run_id}",
        "GET  /v1/runs/{run_id}/trace",
        "GET  /v1/write-plans/pending",
        "POST /v1/runs/{run_id}/approve",
        "POST /v1/runs/{run_id}/reject",
        "POST /v1/search",
        "POST /v1/upload/transcript",
    ]:
        assert endpoint in text


def test_macos_contract_doc_does_not_claim_asr_or_production_release() -> None:
    text = Path("docs/MACOS_COMPANION_APP.md").read_text().lower()

    assert "phase 3 macos shell is implemented" in text
    assert "deferred to later v1.1 phases" in text
    assert "claim asr/audio transcription support" in text
    assert "app store release" not in text


def test_macos_approval_inbox_doc_preserves_backend_write_boundary() -> None:
    text = Path("docs/MACOS_APPROVAL_INBOX.md").read_text()

    assert "does not execute Lark writes" in text
    assert "Companion API" in text
    assert "LarkToolAdapter" in text
    assert "explicit `operation_ids`" in text
    assert "no vague approve-all button" in text
    assert "never calls Lark APIs" in text


def test_macos_prebrief_trace_viewer_doc_is_read_oriented() -> None:
    text = Path("docs/MACOS_PREBRIEF_TRACE_VIEWER.md").read_text()

    assert "does not run its own Agent loop" in text
    assert "does not run its own Agent loop, call Lark APIs, or execute hidden writes" in text
    assert "Trace data is treated as display-only diagnostic context" in text
    assert "Inspecting traces cannot trigger approval" in text
    assert "POST /v1/prebrief" in text
    assert "GET /v1/runs/{run_id}/trace" in text
