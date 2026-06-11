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
