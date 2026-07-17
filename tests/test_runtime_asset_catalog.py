"""Contracts for the manifest-driven Investment Research Harness catalog."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_IDS = {
    line.split(",", 1)[0]
    for line in (
        REPOSITORY_ROOT / "registry/governance/batch-001-candidate-governance.csv"
    ).read_text(encoding="utf-8").splitlines()[1:]
    if line.strip()
}
FIRST_PARTY_IDS = {
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
    "sse-announcement-provider",
}


class RuntimeAssetCatalogContractTests(unittest.TestCase):
    maxDiff = None

    def test_catalog_contains_every_first_party_and_batch_asset_exactly_once(self) -> None:
        from investkit.catalog import load_asset_catalog

        catalog = load_asset_catalog(REPOSITORY_ROOT)
        self.assertEqual(catalog.schema_version, "1.0")
        self.assertEqual(len(catalog.assets), 50)
        self.assertEqual(len({asset.id for asset in catalog.assets}), 50)
        self.assertEqual(
            {asset.id for asset in catalog.assets if asset.origin == "first_party"},
            FIRST_PARTY_IDS,
        )
        self.assertEqual(
            {asset.id for asset in catalog.assets if asset.origin == "candidate"},
            GOVERNANCE_IDS,
        )

    def test_every_asset_has_one_valid_type_decision_state_and_gate_contract(self) -> None:
        from investkit.catalog import (
            ASSET_TYPES,
            DECISIONS,
            RUNTIME_STATES,
            load_asset_catalog,
        )

        catalog = load_asset_catalog(REPOSITORY_ROOT)
        for asset in catalog.assets:
            with self.subTest(asset=asset.id):
                self.assertIn(asset.type, ASSET_TYPES)
                self.assertIn(asset.decision, DECISIONS)
                self.assertIn(asset.state, RUNTIME_STATES)
                self.assertTrue(asset.capabilities)
                self.assertTrue(asset.reason)
                self.assertTrue(asset.evidence)
                self.assertIn(asset.approval_status, {"approved", "not_requested"})
                self.assertIn(asset.network_mode, {"offline", "explicit_permission"})
                if asset.state == "ready":
                    self.assertEqual(asset.approval_status, "approved")
                    self.assertTrue(asset.adapter_id)
                if asset.credentials:
                    self.assertEqual(asset.network_mode, "explicit_permission")
                    self.assertTrue(
                        all(
                            name.endswith(("_APIKEY", "_API_KEY"))
                            for name in asset.credentials
                        )
                    )
                forbidden = " ".join(
                    (asset.adapter_id or "", *asset.dependencies, *asset.evidence)
                ).replace("\\", "/")
                self.assertNotIn("third_party/raw", forbidden)
                self.assertNotIn("adapted/skills", asset.adapter_id or "")

    def test_candidate_states_are_honest_and_not_promoted_by_presence(self) -> None:
        from investkit.catalog import load_asset_catalog

        catalog = load_asset_catalog(REPOSITORY_ROOT)
        by_id = {asset.id: asset for asset in catalog.assets}

        for candidate_id in {f"CICCWM-{index:03d}" for index in range(1, 7)}:
            self.assertEqual(by_id[candidate_id].state, "permission_required")
            self.assertEqual(by_id[candidate_id].approval_status, "approved")
            self.assertEqual(by_id[candidate_id].credentials, ("CICCWM_API_KEY",))
        for candidate_id in {f"GUOSEN-{index:03d}" for index in range(1, 7)}:
            self.assertEqual(by_id[candidate_id].state, "unavailable")
        self.assertEqual(by_id["SKILLHUB-001"].state, "blocked")
        self.assertEqual(by_id["SKILLHUB-001"].decision, "reject")
        for candidate_id in {"BATCH-001-011", "BATCH-001-013"}:
            self.assertEqual(by_id[candidate_id].state, "reference_only")
            self.assertEqual(by_id[candidate_id].decision, "reference")
        for candidate_id in {f"GF-{index:03d}" for index in range(1, 9)}:
            self.assertEqual(by_id[candidate_id].credentials, ("GF_SKILLS_APIKEY",))
            self.assertEqual(by_id[candidate_id].network_mode, "explicit_permission")
            self.assertNotEqual(by_id[candidate_id].state, "ready")

    def test_catalog_filtering_is_deterministic_and_dependency_safe(self) -> None:
        from investkit.catalog import load_asset_catalog

        catalog = load_asset_catalog(REPOSITORY_ROOT)
        blocked = catalog.filter(state="blocked")
        self.assertEqual(tuple(asset.id for asset in blocked), tuple(sorted(asset.id for asset in blocked)))
        self.assertTrue(blocked)
        self.assertTrue(all(asset.state == "blocked" for asset in blocked))

        valuation = catalog.filter(capability="valuation")
        self.assertTrue(valuation)
        self.assertTrue(all("valuation" in asset.capabilities for asset in valuation))

        known_ids = {asset.id for asset in catalog.assets}
        for asset in catalog.assets:
            self.assertTrue(set(asset.dependencies).issubset(known_ids))

    def test_strict_loader_rejects_duplicates_unknown_dependencies_and_fields(self) -> None:
        from investkit.catalog import CatalogValidationError, load_asset_catalog_file

        base = {
            "schema_version": "1.0",
            "catalog_version": "1.0.0",
            "assets": [
                {
                    "id": "one",
                    "name": "One",
                    "origin": "first_party",
                    "type": "agent_skill",
                    "capabilities": ["company_fundamentals"],
                    "decision": "adopt",
                    "approval_status": "approved",
                    "review_status": "governed",
                    "license_status": "project_first_party",
                    "state": "ready",
                    "adapter_kind": "skill",
                    "adapter_id": "skill:one",
                    "dependencies": [],
                    "credentials": [],
                    "network_mode": "offline",
                    "allowed_hosts": [],
                    "platforms": ["codex"],
                    "source": "skills/one",
                    "reason": "governed test asset",
                    "evidence": ["test"],
                }
            ],
        }
        with tempfile.TemporaryDirectory(prefix="investkit-catalog-invalid-") as temp:
            path = Path(temp) / "catalog.json"
            for mutation in ("duplicate", "dependency", "field"):
                value = json.loads(json.dumps(base))
                if mutation == "duplicate":
                    value["assets"].append(value["assets"][0])
                elif mutation == "dependency":
                    value["assets"][0]["dependencies"] = ["missing"]
                else:
                    value["assets"][0]["unexpected"] = True
                path.write_text(json.dumps(value), encoding="utf-8")
                with self.subTest(mutation=mutation):
                    with self.assertRaises(CatalogValidationError):
                        load_asset_catalog_file(path)


class AssetCatalogCliTests(unittest.TestCase):
    maxDiff = None

    def invoke(self, *arguments: str) -> tuple[int, str, str]:
        from investkit.cli import main

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch(
            "investkit.cli.load_provider_environment", return_value=()
        ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(list(arguments))
            except SystemExit as error:
                code = int(error.code or 0)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_assets_list_json_exposes_all_assets_and_filters(self) -> None:
        code, stdout, stderr = self.invoke("assets", "list", "--json")
        self.assertEqual((code, stderr), (0, ""))
        payload = json.loads(stdout)
        self.assertEqual(payload["count"], 50)
        self.assertEqual(len(payload["assets"]), 50)
        self.assertEqual(payload["assets"], sorted(payload["assets"], key=lambda item: item["id"]))

        code, stdout, stderr = self.invoke(
            "assets", "list", "--state", "blocked", "--json"
        )
        self.assertEqual((code, stderr), (0, ""))
        payload = json.loads(stdout)
        self.assertTrue(payload["assets"])
        self.assertTrue(all(item["state"] == "blocked" for item in payload["assets"]))

    def test_assets_show_reports_credentials_by_name_without_secret_value(self) -> None:
        code, stdout, stderr = self.invoke("assets", "show", "GF-002", "--json")
        self.assertEqual((code, stderr), (0, ""))
        payload = json.loads(stdout)
        self.assertEqual(payload["id"], "GF-002")
        self.assertEqual(payload["credentials"], ["GF_SKILLS_APIKEY"])
        self.assertNotIn("credential_value", payload)

        code, stdout, stderr = self.invoke("assets", "show", "does-not-exist")
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("not found", stderr.lower())


class AssetCatalogDoctorTests(unittest.TestCase):
    def test_doctor_validates_catalog_and_reports_missing_credentials_without_values(self) -> None:
        from investkit.doctor import run_doctor
        from investkit.initializer import initialize_project

        with tempfile.TemporaryDirectory(prefix="investkit-catalog-doctor-") as temp:
            project = Path(temp) / "project"
            project.mkdir()
            result = initialize_project(project, source_root=REPOSITORY_ROOT)
            self.assertEqual(result.exit_code, 0)
            with mock.patch.dict("os.environ", {}, clear=True):
                report = run_doctor(project, source_root=REPOSITORY_ROOT)
            catalog_checks = [check for check in report.checks if "asset catalog" in check.name.lower()]
            self.assertTrue(catalog_checks)
            self.assertTrue(any(check.status.value == "PASS" for check in catalog_checks))
            gate_checks = [check for check in report.checks if "execution gate" in check.name.lower()]
            self.assertTrue(gate_checks)
            self.assertTrue(any("GF_SKILLS_APIKEY" in check.message for check in gate_checks))

    def test_doctor_fails_a_malformed_catalog_without_repairing_it(self) -> None:
        from investkit.doctor import run_doctor
        from investkit.initializer import initialize_project

        with tempfile.TemporaryDirectory(prefix="investkit-catalog-corrupt-") as temp:
            root = Path(temp)
            source = root / "source"
            for directory in ("skills", "agents", "workflows", "specs", "schemas", "packages", "workspace-template", "fixtures"):
                shutil.copytree(REPOSITORY_ROOT / directory, source / directory)
            project = root / "project"
            project.mkdir()
            self.assertEqual(initialize_project(project, source_root=source).exit_code, 0)
            path = source / "schemas/runtime-asset-catalog-v1.json"
            original = path.read_bytes()
            value = json.loads(original)
            value["unexpected"] = True
            path.write_text(json.dumps(value), encoding="utf-8")
            report = run_doctor(project, source_root=source)
            self.assertNotEqual(report.exit_code, 0)
            self.assertTrue(
                any(
                    check.status.value == "FAIL" and "asset catalog" in check.name.lower()
                    for check in report.checks
                )
            )
            self.assertNotEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
