# Backend architecture

## Dependency injection

- The backend owns its composition root and constructs one lazy `Injector` for the application. The React web app does not share the Python container.
- Register replaceable service implementations against their interfaces with `@service(Interface)`. The backend service package imports implementation modules so registrations exist before the injector is built.
- Bind registered services as singletons and inject their dependencies through typed constructors decorated with `@inject` from `shared.di`. Resolve application entry-point dependencies from the injector; services should not reach into the global injector themselves.
- Keep configuration and external clients at the composition root. Pure domain models and deterministic calculations do not need bindings unless they have replaceable dependencies.
- Keep this helper in `apps/backend` until another Python application needs the same generic DI behavior. Each application still owns its own bindings and injector instance.

## Settings

- Centralize backend configuration in `shared.settings.Settings`, reading environment variables and `apps/backend/.env`.
- Include `ENVIRONMENT`, `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_TIMEOUT_SECONDS`; leave the OpenAI key/model unset by default, and require a confirmed supported model before using it.
- Expose the optional `ENVIRONMENT` setting with `is_development` and `is_production` convenience properties.
- Bind one `Settings` instance as a singleton in the backend injector; services receive it through constructor injection. `get_settings()` is available to application entry points.
- Provide an ignored `apps/backend/.env` for local values and a tracked `.env.example` with placeholders. Keep real secrets out of version control; add further fields when a feature needs them.

## Acceptance examples

1. Building the backend injector resolves an interface to its registered implementation.
2. Constructor dependencies are resolved from the same injector, and singleton services return the same instance.
3. The lazy injector does not construct the underlying container until the first resolution.
4. Environment variables populate `Settings`, and all resolutions from one injector return its same settings instance.
