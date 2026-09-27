# Training plan behavior

The plan helps a runner prepare for a selected 5 km, 10 km, half marathon, or marathon. It is a revisable proposal, not a diagnosis, injury prediction, or guarantee of race performance.

## Planning flow

1. Validate the race goal and user constraints from [domain.md](domain.md).
2. Obtain an available history through [the training data provider](data-sources.md). Compute `TrainingProfile` in application code, preserving coverage and missing data.
3. If essential information is absent, return `needs_more_information`; if the goal cannot reasonably fit the available time and observed baseline, return `goal_needs_revision` with a concrete explanation. Do not force a plan.
4. Produce one structured `PlanResult`. Start with one model request, using only the necessary approved context; additional requests require evidence from tests or evaluation that they improve the result.
5. Validate the structured response and its cross-field rules in application code before returning it. A syntactically valid model response alone is insufficient.

The initial implementation can return a deterministic example result from synthetic data. A live LLM is not required to test domain rules or UI states. Confirm the exact model ID and structured-output support before adding any OpenAI integration; secrets remain server-side.

## Coaching content

- Base recommendations on the observed running pattern, the available training days, and the time until the race. Distinguish observed facts from user reports and proposed workouts in the rationale.
- Provide a weekly focus and daily purpose, with easy work, appropriate recovery, and optional quality or longer runs when the baseline supports them. Explain meaningful changes in load rather than applying a universal percentage rule.
- Express intensity primarily as understandable effort (`easy`, `moderate`, `hard`). Recorded heart rate can add context about internal load alongside distance, duration, and reported fatigue, but session averages alone do not define personal zones or prove improved fitness. When the runner supplies a personal easy-HR range, an easy session may show it as an optional secondary target; otherwise show effort only. Do not require HR, pace, or a predicted finishing time.
- Interpret heart rate in context: terrain, heat, fatigue, and sensor quality may change the reading. Do not infer a medical condition or force the runner to chase a number when perceived effort disagrees.
- Respect maximum session duration when supplied. Do not schedule a training session on an unavailable day. Show the race date and a coherent lead-in to it; do not fabricate a taper for an event too close to plan for.
- Current pain/injury `yes` or fatigue `high` should prevent an aggressive plan and prompt clarification or professional advice as appropriate. `unknown` is not equivalent to `no`.
- State how to adjust or skip a workout when symptoms, unusual fatigue, or missed sessions occur; do not prescribe making up missed volume automatically.

Individualized load and recovery, including subjective responses, are more informative than treating weekly kilometres as a complete measure of readiness. The [IOC consensus on training load and injury](https://bjsm.bmj.com/content/50/17/1030) also notes that no single marker reliably predicts injury. These are design principles, not fixed medical thresholds.

## Acceptance examples for TDD

| Given | Expected |
| --- | --- |
| A complete recent history, a future 10 km race, and three available weekdays | `ready`, a dated plan ending on race day, no conflicting training dates, and an explanation tied to the observed baseline. |
| Partial history or no recent running evidence | `needs_more_information`; never claim a measured zero-volume baseline from missing data. |
| A marathon date too close for the observed baseline | `goal_needs_revision` with a specific reason; no fabricated full plan. The feasibility criteria must be agreed and tested before automation. |
| A user with current pain/injury or high fatigue | No aggressive `ready` plan; request clarification or advise review as appropriate. |
| The model proposes duplicate dates, sessions on unavailable weekdays, or contradictory weekly totals | Reject the proposal rather than rendering it. |
| A missed workout during the plan | Guidance explains that missed volume is not automatically added to the following day. |
| Most recorded runs have no heart-rate reading and no range was supplied | A valid effort-based plan remains possible; no bpm target, fabricated zone, or HR-based readiness claim appears. |
| The runner supplies a valid personal easy-HR range | An easy session may show that range, with an effort cue; a model-proposed range outside the supplied bounds is rejected. |

Exact minimum-history and feasibility thresholds are intentionally undecided: decide them from evidence and examples before writing a scoring algorithm. Do not ask the LLM to make hidden eligibility decisions that cannot be inspected or tested.
