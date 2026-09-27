from __future__ import annotations

import unittest
from datetime import date

from pydantic import ValidationError

from models import (
    PlanRequest,
    RaceGoal,
    ReportedTrainingBaseline,
    RunnerConstraints,
    TrainingProfile,
)
from services.core.training_profile import calculate_reported_profile


def make_baseline(**changes: object) -> ReportedTrainingBaseline:
    data: dict[str, object] = {
        "usual_runs_per_week": 2.5,
        "approx_weekly_running_distance_m": 12000,
    }
    data.update(changes)
    return ReportedTrainingBaseline(**data)


def make_request(as_of_date: date = date(2026, 9, 27)) -> PlanRequest:
    return PlanRequest(
        goal=RaceGoal(
            distance_m=10000,
            race_date=date(2026, 12, 1),
            goal_type="finish",
        ),
        constraints=RunnerConstraints(
            available_weekdays={2, 4, 6},
            experience="beginner",
            current_pain_or_injury="no",
            fatigue="low",
        ),
        as_of_date=as_of_date,
    )


class ReportedBaselineTests(unittest.TestCase):
    def test_baseline_accepts_estimates_and_preserves_unknown_optional_values(
        self,
    ) -> None:
        baseline = make_baseline()

        self.assertEqual(baseline.usual_runs_per_week, 2.5)
        self.assertEqual(baseline.approx_weekly_running_distance_m, 12000)
        self.assertIsNone(baseline.recent_longest_run_m)
        self.assertIsNone(baseline.last_run_date)

        zero = make_baseline(
            usual_runs_per_week=0,
            approx_weekly_running_distance_m=0,
        )
        self.assertEqual(zero.usual_runs_per_week, 0)
        self.assertEqual(zero.approx_weekly_running_distance_m, 0)

    def test_baseline_rejects_out_of_range_frequency_and_negative_distances(
        self,
    ) -> None:
        for value in (-0.1, 7.1, float("nan")):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                make_baseline(usual_runs_per_week=value)

        with self.assertRaises(ValidationError):
            make_baseline(approx_weekly_running_distance_m=-1)
        with self.assertRaises(ValidationError):
            make_baseline(recent_longest_run_m=-1)

    def test_reported_profile_preserves_basis_estimates_and_optional_unknowns(
        self,
    ) -> None:
        baseline = make_baseline(
            recent_longest_run_m=9000,
            last_run_date=date(2026, 9, 20),
        )

        profile = calculate_reported_profile(make_request(), baseline)

        self.assertIsInstance(profile, TrainingProfile)
        self.assertEqual(profile.basis, "reported")
        self.assertEqual(profile.usual_runs_per_week, 2.5)
        self.assertEqual(profile.weekly_running_distance_m, 12000)
        self.assertEqual(profile.recent_longest_run_m, 9000)
        self.assertEqual(profile.recent_training_gap_days, 7)
        self.assertIsNone(profile.heart_rate_coverage)
        self.assertTrue(profile.data_limitations)

    def test_reported_profile_leaves_unknown_values_unknown(self) -> None:
        profile = calculate_reported_profile(make_request(), make_baseline())

        self.assertIsNone(profile.recent_longest_run_m)
        self.assertIsNone(profile.recent_training_gap_days)
        self.assertIsNone(profile.heart_rate_coverage)

    def test_reported_last_run_cannot_be_after_request_date(self) -> None:
        baseline = make_baseline(last_run_date=date(2026, 9, 28))

        with self.assertRaises(ValueError):
            calculate_reported_profile(make_request(), baseline)


if __name__ == "__main__":
    unittest.main()
