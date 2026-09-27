"""Deterministic profile derived from reported or observed training data."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class TrainingProfile(BaseModel):
    basis: Literal["reported", "observed"]
    usual_runs_per_week: float | None = Field(
        default=None, ge=0, le=7, allow_inf_nan=False
    )
    weekly_running_distance_m: int | None = Field(default=None, ge=0)
    recent_longest_run_m: int | None = Field(default=None, ge=0)
    recent_training_gap_days: int | None = Field(default=None, ge=0)
    heart_rate_coverage: float | None = Field(default=None, ge=0, le=1)
    data_limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_basis(self) -> TrainingProfile:
        if self.basis == "reported" and self.heart_rate_coverage is not None:
            raise ValueError("heart-rate coverage is unknown for a reported baseline")
        return self
