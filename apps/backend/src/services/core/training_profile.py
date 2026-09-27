"""Build deterministic training context from a user-reported baseline."""

from models.profile import TrainingProfile
from models.request import PlanRequest, ReportedTrainingBaseline


def calculate_reported_profile(
    request: PlanRequest,
    baseline: ReportedTrainingBaseline,
) -> TrainingProfile:
    """Preserve reported estimates and derive only the known recency gap."""
    if (
        baseline.last_run_date is not None
        and baseline.last_run_date > request.as_of_date
    ):
        raise ValueError("last_run_date cannot be after as_of_date")

    limitations = ["Training baseline is self-reported and approximate."]
    if baseline.recent_longest_run_m is None:
        limitations.append("Recent longest run is unknown.")
    if baseline.last_run_date is None:
        limitations.append("Last run date is unknown.")

    return TrainingProfile(
        basis="reported",
        usual_runs_per_week=baseline.usual_runs_per_week,
        weekly_running_distance_m=baseline.approx_weekly_running_distance_m,
        recent_longest_run_m=baseline.recent_longest_run_m,
        recent_training_gap_days=(
            (request.as_of_date - baseline.last_run_date).days
            if baseline.last_run_date is not None
            else None
        ),
        data_limitations=limitations,
    )
