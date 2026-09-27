# Domain model

Model what the runner reports, what an activity source observes, and what the planner proposes as separate concepts. Input and output models are implemented as Pydantic models under `apps/backend/src/models`.

## Input models

| Model | Fields | Meaning |
| --- | --- | --- |
| `RunActivity` | `source_id: str`, `started_at: datetime`, `distance_m: int`, `moving_time_s: int`, `elevation_gain_m: float | None`, `average_heart_rate_bpm: int | None` | One observed run. `source_id` identifies a record within one provider, not a public URL. Heart rate in beats per minute (bpm) is an optional measured session average, not an intensity zone. |
| `TrainingHistory` | `provider_id: str`, `from_date: date`, `through_date: date`, `runs: list[RunActivity]`, `coverage: complete | partial`, `coverage_note: str | None` | A provider's available running history for an inclusive date range. An empty result is not automatically proof of inactivity. |
| `ReportedTrainingBaseline` | `usual_runs_per_week: float`, `approx_weekly_running_distance_m: int`, `recent_longest_run_m: int | None`, `last_run_date: date | None` | A runner's approximate summary of the 28 calendar days ending on the request's `as_of_date` (inclusive). Runs per week is a typical estimate in `[0, 7]`; all supplied distances are non-negative metres. `recent_longest_run_m` refers to this 28-day period. The longest run and last-run date may be unknown (`None`). These are user reports, not reconstructed activities or measured coverage. |
| `RaceGoal` | `distance_m: 5000 | 10000 | 21098 | 42195`, `race_date: date`, `goal_type: finish | target_time`, `target_time_s: int | None` | Selected event. `21098` m is the nearest whole-metre representation of the official 21.0975 km half marathon; use `42195` m for the marathon. A target time is present only for `target_time`. |
| `HeartRateRange` | `min_bpm: int`, `max_bpm: int` | An optional personal intensity range supplied by the runner, with `min_bpm < max_bpm`; never calculated from age or a workout's highest reading. |
| `RunnerConstraints` | `available_weekdays: set[int]`, `max_session_minutes: int | None`, `experience: beginner | intermediate | advanced`, `current_pain_or_injury: yes | no | unknown`, `fatigue: low | moderate | high | unknown`, `easy_heart_rate_range: HeartRateRange | None` | Explicitly supplied by the runner; weekdays are ISO 1 (Monday) through 7 (Sunday). Never infer injury, fatigue, availability, or a personal HR range from activity data. |
| `PlanRequest` | `goal: RaceGoal`, `constraints: RunnerConstraints`, `as_of_date: date` | Goal and runner constraints supplied by the user or application. The use case receives either a `ReportedTrainingBaseline` or, when a future provider is enabled, a `TrainingHistory` separately. |

When an activity provider is added later, only `RunActivity` is initially required from it. Cross-training may be added when a specific planning rule needs it; do not treat cycling distance as running distance. Do not require heart-rate data to generate a plan.

## Derived, deterministic context

`TrainingProfile` is deterministic context derived from either a `ReportedTrainingBaseline` or a sufficiently covered `TrainingHistory`, not invented by a model. It records its basis so reported estimates are never presented as observed activity:

| Field | Definition |
| --- | --- |
| `basis` | `reported` for a self-reported summary or `observed` for activity-provider data. |
| `usual_runs_per_week` | Runner-reported estimate for `reported`; derived from observed runs only when the analysis window has sufficient coverage. |
| `weekly_running_distance_m` | Approximate user-reported value for `reported`; observed per-calendar-week distance for `observed`, including zero weeks only when coverage is complete. |
| `recent_longest_run_m` | User-reported value or `None` when unknown for `reported`; maximum observed run in the analysis window for `observed`. |
| `recent_training_gap_days` | Derived from `last_run_date` when supplied for `reported`; derived from the last observed run only if coverage is complete through `as_of_date` for `observed`. |
| `heart_rate_coverage` | Available only for observed activities with run-level heart-rate readings; unknown for a reported summary. Never infer a fraction from summary data. |
| `data_limitations` | Missing, approximate, or partial information relevant to interpretation. |

The manual baseline summarizes the 28 calendar days ending on `as_of_date`; its weekly values are estimates, not per-week measurements. A supplied `last_run_date` must not be after `as_of_date`. For observed history, the recent analysis window and its minimum coverage must be specified and tested before computing an observed baseline; do not silently call partial history complete. Distances use metres in backend contracts, durations seconds in recorded/goal data and minutes in planned sessions, dates ISO 8601, and pace only seconds per kilometre when explicitly supported by evidence. The UI may accept/display kilometres but converts them to metres at the API boundary.

## Proposed output models

| Model | Fields | Meaning |
| --- | --- | --- |
| `TrainingSession` | `date: date`, `kind: easy | long | quality | recovery | rest | cross_training`, `duration_minutes: int | None`, `distance_m: int | None`, `effort: easy | moderate | hard | none`, `target_heart_rate_range: HeartRateRange | None`, `instructions: str`, `purpose: str` | A single actionable day. A rest day has no duration, distance, or HR target and `effort=none`. A training day has at least duration or distance. HR is supplementary to effort and is only set when the runner supplied an appropriate personal range. |
| `TrainingWeek` | `week_start: date`, `phase: base | build | taper | race`, `sessions: list[TrainingSession]`, `planned_running_distance_m: int | None`, `focus: str` | A calendar week. Distance total is calculated from sessions only when all running sessions specify distance; otherwise it is absent, not guessed. |
| `TrainingPlan` | `goal: RaceGoal`, `summary: str`, `rationale: list[str]`, `weeks: list[TrainingWeek]`, `adjustment_guidance: list[str]` | The proposed plan and its explanation. |
| `PlanResult` | `status: ready | needs_more_information | goal_needs_revision`, `plan: TrainingPlan | None`, `questions: list[str]`, `reason: str | None` | One response shape for the web page. Only `ready` contains a plan; other states tell the runner what to do next. |

## Boundaries and invariants

- The UI submits reported baseline data separately from goal/constraints. A future provider returns observed data; the profile calculator preserves each basis; the planner proposes sessions; a validator checks the proposal; the UI formats the result. Do not convert a reported summary into fabricated `RunActivity` records.
- A planning invocation uses one training-data basis: a reported baseline or observed history. Do not blend the two without explicit reconciliation rules.
- Reject negative distances, non-positive moving times for runs, invalid dates, duplicate `(provider, source_id)` records, and target times without `goal_type=target_time`.
- A `ready` result has a plan and no unanswered questions. Other statuses have no plan and a useful reason or question.
- Planned dates are unique, ordered, within the planning interval, and compatible with available weekdays. The race date is the sole exception to weekday availability when the user has explicitly chosen it.
- Do not invent metrics or exact pace targets when source data or user context is missing. Null means unknown; zero means measured zero.
- Reject non-positive heart-rate readings and inverted personal ranges. A missing sensor reading stays null; do not derive maximum HR, training zones, cardiac diagnoses, or heart-rate trends from session averages alone. A high or low reading by itself is not an injury-risk score.

## First TDD examples

1. A valid four-week reported baseline creates a `reported` profile without individual activity records; frequency and weekly distance are estimates, not precision measurements.
2. An unknown longest run or last-run date remains `None`; neither is replaced by zero or inferred.
3. A reported summary does not claim exact per-week totals or heart-rate coverage.
4. Runs per week outside `[0, 7]` and negative reported distances are rejected; zero remains a reported zero, not missing data.
5. A supplied last-run date after `as_of_date` is rejected when validating the request and baseline together.
6. An observed history with three runs in one week produces the correct count, total distance, and longest run when coverage permits.
7. Duplicate `(provider_id, source_id)` records are rejected before calculating observed weekly distance.
8. A rest session with distance, or a `ready` result without a plan, is rejected.
9. Missing heart-rate readings never prevent an otherwise valid effort-based plan.
10. An invalid personal HR range is rejected; without a supplied range, sessions have no bpm target.
