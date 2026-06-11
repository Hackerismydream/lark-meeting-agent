"""Evaluation task definitions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EvalTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    fixture_id: str
    dataset: str
    task_type: str
    query_id: str | None = None
    expected_turn_ids: list[str] = Field(default_factory=list)


class EvalPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    fixture_id: str
    dataset: str
    task_type: str
    predicted_turn_ids: list[str] = Field(default_factory=list)
    answer: str | None = None
    sufficient: bool = True
    artifact_paths: list[str] = Field(default_factory=list)
