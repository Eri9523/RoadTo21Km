# Domain model

Model what the runner knows, what the training history shows, and what the planner proposes as separate concepts. These are proposed Python/Pydantic contracts; no production classes exist yet.

## Input models

| Model | Fields | Meaning |
| --- | --- | --- |
| `RunActivity` | `source_id: str`, `started_at: datetime`, `distance_m: int`, `moving_time_s: int`, `elevation_gain_m: float | None`, `average_heart_rate_bpm: int | None` | One observed run. `source_id` identifies a record within one provider, not a public URL. Heart rate in beats per minute (bpm) is an optional measured session average, not an intensity zone. |
| `TrainingHistory` | `provider_id: str`, `from_date: date`, `through_date: date`, `runs: list[RunActivity]`, `coverage: complete | partial`, `coverage_note: str | None` | A provider's available running history for an inclusive date range. An empty result is not automatically proof of inactivity. |
| `RaceGoal` | `distance_m: 5000 | 10000 | 21098 | 42195`, `race_date: date`, `goal_type: finish | target_time`, `target_time_s: int | None` | Selected event. `21098` m is the nearest whole-metre representation of the official 21.0975 km half marathon; use `42195` m for the marathon. A target time is present only for `target_time`. |
| `HeartRateRange` | `min_bpm: int`, `max_bpm: int` | An optional personal intensity range supplied by the runner, with `min_bpm < max_bpm`; never calculated from age or a workout's highest reading. |
| `RunnerConstraints` | `available_weekdays: set[int]`, `max_session_minutes: int | None`, `experience: beginner | intermediate | advanced`, `current_pain_or_injury: yes | no | unknown`, `fatigue: low | moderate | high | unknown`, `easy_heart_rate_range: HeartRateRange | None` | Explicitly supplied by the runner; weekdays are ISO 1 (Monday) through 7 (Sunday). Never infer injury, fatigue, availability, or a personal HR range from activity data. |
| `PlanRequest` | `goal: RaceGoal`, `constraints: RunnerConstraints`, `as_of_date: date` | Inputs supplied by the user or application before loading history. The provider supplies `TrainingHistory` separately. |

Only `RunActivity` is initially required from a data provider. Cross-training may be added when a specific planning rule needs it; do not treat cycling distance as running distance. Do not require heart-rate data to generate a plan.

## Derived, deterministic context

`TrainingProfile` is computed from `TrainingHistory`, not invented by the model:

| Field | Definition |
| --- | --- |
| `observed_weeks` | Calendar weeks covered by the requested period; mark partial weeks or partial provider coverage. |
| `weekly_running_distance_m` | Running distance by calendar week, including zero-activity weeks only when coverage is complete. |
| `weekly_run_count` | Number of runs per calendar week under the same coverage rule. |
| `recent_longest_run_m` | Maximum run distance in the recent analysis window; absent when no runs were observed. |
| `recent_training_gap_days` | Days since the last observed run, if coverage is complete through `as_of_date`. |
| `heart_rate_coverage` | Count of runs with a valid average heart-rate reading out of all observed runs; unknown when there are no runs, not `0/0`. Report as a fraction, not a readiness score. |
| `data_limitations` | Missing coverage and missing optional measurements relevant to interpretation. |

The recent analysis window and its minimum coverage must be specified and tested before implementation; do not silently call a partial history a complete training baseline. Distances use metres, durations seconds in recorded/goal data and minutes in planned sessions, dates ISO 8601, and pace only seconds per kilometre when explicitly supported by evidence. Display formatting belongs to the UI.

## Proposed output models

| Model | Fields | Meaning |
| --- | --- | --- |
| `TrainingSession` | `date: date`, `kind: easy | long | quality | recovery | rest | cross_training`, `duration_minutes: int | None`, `distance_m: int | None`, `effort: easy | moderate | hard | none`, `target_heart_rate_range: HeartRateRange | None`, `instructions: str`, `purpose: str` | A single actionable day. A rest day has no duration, distance, or HR target and `effort=none`. A training day has at least duration or distance. HR is supplementary to effort and is only set when the runner supplied an appropriate personal range. |
| `TrainingWeek` | `week_start: date`, `phase: base | build | taper | race`, `sessions: list[TrainingSession]`, `planned_running_distance_m: int | None`, `focus: str` | A calendar week. Distance total is calculated from sessions only when all running sessions specify distance; otherwise it is absent, not guessed. |
| `TrainingPlan` | `goal: RaceGoal`, `summary: str`, `rationale: list[str]`, `weeks: list[TrainingWeek]`, `adjustment_guidance: list[str]` | The proposed plan and its explanation. |
| `PlanResult` | `status: ready | needs_more_information | goal_needs_revision`, `plan: TrainingPlan | None`, `questions: list[str]`, `reason: str | None` | One response shape for the web page. Only `ready` contains a plan; other states tell the runner what to do next. |

## Boundaries and invariants

- The provider returns observed data; the profile calculator derives metrics; the planner proposes sessions; a validator checks the proposal; the UI formats the result. None of these roles owns another role's data.
- Reject negative distances, non-positive moving times for runs, invalid dates, duplicate `(provider, source_id)` records, and target times without `goal_type=target_time`.
- A `ready` result has a plan and no unanswered questions. Other statuses have no plan and a useful reason or question.
- Planned dates are unique, ordered, within the planning interval, and compatible with available weekdays. The race date is the sole exception to weekday availability when the user has explicitly chosen it.
- Do not invent metrics or exact pace targets when source data or user context is missing. Null means unknown; zero means measured zero.
- Reject non-positive heart-rate readings and inverted personal ranges. A missing sensor reading stays null; do not derive maximum HR, training zones, cardiac diagnoses, or heart-rate trends from session averages alone. A high or low reading by itself is not an injury-risk score.

## First TDD examples

1. A complete history with three runs in one week produces the correct count, total distance, and longest run.
2. A partial history with no runs does not produce a zero-volume baseline.
3. Duplicate `(provider_id, source_id)` records are rejected before calculating weekly distance.
4. A rest session with distance, or a `ready` result without a plan, is rejected.
5. Missing heart-rate readings leave `heart_rate_coverage` incomplete and never prevent an otherwise valid plan.
6. An invalid personal HR range is rejected; without a supplied range, sessions have no bpm target.
