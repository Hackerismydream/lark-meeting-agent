from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from nanobot.meeting_data.fixture_store import load_fixtures
from nanobot.meeting_data.schemas import MeetingFixture


SENSITIVE_KEY_RE = re.compile(r"(token|secret|cookie|authorization|password|passcode|open_id|user_id|email|mobile|phone|chat_id)", re.I)
SENSITIVE_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]+|Bearer\s+[A-Za-z0-9_.-]+)")


def scenario_dir(out_root: Path | str, name: str) -> Path:
    path = Path(out_root) / name
    path.mkdir(parents=True, exist_ok=True)
    (path / "screenshots").mkdir(parents=True, exist_ok=True)
    write_screenshot_readme(path / "screenshots" / "README.md")
    return path


def real_writes_enabled() -> bool:
    return os.environ.get("LMA_DEMO_ENABLE_REAL_WRITES", "0") == "1"


def sandbox_chat_id() -> str | None:
    return os.environ.get("LMA_DEMO_CHAT_ID") or os.environ.get("LMA_DEMO_SANDBOX_CHAT_ID")


def sandbox_doc_folder_token() -> str | None:
    return os.environ.get("LMA_DEMO_DOC_FOLDER_TOKEN")


def load_fixture_for_demo(fixtures_root: Path | str, fixture_id: str | None = None) -> MeetingFixture:
    fixtures = load_fixtures(fixtures_root)
    if not fixtures:
        raise SystemExit(f"no MeetingFixture JSON found under {fixtures_root}")
    if fixture_id:
        for fixture in fixtures:
            if fixture.fixture_id == fixture_id:
                return fixture
        raise SystemExit(f"fixture not found: {fixture_id}")
    return fixtures[0]


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if SENSITIVE_KEY_RE.search(str(key)) else sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return SENSITIVE_VALUE_RE.sub("[REDACTED]", value)
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sanitize(payload), ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def append_command_log(path: Path, command: str, details: dict[str, Any] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(command + "\n")
        if details:
            handle.write(json.dumps(sanitize(details), ensure_ascii=False, sort_keys=True, default=str) + "\n")


def write_screenshot_readme(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "# Screenshot placeholders",
                "",
                "Screenshots are intentionally not captured automatically in Stage 3.",
                "Use Stage 4 / Computer Use or manual capture after verifying private content is safe.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_blocker(path: Path, title: str, error: Exception | str) -> None:
    path.write_text(f"# {title}\n\n```text\n{sanitize(str(error))}\n```\n", encoding="utf-8")
