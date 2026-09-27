"""Observed running activity and provider history models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RunActivity(BaseModel):
    source_id: str = Field(min_length=1)
    started_at: datetime
    distance_m: int = Field(ge=0)
    moving_time_s: int = Field(gt=0)
    elevation_gain_m: float | None = None
    average_heart_rate_bpm: int | None = Field(default=None, gt=0)


class TrainingHistory(BaseModel):
    provider_id: str = Field(min_length=1)
    from_date: date
    through_date: date
    runs: list[RunActivity]
    coverage: Literal["complete", "partial"]
    coverage_note: str | None = None

    @model_validator(mode="after")
    def validate_period_and_run_ids(self) -> TrainingHistory:
        if self.from_date > self.through_date:
            raise ValueError("from_date must be on or before through_date")
        source_ids = [run.source_id for run in self.runs]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("run source_id values must be unique within a provider")
        return self
