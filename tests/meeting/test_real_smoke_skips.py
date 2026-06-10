from __future__ import annotations

import os
import shutil

import pytest


def test_real_lark_smoke_is_explicitly_opt_in() -> None:
    if os.environ.get("RUN_REAL_LARK_TESTS") != "1":
        pytest.skip("set RUN_REAL_LARK_TESTS=1 to run local lark-cli smoke tests")
    assert shutil.which("lark-cli")


def test_real_llm_smoke_is_explicitly_opt_in() -> None:
    if os.environ.get("RUN_REAL_LLM_TESTS") != "1":
        pytest.skip("set RUN_REAL_LLM_TESTS=1 to run local LLM smoke tests")
    assert os.environ.get("LMA_LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
