from __future__ import annotations

import unittest
from typing import Protocol

from shared.di import LazyInjector, build_injector, inject, service
from shared.settings import Settings


class Helper(Protocol):
    pass


class Greeting(Protocol):
    def message(self) -> str: ...


@service(Helper)
class HelperImpl:
    pass


@service(Greeting)
class GreetingImpl:
    @inject
    def __init__(self, helper: Helper) -> None:
        self._helper = helper

    def message(self) -> str:
        return "ready"


class DependencyInjectionTests(unittest.TestCase):
    def test_build_injector_resolves_registered_services_and_dependencies(self) -> None:
        container = build_injector()

        greeting = container.get(Greeting)
        self.assertIsInstance(greeting, GreetingImpl)
        self.assertIs(greeting, container.get(Greeting))
        self.assertIsInstance(greeting._helper, HelperImpl)
        self.assertEqual(greeting.message(), "ready")

    def test_lazy_injector_builds_only_when_first_resolved(self) -> None:
        builds = 0

        def builder():
            nonlocal builds
            builds += 1
            return build_injector()

        lazy = LazyInjector(builder)
        self.assertEqual(builds, 0)
        lazy.get(Greeting)
        self.assertEqual(builds, 1)

    def test_injector_binds_one_settings_instance(self) -> None:
        container = build_injector()

        self.assertIsInstance(container.get(Settings), Settings)
        self.assertIs(container.get(Settings), container.get(Settings))


if __name__ == "__main__":
    unittest.main()
