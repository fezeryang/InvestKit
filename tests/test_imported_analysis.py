"""Focused TDD contracts for imported-data Investment Core analysis."""

from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
from typing import Any, Mapping
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_IMPORTED_TERMS = (
    "aurora",
    "backlog",
    "battery",
    "fictional",
    "fixture",
    "municipal",
    "tender",
)


def _source(
    source_id: str,
    *,
    quality: str = "high",
    freshness: str = "current",
    conflicts: list[str] | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "source_id": source_id,
        "publisher": "Example Software Holdings, Inc.",
        "title": f"Evidence for {source_id}",
        "source_type": "issuer-filing",
        "locator": f"https://example.invalid/{source_id}",
        "publication_date": "2025-02-20",
        "as_of_date": "2024-12-31",
        "retrieved_at": "2025-02-21T00:00:00Z",
        "quality": quality,
        "freshness": freshness,
        "access_notes": "Public issuer material; locator metadata only.",
        "license_notes": "Reuse status must be confirmed by the analyst.",
    }
    if conflicts:
        record["conflicts"] = conflicts
    return record


def _base_inputs() -> dict[str, Any]:
    sources = [
        _source("identity-source"),
        _source("profile-source"),
        _source(
            "financial-source",
            quality="medium",
            freshness="stale",
            conflicts=["Revenue definitions differ across the compared periods."],
        ),
        _source("valuation-source"),
    ]
    warning = "User-supplied imported data was not independently fetched."
    return {
        "input_mode": "imported",
        "sources": {
            "input_mode": "imported",
            "schema_version": "1.0",
            "sources": sources,
        },
        "identity": {
            "security_id": "US-EXAMPLE-XMPL",
            "ticker": "XMPL",
            "legal_name": "Example Software Holdings, Inc.",
            "exchange": "NASDAQ",
            "source_ids": ["identity-source"],
            "warnings": [warning],
        },
        "profile": {
            "business_model": "Subscription software and support services.",
            "segments": ["Software", "Support"],
            "customers": "Enterprise customers",
            "suppliers": "Cloud infrastructure providers",
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
            "source_ids": ["profile-source"],
            "warnings": [warning],
        },
        "statements": {
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
            "source_ids": ["financial-source"],
            "warnings": [warning],
        },
        "valuation_inputs": {
            "forecast_unlevered_free_cash_flow": None,
            "wacc": None,
            "terminal_growth": None,
            "diluted_shares": None,
            "cash": 260.0,
            "total_debt": 160.0,
            "scenario_assumptions": None,
            "sensitivity_wacc_values": None,
            "sensitivity_terminal_growth_values": None,
            "source_ids": ["valuation-source"],
            "warnings": [warning],
        },
        "peers": {
            "peers": None,
            "selection_method": None,
            "source_ids": [],
            "warnings": [warning],
        },
        "earnings": {
            "events": None,
            "transcript_available": False,
            "source_ids": ["financial-source"],
            "warnings": [warning],
        },
        "catalysts": {
            "events": None,
            "source_ids": [],
            "warnings": [warning],
        },
    }


def _run(
    capability: str,
    base: Mapping[str, Any],
    prior: Mapping[str, Any],
    *,
    active_source_ids: list[str] | None = None,
) -> dict[str, Any]:
    from investkit.capabilities.analysis import run_capability

    inputs = {**base, "capability_results": prior}
    if active_source_ids is not None:
        inputs["active_source_ids"] = active_source_ids
    return run_capability(capability, inputs)


class ImportedAnalysisTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.base = _base_inputs()

    def test_imported_pipeline_is_neutral_source_specific_and_skips_true_gaps(self) -> None:
        from investkit.capabilities.contracts import validate_capability_result

        prior: dict[str, Any] = {}
        stage_sources: dict[str, list[str] | None] = {
            "security-identification": ["identity-source"],
            "company-deep-research": ["profile-source"],
            "business-model-analysis": ["profile-source"],
            "financial-statement-analysis": ["financial-source"],
            "earnings-quality-analysis": ["financial-source"],
            "valuation-analysis": ["valuation-source"],
            "comps-analysis": [],
            "earnings-analysis": ["financial-source"],
            "investment-thesis": None,
            "bear-case-analysis": None,
            "catalyst-analysis": [],
            "source-verification": None,
            "investment-report": None,
        }
        for capability, active_sources in stage_sources.items():
            with self.subTest(capability=capability):
                result = _run(
                    capability,
                    self.base,
                    prior,
                    active_source_ids=active_sources,
                )
                validate_capability_result(result, expected=capability)
                prior[capability] = result

        self.assertEqual(prior["security-identification"]["source_ids"], ["identity-source"])
        self.assertEqual(prior["company-deep-research"]["source_ids"], ["profile-source"])
        self.assertEqual(prior["business-model-analysis"]["source_ids"], ["profile-source"])
        self.assertEqual(
            prior["financial-statement-analysis"]["source_ids"],
            ["financial-source"],
        )
        self.assertEqual(prior["earnings-quality-analysis"]["source_ids"], ["financial-source"])
        for capability in (
            "valuation-analysis",
            "comps-analysis",
            "earnings-analysis",
            "catalyst-analysis",
        ):
            self.assertEqual(prior[capability]["status"], "skipped", capability)
            self.assertTrue(prior[capability]["skip_reason"])
            self.assertTrue(prior[capability]["missing_inputs"])

        serialized = json.dumps(prior, sort_keys=True).casefold()
        for term in FORBIDDEN_IMPORTED_TERMS:
            self.assertNotIn(term, serialized)

    def test_imported_thesis_and_bear_case_derive_monitoring_from_upstream_evidence(self) -> None:
        prior: dict[str, Any] = {}
        for capability, sources in (
            ("company-deep-research", ["profile-source"]),
            ("business-model-analysis", ["profile-source"]),
            ("financial-statement-analysis", ["financial-source"]),
            ("earnings-quality-analysis", ["financial-source"]),
            ("valuation-analysis", ["valuation-source"]),
            ("comps-analysis", []),
            ("earnings-analysis", ["financial-source"]),
        ):
            prior[capability] = _run(
                capability,
                self.base,
                prior,
                active_source_ids=sources,
            )

        thesis = _run("investment-thesis", self.base, prior)
        prior["investment-thesis"] = thesis
        bear = _run("bear-case-analysis", self.base, prior)
        thesis_text = json.dumps(thesis, sort_keys=True).casefold()
        bear_text = json.dumps(bear, sort_keys=True).casefold()

        self.assertEqual(thesis["status"], "completed")
        self.assertEqual(bear["status"], "completed")
        self.assertIn("renewal rates", thesis_text)
        self.assertIn("operating cash conversion", thesis_text)
        self.assertIn("monitoring_kpis", thesis["method"])
        self.assertRegex(bear_text, r"customer concentration|cloud hosting costs")
        self.assertNotEqual(
            bear["method"]["counter_thesis"],
            thesis["method"]["thesis_statement"],
        )
        for term in FORBIDDEN_IMPORTED_TERMS:
            self.assertNotIn(term, thesis_text + bear_text)

    def test_source_verification_preserves_source_quality_freshness_conflicts_and_gaps(self) -> None:
        prior = {
            "company-deep-research": _run(
                "company-deep-research",
                self.base,
                {},
                active_source_ids=["profile-source"],
            ),
            "financial-statement-analysis": _run(
                "financial-statement-analysis",
                self.base,
                {},
                active_source_ids=["financial-source"],
            ),
            "unresolved-evidence": {
                "facts": [
                    {
                        "id": "fact-unresolved",
                        "statement": "A deliberately unresolved test claim.",
                        "source_ids": ["missing-source"],
                    }
                ],
                "warnings": ["A source conflict remains unresolved."],
                "source_ids": ["missing-source"],
            },
        }
        result = _run("source-verification", self.base, prior)
        method = result["method"]
        reviews = [
            review
            for claim in method["claim_ledger"]
            for review in claim["source_reviews"]
        ]

        self.assertEqual(result["status"], "completed")
        self.assertIn("medium", {review["quality"] for review in reviews})
        self.assertIn("stale", {review["freshness"] for review in reviews})
        self.assertIn("financial-source", method["stale_source_ids"])
        self.assertIn("missing-source", method["unresolved_source_ids"])
        self.assertRegex(" ".join(method["conflicts"]), r"Revenue definitions|source conflict")
        self.assertEqual(method["gate_status"], "pass_with_disclosed_gaps")
        self.assertEqual(
            {claim["claim_type"] for claim in method["claim_ledger"]},
            {"fact", "finding", "risk"},
        )

    def test_source_verification_derives_staleness_from_dates_not_only_label(self) -> None:
        base = deepcopy(self.base)
        for source in base["sources"]["sources"]:
            source["freshness"] = "current"
            source["publication_date"] = "2020-02-20"
            source["as_of_date"] = "2020-01-31"
            source["retrieved_at"] = "2026-07-16T00:00:00Z"
        prior = {
            "company-deep-research": _run(
                "company-deep-research",
                base,
                {},
                active_source_ids=["profile-source"],
            )
        }

        result = _run("source-verification", base, prior)

        self.assertEqual(result["status"], "completed")
        self.assertIn("profile-source", result["method"]["stale_source_ids"])
        self.assertRegex(" ".join(result["warnings"]).casefold(), r"stale|refresh")

    def test_missing_profile_fields_are_unknowns_and_never_sourced_as_facts(self) -> None:
        base = deepcopy(self.base)
        profile = base["profile"]
        profile.update(
            {
                "management": {},
                "capital_allocation": {},
                "competitive_context": {},
                "competitive_position": None,
                "payer": None,
                "customers": None,
                "value_proposition": None,
            }
        )
        company = _run(
            "company-deep-research",
            base,
            {},
            active_source_ids=["profile-source"],
        )
        business = _run(
            "business-model-analysis",
            base,
            {},
            active_source_ids=["profile-source"],
        )

        company_fact_ids = {fact["id"] for fact in company["facts"]}
        self.assertNotIn("fact-company-management", company_fact_ids)
        self.assertNotIn("fact-company-capital-allocation", company_fact_ids)
        self.assertNotIn("fact-company-competitive-context", company_fact_ids)
        company_unknown_ids = {unknown["id"] for unknown in company["unknowns"]}
        self.assertTrue(
            {
                "unknown-company-management",
                "unknown-company-capital-allocation",
                "unknown-company-competitive-context",
            }.issubset(company_unknown_ids)
        )

        business_fact_ids = {fact["id"] for fact in business["facts"]}
        self.assertNotIn("fact-payer", business_fact_ids)
        self.assertNotIn("fact-value-proposition", business_fact_ids)
        business_unknown_ids = {unknown["id"] for unknown in business["unknowns"]}
        self.assertTrue(
            {"unknown-business-payer", "unknown-business-value-proposition"}.issubset(
                business_unknown_ids
            )
        )
        finding_text = " ".join(
            str(finding["statement"]) for finding in business["findings"]
        ).casefold()
        self.assertNotIn("links the disclosed revenue model, payer, and value proposition", finding_text)

    def test_direct_capabilities_keep_all_operation_sources_in_canonical_order(self) -> None:
        expected_sources = ["financial-source", "profile-source"]

        for capability in (
            "security-identification",
            "company-deep-research",
            "business-model-analysis",
            "financial-statement-analysis",
            "earnings-quality-analysis",
        ):
            with self.subTest(capability=capability):
                forward = _run(
                    capability,
                    self.base,
                    {},
                    active_source_ids=list(reversed(expected_sources)),
                )
                reverse = _run(
                    capability,
                    self.base,
                    {},
                    active_source_ids=expected_sources,
                )
                self.assertEqual(forward, reverse)
                sourced_records = [
                    record
                    for field in ("facts", "findings", "risks")
                    for record in forward[field]
                    if record.get("source_ids")
                ]
                self.assertTrue(sourced_records)
                self.assertTrue(
                    all(record["source_ids"] == expected_sources for record in sourced_records)
                )

        base = deepcopy(self.base)
        base["valuation_inputs"].update(
            {
                "forecast_unlevered_free_cash_flow": [100.0, 110.0, 120.0, 130.0, 140.0],
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
        valuation_sources = ["price-source", "valuation-source"]
        valuation = _run(
            "valuation-analysis",
            base,
            {},
            active_source_ids=list(reversed(valuation_sources)),
        )
        self.assertEqual(valuation["status"], "completed")
        for field in ("facts", "findings", "risks"):
            self.assertTrue(
                all(
                    record["source_ids"] == valuation_sources
                    for record in valuation[field]
                    if record.get("source_ids")
                )
            )

    def test_nonfinite_values_are_rejected_and_extreme_metrics_degrade_safely(self) -> None:
        from investkit.capabilities.contracts import validate_capability_result

        base = deepcopy(self.base)
        periods = base["statements"]["periods"]
        periods[0]["revenue"] = 1e-308
        periods[1]["revenue"] = 1e308
        result = _run(
            "financial-statement-analysis",
            base,
            {},
            active_source_ids=["financial-source"],
        )
        json.dumps(result, allow_nan=False)
        self.assertIsNone(result["method"]["metrics"]["revenue_growth"])
        self.assertIn(
            "unknown-financial-revenue-growth",
            {unknown["id"] for unknown in result["unknowns"]},
        )

        invalid = deepcopy(result)
        invalid["method"]["nested_nonfinite"] = {"value": math.nan}
        with self.assertRaisesRegex(ValueError, "non-finite"):
            validate_capability_result(
                invalid,
                expected="financial-statement-analysis",
            )

        extreme_valuation = deepcopy(self.base)
        extreme_valuation["valuation_inputs"].update(
            {
                "forecast_unlevered_free_cash_flow": [1e308] * 5,
                "wacc": 0.10,
                "terminal_growth": 0.03,
                "diluted_shares": 1.0,
                "cash": 1e308,
                "total_debt": 0.0,
                "scenario_assumptions": {
                    name: {
                        "wacc": 0.10,
                        "terminal_growth": 0.03,
                        "cash_flow_multiplier": 2.0,
                    }
                    for name in ("bear", "base", "bull")
                },
                "sensitivity_wacc_values": [0.09, 0.10, 0.11],
                "sensitivity_terminal_growth_values": [0.02, 0.03, 0.04],
            }
        )
        try:
            extreme_result = _run(
                "valuation-analysis",
                extreme_valuation,
                {},
                active_source_ids=["valuation-source"],
            )
        except ValueError as error:
            self.assertRegex(str(error), "non-finite|finite")
        else:
            json.dumps(extreme_result, allow_nan=False)
            validate_capability_result(extreme_result, expected="valuation-analysis")

    def test_industry_comparison_preserves_point_in_time_benchmark_definitions(self) -> None:
        base = deepcopy(self.base)
        base["peers"].update(
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
                "industry_benchmark": {
                    "classification": "Example Software",
                    "as_of_date": "2025-02-20",
                    "sample_size": 27,
                    "metrics": {
                        "revenue_growth": {
                            "target": 0.1333,
                            "industry_median": 0.09,
                            "percentile": 0.72,
                            "definition": "year-over-year revenue growth",
                        },
                        "return_on_equity": {
                            "target": 0.1116,
                            "industry_median": 0.08,
                            "percentile": 0.68,
                            "definition": "net income divided by period-end equity",
                        },
                    },
                },
            }
        )
        result = _run(
            "comps-analysis",
            base,
            {},
            active_source_ids=["valuation-source"],
        )

        self.assertEqual(result["status"], "completed")
        comparison = result["method"]["industry_comparison"]
        self.assertEqual(comparison["classification"], "Example Software")
        self.assertEqual(comparison["as_of_date"], "2025-02-20")
        self.assertEqual(comparison["sample_size"], 27)
        self.assertAlmostEqual(
            comparison["metrics"]["revenue_growth"]["difference_to_median"],
            0.0433,
        )
        self.assertEqual(
            comparison["metrics"]["return_on_equity"]["definition"],
            "net income divided by period-end equity",
        )

    def test_industry_comparison_rejects_missing_vintage_or_definition(self) -> None:
        for benchmark in (
            {
                "classification": "Example Software",
                "sample_size": 27,
                "metrics": {
                    "revenue_growth": {
                        "target": 0.1,
                        "industry_median": 0.08,
                        "percentile": 0.6,
                        "definition": "year-over-year revenue growth",
                    }
                },
            },
            {
                "classification": "Example Software",
                "as_of_date": "2025-02-20",
                "sample_size": 27,
                "metrics": {
                    "revenue_growth": {
                        "target": 0.1,
                        "industry_median": 0.08,
                        "percentile": 0.6,
                    }
                },
            },
        ):
            with self.subTest(benchmark=benchmark):
                base = deepcopy(self.base)
                base["peers"].update(
                    {
                        "peers": [
                            {
                                "security_id": "US-PEER-A",
                                "status": "included",
                                "market_capitalization": 1200.0,
                                "net_income": 100.0,
                            }
                        ],
                        "industry_benchmark": benchmark,
                    }
                )
                with self.assertRaises(ValueError):
                    _run(
                        "comps-analysis",
                        base,
                        {},
                        active_source_ids=["valuation-source"],
                    )

    def test_valuation_separates_consensus_model_forecast_and_target_range(self) -> None:
        base = deepcopy(self.base)
        base["valuation_inputs"].update(
            {
                "forecast_unlevered_free_cash_flow": [100.0, 110.0, 120.0, 130.0, 140.0],
                "forecast_metadata": {
                    "as_of_date": "2025-02-20",
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
                    "observation_time": "2025-02-20T08:00:00Z",
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
        result = _run(
            "valuation-analysis",
            base,
            {},
            active_source_ids=["valuation-source"],
        )

        self.assertEqual(result["status"], "completed")
        method = result["method"]
        self.assertEqual(method["forecast_provenance"], "investkit_model")
        self.assertEqual(method["forecast_metadata"]["as_of_date"], "2025-02-20")
        self.assertEqual(method["consensus"]["contributor_count"], 8)
        self.assertAlmostEqual(
            method["consensus"]["periods"][0]["eps_dispersion"],
            0.26,
        )
        target_range = method["target_value_range"]
        self.assertLess(target_range["low"], target_range["base"])
        self.assertLess(target_range["base"], target_range["high"])
        self.assertEqual(target_range["basis"], "scenario DCF; not a guaranteed target price")

    def test_consensus_requires_vintage_contributors_and_dispersion_bounds(self) -> None:
        invalid_consensus = (
            {"contributor_count": 3, "periods": []},
            {"observation_time": "2025-02-20T08:00:00Z", "periods": []},
            {
                "observation_time": "2025-02-20T08:00:00Z",
                "contributor_count": 3,
                "periods": [
                    {
                        "fiscal_year": "2025",
                        "eps_mean": 1.0,
                        "eps_low": 1.2,
                        "eps_high": 0.8,
                    }
                ],
            },
        )
        for consensus in invalid_consensus:
            with self.subTest(consensus=consensus):
                base = deepcopy(self.base)
                base["valuation_inputs"]["consensus"] = consensus
                with self.assertRaises(ValueError):
                    _run(
                        "valuation-analysis",
                        base,
                        {},
                        active_source_ids=["valuation-source"],
                    )

    def test_sparse_period_labels_do_not_claim_financial_calculations(self) -> None:
        from investkit.capabilities.contracts import validate_capability_result

        base = deepcopy(self.base)
        base["statements"] = {
            "periods": [{"fiscal_year": "2023"}, {"fiscal_year": "2024"}],
            "source_ids": ["financial-source"],
            "warnings": ["Only period labels were supplied."],
        }

        for capability in (
            "financial-statement-analysis",
            "earnings-quality-analysis",
        ):
            with self.subTest(capability=capability):
                result = _run(
                    capability,
                    base,
                    {},
                    active_source_ids=["financial-source"],
                )
                validate_capability_result(result, expected=capability)
                self.assertEqual(result["status"], "skipped")
                self.assertEqual(result["facts"], [])
                self.assertEqual(result["estimates"], [])
                self.assertEqual(result["findings"], [])
                text = json.dumps(result, sort_keys=True).casefold()
                self.assertNotIn("diagnostics are calculated", text)
                self.assertNotIn("periods support revenue", text)

    def test_source_free_gap_profile_skips_without_requiring_provenance(self) -> None:
        from investkit.capabilities.contracts import validate_capability_result

        base = deepcopy(self.base)
        base["profile"] = {
            "business_model": None,
            "segments": [],
            "management": {},
            "capital_allocation": {},
            "competitive_context": {},
            "source_ids": [],
            "warnings": ["Company-profile evidence was not supplied."],
            "input_mode": "imported",
        }

        for capability in ("company-deep-research", "business-model-analysis"):
            with self.subTest(capability=capability):
                result = _run(capability, base, {}, active_source_ids=[])
                validate_capability_result(result, expected=capability)
                self.assertEqual(result["status"], "skipped")
                self.assertEqual(result["source_ids"], [])
                self.assertTrue(result["skip_reason"])

    def test_identity_only_upstream_does_not_fabricate_thesis_or_bear_case(self) -> None:
        from investkit.capabilities.contracts import validate_capability_result

        base = deepcopy(self.base)
        base["profile"] = {
            "business_model": None,
            "segments": [],
            "source_ids": [],
            "warnings": ["No sourced profile was supplied."],
        }
        base["statements"] = {
            "periods": [{"fiscal_year": "2023"}, {"fiscal_year": "2024"}],
            "source_ids": [],
            "warnings": ["No financial values were supplied."],
        }

        prior: dict[str, Any] = {
            "security-identification": _run(
                "security-identification",
                base,
                {},
                active_source_ids=["identity-source"],
            )
        }
        for capability, sources in (
            ("company-deep-research", []),
            ("business-model-analysis", []),
            ("financial-statement-analysis", []),
            ("earnings-quality-analysis", []),
        ):
            prior[capability] = _run(
                capability,
                base,
                prior,
                active_source_ids=sources,
            )

        thesis = _run("investment-thesis", base, prior)
        prior["investment-thesis"] = thesis
        bear = _run("bear-case-analysis", base, prior)
        prior["bear-case-analysis"] = bear
        verification = _run("source-verification", base, prior)
        prior["source-verification"] = verification
        report = _run("investment-report", base, prior)
        validate_capability_result(thesis, expected="investment-thesis")
        validate_capability_result(bear, expected="bear-case-analysis")
        validate_capability_result(verification, expected="source-verification")
        validate_capability_result(report, expected="investment-report")
        self.assertEqual(thesis["status"], "skipped")
        self.assertEqual(bear["status"], "skipped")
        self.assertEqual(verification["status"], "completed")
        self.assertEqual(report["status"], "completed")
        serialized = json.dumps(
            {"thesis": thesis, "bear": bear, "report": report}
        ).casefold()
        self.assertNotIn("source-backed operating performance", serialized)
        self.assertNotIn("material operating risks remain incompletely quantified", serialized)
        self.assertNotIn("supporting evidence could deteriorate", serialized)

    def test_demo_mode_retains_the_explicit_fictional_and_demo_specific_boundary(self) -> None:
        from investkit.capabilities.analysis import run_capability
        from investkit.providers.demo import DemoProvider

        provider = DemoProvider(REPOSITORY_ROOT)
        identity = provider.identify_security("demo")
        security_id = str(identity["security_id"])
        metadata = provider.get_source_metadata(security_id)
        sources = {"sources": [dict(metadata)]}
        security = run_capability(
            "security-identification",
            {
                "input_mode": "demo",
                "identity": identity,
                "source_metadata": metadata,
                "sources": sources,
            },
        )
        business = run_capability(
            "business-model-analysis",
            {
                "input_mode": "demo",
                "profile": provider.get_security_profile(security_id),
                "source_metadata": metadata,
                "sources": sources,
            },
        )
        serialized = json.dumps({"security": security, "business": business}).casefold()
        self.assertRegex(serialized, r"fictional|fixture")
        self.assertRegex(serialized, r"tender|backlog")


if __name__ == "__main__":
    unittest.main()
