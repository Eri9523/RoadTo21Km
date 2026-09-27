"""Proposed training plan and result models."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .request import HeartRateRange, RaceGoal


class TrainingSession(BaseModel):
    date: date
    kind: Literal["easy", "long", "quality", "recovery", "rest", "cross_training"]
    duration_minutes: int | None = Field(default=None, gt=0)
    distance_m: int | None = Field(default=None, ge=0)
    effort: Literal["easy", "moderate", "hard", "none"]
    target_heart_rate_range: HeartRateRange | None = None
    instructions: str
    purpose: str

    @model_validator(mode="after")
    def validate_workload(self) -> TrainingSession:
        if self.kind == "rest":
            if (
                self.duration_minutes is not None
                or self.distance_m is not None
                or self.target_heart_rate_range is not None
                or self.effort != "none"
            ):
                raise ValueError("rest sessions cannot have workload or an HR target")
        elif self.duration_minutes is None and self.distance_m is None:
            raise ValueError("training sessions need a duration or distance")
        return self


class TrainingWeek(BaseModel):
    week_start: date
    phase: Literal["base", "build", "taper", "race"]
    sessions: list[TrainingSession]
    planned_running_distance_m: int | None = Field(default=None, ge=0)
    focus: str

    @model_validator(mode="after")
    def calculate_running_distance(self) -> TrainingWeek:
        running_sessions = [
            session
            for session in self.sessions
            if session.kind not in {"rest", "cross_training"}
        ]
        if running_sessions and all(
            session.distance_m is not None for session in running_sessions
        ):
            total = sum(session.distance_m or 0 for session in running_sessions)
        else:
            total = None

        if self.planned_running_distance_m not in {None, total}:
            raise ValueError(
                "planned_running_distance_m must match known running sessions"
            )
        self.planned_running_distance_m = total
        return self


class TrainingPlan(BaseModel):
    goal: RaceGoal
    summary: str
    rationale: list[str]
    weeks: list[TrainingWeek]
    adjustment_guidance: list[str]

    @model_validator(mode="after")
    def validate_session_order(self) -> TrainingPlan:
        week_starts = [week.week_start for week in self.weeks]
        if week_starts != sorted(week_starts):
            raise ValueError("training weeks must be ordered by week_start")

        session_dates = [
            session.date for week in self.weeks for session in week.sessions
        ]
        if len(session_dates) != len(set(session_dates)):
            raise ValueError("training session dates must be unique")
        if session_dates != sorted(session_dates):
            raise ValueError("training session dates must be ordered")
        return self


class PlanResult(BaseModel):
    status: Literal["ready", "needs_more_information", "goal_needs_revision"]
    plan: TrainingPlan | None = None
    questions: list[str] = Field(default_factory=list)
    reason: str | None = None

    @model_validator(mode="after")
    def validate_result_state(self) -> PlanResult:
        if self.status == "ready":
            if self.plan is None or self.questions:
                raise ValueError(
                    "ready results need a plan and no unanswered questions"
                )
        else:
            if self.plan is not None:
                raise ValueError("non-ready results cannot contain a plan")
            has_question = any(question.strip() for question in self.questions)
            if not has_question and not (self.reason and self.reason.strip()):
                raise ValueError("non-ready results need a reason or a useful question")
        return self
