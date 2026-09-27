from __future__ import annotations

import unittest
from datetime import date, datetime

from pydantic import ValidationError

from models import (
    HeartRateRange,
    PlanResult,
    RaceGoal,
    RunActivity,
    RunnerConstraints,
    TrainingHistory,
    TrainingPlan,
    TrainingSession,
    TrainingWeek,
)


def make_run(source_id: str = "run-1", **changes: object) -> RunActivity:
    data: dict[str, object] = {
        "source_id": source_id,
        "started_at": datetime(2026, 9, 1, 7),
        "distance_m": 5000,
        "moving_time_s": 1800,
    }
    data.update(changes)
    return RunActivity(**data)


def make_goal(**changes: object) -> RaceGoal:
    data: dict[str, object] = {
        "distance_m": 21098,
        "race_date": date(2026, 12, 1),
        "goal_type": "finish",
    }
    data.update(changes)
    return RaceGoal(**data)


class InputModelTests(unittest.TestCase):
    def test_run_activity_rejects_negative_distance_and_nonpositive_values(
        self,
    ) -> None:
        with self.assertRaises(ValidationError):
            make_run(distance_m=-1)
        with self.assertRaises(ValidationError):
            make_run(moving_time_s=0)
        with self.assertRaises(ValidationError):
            make_run(average_heart_rate_bpm=0)

    def test_run_activity_keeps_missing_optional_measurements_null(self) -> None:
        run = make_run()

        self.assertIsNone(run.elevation_gain_m)
        self.assertIsNone(run.average_heart_rate_bpm)

    def test_training_history_rejects_reversed_periods_and_duplicate_source_ids(
        self,
    ) -> None:
        with self.assertRaises(ValidationError):
            TrainingHistory(
                provider_id="fixture",
                from_date=date(2026, 9, 2),
                through_date=date(2026, 9, 1),
                runs=[],
                coverage="complete",
            )

        with self.assertRaises(ValidationError):
            TrainingHistory(
                provider_id="fixture",
                from_date=date(2026, 9, 1),
                through_date=date(2026, 9, 7),
                runs=[make_run(), make_run()],
                coverage="complete",
            )

    def test_race_goal_requires_target_time_only_for_target_time_goals(self) -> None:
        with self.assertRaises(ValidationError):
            make_goal(goal_type="target_time")
        with self.assertRaises(ValidationError):
            make_goal(goal_type="finish", target_time_s=7200)
        with self.assertRaises(ValidationError):
            make_goal(goal_type="target_time", target_time_s=0)

        goal = make_goal(goal_type="target_time", target_time_s=7200)
        self.assertEqual(goal.target_time_s, 7200)

    def test_heart_rate_and_weekday_ranges_are_validated(self) -> None:
        with self.assertRaises(ValidationError):
            HeartRateRange(min_bpm=0, max_bpm=150)
        with self.assertRaises(ValidationError):
            HeartRateRange(min_bpm=150, max_bpm=140)
        with self.assertRaises(ValidationError):
            RunnerConstraints(
                available_weekdays={0},
                experience="beginner",
                current_pain_or_injury="no",
                fatigue="low",
            )


class PlanModelTests(unittest.TestCase):
    def test_rest_and_training_sessions_enforce_workload_rules(self) -> None:
        with self.assertRaises(ValidationError):
            TrainingSession(
                date=date(2026, 9, 1),
                kind="rest",
                distance_m=1000,
                effort="none",
                instructions="Rest",
                purpose="Recovery",
            )
        with self.assertRaises(ValidationError):
            TrainingSession(
                date=date(2026, 9, 1),
                kind="easy",
                effort="easy",
                instructions="Easy run",
                purpose="Build endurance",
            )

    def test_week_distance_is_derived_only_when_all_running_distances_are_known(
        self,
    ) -> None:
        week = TrainingWeek(
            week_start=date(2026, 8, 31),
            phase="base",
            sessions=[
                TrainingSession(
                    date=date(2026, 9, 1),
                    kind="easy",
                    distance_m=5000,
                    effort="easy",
                    instructions="Easy run",
                    purpose="Build endurance",
                ),
                TrainingSession(
                    date=date(2026, 9, 3),
                    kind="long",
                    distance_m=8000,
                    effort="easy",
                    instructions="Long run",
                    purpose="Build endurance",
                ),
            ],
            focus="Build endurance",
        )
        self.assertEqual(week.planned_running_distance_m, 13000)

        incomplete = TrainingWeek(
            week_start=date(2026, 8, 31),
            phase="base",
            sessions=[
                TrainingSession(
                    date=date(2026, 9, 1),
                    kind="easy",
                    duration_minutes=30,
                    effort="easy",
                    instructions="Easy run",
                    purpose="Build endurance",
                )
            ],
            focus="Build endurance",
        )
        self.assertIsNone(incomplete.planned_running_distance_m)

    def test_plan_rejects_duplicate_or_out_of_order_session_dates(self) -> None:
        week = TrainingWeek(
            week_start=date(2026, 8, 31),
            phase="base",
            sessions=[
                TrainingSession(
                    date=date(2026, 9, 2),
                    kind="easy",
                    duration_minutes=30,
                    effort="easy",
                    instructions="Easy run",
                    purpose="Build endurance",
                ),
                TrainingSession(
                    date=date(2026, 9, 1),
                    kind="easy",
                    duration_minutes=30,
                    effort="easy",
                    instructions="Easy run",
                    purpose="Build endurance",
                ),
            ],
            focus="Build endurance",
        )

        with self.assertRaises(ValidationError):
            TrainingPlan(
                goal=make_goal(),
                summary="Plan",
                rationale=[],
                weeks=[week],
                adjustment_guidance=[],
            )

    def test_plan_result_matches_its_status(self) -> None:
        with self.assertRaises(ValidationError):
            PlanResult(status="ready", questions=[], reason=None)
        with self.assertRaises(ValidationError):
            PlanResult(status="needs_more_information", questions=[], reason=None)

        result = PlanResult(
            status="needs_more_information",
            questions=["How many days can you run?"],
            reason=None,
        )
        self.assertIsNone(result.plan)


if __name__ == "__main__":
    unittest.main()
