"""Runner goals, constraints, and planning request models."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

RaceDistance = Literal[5000, 10000, 21098, 42195]
Weekday = Annotated[int, Field(ge=1, le=7)]


class RaceGoal(BaseModel):
    distance_m: RaceDistance
    race_date: date
    goal_type: Literal["finish", "target_time"]
    target_time_s: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_target_time(self) -> RaceGoal:
        if self.goal_type == "target_time" and self.target_time_s is None:
            raise ValueError("target_time_s is required for a target_time goal")
        if self.goal_type == "finish" and self.target_time_s is not None:
            raise ValueError("target_time_s is only valid for a target_time goal")
        return self


class HeartRateRange(BaseModel):
    min_bpm: int = Field(gt=0)
    max_bpm: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_range(self) -> HeartRateRange:
        if self.min_bpm >= self.max_bpm:
            raise ValueError("min_bpm must be less than max_bpm")
        return self


class RunnerConstraints(BaseModel):
    available_weekdays: set[Weekday]
    max_session_minutes: int | None = Field(default=None, gt=0)
    experience: Literal["beginner", "intermediate", "advanced"]
    current_pain_or_injury: Literal["yes", "no", "unknown"]
    fatigue: Literal["low", "moderate", "high", "unknown"]
    easy_heart_rate_range: HeartRateRange | None = None


class PlanRequest(BaseModel):
    goal: RaceGoal
    constraints: RunnerConstraints
    as_of_date: date


class ReportedTrainingBaseline(BaseModel):
    usual_runs_per_week: float = Field(ge=0, le=7, allow_inf_nan=False)
    approx_weekly_running_distance_m: int = Field(ge=0)
    recent_longest_run_m: int | None = Field(default=None, ge=0)
    last_run_date: date | None = None
