"""Security contracts for optional project-local provider environment loading."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


class ProjectEnvironmentTests(unittest.TestCase):
    def test_loads_only_allowlisted_credentials_without_overriding_process_env(self) -> None:
        from investkit.environment import load_provider_environment

        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            path = project / ".env"
            path.write_text("MX_APIKEY='file-mx'\nGF_SKILLS_APIKEY=file-gf\n", encoding="utf-8")
            path.chmod(0o600)
            with mock.patch.dict(os.environ, {"MX_APIKEY": "process-mx"}, clear=True):
                loaded = load_provider_environment(project)
                self.assertEqual(os.environ["MX_APIKEY"], "process-mx")
                self.assertEqual(os.environ["GF_SKILLS_APIKEY"], "file-gf")
            self.assertEqual(loaded, ("GF_SKILLS_APIKEY",))

    def test_rejects_readable_symlink_oversized_and_unknown_syntax(self) -> None:
        from investkit.environment import ProviderEnvironmentError, load_provider_environment

        cases = (
            ("UNKNOWN_KEY=value\n", 0o600),
            ("CICCWM_API_KEY=value：\n", 0o600),
            ("GF_SKILLS_APIKEY=value\n", 0o644),
            ("GF_SKILLS_APIKEY=" + ("x" * 70_000), 0o600),
        )
        for content, mode in cases:
            with tempfile.TemporaryDirectory() as temp:
                project = Path(temp)
                path = project / ".env"
                path.write_text(content, encoding="utf-8")
                path.chmod(mode)
                with self.subTest(mode=mode, size=len(content)), self.assertRaises(
                    ProviderEnvironmentError
                ):
                    load_provider_environment(project)
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            target = project / "secret.env"
            target.write_text("GF_SKILLS_APIKEY=value\n", encoding="utf-8")
            target.chmod(0o600)
            (project / ".env").symlink_to(target)
            with self.assertRaises(ProviderEnvironmentError):
                load_provider_environment(project)


if __name__ == "__main__":
    unittest.main()
