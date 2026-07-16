"""Contracts for governed first-party Runtime assets and the Demo Provider."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import socket
from typing import Any, Mapping
from unittest import mock
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

INVESTMENT_CORE_SKILLS = {
    "company-deep-research",
    "business-model-analysis",
    "financial-statement-analysis",
    "earnings-quality-analysis",
    "valuation-analysis",
    "comps-analysis",
    "earnings-analysis",
    "investment-thesis",
    "bear-case-analysis",
    "catalyst-analysis",
    "source-verification",
    "investment-report",
}

CORE_SKILLS = {"security-identification", *INVESTMENT_CORE_SKILLS}

REQUIRED_SPECS = {
    "research-principles.md",
    "evidence-policy.md",
    "source-policy.md",
    "financial-data-policy.md",
    "valuation-policy.md",
    "risk-policy.md",
    "report-policy.md",
}

SKILL_CONTRACT_TERMS = (
    "objective",
    "responsibility boundary",
    "positive triggers",
    "near-miss negative triggers",
    "inputs",
    "missing-data behavior",
    "used specs",
    "analytical procedure",
    "output contract",
    "source requirements",
    "risk and non-advice boundaries",
    "composition",
    "evals",
)

EXPECTED_WORKFLOW_STEPS = (
    "security-identification",
    "company-deep-research",
    "business-model-analysis",
    "financial-statement-analysis",
    "earnings-quality-analysis",
    "valuation-analysis",
    "comps-analysis",
    "earnings-analysis",
    "investment-thesis",
    "bear-case-analysis",
    "catalyst-analysis",
    "source-verification",
    "investment-report",
)

PROVIDER_METHODS = (
    "identify_security",
    "get_security_profile",
    "get_financial_statements",
    "get_price_history",
    "get_valuation_inputs",
    "get_source_metadata",
    "get_peer_comparables",
    "get_earnings_history",
    "get_catalyst_events",
)

REQUIRED_PROVIDER_METADATA = {
    "as_of_date",
    "currency",
    "market",
    "source",
    "is_demo",
    "warnings",
}

VERSION_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?(?:spec\s+)?version(?:\*\*)?\s*"
    r"[:=-]\s*`?v?([0-9]+(?:\.[0-9]+){1,2})"
)


def _demo_provider_type():
    from investkit.providers.demo import DemoProvider

    return DemoProvider


def _normalize_step(value: str) -> str:
    return re.sub(r"-+", "-", value.strip().lower().replace("_", " ").replace(" ", "-"))


def _workflow_step_ids(workflow: Mapping[str, Any]) -> tuple[str, ...]:
    values = workflow.get("steps", [])
    result: list[str] = []
    for value in values:
        if isinstance(value, str):
            result.append(_normalize_step(value))
        elif isinstance(value, Mapping):
            identifier = value.get("id", value.get("name", ""))
            result.append(_normalize_step(str(identifier)))
    return tuple(result)


def _identifier(record: Mapping[str, Any]) -> str:
    for key in ("security_id", "identifier", "symbol", "ticker", "id"):
        value = record.get(key)
        if value:
            return str(value)
    raise AssertionError("identify_security must return a stable security identifier")


def _contains_none(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, Mapping):
        return any(_contains_none(child) for child in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_none(child) for child in value)
    return False


class FirstPartyAssetContractTests(unittest.TestCase):
    maxDiff = None

    def test_all_runtime_skills_publish_the_complete_contract(self) -> None:
        for skill_name in sorted(CORE_SKILLS):
            with self.subTest(skill=skill_name):
                path = REPOSITORY_ROOT / "skills" / skill_name / "SKILL.md"
                self.assertTrue(path.is_file(), f"missing first-party Skill: {path}")
                text = path.read_text(encoding="utf-8")
                normalized = re.sub(r"[`*_#]", "", text).lower()
                for term in SKILL_CONTRACT_TERMS:
                    self.assertIn(term, normalized)
                self.assertNotIn("third_party/raw", normalized.replace("\\", "/"))
                self.assertNotIn("adapted/skills", normalized.replace("\\", "/"))
                self.assertRegex(normalized, r"no\s+(?:brokerage|order placement|real-money)")

    def test_all_seven_specs_have_explicit_versions_and_stable_checksums(self) -> None:
        actual = {path.name for path in (REPOSITORY_ROOT / "specs").glob("*.md")}
        self.assertEqual(actual, REQUIRED_SPECS)

        checksums: dict[str, str] = {}
        for spec_name in sorted(REQUIRED_SPECS):
            with self.subTest(spec=spec_name):
                path = REPOSITORY_ROOT / "specs" / spec_name
                text = path.read_text(encoding="utf-8")
                self.assertRegex(text, VERSION_RE)
                checksum = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertRegex(checksum, r"^[0-9a-f]{64}$")
                checksums[spec_name] = checksum
        self.assertEqual(len(set(checksums.values())), len(REQUIRED_SPECS))

    def test_company_deep_dive_workflow_declares_the_required_order(self) -> None:
        path = REPOSITORY_ROOT / "workflows/company-deep-dive.json"
        self.assertTrue(path.is_file())
        workflow = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(workflow.get("id"), "company-deep-dive")
        self.assertTrue(workflow.get("version"))
        self.assertEqual(_workflow_step_ids(workflow), EXPECTED_WORKFLOW_STEPS)
        serialized = json.dumps(workflow).lower()
        self.assertIn("company-deep-research", serialized)
        self.assertIn("source-verification", serialized)
        self.assertIn("report", serialized)

    def test_runtime_has_no_trellis_import_or_path_dependency(self) -> None:
        runtime_root = REPOSITORY_ROOT / "src/investkit"
        self.assertTrue(runtime_root.is_dir())
        for path in runtime_root.rglob("*.py"):
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT)):
                text = path.read_text(encoding="utf-8")
                tree = ast.parse(text, filename=str(path))
                imported: list[str] = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported.append(node.module)
                self.assertFalse(any(name.startswith("trellis") for name in imported))
                self.assertNotRegex(text, r"(?i)(?:^|[/\\])\.trellis(?:[/\\]|$)")


class DemoProviderContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = _demo_provider_type()(asset_root=REPOSITORY_ROOT)

    def call_all_methods(self) -> dict[str, Mapping[str, Any]]:
        identity = self.provider.identify_security("demo")
        self.assertIsInstance(identity, Mapping)
        security_id = _identifier(identity)
        return {
            "identify_security": identity,
            "get_security_profile": self.provider.get_security_profile(security_id),
            "get_financial_statements": self.provider.get_financial_statements(security_id),
            "get_price_history": self.provider.get_price_history(security_id),
            "get_valuation_inputs": self.provider.get_valuation_inputs(security_id),
            "get_source_metadata": self.provider.get_source_metadata(security_id),
            "get_peer_comparables": self.provider.get_peer_comparables(security_id),
            "get_earnings_history": self.provider.get_earnings_history(security_id),
            "get_catalyst_events": self.provider.get_catalyst_events(security_id),
        }

    def test_provider_implements_all_nine_operations_and_metadata(self) -> None:
        for method_name in PROVIDER_METHODS:
            self.assertTrue(callable(getattr(self.provider, method_name, None)), method_name)

        responses = self.call_all_methods()
        self.assertEqual(set(responses), set(PROVIDER_METHODS))
        for method_name, response in responses.items():
            with self.subTest(method=method_name):
                self.assertIsInstance(response, Mapping)
                self.assertTrue(REQUIRED_PROVIDER_METADATA.issubset(response))
                self.assertTrue(response["is_demo"])
                self.assertTrue(response["as_of_date"])
                self.assertTrue(response["currency"])
                self.assertTrue(response["market"])
                self.assertTrue(response["source"])
                self.assertTrue(
                    response.get("fixture_version") or response.get("retrieved_at")
                )
                self.assertIsInstance(response["warnings"], list)
                self.assertTrue(response["warnings"])

    def test_provider_is_fully_offline(self) -> None:
        with (
            mock.patch.object(
                socket,
                "create_connection",
                side_effect=AssertionError("network access is forbidden"),
            ),
            mock.patch(
                "urllib.request.urlopen",
                side_effect=AssertionError("network access is forbidden"),
            ),
        ):
            responses = self.call_all_methods()
        self.assertEqual(len(responses), 9)

    def test_fixture_exposes_missing_values_and_actionable_warnings(self) -> None:
        responses = self.call_all_methods()
        self.assertTrue(any(_contains_none(response) for response in responses.values()))
        warnings = " ".join(
            str(warning)
            for response in responses.values()
            for warning in response.get("warnings", [])
        ).lower()
        self.assertRegex(warnings, r"missing|unknown|unavailable|not available")


if __name__ == "__main__":
    unittest.main()
