"""Contracts for dependency-aware, permission-gated Harness planning."""

from __future__ import annotations

from dataclasses import replace
import contextlib
import io
import json
import os
from pathlib import Path
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class AssetPolicyTests(unittest.TestCase):
    def test_credential_and_network_permission_are_separate_gates(self) -> None:
        from investkit.catalog import load_asset_catalog
        from investkit.planning import evaluate_asset_state

        asset = load_asset_catalog(REPOSITORY_ROOT).get("GF-002")
        executable = replace(
            asset,
            decision="adapt",
            approval_status="approved",
            state="credential_required",
        )
        self.assertEqual(
            evaluate_asset_state(executable, credential_names=set(), allow_network=False),
            "credential_required",
        )
        self.assertEqual(
            evaluate_asset_state(
                executable,
                credential_names={"GF_SKILLS_APIKEY"},
                allow_network=False,
            ),
            "permission_required",
        )
        self.assertEqual(
            evaluate_asset_state(
                executable,
                credential_names={"GF_SKILLS_APIKEY"},
                allow_network=True,
            ),
            "ready",
        )

    def test_review_and_safety_blocks_cannot_be_bypassed_by_credentials(self) -> None:
        from investkit.catalog import load_asset_catalog
        from investkit.planning import evaluate_asset_state

        catalog = load_asset_catalog(REPOSITORY_ROOT)
        for identifier in ("GUOSEN-002",):
            asset = catalog.get(identifier)
            self.assertEqual(
                evaluate_asset_state(
                    asset,
                    credential_names={"GF_SKILLS_APIKEY"},
                    allow_network=True,
                ),
                asset.state,
            )


class DynamicPlannerTests(unittest.TestCase):
    def test_planner_selects_ready_assets_and_dependencies_in_topological_order(self) -> None:
        from investkit.catalog import load_asset_catalog
        from investkit.planning import build_research_plan

        catalog = load_asset_catalog(REPOSITORY_ROOT)
        plan = build_research_plan(catalog, capabilities=("valuation",))
        selected_ids = tuple(item.asset_id for item in plan.selected)
        self.assertIn("valuation-analysis", selected_ids)
        self.assertIn("comps-analysis", selected_ids)
        self.assertLess(selected_ids.index("security-identification"), selected_ids.index("comps-analysis"))
        self.assertLess(selected_ids.index("financial-statement-analysis"), selected_ids.index("valuation-analysis"))
        self.assertEqual(plan.blocked_capabilities, ())
        self.assertTrue(any(item.asset_id == "GF-003" for item in plan.considered))
        self.assertTrue(all(item.effective_state == "ready" for item in plan.selected))

    def test_planner_requires_permission_then_selects_the_approved_sse_provider(self) -> None:
        from investkit.catalog import load_asset_catalog
        from investkit.planning import build_research_plan

        catalog = load_asset_catalog(REPOSITORY_ROOT)
        blocked_plan = build_research_plan(
            catalog,
            capabilities=("security_identification",),
            required_types=("data_provider",),
            credential_names={"GF_SKILLS_APIKEY"},
            allow_network=False,
        )
        self.assertEqual(blocked_plan.selected, ())
        self.assertEqual(blocked_plan.blocked_capabilities, ("security_identification",))
        states = {item.asset_id: item.effective_state for item in blocked_plan.considered}
        self.assertEqual(states["sse-announcement-provider"], "permission_required")
        self.assertEqual(states["GF-002"], "permission_required")
        plan = build_research_plan(
            catalog,
            capabilities=("security_identification",),
            required_types=("data_provider",),
            allow_network=True,
        )
        self.assertEqual(plan.blocked_capabilities, ())
        self.assertEqual(
            [item.asset_id for item in plan.selected],
            ["sse-announcement-provider"],
        )
        self.assertNotIn("CICCWM-001", {item.asset_id for item in plan.selected})

    def test_plan_output_is_stable_and_explains_every_candidate(self) -> None:
        from investkit.catalog import load_asset_catalog
        from investkit.planning import build_research_plan

        catalog = load_asset_catalog(REPOSITORY_ROOT)
        first = build_research_plan(
            catalog,
            capabilities=("company_fundamentals", "financial_statements", "valuation"),
        )
        second = build_research_plan(
            catalog,
            capabilities=("valuation", "financial_statements", "company_fundamentals"),
        )
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertTrue(all(item.reason for item in (*first.selected, *first.considered)))
        self.assertEqual(first.catalog_version, catalog.catalog_version)


class DynamicPlannerCliTests(unittest.TestCase):
    def invoke(self, *arguments: str) -> tuple[int, str, str]:
        from investkit.cli import main

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch(
            "investkit.cli.load_provider_environment", return_value=()
        ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(arguments))
            except SystemExit as error:
                code = int(error.code or 0)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_assets_plan_exposes_selected_dependencies_and_blocked_capabilities(self) -> None:
        code, stdout, stderr = self.invoke(
            "assets", "plan", "--capability", "valuation", "--json"
        )
        self.assertEqual((code, stderr), (0, ""))
        payload = json.loads(stdout)
        self.assertTrue(payload["runnable"])
        self.assertIn("valuation-analysis", [item["asset_id"] for item in payload["selected"]])

        code, stdout, stderr = self.invoke(
            "assets",
            "plan",
            "--capability",
            "security_identification",
            "--type",
            "data_provider",
            "--json",
        )
        self.assertEqual((code, stderr), (1, ""))
        payload = json.loads(stdout)
        self.assertEqual(payload["blocked_capabilities"], ["security_identification"])

        code, stdout, stderr = self.invoke(
            "assets",
            "plan",
            "--capability",
            "security_identification",
            "--type",
            "data_provider",
            "--allow-network",
            "--json",
        )
        self.assertEqual((code, stderr), (0, ""))
        payload = json.loads(stdout)
        self.assertEqual(
            [item["asset_id"] for item in payload["selected"]],
            ["sse-announcement-provider"],
        )


if __name__ == "__main__":
    unittest.main()
