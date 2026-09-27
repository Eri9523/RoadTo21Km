# Training data sources

The planning domain depends on a small training-history contract, not on Strava or any particular vendor. The first provider uses synthetic fixtures. A real provider requires its own permission and data-handling review before implementation.

## Provider contract

Conceptual Python interface, located alongside the backend's service interfaces when implemented:

```python
from datetime import date
from typing import Protocol


class TrainingDataProvider(Protocol):
    def get_history(self, from_date: date, through_date: date) -> TrainingHistory: ...
```

`TrainingHistory` and `RunActivity` are defined in [domain.md](domain.md). This is a single-user installation: no speculative user repository or multi-tenant provider API is needed. A provider maps its own records into these models and reports partial coverage explicitly. Authentication, pagination, retries, and vendor-specific fields remain inside that provider. An unavailable provider returns a distinct integration error, not an empty complete history.

## First implementation and tests

- `FixtureTrainingDataProvider` supplies synthetic runs for repeatable tests, demonstrations, and UI development. Fixtures are fictional and safe to commit.
- Contract tests verify inclusive date filtering, unit conversion, stable identity, empty complete history versus missing coverage, and provider failure.
- A provider preserves measured average heart rate in bpm when available and `None` when missing; it does not synthesize zone boundaries or replace a missing reading with zero.
- The profile calculator and planner tests use `TrainingHistory` directly; they do not need network access or a vendor SDK.

## Real-data gate

As of the [Strava API Policy effective June 1, 2026](https://www.strava.com/legal/api_policy), API-derived Strava data, including aggregates, may not be used to operate an AI application (§5.3). Do not implement a Strava API-to-LLM provider or an unofficial Strava MCP server. The policy describes personal use of an athlete's own data via **Strava's official MCP** for subscribers (§3.5), but its availability and integration requirements have not been verified for this app. A public source repository does not grant access to another person's data. Each installation would need its own authorized connection, and no shared credentials or hosted relay.

Before adding any real-data provider, document its official access path, permitted uses with the chosen model, authentication flow, data minimization, retention/deletion behavior, and failure states. Do not commit real training histories, tokens, `.env` files, or model prompts containing personal data. Treat legal and platform terms as external constraints that may change, not assumptions a provider can bypass.
