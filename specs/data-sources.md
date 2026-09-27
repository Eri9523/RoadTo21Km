# Training data sources

The first user flow accepts a short, approximate training summary entered manually; it does not require a connected activity provider or individual activity records. `ReportedTrainingBaseline` is the runner's estimate for the 28 calendar days ending on `as_of_date` (inclusive). Keep this reported input separate from observed `TrainingHistory` returned by any provider. Synthetic fixtures are for tests and demonstrations, not the source for the manual flow. A real provider requires its own permission and data-handling review before implementation.

## Manual baseline

The planning use case receives `PlanRequest` and `ReportedTrainingBaseline` as two separate domain models. The web API may wrap them in one JSON request, but does not merge the baseline fields into `PlanRequest`. The runner estimates typical runs per week and weekly running distance for the 28-day period; label both as approximate. The longest run during that period and date of the last run are optional and remain unknown when the runner does not know them. The client may display kilometres, but backend/API values use metres.

The JSON property names and semantics are the cross-language contract for the first slice. Keep the TypeScript form types in the web app and the Pydantic domain types in the backend; do not add a shared package for this small payload. Generate web types from an API schema only when the backend HTTP contract is introduced.

Do not expand summary values into fabricated `RunActivity` records or report provider-style coverage/heart-rate percentages. Preserve that the values were reported and approximate when computing the profile and explaining a plan.

## Future provider contract

Conceptual Python interface, located alongside the backend's service interfaces when implemented:

```python
from datetime import date
from typing import Protocol


class TrainingDataProvider(Protocol):
    def get_history(self, from_date: date, through_date: date) -> TrainingHistory: ...
```

`TrainingHistory` and `RunActivity` are defined in [domain.md](domain.md). This is a single-user installation: no speculative user repository or multi-tenant provider API is needed. A provider maps its own records into these models and reports partial coverage explicitly. Authentication, pagination, retries, and vendor-specific fields remain inside that provider. An unavailable provider returns a distinct integration error, not an empty complete history.

## Fixtures and tests

- A synthetic history fixture supplies fictional observed runs for repeatable tests and demonstrations; it is not the default runtime input.
- Manual-input tests verify non-negative values, valid runs-per-week range, preservation of unknown optional fields, and the distinction between reported and observed data.
- Future provider contract tests verify inclusive date filtering, unit conversion, stable identity, empty complete history versus missing coverage, and provider failure.
- A provider preserves measured average heart rate in bpm when available and `None` when missing; it does not synthesize zone boundaries or replace a missing reading with zero.
- The initial profile calculator and planner consume `ReportedTrainingBaseline` directly; they do not need network access or a vendor SDK. Later observed-history tests can use `TrainingHistory` directly.

## Real-data gate

As of the [Strava API Policy effective June 1, 2026](https://www.strava.com/legal/api_policy), API-derived Strava data, including aggregates, may not be used to operate an AI application (§5.3). Do not implement a Strava API-to-LLM provider or an unofficial Strava MCP server. The policy describes personal use of an athlete's own data via **Strava's official MCP** for subscribers (§3.5), but its availability and integration requirements have not been verified for this app. A public source repository does not grant access to another person's data. Each installation would need its own authorized connection, and no shared credentials or hosted relay.

Before adding any real-data provider, document its official access path, permitted uses with the chosen model, authentication flow, data minimization, retention/deletion behavior, and failure states. Do not commit real training histories, tokens, `.env` files, or model prompts containing personal data. Treat legal and platform terms as external constraints that may change, not assumptions a provider can bypass.
