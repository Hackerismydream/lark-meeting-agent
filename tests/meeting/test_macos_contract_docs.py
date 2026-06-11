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
    assert "app store released" not in text
    assert "notarization completed" not in text


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


def test_macos_search_upload_doc_rejects_audio_and_preserves_backend_boundary() -> None:
    text = Path("docs/MACOS_SEARCH_UPLOAD.md").read_text()

    assert "POST /v1/search" in text
    assert "meeting_id" in text
    assert "segment_id" in text
    assert ".txt" in text and ".md" in text and ".json" in text
    assert "does not implement ASR" in text
    assert "audio transcription" in text
    assert "Real writes still require backend approval and LarkToolAdapter execution" in text


def test_macos_security_and_packaging_docs_are_honest_about_release_state() -> None:
    security = Path("docs/MACOS_SECURITY.md").read_text()
    packaging = Path("docs/MACOS_PACKAGING.md").read_text()
    qa = Path("docs/MACOS_MANUAL_QA.md").read_text()

    assert "must not call Lark APIs directly" in security
    assert "Persistent bearer tokens use macOS Keychain Services" in security
    assert "Signing and notarization are not completed" in packaging
    assert "Do not describe the app as App Store released" in packaging
    assert "No direct Lark writes occur from macOS" in qa
    assert ".mp3" in qa and ".wav" in qa and ".m4a" in qa
