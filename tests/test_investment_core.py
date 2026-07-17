"""Behavioral RED contracts for InvestKit v0.2 Investment Core Pack.

The suite intentionally imports new v0.2 modules lazily so unittest discovery
remains healthy before implementation.  A missing module is reported as a
normal assertion failure that names the absent production contract.
"""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import re
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import tomllib
from typing import Any, Iterable, Mapping, Sequence, cast
from unittest import mock
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

INVESTMENT_CORE_SKILLS = (
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
RUNTIME_SKILLS = ("security-identification", *INVESTMENT_CORE_SKILLS)
WORKFLOW_STEPS = RUNTIME_SKILLS

REQUIRED_SPECS = {
    "research-principles.md",
    "evidence-policy.md",
    "source-policy.md",
    "financial-data-policy.md",
    "valuation-policy.md",
    "risk-policy.md",
    "report-policy.md",
}

RESULT_FIELDS = {
    "schema_version",
    "capability",
    "status",
    "skill",
    "method",
    "facts",
    "assumptions",
    "estimates",
    "unknowns",
    "findings",
    "risks",
    "warnings",
    "source_ids",
}

SKILL_SECTION_TERMS = (
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

REPORT_SECTIONS = (
    "Research Subject",
    "Demo Data Declaration",
    "Data Date",
    "Executive Summary",
    "Company Overview",
    "Business Model Analysis",
    "Financial Analysis",
    "Earnings Quality",
    "Valuation Analysis",
    "Comparable Companies Analysis",
    "Earnings Analysis",
    "Investment Thesis",
    "Bull / Base Case",
    "Independent Bear Case",
    "Catalyst Analysis",
    "Positive Evidence",
    "Negative Evidence",
    "Primary Risks",
    "Assumptions",
    "Estimates",
    "Unknowns / To Verify",
    "Skipped Capabilities",
    "Source Conflicts",
    "Data Sources",
    "Used Skills",
    "Loaded Specs",
    "Generation Time",
    "Research Boundary",
)


def _require_module(name: str) -> Any:
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as error:
        missing_name = str(error.name)
        if (
            missing_name == name
            or missing_name.startswith(name + ".")
            or name.startswith(missing_name + ".")
        ):
            raise AssertionError(f"missing v0.2 production module: {name}") from error
        raise


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md must begin with YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise AssertionError("SKILL.md frontmatter is not closed")
    raw = text[4:marker]
    values: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith((" ", "\t")) or ":" not in line:
            raise AssertionError("frontmatter must use one-line top-level scalar fields")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values, text[marker + 5 :]


def _markdown_links(text: str) -> list[str]:
    return [
        value.strip()
        for value in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        if value.strip() and not value.startswith(("http://", "https://", "#"))
    ]


def _provider_metadata(record: Mapping[str, Any]) -> None:
    required = {"as_of_date", "currency", "market", "source", "is_demo", "warnings"}
    if not required.issubset(record):
        raise AssertionError(f"provider record is missing {sorted(required - set(record))}")
    if record["is_demo"] is not True:
        raise AssertionError("offline Provider record must set is_demo: true")
    if not record.get("fixture_version") and not record.get("retrieved_at"):
        raise AssertionError("provider record needs a fixture version or retrieval time")
    if not isinstance(record["warnings"], list) or not record["warnings"]:
        raise AssertionError("provider warnings must be a non-empty list")


def _result_ids(result: Mapping[str, Any]) -> set[str]:
    identifiers: set[str] = set()
    for key in ("facts", "assumptions", "estimates", "unknowns", "findings", "risks"):
        values = result.get(key, [])
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, Mapping) and value.get("id"):
                identifiers.add(str(value["id"]))
    return identifiers


def _source_ids(value: Mapping[str, Any]) -> set[str]:
    records = value.get("sources", [])
    if not isinstance(records, list):
        return set()
    return {
        str(record.get("source_id"))
        for record in records
        if isinstance(record, Mapping) and record.get("source_id")
    }


def _cell_value(cell: Any) -> float | None:
    if isinstance(cell, (int, float)) and not isinstance(cell, bool):
        return float(cell)
    if isinstance(cell, Mapping):
        for key in ("equity_value_per_share", "per_share", "value"):
            value = cell.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
    return None


def _method_list(method: Mapping[str, Any], *keys: str) -> list[Any]:
    for key in keys:
        value = method.get(key)
        if isinstance(value, list):
            return value
    return []


class SkillAndCatalogContractTests(unittest.TestCase):
    maxDiff = None

    def test_catalog_has_exact_prerequisite_and_twelve_core_skills(self) -> None:
        catalog = _require_module("investkit.capabilities.catalog")
        self.assertEqual(tuple(catalog.INVESTMENT_CORE_SKILLS), INVESTMENT_CORE_SKILLS)
        self.assertEqual(tuple(catalog.RUNTIME_SKILLS), RUNTIME_SKILLS)

    def test_canonical_skill_directories_are_the_exact_release_set(self) -> None:
        actual = {
            path.name
            for path in (REPOSITORY_ROOT / "skills").iterdir()
            if path.is_dir() and not path.name.startswith(".")
        }
        self.assertEqual(actual, set(RUNTIME_SKILLS))
        self.assertNotIn("company-research", actual)
        self.assertNotIn("investment-report-writing", actual)

    def test_all_skill_frontmatter_has_only_name_and_description(self) -> None:
        for skill_name in RUNTIME_SKILLS:
            with self.subTest(skill=skill_name):
                path = REPOSITORY_ROOT / "skills" / skill_name / "SKILL.md"
                self.assertTrue(path.is_file(), f"missing governed Skill: {path}")
                metadata, body = _frontmatter(path.read_text(encoding="utf-8"))
                self.assertEqual(set(metadata), {"name", "description"})
                self.assertEqual(metadata["name"], skill_name)
                description = metadata["description"].lower()
                self.assertIn("use when", description)
                self.assertIn("do not use", description)
                self.assertRegex(body, r"(?im)^version\s*:\s*0\.2\.0\s*$")

    def test_all_skills_publish_professional_behavioral_contracts(self) -> None:
        for skill_name in RUNTIME_SKILLS:
            with self.subTest(skill=skill_name):
                path = REPOSITORY_ROOT / "skills" / skill_name / "SKILL.md"
                self.assertTrue(path.is_file(), f"missing governed Skill: {path}")
                text = path.read_text(encoding="utf-8")
                normalized = re.sub(r"[`*_#]", "", text).lower()
                for term in SKILL_SECTION_TERMS:
                    self.assertIn(term, normalized)
                self.assertRegex(normalized, r"completed|skipped|failed")
                self.assertIn("facts", normalized)
                self.assertIn("assumptions", normalized)
                self.assertIn("estimates", normalized)
                self.assertIn("unknowns", normalized)
                self.assertNotIn("third_party/raw", normalized.replace("\\", "/"))
                self.assertNotIn("adapted/skills", normalized.replace("\\", "/"))

    def test_each_skill_has_direct_resolvable_references_and_trigger_evals(self) -> None:
        for skill_name in RUNTIME_SKILLS:
            with self.subTest(skill=skill_name):
                root = REPOSITORY_ROOT / "skills" / skill_name
                skill_path = root / "SKILL.md"
                self.assertTrue(skill_path.is_file(), f"missing governed Skill: {skill_path}")
                links = _markdown_links(skill_path.read_text(encoding="utf-8"))
                self.assertIn("references/trigger-evals.json", links)
                for relative in links:
                    path = root / relative
                    self.assertFalse(path.is_symlink(), relative)
                    self.assertTrue(path.is_file(), f"broken Skill reference: {relative}")
                    self.assertTrue(path.resolve().is_relative_to(root.resolve()))
                    self.assertLessEqual(len(Path(relative).parts), 2)

    def test_discovery_returns_every_approved_nested_skill_file_only(self) -> None:
        catalog = _require_module("investkit.capabilities.catalog")
        for skill_name in RUNTIME_SKILLS:
            with self.subTest(skill=skill_name):
                root = REPOSITORY_ROOT / "skills" / skill_name
                expected = tuple(
                    sorted(
                        path
                        for path in root.rglob("*")
                        if path.is_file() and not path.is_symlink()
                    )
                )
                actual = tuple(
                    sorted(catalog.discover_skill_files(REPOSITORY_ROOT, skill_name))
                )
                self.assertEqual(actual, expected)
        with self.assertRaises((KeyError, ValueError)):
            catalog.discover_skill_files(REPOSITORY_ROOT, "unapproved-skill")

    def test_each_core_skill_has_a_complete_capability_synthesis(self) -> None:
        report_root = REPOSITORY_ROOT / "reports/capabilities"
        actual = {path.name for path in report_root.glob("*-synthesis.md")}
        expected = {f"{name}-synthesis.md" for name in INVESTMENT_CORE_SKILLS}
        self.assertEqual(actual, expected)
        for name in INVESTMENT_CORE_SKILLS:
            with self.subTest(capability=name):
                text = (report_root / f"{name}-synthesis.md").read_text(encoding="utf-8")
                normalized = text.lower()
                for term in (
                    "candidate",
                    "strength",
                    "weakness",
                    "adopt",
                    "reject",
                    "license",
                    "final",
                    "eval",
                ):
                    self.assertIn(term, normalized)
                self.assertRegex(
                    normalized,
                    r"(?s)no .{0,200}(?:executed|installed|called)|"
                    r"not (?:executed|installed)",
                )
                self.assertRegex(
                    normalized,
                    r"(?s)no .{0,200}copied|not copied|no-copy|independent",
                )

    def test_trigger_eval_files_cover_two_positive_and_two_near_misses(self) -> None:
        for skill_name in RUNTIME_SKILLS:
            with self.subTest(skill=skill_name):
                path = (
                    REPOSITORY_ROOT
                    / "skills"
                    / skill_name
                    / "references/trigger-evals.json"
                )
                self.assertTrue(path.is_file(), f"missing trigger Eval contract: {path}")
                payload = _read_json(path)
                self.assertEqual(payload.get("skill"), skill_name)
                self.assertEqual(payload.get("schema_version"), "1.0")
                cases = payload.get("cases")
                self.assertIsInstance(cases, list)
                positives = 0
                negatives = 0
                for case in cases:
                    self.assertIsInstance(case, Mapping)
                    self.assertTrue(case.get("id"))
                    self.assertTrue(case.get("question"))
                    self.assertIsInstance(case.get("expected_skills"), list)
                    self.assertIsInstance(case.get("excluded_skills"), list)
                    positives += skill_name in case["expected_skills"]
                    negatives += skill_name in case["excluded_skills"]
                self.assertGreaterEqual(positives, 2)
                self.assertGreaterEqual(negatives, 2)

    def test_deterministic_trigger_evaluator_passes_all_include_exclude_cases(self) -> None:
        catalog = _require_module("investkit.capabilities.catalog")
        for skill_name in RUNTIME_SKILLS:
            path = (
                REPOSITORY_ROOT
                / "skills"
                / skill_name
                / "references/trigger-evals.json"
            )
            self.assertTrue(path.is_file(), f"missing trigger Eval contract: {path}")
            payload = _read_json(path)
            for case in payload["cases"]:
                question = str(case["question"])
                with self.subTest(skill=skill_name, case=case["id"]):
                    if skill_name in case["expected_skills"]:
                        self.assertTrue(catalog.evaluate_trigger(question, skill_name))
                    if skill_name in case["excluded_skills"]:
                        self.assertFalse(catalog.evaluate_trigger(question, skill_name))

    def test_quick_validate_accepts_exactly_the_thirteen_governed_skills(self) -> None:
        validator = REPOSITORY_ROOT / "scripts/quick_validate.py"
        skill_dirs = [REPOSITORY_ROOT / "skills" / name for name in RUNTIME_SKILLS]
        completed = subprocess.run(
            [sys.executable, str(validator), *(str(path) for path in skill_dirs)],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("validated exactly 13 governed Skills", completed.stdout)

        incomplete = subprocess.run(
            [sys.executable, str(validator), *(str(path) for path in skill_dirs[:-1])],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(incomplete.returncode, 0)
        self.assertIn("expected exactly the 13", incomplete.stderr)

    def test_quick_validate_rejects_malformed_governed_files(self) -> None:
        validator = REPOSITORY_ROOT / "scripts/quick_validate.py"
        invalid_cases = {
            "openai-default-prompt": (
                "agents/openai.yaml",
                'interface:\n  display_name: "Security Identification"\n'
                '  short_description: "Resolve a stable security identity"\n'
                '  default_prompt: "Resolve this security without the governed Skill."\n',
            ),
            "eval-schema-version": (
                "references/trigger-evals.json",
                json.dumps(
                    {
                        "schema_version": "2.0",
                        "skill": "security-identification",
                        "cases": [
                            {
                                "id": f"case-{index}",
                                "question": f"Question {index}",
                                "expected_skills": ["security-identification"]
                                if index < 2
                                else [],
                                "excluded_skills": []
                                if index < 2
                                else ["security-identification"],
                            }
                            for index in range(4)
                        ],
                    }
                ),
            ),
            "empty-method-contract": ("references/method-contract.md", " \n"),
            "unexpected-governed-file": ("references/extra.md", "# Unexpected\n"),
        }
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            for case_name, (relative, content) in invalid_cases.items():
                with self.subTest(case=case_name):
                    case_root = temporary_root / case_name
                    skill_dirs = []
                    for skill_name in RUNTIME_SKILLS:
                        destination = case_root / skill_name
                        shutil.copytree(REPOSITORY_ROOT / "skills" / skill_name, destination)
                        skill_dirs.append(destination)
                    target = case_root / "security-identification" / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(content, encoding="utf-8")
                    completed = subprocess.run(
                        [
                            sys.executable,
                            str(validator),
                            *(str(path) for path in skill_dirs),
                        ],
                        cwd=REPOSITORY_ROOT,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertNotEqual(
                        completed.returncode,
                        0,
                        completed.stdout + completed.stderr,
                    )


class CapabilityResultContractTests(unittest.TestCase):
    def setUp(self) -> None:
        contracts = _require_module("investkit.capabilities.contracts")
        self.build_result = contracts.build_capability_result
        self.validate_result = contracts.validate_capability_result

    def valid_result(self, *, status: str = "completed") -> dict[str, Any]:
        arguments: dict[str, Any] = {
            "status": status,
            "skill": {"name": "business-model-analysis", "version": "0.2.0"},
            "method": {"name": "business-model-map", "version": "1.0"},
            "facts": [
                {
                    "id": "fact-revenue-model",
                    "statement": "The fictional fixture has two revenue components.",
                    "source_ids": ["demo-source"],
                }
            ],
            "assumptions": [
                {
                    "id": "assumption-renewal",
                    "statement": "Renewal behavior is representative.",
                    "rationale": "Only one historical cohort is available.",
                    "materiality": "high",
                }
            ],
            "estimates": [
                {
                    "id": "estimate-mix",
                    "label": "Recurring revenue mix",
                    "value": 0.3,
                    "method": "reported recurring revenue / total revenue",
                    "input_ids": ["fact-revenue-model", "assumption-renewal"],
                }
            ],
            "unknowns": [
                {
                    "id": "unknown-retention",
                    "gap": "Customer retention detail is unavailable.",
                    "impact": "Lifetime-value analysis cannot be completed.",
                }
            ],
            "findings": [
                {
                    "id": "finding-hybrid",
                    "statement": "The business model is hybrid.",
                    "source_ids": ["demo-source"],
                }
            ],
            "risks": [
                {
                    "id": "risk-concentration",
                    "statement": "Tender concentration.",
                    "source_ids": ["demo-source"],
                }
            ],
            "warnings": ["Fictional demo data only."],
        }
        if status == "skipped":
            arguments.update(
                {
                    "facts": [],
                    "assumptions": [],
                    "estimates": [],
                    "findings": [],
                    "skip_reason": "No defensible input dataset.",
                    "missing_inputs": ["customer cohorts"],
                }
            )
        return self.build_result("business-model-analysis", **arguments)

    def test_completed_result_has_the_exact_envelope_and_validates(self) -> None:
        result = self.valid_result()
        self.assertEqual(set(result), RESULT_FIELDS)
        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["status"], "completed")
        self.validate_result(result, expected="business-model-analysis")

    def test_source_ids_are_the_deduplicated_union_of_fact_references(self) -> None:
        result = self.valid_result()
        self.assertEqual(result["source_ids"], ["demo-source"])

    def test_invalid_status_is_rejected(self) -> None:
        result = self.valid_result()
        result["status"] = "pending"
        with self.assertRaises((TypeError, ValueError)):
            self.validate_result(result, expected="business-model-analysis")

    def test_fact_without_id_statement_or_source_is_rejected(self) -> None:
        for key in ("id", "statement", "source_ids"):
            with self.subTest(field=key):
                result = self.valid_result()
                result["facts"][0].pop(key)
                with self.assertRaises((TypeError, ValueError)):
                    self.validate_result(result, expected="business-model-analysis")

    def test_assumption_requires_rationale_and_materiality(self) -> None:
        for key in ("rationale", "materiality"):
            with self.subTest(field=key):
                result = self.valid_result()
                result["assumptions"][0].pop(key)
                with self.assertRaises((TypeError, ValueError)):
                    self.validate_result(result, expected="business-model-analysis")

    def test_estimate_requires_method_and_material_inputs(self) -> None:
        result = self.valid_result()
        result["estimates"][0].pop("method")
        with self.assertRaises((TypeError, ValueError)):
            self.validate_result(result, expected="business-model-analysis")
        result = self.valid_result()
        result["estimates"][0].pop("input_ids")
        with self.assertRaises((TypeError, ValueError)):
            self.validate_result(result, expected="business-model-analysis")

    def test_unknown_requires_a_gap_and_decision_impact(self) -> None:
        result = self.valid_result()
        result["unknowns"][0].pop("impact")
        with self.assertRaises((TypeError, ValueError)):
            self.validate_result(result, expected="business-model-analysis")

    def test_skipped_result_requires_reason_and_missing_inputs(self) -> None:
        result = self.valid_result(status="skipped")
        self.validate_result(result, expected="business-model-analysis")
        for key in ("skip_reason", "missing_inputs"):
            with self.subTest(field=key):
                invalid = deepcopy(result)
                invalid.pop(key)
                with self.assertRaises((TypeError, ValueError)):
                    self.validate_result(invalid, expected="business-model-analysis")

    def test_failed_is_valid_but_capability_mismatch_is_not(self) -> None:
        failed = self.valid_result(status="failed")
        self.validate_result(failed, expected="business-model-analysis")
        with self.assertRaises((TypeError, ValueError)):
            self.validate_result(failed, expected="valuation-analysis")

    def test_earnings_quality_keeps_missing_numeric_inputs_out_of_facts(self) -> None:
        analysis = _require_module("investkit.capabilities.analysis")
        result = analysis.run_capability(
            "earnings-quality-analysis",
            {
                "sources": {"sources": [{"source_id": "demo-source"}]},
                "statements": {
                    "periods": [
                        {"fiscal_year": 2024, "total_assets": 100.0},
                        {
                            "fiscal_year": 2025,
                            "cash_from_operations": None,
                            "net_income": None,
                            "total_assets": 110.0,
                        },
                    ],
                    "units": "USD millions",
                },
            },
        )
        self.assertEqual(result["status"], "completed")
        self.assertFalse(result["facts"])
        unknown_ids = {record["id"] for record in result["unknowns"]}
        self.assertIn("unknown-quality-net-income", unknown_ids)
        self.assertIn("unknown-quality-operating-cash", unknown_ids)
        self.assertNotIn("None", json.dumps(result["facts"]))


class DemoProviderV02Tests(unittest.TestCase):
    def setUp(self) -> None:
        from investkit.providers.demo import DemoProvider

        self.provider = DemoProvider(REPOSITORY_ROOT)
        self.identity = self.provider.identify_security("demo")
        self.security_id = str(self.identity["security_id"])

    def all_records(self) -> dict[str, Mapping[str, Any]]:
        for name in (
            "get_peer_comparables",
            "get_earnings_history",
            "get_catalyst_events",
        ):
            self.assertTrue(
                callable(getattr(self.provider, name, None)),
                f"missing v0.2 Demo Provider operation: {name}",
            )
        return {
            "identify_security": self.identity,
            "get_security_profile": self.provider.get_security_profile(self.security_id),
            "get_financial_statements": self.provider.get_financial_statements(
                self.security_id
            ),
            "get_price_history": self.provider.get_price_history(self.security_id),
            "get_valuation_inputs": self.provider.get_valuation_inputs(self.security_id),
            "get_source_metadata": self.provider.get_source_metadata(self.security_id),
            "get_peer_comparables": self.provider.get_peer_comparables(self.security_id),
            "get_earnings_history": self.provider.get_earnings_history(self.security_id),
            "get_catalyst_events": self.provider.get_catalyst_events(self.security_id),
        }

    def test_all_nine_provider_operations_are_offline_and_provenanced(self) -> None:
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
            records = self.all_records()
        self.assertEqual(len(records), 9)
        for name, record in records.items():
            with self.subTest(operation=name):
                _provider_metadata(record)

    def test_peer_fixture_has_inclusions_exclusions_and_reasons(self) -> None:
        self.assertTrue(
            callable(getattr(self.provider, "get_peer_comparables", None)),
            "missing v0.2 Demo Provider operation: get_peer_comparables",
        )
        record = self.provider.get_peer_comparables(self.security_id)
        peers = record.get("peers", record.get("comparables"))
        self.assertIsInstance(peers, list)
        self.assertGreaterEqual(len(peers), 3)
        statuses = {peer.get("status") for peer in peers if isinstance(peer, Mapping)}
        self.assertTrue({"included", "excluded"}.issubset(statuses))
        excluded = [peer for peer in peers if peer.get("status") == "excluded"]
        self.assertTrue(all(peer.get("reason") for peer in excluded))

    def test_earnings_and_catalyst_fixtures_preserve_missingness(self) -> None:
        self.assertTrue(
            callable(getattr(self.provider, "get_earnings_history", None)),
            "missing v0.2 Demo Provider operation: get_earnings_history",
        )
        self.assertTrue(
            callable(getattr(self.provider, "get_catalyst_events", None)),
            "missing v0.2 Demo Provider operation: get_catalyst_events",
        )
        earnings = self.provider.get_earnings_history(self.security_id)
        periods = earnings.get("events", earnings.get("periods"))
        self.assertIsInstance(periods, list)
        self.assertTrue(periods)
        self.assertTrue(
            any(
                isinstance(period, Mapping)
                and {"actual", "expectation", "guidance"}.issubset(period)
                for period in periods
            )
        )
        self.assertTrue(
            any(
                isinstance(period, Mapping)
                and period.get("transcript_available") is False
                for period in periods
            )
        )
        catalyst_record = self.provider.get_catalyst_events(self.security_id)
        events = catalyst_record.get("events")
        self.assertIsInstance(events, list)
        self.assertTrue(events)
        for event in cast(list[Mapping[str, Any]], events):
            self.assertTrue(event.get("date") or event.get("window"))
            self.assertTrue(event.get("source_ids"))
            self.assertIn("materiality", event)
            self.assertIn("uncertainty", event)


class InvestmentCoreWorkflowTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="investkit-v02-workflow-")
        self.project_root = Path(self.temporary.name) / "project"
        self.project_root.mkdir()
        from investkit.initializer import initialize_project
        from investkit.research.workflow import run_demo_research

        initialized = initialize_project(self.project_root, source_root=REPOSITORY_ROOT)
        self.assertEqual(initialized.exit_code, 0, initialized)
        self.result = run_demo_research(self.project_root, REPOSITORY_ROOT)
        self.assertEqual(self.result.status, "completed", self.result)
        self.task_path = self.result.task_path

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def capability(self, name: str) -> dict[str, Any]:
        path = self.task_path / "capabilities" / f"{name}.json"
        self.assertTrue(path.is_file(), f"missing v0.2 capability artifact: {path}")
        value = _read_json(path)
        self.assertIsInstance(value, dict)
        return value

    def test_workflow_has_exact_thirteen_steps_and_one_result_per_step(self) -> None:
        plan = _read_json(self.task_path / "plan.json")
        self.assertEqual(plan.get("workflow"), "company-deep-dive")
        self.assertEqual(tuple(step["id"] for step in plan["steps"]), WORKFLOW_STEPS)
        self.assertTrue(all(step["status"] == "completed" for step in plan["steps"]))
        actual = {path.stem for path in (self.task_path / "capabilities").glob("*.json")}
        self.assertEqual(actual, set(WORKFLOW_STEPS))

    def test_every_capability_artifact_is_schema_valid_and_source_resolved(self) -> None:
        contracts = _require_module("investkit.capabilities.contracts")
        sources = _source_ids(_read_json(self.task_path / "sources.json"))
        self.assertTrue(sources)
        for name in WORKFLOW_STEPS:
            with self.subTest(capability=name):
                result = self.capability(name)
                contracts.validate_capability_result(result, expected=name)
                self.assertTrue(RESULT_FIELDS.issubset(result))
                for fact in result["facts"]:
                    self.assertTrue(set(fact["source_ids"]).issubset(sources))

    def test_company_and_business_results_are_substantive_and_bounded(self) -> None:
        company = json.dumps(self.capability("company-deep-research"), sort_keys=True).lower()
        for term in ("segment", "management", "capital allocation", "competitive", "unknown"):
            self.assertIn(term, company)
        business = json.dumps(self.capability("business-model-analysis"), sort_keys=True).lower()
        for term in (
            "revenue model",
            "payer",
            "value proposition",
            "order",
            "backlog",
            "cash",
            "fragil",
        ):
            self.assertIn(term, business)
        self.assertNotRegex(business, r"\bbuy\b|\bsell\b|guaranteed return")

    def test_financial_and_earnings_quality_results_use_guarded_methods(self) -> None:
        financial = self.capability("financial-statement-analysis")
        financial_text = json.dumps(financial, sort_keys=True).lower()
        for term in ("period", "revenue", "margin", "cash flow", "leverage", "liquidity"):
            self.assertIn(term, financial_text)
        self.assertTrue(financial["estimates"])
        quality = self.capability("earnings-quality-analysis")
        quality_text = json.dumps(quality, sort_keys=True).lower()
        for term in ("cash conversion", "accrual", "working capital", "one-off"):
            self.assertIn(term, quality_text)
        self.assertEqual(
            quality["method"]["working_capital_review"]["status"], "completed"
        )
        self.assertTrue(
            any(
                estimate.get("id") == "estimate-working-capital-change"
                for estimate in quality["estimates"]
            )
        )
        self.assertNotRegex(quality_text, r"fraud probability|\bbuy\b|\bsell\b")

    def test_dcf_has_three_scenarios_bridge_and_guarded_odd_sensitivity(self) -> None:
        valuation = self.capability("valuation-analysis")
        method = valuation["method"]
        scenarios = method.get("scenarios")
        self.assertIsInstance(scenarios, Mapping)
        self.assertEqual(set(scenarios), {"bear", "base", "bull"})
        for name, scenario in scenarios.items():
            with self.subTest(scenario=name):
                self.assertGreater(scenario["wacc"], scenario["terminal_growth"])
                self.assertGreater(scenario["diluted_shares"], 0)
                self.assertIsInstance(scenario["enterprise_value"], (int, float))
                self.assertIsInstance(scenario["equity_value"], (int, float))
                self.assertIsInstance(
                    scenario["equity_value_per_share"], (int, float)
                )
        self.assertTrue(method.get("ev_to_equity_bridge"))
        sensitivity = method.get("sensitivity")
        self.assertIsInstance(sensitivity, Mapping)
        wacc_values = _method_list(sensitivity, "wacc_values", "wacc")
        growth_values = _method_list(
            sensitivity, "terminal_growth_values", "terminal_growth"
        )
        grid = _method_list(sensitivity, "grid", "values")
        self.assertGreaterEqual(len(wacc_values), 3)
        self.assertGreaterEqual(len(growth_values), 3)
        self.assertEqual(len(wacc_values) % 2, 1)
        self.assertEqual(len(growth_values) % 2, 1)
        self.assertEqual(len(grid), len(growth_values))
        self.assertTrue(all(len(row) == len(wacc_values) for row in grid))
        center = _cell_value(grid[len(growth_values) // 2][len(wacc_values) // 2])
        self.assertIsNotNone(center)
        self.assertAlmostEqual(
            cast(float, center),
            float(scenarios["base"]["equity_value_per_share"]),
            places=8,
        )
        for row_index, growth in enumerate(growth_values):
            for column_index, wacc in enumerate(wacc_values):
                if wacc <= growth:
                    self.assertIsNone(_cell_value(grid[row_index][column_index]))

    def test_comps_excludes_invalid_metrics_and_uses_valid_medians(self) -> None:
        result = self.capability("comps-analysis")
        method = result["method"]
        ledger = method.get("peer_ledger")
        self.assertIsInstance(ledger, list)
        self.assertTrue(any(peer.get("status") == "excluded" for peer in ledger))
        serialized = json.dumps(ledger, sort_keys=True).lower()
        self.assertRegex(serialized, r"negative|zero|missing|not comparable")
        distributions = method.get("distributions")
        self.assertIsInstance(distributions, Mapping)
        self.assertTrue(distributions)
        for metric, distribution in distributions.items():
            with self.subTest(metric=metric):
                observations = distribution.get("observations")
                self.assertIsInstance(observations, list)
                self.assertTrue(observations)
                self.assertEqual(distribution.get("sample_size"), len(observations))
                self.assertAlmostEqual(
                    distribution.get("median"), statistics.median(observations)
                )
                quartiles = distribution.get("quartiles")
                self.assertIsInstance(quartiles, Mapping)
                self.assertLessEqual(quartiles["q1"], distribution["median"])
                self.assertGreaterEqual(quartiles["q3"], distribution["median"])
                self.assertEqual(
                    distribution.get("range"),
                    {"low": min(observations), "high": max(observations)},
                )
        implied_ranges = method.get("implied_ranges")
        self.assertIsInstance(implied_ranges, Mapping)
        self.assertTrue(implied_ranges)
        self.assertIn("ev_to_operating_income", implied_ranges)
        for metric, implied_range in implied_ranges.items():
            with self.subTest(implied_metric=metric):
                self.assertTrue(implied_range.get("equity_value_range"))
                self.assertTrue(implied_range.get("equity_value_per_share_range"))
                self.assertTrue(implied_range.get("selected_rationale"))
        self.assertEqual(
            method["relative_ev_to_equity_bridge"].get("status"), "completed"
        )

    def test_earnings_separates_expectations_guidance_and_missing_transcript(self) -> None:
        result = self.capability("earnings-analysis")
        method = result["method"]
        self.assertEqual(method.get("mode"), "review")
        self.assertTrue(method.get("consensus_comparison"))
        self.assertTrue(method.get("guidance_comparison"))
        self.assertIn("observation_time", json.dumps(method["consensus_comparison"]))
        self.assertIn("midpoint", json.dumps(method["guidance_comparison"]))
        self.assertIs(method.get("transcript_available"), False)
        self.assertTrue(result["unknowns"])
        self.assertRegex(json.dumps(result).lower(), r"transcript.*unknown|unknown.*transcript")

    def test_thesis_is_falsifiable_and_bear_case_is_independent(self) -> None:
        thesis = self.capability("investment-thesis")
        thesis_method = thesis["method"]
        for key in (
            "thesis_statement",
            "time_horizon",
            "bull_case",
            "base_case",
            "bear_case_seed",
            "pillars",
            "falsifiers",
            "evidence_sufficiency",
        ):
            self.assertTrue(thesis_method.get(key), key)
        for pillar in thesis_method["pillars"]:
            self.assertTrue(pillar.get("confirming_evidence"))
            self.assertTrue(
                pillar.get("disconfirming_evidence") or pillar.get("evidence_gap")
            )
        bear = self.capability("bear-case-analysis")
        bear_method = bear["method"]
        for key in (
            "thesis_snapshot_checksum",
            "counter_thesis",
            "fragile_assumptions",
            "failure_signals",
            "thesis_killers_for_bear_case",
            "independence_check",
        ):
            self.assertTrue(bear_method.get(key), key)
        self.assertNotEqual(
            bear_method["counter_thesis"], thesis_method["thesis_statement"]
        )
        self.assertTrue(bear_method["independence_check"].get("passed"))
        self.assertNotRegex(json.dumps(bear).lower(), r"\bshort\b|\bsell\b|stop loss")

    def test_catalysts_and_source_verification_preserve_uncertainty_and_conflicts(self) -> None:
        catalyst = self.capability("catalyst-analysis")
        events = catalyst["method"].get("events")
        self.assertIsInstance(events, list)
        self.assertTrue(events)
        for event in events:
            self.assertTrue(event.get("date") or event.get("window"))
            self.assertIn("materiality", event)
            self.assertIn("uncertainty", event)
            self.assertTrue(event.get("dependencies"))
            self.assertTrue(event.get("downside_path"))
        verification = self.capability("source-verification")
        method = verification["method"]
        self.assertTrue(method.get("claim_ledger"))
        self.assertIn(
            method.get("gate_status"), {"pass", "pass_with_disclosed_gaps"}
        )
        serialized = json.dumps(method).lower()
        for term in ("quality", "freshness", "coverage", "conflict"):
            self.assertIn(term, serialized)

    def test_missing_peer_data_skips_comps_and_propagates_the_gap(self) -> None:
        from investkit.providers.demo import DemoProvider
        from investkit.providers.base import Provider
        from investkit.research.workflow import run_demo_research

        delegate = DemoProvider(REPOSITORY_ROOT)

        class MissingPeers:
            def __getattr__(self, name: str) -> Any:
                return getattr(delegate, name)

            def get_peer_comparables(self, security_id: str) -> Mapping[str, Any]:
                record = deepcopy(dict(delegate.get_peer_comparables(security_id)))
                record["peers"] = []
                record["comparables"] = []
                record["warnings"] = [*record["warnings"], "Peer data is missing."]
                return record

        result = run_demo_research(
            self.project_root,
            REPOSITORY_ROOT,
            provider=cast(Provider, MissingPeers()),
        )
        self.assertEqual(result.status, "completed")
        comps_path = result.task_path / "capabilities/comps-analysis.json"
        self.assertTrue(comps_path.is_file(), "missing skipped comps capability artifact")
        comps = _read_json(comps_path)
        self.assertEqual(comps["status"], "skipped")
        self.assertTrue(comps["skip_reason"])
        self.assertTrue(comps["missing_inputs"])
        thesis_path = result.task_path / "capabilities/investment-thesis.json"
        self.assertTrue(thesis_path.is_file(), "missing downstream thesis artifact")
        thesis = _read_json(thesis_path)
        self.assertRegex(json.dumps(thesis).lower(), r"comps.*(?:skip|missing|unknown)")
        report = (result.task_path / "report.md").read_text(encoding="utf-8")
        self.assertRegex(report.lower(), r"comps-analysis.*skipped|skipped.*comps")

    def test_report_is_a_no_new_claim_view_with_all_required_disclosures(self) -> None:
        report = (self.task_path / "report.md").read_text(encoding="utf-8")
        for section in REPORT_SECTIONS:
            with self.subTest(section=section):
                self.assertRegex(report, rf"(?im)^#+\s+{re.escape(section)}\s*$")
        self.assertRegex(report, r"(?i)fictional|demo data")
        self.assertRegex(report, r"(?i)not\s+(?:real-time|live)")
        self.assertNotRegex(
            report,
            r"(?i)\b(?:buy|sell|hold)\b|guaranteed (?:return|profit)|"
            r"risk-free return|price will|position size|stop loss",
        )
        allowed_ids: set[str] = set()
        allowed_sources: set[str] = set()
        for name in WORKFLOW_STEPS[:-1]:
            result = self.capability(name)
            allowed_ids.update(_result_ids(result))
            allowed_sources.update(str(value) for value in result["source_ids"])
        report_result = self.capability("investment-report")
        method = report_result["method"]
        self.assertTrue(set(method["emitted_claim_ids"]).issubset(allowed_ids))
        self.assertTrue(set(method["emitted_source_ids"]).issubset(allowed_sources))
        self.assertIn(method["completeness"], {"complete", "complete_with_gaps"})

    def test_completed_resume_preserves_all_analytical_artifacts(self) -> None:
        from investkit.research.workflow import resume_demo_research

        immutable = [
            self.task_path / "report.md",
            self.task_path / "sources.json",
            self.task_path / "assumptions.json",
            self.task_path / "findings.json",
            self.task_path / "risks.json",
            *sorted((self.task_path / "data").glob("*.json")),
            *sorted((self.task_path / "capabilities").glob("*.json")),
        ]
        before = {path.relative_to(self.task_path): path.read_bytes() for path in immutable}
        log_before = (self.task_path / "run-log.json").read_bytes()

        resumed = resume_demo_research(
            self.project_root, self.result.task_id, REPOSITORY_ROOT
        )

        self.assertEqual(resumed.status, "completed")
        after = {path.relative_to(self.task_path): path.read_bytes() for path in immutable}
        self.assertEqual(after, before)
        self.assertNotEqual((self.task_path / "run-log.json").read_bytes(), log_before)

    def test_resume_rejects_a_corrupt_completed_capability_without_overwrite(self) -> None:
        from investkit.research.workflow import resume_demo_research

        report_before = (self.task_path / "report.md").read_bytes()
        path = self.task_path / "capabilities/valuation-analysis.json"
        self.assertTrue(path.is_file(), "missing valuation capability artifact")
        value = _read_json(path)
        value.pop("estimates")
        _write_json(path, value)
        with self.assertRaises(Exception):
            resume_demo_research(self.project_root, self.result.task_id, REPOSITORY_ROOT)
        self.assertEqual((self.task_path / "report.md").read_bytes(), report_before)

    def test_resume_rejects_a_broken_fact_source_id(self) -> None:
        from investkit.research.workflow import resume_demo_research

        path = self.task_path / "capabilities/company-deep-research.json"
        self.assertTrue(path.is_file(), "missing company capability artifact")
        value = _read_json(path)
        self.assertTrue(value["facts"])
        value["facts"][0]["source_ids"] = ["missing-source-id"]
        value["source_ids"] = ["missing-source-id"]
        _write_json(path, value)
        with self.assertRaises(Exception):
            resume_demo_research(self.project_root, self.result.task_id, REPOSITORY_ROOT)

    def test_resume_rejects_external_symlinked_capability_without_reading_it(self) -> None:
        from investkit.research.workflow import resume_demo_research

        outside = Path(self.temporary.name) / "outside-capability.json"
        sentinel = b'{"secret":"outside sentinel"}\n'
        outside.write_bytes(sentinel)
        path = self.task_path / "capabilities/bear-case-analysis.json"
        self.assertTrue(path.is_file(), "missing bear-case capability artifact")
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises(Exception):
            resume_demo_research(self.project_root, self.result.task_id, REPOSITORY_ROOT)
        self.assertEqual(outside.read_bytes(), sentinel)

    def test_failed_resume_skips_verified_capability_artifacts(self) -> None:
        from investkit.providers.demo import DemoProvider
        from investkit.providers.base import Provider
        from investkit.research.workflow import resume_demo_research, run_demo_research

        delegate = DemoProvider(REPOSITORY_ROOT)

        class FailingPeers:
            def __getattr__(self, name: str) -> Any:
                return getattr(delegate, name)

            def get_peer_comparables(self, security_id: str) -> Mapping[str, Any]:
                raise RuntimeError("controlled peer fixture failure")

        failed = run_demo_research(
            self.project_root,
            REPOSITORY_ROOT,
            provider=cast(Provider, FailingPeers()),
        )
        self.assertEqual(failed.status, "failed")
        preserved_paths = sorted((failed.task_path / "capabilities").glob("*.json"))
        self.assertGreaterEqual(len(preserved_paths), 6)
        before = {path.name: path.read_bytes() for path in preserved_paths}

        resumed = resume_demo_research(
            self.project_root, failed.task_id, REPOSITORY_ROOT
        )

        self.assertEqual(resumed.status, "completed")
        self.assertEqual(
            {path.name: path.read_bytes() for path in preserved_paths}, before
        )
        log = (failed.task_path / "run-log.json").read_text(encoding="utf-8").lower()
        self.assertIn("resume-skipped", log)


class InitDoctorPackagingSecurityTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="investkit-v02-harness-")
        self.project_root = Path(self.temporary.name) / "project"
        self.project_root.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def initialize(self) -> Any:
        from investkit.initializer import initialize_project

        return initialize_project(self.project_root, source_root=REPOSITORY_ROOT)

    def test_init_installs_every_nested_approved_file_and_no_legacy_skill(self) -> None:
        result = self.initialize()
        self.assertEqual(result.exit_code, 0, result)
        installed = {
            path.name
            for path in (self.project_root / ".agents/skills").iterdir()
            if path.is_dir()
        }
        self.assertEqual(installed, set(RUNTIME_SKILLS))
        manifest = _read_json(self.project_root / ".investkit/install-manifest.json")
        mappings = [value for value in manifest["mappings"] if value.get("kind") == "skill"]
        expected_sources = {
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for skill in RUNTIME_SKILLS
            for path in (REPOSITORY_ROOT / "skills" / skill).rglob("*")
            if path.is_file() and not path.is_symlink()
        }
        self.assertEqual({value["source"] for value in mappings}, expected_sources)
        for mapping in mappings:
            source = REPOSITORY_ROOT / mapping["source"]
            target = self.project_root / mapping["target"]
            self.assertTrue(target.is_file())
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(mapping["source_sha256"], digest)
            self.assertEqual(mapping["target_sha256"], digest)
            self.assertEqual(target.read_bytes(), source.read_bytes())

    def test_init_preserves_a_conflicting_nested_user_file(self) -> None:
        target = (
            self.project_root
            / ".agents/skills/valuation-analysis/references/trigger-evals.json"
        )
        target.parent.mkdir(parents=True)
        sentinel = b'{"user_owned":true}\n'
        target.write_bytes(sentinel)
        result = self.initialize()
        self.assertNotEqual(result.exit_code, 0)
        self.assertEqual(target.read_bytes(), sentinel)
        self.assertTrue(any(action.action == "WARN" for action in result.actions))

    def test_doctor_fails_when_an_installed_nested_reference_is_missing(self) -> None:
        from investkit.doctor import run_doctor

        self.assertEqual(self.initialize().exit_code, 0)
        missing = (
            self.project_root
            / ".agents/skills/valuation-analysis/references/trigger-evals.json"
        )
        self.assertTrue(missing.is_file(), "init did not install the nested Skill reference")
        missing.unlink()
        report = run_doctor(self.project_root, source_root=REPOSITORY_ROOT)
        self.assertNotEqual(report.exit_code, 0)
        failures = " ".join(
            f"{check.name} {check.message}"
            for check in report.checks
            if str(getattr(check.status, "value", check.status)) == "FAIL"
        ).lower()
        self.assertIn("trigger-evals.json", failures)

    def test_doctor_fails_on_corrupt_capability_or_missing_mandatory_stage(self) -> None:
        from investkit.doctor import run_doctor
        from investkit.research.workflow import run_demo_research

        self.assertEqual(self.initialize().exit_code, 0)
        result = run_demo_research(self.project_root, REPOSITORY_ROOT)
        path = result.task_path / "capabilities/source-verification.json"
        self.assertTrue(path.is_file(), "demo did not persist source-verification result")
        value = _read_json(path)
        value["status"] = "pending"
        _write_json(path, value)
        report = run_doctor(self.project_root, source_root=REPOSITORY_ROOT)
        self.assertNotEqual(report.exit_code, 0)
        failures = " ".join(
            f"{check.name} {check.message}"
            for check in report.checks
            if str(getattr(check.status, "value", check.status)) == "FAIL"
        ).lower()
        self.assertRegex(failures, r"source-verification|capabilit|status")

    def test_runtime_has_no_network_subprocess_or_trellis_dependency(self) -> None:
        forbidden_imports = {"requests", "httpx", "subprocess", "urllib.request"}
        runtime_root = REPOSITORY_ROOT / "src/investkit"
        # Network code is permitted only in dedicated, permission-gated Providers;
        # the imported/local FileProvider and workflow core must remain offline.
        paths = [runtime_root / "providers" / "file.py"]
        for path in paths:
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT)):
                text = path.read_text(encoding="utf-8")
                tree = ast.parse(text, filename=str(path))
                imports: set[str] = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.update(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module)
                self.assertFalse(imports & forbidden_imports)
                self.assertFalse(any(name.startswith("trellis") for name in imports))
                self.assertNotRegex(text, r"(?i)(?:^|[/\\])\.trellis(?:[/\\]|$)")
                self.assertNotRegex(text, r"os\.(?:getenv|environ)\s*[\[(]")

    def test_packaging_declares_every_nested_skill_file_and_no_dependencies(self) -> None:
        pyproject = tomllib.loads(
            (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(pyproject["project"]["dependencies"], [])
        data_files = pyproject["tool"]["setuptools"]["data-files"]
        declared: set[Path] = set()
        for patterns in data_files.values():
            for pattern in patterns:
                declared.update(REPOSITORY_ROOT.glob(pattern))
        expected: set[Path] = set()
        for skill in RUNTIME_SKILLS:
            root = REPOSITORY_ROOT / "skills" / skill
            self.assertTrue(root.is_dir(), f"missing packaged Skill source: {skill}")
            expected.update(
                path for path in root.rglob("*") if path.is_file() and not path.is_symlink()
            )
        self.assertTrue(expected.issubset(declared), sorted(expected - declared))


if __name__ == "__main__":
    unittest.main()
