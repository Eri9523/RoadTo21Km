# Product scope and user journey

RoadTo21Km is an open-source, single-user-per-installation planning prototype. A runner chooses a 5 km, 10 km, half marathon, or marathon goal and receives an understandable, adaptable training proposal grounded in available running history and their own constraints. The first usable version runs on fictional activity data; a real source is a later decision under [data-sources.md](data-sources.md).

## One-page journey

1. See the current data source and whether training history is available, incomplete, or unavailable.
2. Review the observed baseline and its coverage, including how many runs have heart-rate data. Choose race distance and date; optionally set a time goal. Provide available weekdays, session-time limit, current pain/fatigue information, and an optional personal easy-HR range.
3. Request a plan. See the generation state and then either a plan, the specific missing information, or a reason to revise the goal.
4. Inspect weekly focus and individual sessions, including rest, intensity, purpose, and adjustment guidance. Change inputs and regenerate without losing visibility of the current state.

The initial UI can be a single React route. Use clear headings and labeled controls, keyboard-operable interaction, visible loading/error states, and text explanations alongside any chart or color. Distinguish *observed*, *reported*, and *proposed* values. Never display an unsupported readiness score or unexplained risk label.

## MVP boundaries

- In: synthetic-history provider, validated goal and constraints, computed history profile, structured plan result, and one-page rendering of all result states.
- Later, once independently verified: a permitted real-data provider and an optional live model call with validated structured output.
- Out of scope for the first slice: social accounts, multi-user hosting, Strava API-to-LLM ingestion, GPS maps, automatic injury diagnoses, and guaranteed race-time predictions.

## Acceptance examples

| Scenario | Observable behavior |
| --- | --- |
| First visit | The page identifies synthetic data as synthetic and explains the next action. |
| Valid request | The runner can review inputs, submit once, see progress, and read either the generated plan or a specific next step. |
| Missing or invalid race date, non-positive target time, or no available weekdays | The relevant field displays a recoverable error without generating a plan. A positive but unrealistic target is handled as `goal_needs_revision`. |
| History unavailable or incomplete | The page explains coverage limits; it does not present missing runs as evidence of inactivity. |
| Model or provider failure | The page reports the failure and permits retry; it does not show a stale result as newly generated. |
| Plan displayed | Dates, session purpose, effort, rest, and rationale can be read without relying on color alone or opening another route. |
| Heart-rate data missing or a personal range not supplied | The plan remains readable through effort cues; the page identifies missing HR data instead of showing invented zones or a readiness score. |

The backend contract is specified in [domain.md](domain.md), and plan validity in [training-plan.md](training-plan.md). Tests should start with these acceptance examples rather than a screenshot or a live API call.
