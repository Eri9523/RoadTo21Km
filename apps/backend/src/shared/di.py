"""Service registration and lazy dependency injector."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from injector import Injector, inject, singleton

_service_registry: dict[type, type] = {}


def service(protocol: type) -> Callable[[type], type]:
    """Register a class as the implementation for a protocol."""

    def decorator(implementation: type) -> type:
        _service_registry[protocol] = implementation
        return implementation

    return decorator


def build_injector() -> Injector:
    """Build an Injector with all registered service implementations."""
    import services  # noqa: F401 — trigger @service registration

    def configure(binder: Any) -> None:
        from .settings import Settings

        binder.bind(Settings, to=Settings(), scope=singleton)
        for protocol, implementation in _service_registry.items():
            binder.bind(protocol, to=implementation, scope=singleton)

    return Injector([configure])


class LazyInjector:
    """Create the underlying Injector on its first use."""

    def __init__(self, builder: Callable[[], Injector]) -> None:
        self._builder = builder
        self._instance: Injector | None = None

    def _resolve(self) -> Injector:
        if self._instance is None:
            self._instance = self._builder()
        return self._instance

    def get(self, dependency: Any) -> Any:
        """Resolve a dependency by its type."""
        return self._resolve().get(dependency)


injector = LazyInjector(build_injector)
