"""Pinned real-issuer acceptance for the imported research product path."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
from typing import Any
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPOSITORY_ROOT / "fixtures/acceptance/microsoft-fy2025.json"
SEC_INDEX_SOURCE = "sec-msft-fy2025-10k-index"
SEC_FILING_SOURCE = "sec-msft-fy2025-10k"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected object in {path}")
    return value


class MicrosoftFixtureEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = _read_json(FIXTURE_PATH)
        cls.operations = cls.bundle["operations"]
        if not isinstance(cls.operations, dict):
            raise AssertionError("fixture operations must be an object")

    def test_identity_sources_and_intentional_gaps_are_exact(self) -> None:
        security = self.bundle["security"]
        self.assertEqual(
            security,
            {
                "security_id": "NASDAQ:MSFT",
                "ticker": "MSFT",
                "legal_name": "Microsoft Corporation",
                "exchange": "Nasdaq",
                "aliases": ["MSFT", "Microsoft", "Microsoft Corporation"],
            },
        )
        self.assertEqual(
            {source["source_id"] for source in self.bundle["sources"]},
            {SEC_INDEX_SOURCE, SEC_FILING_SOURCE},
        )
        for operation_name, field in (
            ("get_price_history", "observations"),
            ("get_peer_comparables", "peers"),
            ("get_catalyst_events", "events"),
        ):
            operation = self.operations[operation_name]
            self.assertEqual(operation["source_ids"], [], operation_name)
            self.assertEqual(operation["data"][field], [], operation_name)
            self.assertTrue(operation["data"]["limitations"], operation_name)
            self.assertTrue(operation["warnings"], operation_name)

    def test_pinned_statement_facts_reproduce_the_evidence_matrix(self) -> None:
        periods = self.operations["get_financial_statements"]["data"]["periods"]
        previous, latest = periods
        self.assertEqual(previous["fiscal_year"], 2024)
        self.assertEqual(latest["fiscal_year"], 2025)
        self.assertAlmostEqual(latest["revenue"] / previous["revenue"] - 1, 0.149321562324)
        self.assertAlmostEqual(latest["gross_profit"] / latest["revenue"], 0.688237423862)
        self.assertAlmostEqual(latest["operating_income"] / latest["revenue"], 0.456219562409)
        self.assertAlmostEqual(latest["cash_from_operations"] / latest["revenue"], 0.483317005296)
        self.assertAlmostEqual(latest["total_debt"] / latest["total_equity"], 0.125629223330)
        self.assertAlmostEqual(latest["cash_and_equivalents"] / latest["total_debt"], 0.700841231953)
        self.assertAlmostEqual(latest["cash_from_operations"] / latest["net_income"], 1.337123890329)
        average_assets = (latest["total_assets"] + previous["total_assets"]) / 2
        self.assertAlmostEqual(
            (latest["net_income"] - latest["cash_from_operations"]) / average_assets,
            -0.060698429762,
        )
        previous_wc = previous["accounts_receivable"] + previous["inventory"] - previous["accounts_payable"]
        latest_wc = latest["accounts_receivable"] + latest["inventory"] - latest["accounts_payable"]
        self.assertEqual(latest_wc - previous_wc, 6945)
        self.assertAlmostEqual(latest["current_assets"] / latest["current_liabilities"], 1.353446444504)
        self.assertEqual(latest["cash_from_operations"] + latest["capital_expenditure"], 71611)


class MicrosoftImportedWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="investkit-msft-acceptance-"
        )
        self.project_root = Path(self._temporary_directory.name) / "project"
        self.project_root.mkdir()
        from investkit.initializer import initialize_project

        initialized = initialize_project(self.project_root, source_root=REPOSITORY_ROOT)
        self.assertEqual(initialized.exit_code, 0, initialized)
        self.input_path = self.project_root / "inputs/microsoft-fy2025.json"
        self.input_path.parent.mkdir()
        shutil.copy2(FIXTURE_PATH, self.input_path)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_provider_preserves_operation_specific_sources(self) -> None:
        from investkit.providers.file import FileProvider

        provider = FileProvider(self.project_root, self.input_path)
        identity = provider.identify_security("MSFT")
        self.assertEqual(identity["security_id"], "NASDAQ:MSFT")
        self.assertEqual(
            identity["source_ids"], [SEC_INDEX_SOURCE, SEC_FILING_SOURCE]
        )
        self.assertEqual(
            provider.get_financial_statements("NASDAQ:MSFT")["source_ids"],
            [SEC_FILING_SOURCE],
        )
        for response in (
            provider.get_price_history("NASDAQ:MSFT"),
            provider.get_peer_comparables("NASDAQ:MSFT"),
            provider.get_catalyst_events("NASDAQ:MSFT"),
        ):
            self.assertEqual(response["source_ids"], [])
            self.assertTrue(response["warnings"])

    def test_full_real_issuer_workflow_is_sourced_neutral_and_reproducible(self) -> None:
        from investkit.research.workflow import resume_research, run_research

        result = run_research(
            self.project_root,
            REPOSITORY_ROOT,
            input_path=self.input_path,
            question="What does Microsoft FY2025 filing evidence support about financial durability and risk?",
        )
        self.assertEqual(result.status, "completed", result.error)
        sources = _read_json(result.task_path / "sources.json")["sources"]
        known_source_ids = {source["source_id"] for source in sources}
        self.assertEqual(known_source_ids, {SEC_INDEX_SOURCE, SEC_FILING_SOURCE})

        capability_root = result.task_path / "capabilities"
        capabilities = {
            path.stem: _read_json(path) for path in capability_root.glob("*.json")
        }
        self.assertEqual(len(capabilities), 13)
        self.assertEqual(capabilities["valuation-analysis"]["status"], "skipped")
        self.assertEqual(capabilities["comps-analysis"]["status"], "skipped")
        self.assertEqual(capabilities["catalyst-analysis"]["status"], "skipped")
        self.assertEqual(capabilities["earnings-analysis"]["status"], "completed")
        for capability, envelope in capabilities.items():
            with self.subTest(capability=capability):
                self.assertTrue(set(envelope["source_ids"]).issubset(known_source_ids))
                for field in ("facts", "findings", "risks"):
                    for record in envelope[field]:
                        self.assertTrue(
                            set(record.get("source_ids", [])).issubset(known_source_ids)
                        )
        identity_records = [
            record
            for field in ("facts", "findings", "risks")
            for record in capabilities["security-identification"][field]
            if record.get("source_ids")
        ]
        expected_identity_sources = sorted([SEC_INDEX_SOURCE, SEC_FILING_SOURCE])
        self.assertTrue(identity_records)
        self.assertTrue(
            all(
                record["source_ids"] == expected_identity_sources
                for record in identity_records
            )
        )
        for capability in (
            "company-deep-research",
            "business-model-analysis",
            "financial-statement-analysis",
            "earnings-quality-analysis",
            "earnings-analysis",
        ):
            with self.subTest(relevant_source_capability=capability):
                sourced_records = [
                    record
                    for field in ("facts", "findings", "risks")
                    for record in capabilities[capability][field]
                    if record.get("source_ids")
                ]
                self.assertTrue(sourced_records)
                self.assertTrue(
                    all(
                        record["source_ids"] == [SEC_FILING_SOURCE]
                        for record in sourced_records
                    )
                )

        metrics = capabilities["financial-statement-analysis"]["method"]["metrics"]
        self.assertAlmostEqual(metrics["revenue_growth"], 0.149321562324)
        self.assertAlmostEqual(metrics["gross_margin"], 0.688237423862)
        quality = capabilities["earnings-quality-analysis"]["method"]
        self.assertAlmostEqual(quality["cash_conversion"], 1.337123890329)
        self.assertAlmostEqual(quality["accrual_ratio"], -0.060698429762)
        self.assertEqual(quality["working_capital_review"]["change"], 6945)

        company = capabilities["company-deep-research"]
        company_fact_ids = {fact["id"] for fact in company["facts"]}
        self.assertNotIn("fact-company-management", company_fact_ids)
        self.assertNotIn("fact-company-capital-allocation", company_fact_ids)
        company_unknown_ids = {unknown["id"] for unknown in company["unknowns"]}
        self.assertTrue(
            {"unknown-company-management", "unknown-company-capital-allocation"}.issubset(
                company_unknown_ids
            )
        )
        business = capabilities["business-model-analysis"]
        business_fact_ids = {fact["id"] for fact in business["facts"]}
        self.assertNotIn("fact-payer", business_fact_ids)
        self.assertNotIn("fact-value-proposition", business_fact_ids)

        earnings = capabilities["earnings-analysis"]
        self.assertNotIn(
            "assumption-consensus-vintage",
            {assumption["id"] for assumption in earnings["assumptions"]},
        )
        self.assertNotIn(
            "finding-earnings-bridges",
            {finding["id"] for finding in earnings["findings"]},
        )
        earnings_unknowns = " ".join(
            str(unknown.get("gap", "")) for unknown in earnings["unknowns"]
        ).casefold()
        for missing_input in ("expectation", "guidance", "transcript"):
            self.assertRegex(
                earnings_unknowns,
                rf"{missing_input}.*not supplied in this bundle|not supplied in this bundle.*{missing_input}",
            )
        json.dumps(capabilities, allow_nan=False)

        report = (result.task_path / "report.md").read_text(encoding="utf-8")
        lower_report = report.lower()
        for expected in (
            "microsoft corporation",
            "msft",
            "2025-06-30",
            "user-supplied",
            "not independently",
        ):
            self.assertIn(expected, lower_report)
        for forbidden in (
            "fictional",
            "aurora",
            "lantern",
            "tender",
            "backlog",
            "municipal",
            "battery",
        ):
            self.assertNotIn(forbidden, lower_report)
        self.assertNotRegex(lower_report, r"\b(?:buy|sell|hold)\b|guaranteed return|stop loss")

        before = {
            path.relative_to(result.task_path).as_posix(): path.read_bytes()
            for path in result.task_path.rglob("*")
            if path.is_file()
        }
        self.input_path.unlink()
        resumed = resume_research(self.project_root, result.task_id, REPOSITORY_ROOT)
        self.assertEqual(resumed.status, "completed")
        after = {
            path.relative_to(result.task_path).as_posix(): path.read_bytes()
            for path in result.task_path.rglob("*")
            if path.is_file()
        }
        self.assertEqual(set(before), set(after))
        for relative_path, content in before.items():
            if relative_path != "run-log.json":
                self.assertEqual(after[relative_path], content, relative_path)


if __name__ == "__main__":
    unittest.main()
