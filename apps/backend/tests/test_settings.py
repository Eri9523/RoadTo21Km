from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from shared.settings import Settings, get_settings


class SettingsTests(unittest.TestCase):
    def test_defaults_environment_to_none(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)

        self.assertIsNone(settings.ENVIRONMENT)
        self.assertIsNone(settings.OPENAI_API_KEY)
        self.assertIsNone(settings.OPENAI_MODEL)
        self.assertEqual(settings.OPENAI_TIMEOUT_SECONDS, 120.0)
        self.assertFalse(settings.is_development)
        self.assertFalse(settings.is_production)

    def test_environment_variable_overrides_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "ENVIRONMENT=from-file\n"
                "OPENAI_API_KEY=test-key\n"
                "OPENAI_MODEL=test-model\n"
                "OPENAI_TIMEOUT_SECONDS=45\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {"ENVIRONMENT": "from-environment"},
                clear=True,
            ):
                settings = Settings(_env_file=env_file)

        self.assertEqual(settings.ENVIRONMENT, "from-environment")
        self.assertEqual(settings.OPENAI_API_KEY, "test-key")
        self.assertEqual(settings.OPENAI_MODEL, "test-model")
        self.assertEqual(settings.OPENAI_TIMEOUT_SECONDS, 45.0)

    def test_environment_helpers(self) -> None:
        self.assertTrue(Settings(ENVIRONMENT="development").is_development)
        self.assertTrue(Settings(ENVIRONMENT="production").is_production)

    def test_get_settings_returns_the_injector_singleton(self) -> None:
        self.assertIs(get_settings(), get_settings())


if __name__ == "__main__":
    unittest.main()
