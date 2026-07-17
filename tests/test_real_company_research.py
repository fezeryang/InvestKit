"""Acceptance contracts for the provider-neutral real-company research path."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any
from unittest import mock
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OPERATION_NAMES = (
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


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _source(source_id: str, title: str) -> dict[str, Any]:
    today = date.today().isoformat()
    return {
        "source_id": source_id,
        "publisher": "Example Issuer",
        "title": title,
        "source_type": "issuer-filing",
        "locator": f"https://example.invalid/{source_id}",
        "publication_date": today,
        "as_of_date": today,
        "retrieved_at": _timestamp(),
        "quality": "high",
        "freshness": "current",
        "access_notes": "Public issuer material; locator metadata only.",
        "license_notes": "Reuse status must be confirmed by the analyst.",
    }


def valid_bundle() -> dict[str, Any]:
    """Return a deliberately generic bundle with no Aurora/tender concepts."""

    today = date.today().isoformat()
    sources = [
        _source("issuer-profile", "Annual report company profile"),
        _source("issuer-financials", "Annual report financial statements"),
        _source("issuer-market", "Analyst-supplied dated market observation"),
    ]
    common = {"warnings": ["User-supplied imported data was not independently fetched."]}
    operations: dict[str, Any] = {
        "identify_security": {
            "source_ids": ["issuer-profile"],
            "data": {
                "security_id": "US-EXAMPLE-XMPL",
                "ticker": "XMPL",
                "legal_name": "Example Software Holdings, Inc.",
                "exchange": "NASDAQ",
                "aliases": ["Example Software"],
            },
            **common,
        },
        "get_security_profile": {
            "source_ids": ["issuer-profile"],
            "data": {
                "business_model": "Subscription software and support services.",
                "segments": ["Software", "Support"],
                "products": ["Cloud platform"],
                "customers": "Enterprise customers",
                "suppliers": "Cloud infrastructure providers",
                "geographies": ["United States"],
                "competitive_position": "Competes on workflow depth and integration.",
                "business_risks": ["Customer concentration", "Cloud hosting costs"],
                "revenue_model": "subscription",
                "payer": "enterprise customers",
                "value_proposition": "workflow automation",
                "revenue_components": {"subscription": 0.82, "support": 0.18},
                "order_to_cash": None,
                "employee_count": None,
                "customer_concentration_percent": None,
                "research_drivers": ["renewal rates", "operating cash conversion"],
            },
            **common,
        },
        "get_financial_statements": {
            "source_ids": ["issuer-financials"],
            "data": {
                "accounting_basis": "US GAAP",
                "period_type": "annual",
                "units": "USD millions",
                "periods": [
                    {
                        "fiscal_year": "2023",
                        "revenue": 900.0,
                        "gross_profit": 630.0,
                        "operating_income": 90.0,
                        "net_income": 68.0,
                        "cash_from_operations": 115.0,
                        "total_assets": 1500.0,
                        "cash_and_equivalents": 210.0,
                        "total_debt": 180.0,
                        "total_equity": 760.0,
                        "accounts_receivable": 120.0,
                        "inventory": None,
                        "accounts_payable": 40.0,
                    },
                    {
                        "fiscal_year": "2024",
                        "revenue": 1020.0,
                        "gross_profit": 735.0,
                        "operating_income": 128.0,
                        "net_income": 96.0,
                        "cash_from_operations": 154.0,
                        "total_assets": 1650.0,
                        "cash_and_equivalents": 260.0,
                        "total_debt": 160.0,
                        "total_equity": 860.0,
                        "accounts_receivable": 135.0,
                        "inventory": None,
                        "accounts_payable": 48.0,
                    },
                ],
            },
            **common,
        },
        "get_price_history": {
            "source_ids": [],
            "data": {"observations": None, "latest_price": None},
            **common,
        },
        "get_valuation_inputs": {
            "source_ids": ["issuer-financials"],
            "data": {
                "forecast_unlevered_free_cash_flow": None,
                "wacc": None,
                "terminal_growth": None,
                "diluted_shares": None,
                "cash": 260.0,
                "total_debt": 160.0,
                "scenario_assumptions": None,
                "sensitivity_wacc_values": None,
                "sensitivity_terminal_growth_values": None,
            },
            **common,
        },
        "get_source_metadata": {
            "source_ids": [source["source_id"] for source in sources],
            "data": {"sources": deepcopy(sources), "limitations": ["No live acquisition."]},
            **common,
        },
        "get_peer_comparables": {
            "source_ids": [],
            "data": {"peers": None, "selection_method": None},
            **common,
        },
        "get_earnings_history": {
            "source_ids": ["issuer-financials"],
            "data": {"events": None, "transcript_available": False},
            **common,
        },
        "get_catalyst_events": {
            "source_ids": [],
            "data": {"events": None},
            **common,
        },
    }
    return {
        "schema_version": "1.0",
        "bundle_version": "example-2024-annual-v1",
        "created_at": _timestamp(),
        "retrieved_at": _timestamp(),
        "as_of_date": today,
        "currency": "USD",
        "market": "NASDAQ",
        "status": "imported",
        "warnings": [
            "The bundle was prepared by the user and is not independently guaranteed."
        ],
        "security": deepcopy(operations["identify_security"]["data"]),
        "sources": sources,
        "operations": operations,
    }


def _write_bundle(path: Path, value: dict[str, Any] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value or valid_bundle(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


class FileProviderContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="investkit-import-provider-"
        )
        self.project_root = Path(self._temporary_directory.name) / "project"
        self.project_root.mkdir()
        self.bundle_path = _write_bundle(self.project_root / "inputs/company.json")

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def provider(self):
        from investkit.providers.file import FileProvider

        return FileProvider(self.project_root, self.bundle_path)

    def test_valid_bundle_serves_all_nine_operations_with_import_provenance(self) -> None:
        provider = self.provider()
        identity = provider.identify_security("XMPL")
        security_id = str(identity["security_id"])
        calls = (
            provider.identify_security,
            provider.get_security_profile,
            provider.get_financial_statements,
            provider.get_price_history,
            provider.get_valuation_inputs,
            provider.get_source_metadata,
            provider.get_peer_comparables,
            provider.get_earnings_history,
            provider.get_catalyst_events,
        )
        for operation in calls:
            with self.subTest(operation=operation.__name__):
                response = operation("XMPL" if operation is calls[0] else security_id)
                self.assertIs(response["is_demo"], False)
                self.assertEqual(response["input_mode"], "imported")
                self.assertEqual(response["bundle_version"], "example-2024-annual-v1")
                self.assertRegex(str(response["bundle_sha256"]), r"^[0-9a-f]{64}$")
                if operation.__name__ in {
                    "get_price_history",
                    "get_peer_comparables",
                    "get_catalyst_events",
                }:
                    self.assertEqual(response["source_ids"], [])
                else:
                    self.assertTrue(response["source_ids"])
                self.assertTrue(response["warnings"])
        self.assertEqual(provider.bundle_sha256, hashlib.sha256(self.bundle_path.read_bytes()).hexdigest())

    def test_provider_is_snapshot_based_and_does_not_reread_mutated_input(self) -> None:
        provider = self.provider()
        original = provider.get_security_profile("US-EXAMPLE-XMPL")
        changed = valid_bundle()
        changed["operations"]["get_security_profile"]["data"]["business_model"] = "CHANGED"
        _write_bundle(self.bundle_path, changed)
        self.assertEqual(provider.get_security_profile("US-EXAMPLE-XMPL"), original)

    def test_invalid_bundle_shapes_fail_closed(self) -> None:
        mutations: dict[str, Any] = {
            "unsupported-version": lambda value: value.__setitem__("schema_version", "9.0"),
            "empty-warnings": lambda value: value.__setitem__("warnings", []),
            "missing-security": lambda value: value.pop("security"),
            "unresolved-source": lambda value: value["operations"]["get_security_profile"].__setitem__("source_ids", ["absent"]),
            "source-less-identity": lambda value: value["operations"]["identify_security"].__setitem__("source_ids", []),
            "source-less-populated-price": lambda value: (
                value["operations"]["get_price_history"].__setitem__("source_ids", []),
                value["operations"]["get_price_history"]["data"].__setitem__("latest_price", 123.45),
            ),
            "source-metadata-content-mismatch": lambda value: value["operations"][
                "get_source_metadata"
            ]["data"]["sources"][0].__setitem__(
                "locator", "https://different.example.invalid/untrusted"
            ),
            "source-metadata-reference-subset": lambda value: value["operations"][
                "get_source_metadata"
            ].__setitem__("source_ids", ["issuer-profile"]),
            "identity-alias-conflict": lambda value: value["operations"][
                "identify_security"
            ]["data"].__setitem__("aliases", ["Conflicting Alias"]),
            "source-less-limitations-only": lambda value: value["operations"][
                "get_price_history"
            ].__setitem__("data", {"limitations": ["No price evidence supplied."]}),
            "financial-periods-wrong-type": lambda value: value["operations"][
                "get_financial_statements"
            ]["data"].__setitem__("periods", "not-a-list"),
            "earnings-events-wrong-type": lambda value: value["operations"][
                "get_earnings_history"
            ]["data"].__setitem__("events", {}),
            "profile-segments-wrong-type": lambda value: value["operations"][
                "get_security_profile"
            ]["data"].__setitem__("segments", 123),
            "source-publication-after-retrieval": lambda value: (
                value["sources"][0].__setitem__("publication_date", "2025-02-22"),
                value["sources"][0].__setitem__(
                    "retrieved_at", "2025-02-21T00:00:00Z"
                ),
                value["operations"]["get_source_metadata"]["data"]["sources"][
                    0
                ].__setitem__("publication_date", "2025-02-22"),
                value["operations"]["get_source_metadata"]["data"]["sources"][
                    0
                ].__setitem__("retrieved_at", "2025-02-21T00:00:00Z"),
            ),
            "future-as-of": lambda value: value.__setitem__("as_of_date", "2999-01-01"),
            "credential-key": lambda value: value.__setitem__("api_key", "do-not-print-this-value"),
            "credential-value": lambda value: value["warnings"].append("Bearer abcdefghijklmnopqrstuvwxyz"),
            "generic-token-key": lambda value: value["security"].__setitem__(
                "token", "ghp_" + "abcdefghijklmnopqrstuvwxyz0123456789"
            ),
            "basic-authorization": lambda value: value["warnings"].append(
                "Authorization=Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="
            ),
            "aws-access-key": lambda value: value["warnings"].append(
                "AKIA" + "IOSFODNN7EXAMPLE"
            ),
            "jwt-value": lambda value: value["warnings"].append(
                "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature123"
            ),
        }
        from investkit.providers.file import BundleValidationError, FileProvider

        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = valid_bundle()
                mutate(value)
                _write_bundle(self.bundle_path, value)
                with self.assertRaises(BundleValidationError) as caught:
                    FileProvider(self.project_root, self.bundle_path)
                self.assertNotIn("do-not-print-this-value", str(caught.exception))
                self.assertNotIn("abcdefghijklmnopqrstuvwxyz", str(caught.exception))

    def test_common_credential_values_are_rejected_without_echoing_them(self) -> None:
        from investkit.providers.file import BundleValidationError, FileProvider

        credential_values = {
            "slack-bot": "xoxb-" + "1" * 12 + "-" + "A" * 24,
            "slack-app": "xapp-" + "1" * 12 + "-" + "A" * 24,
            "gitlab": "glpat-" + "A" * 24,
            "stripe-secret": "sk_live_" + "A" * 24,
            "stripe-restricted": "rk_live_" + "A" * 24,
            "npm": "npm_" + "A" * 36,
            "google-api": "AIza" + "A" * 35,
            "google-oauth": "ya29." + "A" * 32,
            "github-fine-grained": "github_pat_" + "A" * 32,
            "sendgrid": "SG." + "A" * 16 + "." + "B" * 24,
        }

        for label, credential in credential_values.items():
            with self.subTest(label=label):
                value = valid_bundle()
                value["warnings"].append(f"Imported note {credential}")
                _write_bundle(self.bundle_path, value)
                with self.assertRaises(BundleValidationError) as caught:
                    FileProvider(self.project_root, self.bundle_path)
                self.assertNotIn(credential, str(caught.exception))

    def test_source_identifiers_with_edge_whitespace_are_rejected(self) -> None:
        from investkit.providers.file import BundleValidationError, FileProvider

        mutations = {
            "registry-source-id": lambda value: (
                value["sources"][0].__setitem__("source_id", " issuer-profile"),
                value["operations"]["get_source_metadata"]["data"]["sources"][0].__setitem__(
                    "source_id", " issuer-profile"
                ),
                value["operations"]["identify_security"].__setitem__(
                    "source_ids", [" issuer-profile"]
                ),
                value["operations"]["get_security_profile"].__setitem__(
                    "source_ids", [" issuer-profile"]
                ),
                value["operations"]["get_source_metadata"].__setitem__(
                    "source_ids", [
                        " issuer-profile",
                        "issuer-financials",
                        "issuer-market",
                    ]
                ),
            ),
            "operation-source-id": lambda value: value["operations"][
                "get_security_profile"
            ].__setitem__("source_ids", ["issuer-profile "]),
        }

        for label, mutate in mutations.items():
            with self.subTest(label=label):
                value = valid_bundle()
                mutate(value)
                _write_bundle(self.bundle_path, value)
                with self.assertRaises(BundleValidationError):
                    FileProvider(self.project_root, self.bundle_path)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        self.bundle_path.write_text(
            '{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8"
        )
        from investkit.providers.file import BundleValidationError, FileProvider

        with self.assertRaisesRegex(BundleValidationError, "duplicate"):
            FileProvider(self.project_root, self.bundle_path)

    def test_malformed_and_nonstandard_json_numbers_are_rejected(self) -> None:
        from investkit.providers.file import BundleValidationError, FileProvider

        payloads = (
            '{"schema_version":',
            json.dumps(valid_bundle()).replace('1020.0', 'NaN', 1),
            json.dumps(valid_bundle()).replace('1020.0', 'Infinity', 1),
            json.dumps(valid_bundle()).replace('1020.0', '1e309', 1),
            json.dumps(valid_bundle()).replace('1020.0', '1' * 5000, 1),
            '{"nested":' * 1200 + 'null' + '}' * 1200,
        )
        for payload in payloads:
            with self.subTest(payload=payload[:32]):
                self.bundle_path.write_text(payload, encoding="utf-8")
                with self.assertRaises(BundleValidationError):
                    FileProvider(self.project_root, self.bundle_path)

    def test_unsafe_paths_invalid_encoding_and_oversize_are_rejected(self) -> None:
        from investkit.providers.file import BundleInputError, FileProvider, MAX_BUNDLE_BYTES

        outside = _write_bundle(Path(self._temporary_directory.name) / "outside.json")
        linked = self.project_root / "inputs/linked.json"
        linked.symlink_to(outside)
        linked_parent = self.project_root / "linked-parent"
        linked_parent.symlink_to(outside.parent, target_is_directory=True)
        linked_parent_file = linked_parent / outside.name
        bad_utf8 = self.project_root / "inputs/bad.json"
        bad_utf8.write_bytes(b"\xff\xfe")
        too_large = self.project_root / "inputs/large.json"
        too_large.write_bytes(b" " * (MAX_BUNDLE_BYTES + 1))
        unsafe_paths = [
            outside,
            linked,
            linked_parent_file,
            Path("../outside.json"),
            bad_utf8,
            too_large,
        ]
        if hasattr(os, "mkfifo"):
            fifo = self.project_root / "inputs/bundle.fifo"
            os.mkfifo(fifo)
            unsafe_paths.append(fifo)
        for path in unsafe_paths:
            with self.subTest(path=path.name):
                with self.assertRaises(BundleInputError):
                    FileProvider(self.project_root, path)

    def test_parent_directory_swap_after_preflight_is_rejected(self) -> None:
        import investkit.providers.file as file_provider

        outside_directory = Path(self._temporary_directory.name) / "outside-swap"
        outside_bundle = _write_bundle(outside_directory / self.bundle_path.name)
        original_inputs = self.bundle_path.parent
        moved_inputs = self.project_root / "inputs-before-swap"
        original_check = file_provider._checked_regular_path

        def swap_parent(project_root: Path, relative: Path) -> Path:
            checked = original_check(project_root, relative)
            original_inputs.rename(moved_inputs)
            original_inputs.symlink_to(
                outside_bundle.parent,
                target_is_directory=True,
            )
            return checked

        with mock.patch(
            "investkit.providers.file._checked_regular_path",
            side_effect=swap_parent,
        ):
            with self.assertRaises(file_provider.BundleInputError):
                file_provider.FileProvider(self.project_root, self.bundle_path)

    def test_file_provider_static_surface_has_no_network_subprocess_or_third_party_imports(self) -> None:
        # FileProvider remains the untrusted, offline import boundary. Dedicated
        # public/credentialed providers may contain gated network transports.
        provider_sources = (
            REPOSITORY_ROOT / "src/investkit/providers/file.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "import requests",
            "import httpx",
            "import urllib",
            "import socket",
            "import subprocess",
            "os.system",
            "eval(",
            "exec(",
        ):
            self.assertNotIn(forbidden, provider_sources)


class ImportedReportSafetyTests(unittest.TestCase):
    def test_untrusted_markdown_is_neutralized_without_erasing_a_legal_company_name(
        self,
    ) -> None:
        from investkit.research.report import CAPABILITY_ORDER, render_report

        results = {
            capability: {
                "capability": capability,
                "facts": [],
                "findings": [],
                "method": {},
                "missing_inputs": ["not supplied"],
                "risks": [],
                "skip_reason": "No relevant evidence was supplied.",
                "status": "skipped",
                "unknowns": [],
                "warnings": [],
            }
            for capability in CAPABILITY_ORDER
        }
        report = render_report(
            task_id="research-safe-output",
            question=(
                "Assess evidence <script>alert('x')</script> "
                "![remote](https://attacker.invalid/pixel)"
            ),
            identity={
                "as_of_date": date.today().isoformat(),
                "legal_name": "Best Buy Co., Inc.",
                "market": "NYSE",
                "security_id": "US-BBY",
                "ticker": "BBY",
            },
            capability_results=results,
            sources={
                "sources": [
                    {
                        "source_id": "issuer-file",
                        "title": "[click](javascript:alert('x'))",
                        "locator": "javascript:alert('x')",
                    },
                    {
                        "source_id": "market-data",
                        "title": "Market Data: FY2025 evidence",
                        "locator": "https://example.invalid/market-data",
                    }
                ]
            },
            installed_skills=[],
            loaded_specs=[],
            generation_time=_timestamp(),
            input_mode="imported",
            input_provenance={
                "bundle_version": "safe-test-v1",
                "origin": "inputs/company.json",
                "sha256": "0" * 64,
            },
        )

        self.assertIn("Best Buy Co., Inc.", report)
        self.assertNotIn("<script", report.lower())
        self.assertNotIn("javascript:", report.lower())
        self.assertNotIn("![remote]", report)
        self.assertIn("Market Data: FY2025 evidence", report)

    def test_chinese_investment_action_advice_is_omitted_from_the_report(self) -> None:
        from investkit.research.report import CAPABILITY_ORDER, render_report

        results = {
            capability: {
                "capability": capability,
                "facts": [],
                "findings": [],
                "method": {},
                "missing_inputs": ["not supplied"],
                "risks": [],
                "skip_reason": "No relevant evidence was supplied.",
                "status": "skipped",
                "unknowns": [],
                "warnings": [],
            }
            for capability in CAPABILITY_ORDER
        }
        advice_phrases = (
            "建议买入该股票",
            "建议卖出该股票",
            "建议继续持有该股票",
            "立即建仓",
            "现在减仓",
            "建议增持",
            "建议设置10%仓位",
            "设置止损位",
            "保证收益",
        )

        for advice in advice_phrases:
            with self.subTest(advice=advice):
                report = render_report(
                    task_id="research-safe-cjk-output",
                    question=f"请研究公司，并且{advice}",
                    identity={
                        "as_of_date": date.today().isoformat(),
                        "legal_name": "Example Software Holdings, Inc.",
                        "market": "NASDAQ",
                        "security_id": "US-EXAMPLE-XMPL",
                        "ticker": "XMPL",
                    },
                    capability_results=results,
                    sources={"sources": []},
                    installed_skills=[],
                    loaded_specs=[],
                    generation_time=_timestamp(),
                    input_mode="imported",
                    input_provenance={
                        "bundle_version": "safe-test-v1",
                        "origin": "inputs/company.json",
                        "sha256": "0" * 64,
                    },
                )
                self.assertNotIn(advice, report)
                self.assertIn(
                    "[content omitted by the research-only output boundary]",
                    report,
                )


class CapabilityResultBoundaryTests(unittest.TestCase):
    def test_completed_findings_and_risks_require_identity_text_and_sources(self) -> None:
        from investkit.capabilities.contracts import (
            build_capability_result,
            validate_capability_result,
        )

        result = build_capability_result(
            "company-deep-research",
            status="completed",
            skill={"name": "company-deep-research", "version": "0.3.0"},
            method={"name": "source-led-company-dossier", "version": "1.0"},
            findings=[
                {
                    "id": "finding-supported",
                    "statement": "A source-backed finding.",
                    "source_ids": ["issuer-profile"],
                }
            ],
            risks=[
                {
                    "id": "risk-supported",
                    "statement": "A source-backed risk.",
                    "source_ids": ["issuer-profile"],
                }
            ],
        )

        for field in ("findings", "risks"):
            for required_field in ("id", "statement", "source_ids"):
                with self.subTest(field=field, required_field=required_field):
                    malformed = deepcopy(result)
                    if required_field == "source_ids":
                        malformed[field][0][required_field] = []
                    else:
                        malformed[field][0].pop(required_field)
                    with self.assertRaises((TypeError, ValueError)):
                        validate_capability_result(
                            malformed,
                            expected="company-deep-research",
                        )


class ImportedWorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="investkit-import-workflow-"
        )
        self.project_root = Path(self._temporary_directory.name) / "project"
        self.project_root.mkdir()
        from investkit.initializer import initialize_project

        initialized = initialize_project(self.project_root, source_root=REPOSITORY_ROOT)
        self.assertEqual(initialized.exit_code, 0, initialized)
        self.bundle_path = _write_bundle(self.project_root / "inputs/company.json")

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_generic_research_persists_snapshot_and_neutral_report(self) -> None:
        from investkit.research.workflow import run_research

        result = run_research(
            self.project_root,
            REPOSITORY_ROOT,
            input_path=self.bundle_path,
            question="What do the filings support about durability and risk?",
        )
        self.assertEqual(result.status, "completed", result.error)
        task_path = result.task_path
        task = json.loads((task_path / "task.json").read_text(encoding="utf-8"))
        self.assertEqual(task["input_mode"], "imported")
        self.assertEqual(task["security_query"], "XMPL")
        self.assertEqual(task["question"], "What do the filings support about durability and risk?")
        snapshot = task_path / "input/research-bundle.json"
        self.assertTrue(snapshot.is_file())
        self.assertEqual(task["input"]["sha256"], hashlib.sha256(snapshot.read_bytes()).hexdigest())
        report = (task_path / "report.md").read_text(encoding="utf-8")
        self.assertIn("Example Software Holdings, Inc.", report)
        self.assertIn("user-supplied", report.lower())
        self.assertIn("not independently", report.lower())
        forbidden = ("fictional", "aurora", "tender", "backlog", "municipal")
        serialized = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [task_path / "report.md", *sorted((task_path / "capabilities").glob("*.json"))]
        ).lower()
        for term in forbidden:
            self.assertNotIn(term, serialized)

    def test_decision_intelligence_records_flow_through_workflow_and_report(self) -> None:
        from investkit.research.workflow import run_research

        bundle = valid_bundle()
        today = date.today().isoformat()
        valuation = bundle["operations"]["get_valuation_inputs"]
        valuation["data"].update(
            {
                "forecast_unlevered_free_cash_flow": [100.0, 110.0, 120.0, 130.0, 140.0],
                "forecast_metadata": {
                    "as_of_date": today,
                    "method": "driver-based operating forecast",
                    "periods": [
                        {
                            "fiscal_year": "2025",
                            "revenue": 1120.0,
                            "net_income": 108.0,
                            "unlevered_free_cash_flow": 100.0,
                        }
                    ],
                },
                "consensus": {
                    "observation_time": _timestamp(),
                    "contributor_count": 8,
                    "periods": [
                        {
                            "fiscal_year": "2025",
                            "revenue_mean": 1110.0,
                            "net_income_mean": 105.0,
                            "eps_mean": 1.05,
                            "eps_low": 0.92,
                            "eps_high": 1.18,
                        }
                    ],
                    "revision_30d": {"eps_mean_change": 0.03, "up": 5, "down": 2},
                },
                "wacc": 0.10,
                "terminal_growth": 0.03,
                "diluted_shares": 100.0,
                "cash": 50.0,
                "total_debt": 20.0,
                "scenario_assumptions": {
                    "bear": {"wacc": 0.12, "terminal_growth": 0.02, "cash_flow_multiplier": 0.8},
                    "base": {"wacc": 0.10, "terminal_growth": 0.03, "cash_flow_multiplier": 1.0},
                    "bull": {"wacc": 0.09, "terminal_growth": 0.04, "cash_flow_multiplier": 1.2},
                },
                "sensitivity_wacc_values": [0.09, 0.10, 0.11],
                "sensitivity_terminal_growth_values": [0.02, 0.03, 0.04],
            }
        )
        peers = bundle["operations"]["get_peer_comparables"]
        peers["source_ids"] = ["issuer-market"]
        peers["data"].update(
            {
                "peers": [
                    {
                        "security_id": "US-PEER-A",
                        "status": "included",
                        "market_capitalization": 1200.0,
                        "net_income": 100.0,
                        "total_equity": 500.0,
                        "enterprise_value": 1300.0,
                        "operating_income": 130.0,
                    }
                ],
                "selection_method": "same-industry bounded comparison",
                "industry_benchmark": {
                    "classification": "Example Software",
                    "as_of_date": today,
                    "sample_size": 27,
                    "metrics": {
                        "revenue_growth": {
                            "target": 0.1333,
                            "industry_median": 0.09,
                            "percentile": 0.72,
                            "definition": "year-over-year revenue growth",
                        }
                    },
                },
            }
        )
        _write_bundle(self.bundle_path, bundle)

        result = run_research(
            self.project_root,
            REPOSITORY_ROOT,
            input_path=self.bundle_path,
            question="How do forecasts, industry position, and valuation compare?",
        )

        self.assertEqual(result.status, "completed", result.error)
        valuation_result = json.loads(
            (result.task_path / "capabilities/valuation-analysis.json").read_text(
                encoding="utf-8"
            )
        )
        comps_result = json.loads(
            (result.task_path / "capabilities/comps-analysis.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            valuation_result["method"]["forecast_provenance"],
            "investkit_model",
        )
        self.assertEqual(
            comps_result["method"]["industry_comparison"]["sample_size"],
            27,
        )
        report = (result.task_path / "report.md").read_text(encoding="utf-8")
        self.assertIn("Point-in-time broker consensus", report)
        self.assertIn("Industry-relative revenue growth", report)
        self.assertIn("Scenario DCF value-per-share range", report)

    def test_gap_only_operations_complete_with_disclosed_skips_not_invented_thesis(
        self,
    ) -> None:
        from investkit.research.workflow import run_research

        bundle = valid_bundle()
        operations = bundle["operations"]
        operations["get_security_profile"] = {
            "data": {
                "business_model": None,
                "segments": [],
                "limitations": ["No company-profile evidence was supplied."],
            },
            "source_ids": [],
            "warnings": ["No company-profile evidence was supplied."],
        }
        operations["get_financial_statements"] = {
            "data": {
                "periods": [],
                "limitations": ["No financial-statement evidence was supplied."],
            },
            "source_ids": [],
            "warnings": ["No financial-statement evidence was supplied."],
        }
        operations["get_valuation_inputs"] = {
            "data": {
                "forecast_unlevered_free_cash_flow": None,
                "wacc": None,
                "terminal_growth": None,
                "diluted_shares": None,
                "cash": None,
                "total_debt": None,
                "scenario_assumptions": None,
                "sensitivity_wacc_values": None,
                "sensitivity_terminal_growth_values": None,
                "limitations": ["No valuation evidence was supplied."],
            },
            "source_ids": [],
            "warnings": ["No valuation evidence was supplied."],
        }
        operations["get_earnings_history"] = {
            "data": {
                "events": None,
                "transcript_available": None,
                "limitations": ["No earnings evidence was supplied."],
            },
            "source_ids": [],
            "warnings": ["No earnings evidence was supplied."],
        }
        _write_bundle(self.bundle_path, bundle)

        result = run_research(
            self.project_root,
            REPOSITORY_ROOT,
            input_path=self.bundle_path,
            question="What issuer evidence is actually available?",
        )

        self.assertEqual(result.status, "completed", result.error)
        capabilities = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in (result.task_path / "capabilities").glob("*.json")
        }
        for capability in (
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
        ):
            with self.subTest(capability=capability):
                self.assertEqual(capabilities[capability]["status"], "skipped")
                self.assertTrue(capabilities[capability]["skip_reason"])
                self.assertTrue(capabilities[capability]["missing_inputs"])
        self.assertEqual(capabilities["source-verification"]["status"], "completed")
        self.assertEqual(capabilities["investment-report"]["status"], "completed")
        persisted = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                result.task_path / "report.md",
                *sorted((result.task_path / "capabilities").glob("*.json")),
            ]
        ).casefold()
        for invented in (
            "source-backed operating performance",
            "material operating risks remain incompletely quantified",
            "supporting evidence could deteriorate",
        ):
            self.assertNotIn(invented, persisted)

    def test_imported_chinese_buy_instruction_is_not_copied_into_report(self) -> None:
        from investkit.research.workflow import run_research

        advice = "建议买入该股票"
        bundle = valid_bundle()
        bundle["operations"]["get_security_profile"]["data"][
            "business_model"
        ] = advice
        _write_bundle(self.bundle_path, bundle)

        result = run_research(
            self.project_root,
            REPOSITORY_ROOT,
            input_path=self.bundle_path,
            question="What does the supplied company evidence support?",
        )

        self.assertEqual(result.status, "completed", result.error)
        report = (result.task_path / "report.md").read_text(encoding="utf-8")
        self.assertNotIn(advice, report)
        self.assertIn(
            "[content omitted by the research-only output boundary]",
            report,
        )

    def test_question_markdown_is_safe_while_task_json_preserves_the_question(self) -> None:
        from investkit.research.workflow import resume_research, run_research

        question = (
            "Assess <script>alert('x')</script> and "
            "![remote](https://attacker.invalid/pixel) evidence."
        )
        result = run_research(
            self.project_root,
            REPOSITORY_ROOT,
            input_path=self.bundle_path,
            question=question,
        )
        self.assertEqual(result.status, "completed", result.error)
        task = json.loads(
            (result.task_path / "task.json").read_text(encoding="utf-8")
        )
        question_view = (result.task_path / "question.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(task["question"], question)
        self.assertNotIn("<script", question_view.lower())
        self.assertNotIn("![remote]", question_view)

        resumed = resume_research(
            self.project_root, result.task_id, REPOSITORY_ROOT
        )
        self.assertEqual(resumed.status, "completed")

    def test_completed_resume_uses_snapshot_and_changes_only_run_log(self) -> None:
        from investkit.research.workflow import resume_research, run_research

        result = run_research(
            self.project_root,
            REPOSITORY_ROOT,
            input_path=self.bundle_path,
            question="Assess the evidence and limitations.",
        )
        self.assertEqual(result.status, "completed", result.error)
        before = {
            path.relative_to(result.task_path).as_posix(): path.read_bytes()
            for path in result.task_path.rglob("*")
            if path.is_file()
        }
        self.bundle_path.unlink()
        resumed = resume_research(self.project_root, result.task_id, REPOSITORY_ROOT)
        self.assertEqual(resumed.status, "completed")
        after = {
            path.relative_to(result.task_path).as_posix(): path.read_bytes()
            for path in result.task_path.rglob("*")
            if path.is_file()
        }
        self.assertEqual(set(before), set(after))
        for relative, content in before.items():
            if relative != "run-log.json":
                self.assertEqual(after[relative], content, relative)
        self.assertNotEqual(after["run-log.json"], before["run-log.json"])

    def test_corrupt_snapshot_fails_resume_without_mutation(self) -> None:
        from investkit.research.workflow import resume_research, run_research

        result = run_research(
            self.project_root,
            REPOSITORY_ROOT,
            input_path=self.bundle_path,
            question="Assess source-backed operating evidence.",
        )
        self.assertEqual(result.status, "completed", result.error)
        snapshot = result.task_path / "input/research-bundle.json"
        snapshot.write_text("{}\n", encoding="utf-8")
        before = {
            path.relative_to(result.task_path).as_posix(): path.read_bytes()
            for path in result.task_path.rglob("*")
            if path.is_file()
        }
        with self.assertRaisesRegex(Exception, "snapshot|hash|bundle"):
            resume_research(self.project_root, result.task_id, REPOSITORY_ROOT)
        after = {
            path.relative_to(result.task_path).as_posix(): path.read_bytes()
            for path in result.task_path.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)

    def test_failed_task_resumes_from_snapshot_after_original_is_deleted(self) -> None:
        from investkit.capabilities.analysis import run_capability as actual_run_capability
        from investkit.research.workflow import resume_research, run_research

        failed_once = False

        def flaky_run_capability(name: str, inputs: dict[str, Any]):
            nonlocal failed_once
            if name == "financial-statement-analysis" and not failed_once:
                failed_once = True
                raise RuntimeError("bounded transient analysis failure")
            return actual_run_capability(name, inputs)

        with mock.patch(
            "investkit.research.workflow.run_capability",
            side_effect=flaky_run_capability,
        ):
            failed = run_research(
                self.project_root,
                REPOSITORY_ROOT,
                input_path=self.bundle_path,
                question="Can this task resume from its validated snapshot?",
            )
        self.assertEqual(failed.status, "failed")
        self.assertIn("bounded transient", failed.error or "")
        preserved = {
            relative: (failed.task_path / relative).read_bytes()
            for relative in (
                "capabilities/security-identification.json",
                "capabilities/company-deep-research.json",
                "capabilities/business-model-analysis.json",
                "input/research-bundle.json",
            )
        }
        self.bundle_path.unlink()

        resumed = resume_research(self.project_root, failed.task_id, REPOSITORY_ROOT)
        self.assertEqual(resumed.status, "completed", resumed.error)
        for relative, content in preserved.items():
            self.assertEqual((failed.task_path / relative).read_bytes(), content, relative)

    def test_invalid_rehashed_failed_snapshot_is_rejected_without_run_log_mutation(self) -> None:
        from investkit.capabilities.analysis import run_capability as actual_run_capability
        from investkit.research.workflow import resume_research, run_research

        def fail_financial(name: str, inputs: dict[str, Any]):
            if name == "financial-statement-analysis":
                raise RuntimeError("stop after imported snapshot persistence")
            return actual_run_capability(name, inputs)

        with mock.patch(
            "investkit.research.workflow.run_capability",
            side_effect=fail_financial,
        ):
            failed = run_research(
                self.project_root,
                REPOSITORY_ROOT,
                input_path=self.bundle_path,
                question="Reject a corrupt persisted bundle before writing resume state.",
            )
        self.assertEqual(failed.status, "failed")
        snapshot = failed.task_path / "input/research-bundle.json"
        snapshot.write_text("{}\n", encoding="utf-8")
        task_path = failed.task_path / "task.json"
        task = json.loads(task_path.read_text(encoding="utf-8"))
        task["input"]["sha256"] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        task_path.write_text(
            json.dumps(task, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        before = {
            path.relative_to(failed.task_path).as_posix(): path.read_bytes()
            for path in failed.task_path.rglob("*")
            if path.is_file()
        }

        with self.assertRaisesRegex(Exception, "bundle|schema"):
            resume_research(self.project_root, failed.task_id, REPOSITORY_ROOT)

        after = {
            path.relative_to(failed.task_path).as_posix(): path.read_bytes()
            for path in failed.task_path.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)

    def test_failed_resume_rejects_tampered_provider_data_before_run_log_mutation(
        self,
    ) -> None:
        from investkit.capabilities.analysis import run_capability as actual_run_capability
        from investkit.research.workflow import resume_research, run_research

        def fail_financial(name: str, inputs: dict[str, Any]):
            if name == "financial-statement-analysis":
                raise RuntimeError("stop after provider data persistence")
            return actual_run_capability(name, inputs)

        with mock.patch(
            "investkit.research.workflow.run_capability",
            side_effect=fail_financial,
        ):
            failed = run_research(
                self.project_root,
                REPOSITORY_ROOT,
                input_path=self.bundle_path,
                question="Reject changed provider evidence before resuming.",
            )
        self.assertEqual(failed.status, "failed")
        profile_path = failed.task_path / "data/security-profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        profile["research_drivers"] = ["tampered driver"]
        profile_path.write_text(
            json.dumps(profile, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        before = {
            path.relative_to(failed.task_path).as_posix(): path.read_bytes()
            for path in failed.task_path.rglob("*")
            if path.is_file()
        }

        with self.assertRaisesRegex(Exception, "provider|snapshot|data|evidence"):
            resume_research(self.project_root, failed.task_id, REPOSITORY_ROOT)

        after = {
            path.relative_to(failed.task_path).as_posix(): path.read_bytes()
            for path in failed.task_path.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)

    def test_failed_resume_rejects_rewritten_completed_capability_before_mutation(
        self,
    ) -> None:
        from investkit.capabilities.analysis import run_capability as actual_run_capability
        from investkit.research.workflow import resume_research, run_research

        def fail_financial(name: str, inputs: dict[str, Any]):
            if name == "financial-statement-analysis":
                raise RuntimeError("stop after completed company capabilities")
            return actual_run_capability(name, inputs)

        with mock.patch(
            "investkit.research.workflow.run_capability",
            side_effect=fail_financial,
        ):
            failed = run_research(
                self.project_root,
                REPOSITORY_ROOT,
                input_path=self.bundle_path,
                question="Reject a rewritten completed claim before resuming.",
            )
        self.assertEqual(failed.status, "failed")
        capability_path = (
            failed.task_path / "capabilities/company-deep-research.json"
        )
        capability = json.loads(capability_path.read_text(encoding="utf-8"))
        capability["facts"][0]["statement"] = (
            "A forged but schema-valid company statement."
        )
        capability_path.write_text(
            json.dumps(capability, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        before = {
            path.relative_to(failed.task_path).as_posix(): path.read_bytes()
            for path in failed.task_path.rglob("*")
            if path.is_file()
        }

        with self.assertRaisesRegex(Exception, "capability|evidence|derived|snapshot"):
            resume_research(self.project_root, failed.task_id, REPOSITORY_ROOT)

        after = {
            path.relative_to(failed.task_path).as_posix(): path.read_bytes()
            for path in failed.task_path.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)


class ImportedWorkflowPreflightTests(unittest.TestCase):
    def test_uninitialized_project_is_rejected_without_creating_runtime_state(self) -> None:
        from investkit.research.workflow import run_research

        with tempfile.TemporaryDirectory(prefix="investkit-uninitialized-") as temporary:
            project_root = Path(temporary) / "project"
            project_root.mkdir()
            bundle_path = _write_bundle(project_root / "inputs/company.json")
            before = {
                path.relative_to(project_root).as_posix()
                for path in project_root.rglob("*")
            }
            with self.assertRaisesRegex(Exception, "not initialized"):
                run_research(
                    project_root,
                    REPOSITORY_ROOT,
                    input_path=bundle_path,
                    question="Should fail before task creation.",
                )
            after = {
                path.relative_to(project_root).as_posix()
                for path in project_root.rglob("*")
            }
            self.assertEqual(after, before)


class WorkflowSourceCompositionTests(unittest.TestCase):
    def test_valuation_inputs_union_price_and_method_sources_canonically(self) -> None:
        from investkit.research.workflow import _analysis_inputs

        context = {
            "input_mode": "imported",
            "price_history": {"source_ids": ["issuer-market", "shared-source"]},
            "valuation_inputs": {
                "source_ids": ["issuer-forecast", "shared-source"]
            },
        }

        inputs = _analysis_inputs(context, "valuation-analysis")

        self.assertEqual(
            inputs["active_source_ids"],
            ["issuer-forecast", "issuer-market", "shared-source"],
        )


class ImportedCliContractTests(unittest.TestCase):
    def test_parser_exposes_generic_research_create_and_resume(self) -> None:
        from investkit.cli import build_parser

        parser = build_parser()
        created = parser.parse_args(
            ["research", "--input", "inputs/company.json", "--question", "Why now?"]
        )
        symbol = parser.parse_args(
            [
                "research",
                "--symbol",
                "603868.SH",
                "--question",
                "Why now?",
                "--allow-network",
            ]
        )
        resumed = parser.parse_args(["research", "--resume", "task-123"])
        self.assertEqual(created.command, "research")
        self.assertEqual(created.input, "inputs/company.json")
        self.assertEqual(symbol.symbol, "603868.SH")
        self.assertTrue(symbol.allow_network)
        self.assertEqual(resumed.resume, "task-123")
        for invalid in (
            ["research"],
            ["research", "--input", "x.json"],
            ["research", "--question", "Why?"],
            ["research", "--resume", "task-123", "--input", "x.json"],
            ["research", "--resume", "task-123", "--question", "Why?"],
            ["research", "--symbol", "603868.SH"],
            ["research", "--input", "x.json", "--question", "Why?", "--allow-network"],
            ["research", "--resume", "task-123", "--allow-network"],
        ):
            with self.subTest(invalid=invalid), self.assertRaises(SystemExit):
                parser.parse_args(invalid)


if __name__ == "__main__":
    unittest.main()
