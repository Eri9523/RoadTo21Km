# Product specifications

These specifications are the starting point for work on RoadTo21Km. Read them before changing the application. They describe intended behavior, not implemented features.

| Read in this order | Purpose |
| --- | --- |
| [product.md](product.md) | User journey, scope, and visible states |
| [domain.md](domain.md) | Class model, units, and data boundaries |
| [training-plan.md](training-plan.md) | Planning rules and structured output |
| [data-sources.md](data-sources.md) | Training data provider and integration constraints |

## Working agreement

1. Change the relevant specification and its acceptance examples before changing behavior.
2. Write a failing focused test for an acceptance example, then implement the smallest change that passes it.
3. Keep source-specific fields out of the domain model and model-generated fields out of measured history.
4. Keep specifications in English. Keep personal activity data, tokens, and API keys out of the repository.

The first usable slice uses synthetic running history and a deterministic example plan. A real data source or model call is a later, separately verified slice. See [data-sources.md](data-sources.md) before adding either.
