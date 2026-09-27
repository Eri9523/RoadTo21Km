# Product scope and user journey

RoadTo21Km is an open-source, single-user-per-installation planning prototype. A runner chooses a 5 km, 10 km, half marathon, or marathon goal and receives an understandable, adaptable training proposal based on a short self-reported running baseline and their own constraints. The first usable version does not require connecting an activity account or entering individual runs. A real activity source is a later decision under [data-sources.md](data-sources.md).

## One-page journey

1. Enter an approximate summary of running over the previous four weeks: usual runs per week and approximate weekly running distance. The longest recent run and date of the last run may be left unknown.
2. Choose race distance and date; optionally set a time goal. Provide available weekdays, session-time limit, current pain/fatigue information, and an optional personal easy-HR range.
3. Request a plan. See the generation state and then either a plan, the specific missing information, or a reason to revise the goal.
4. Inspect weekly focus and individual sessions, including rest, intensity, purpose, and adjustment guidance. Change inputs and regenerate without losing visibility of the current state.

The initial UI can be a single React route. Use clear headings and labeled controls, keyboard-operable interaction, visible loading/error states, and text explanations alongside any chart or color. Label baseline values as *reported*, not *observed*, and distinguish them from *proposed* sessions. Never display an unsupported readiness score or unexplained risk label.

## MVP boundaries

- In: manually reported four-week running baseline, validated goal and constraints, computed profile that preserves reported/unknown values, deterministic structured plan result, and one-page rendering of all result states. Synthetic fixtures support tests and demonstrations only.
- Later, once independently verified: a permitted real-data provider and an optional live model call with validated structured output.
- Out of scope for the first slice: social accounts, multi-user hosting, Strava API-to-LLM ingestion, GPS maps, automatic injury diagnoses, and guaranteed race-time predictions.

## Acceptance examples

| Scenario | Observable behavior |
| --- | --- |
| First visit | The page explains that the runner can provide approximate training data without connecting an account or listing individual runs. |
| Valid request | The runner can review the self-reported baseline and constraints, submit once, see progress, and read either the generated plan or a specific next step. |
| Missing or invalid race date, non-positive target time, or no available weekdays | The relevant field displays a recoverable error without generating a plan. A positive but unrealistic target is handled as `goal_needs_revision`. |
| The longest run or last-run date is unknown | The page preserves it as unknown; it does not turn missing input into zero or claim complete activity coverage. |
| Model or provider failure | The page reports the failure and permits retry; it does not show a stale result as newly generated. |
| Plan displayed | Dates, session purpose, effort, rest, and rationale can be read without relying on color alone or opening another route. |
| Activity-level heart-rate data is not supplied, or no personal range is set | The plan remains readable through effort cues; the page does not invent HR coverage, zones, or a readiness score. |

The backend contract is specified in [domain.md](domain.md), and plan validity in [training-plan.md](training-plan.md). Tests should start with these acceptance examples rather than a screenshot or a live API call.
