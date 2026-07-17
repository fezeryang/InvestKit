"""Published research-bundle contract and delivery parity tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import tomllib
from typing import Any
from unittest import mock
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_RELATIVE_PATH = Path("schemas/research-bundle-v1.schema.json")
TEMPLATE_RELATIVE_PATH = Path("schemas/research-bundle-v1.template.json")
OPERATION_NAMES = {
    "identify_security",
    "get_security_profile",
    "get_financial_statements",
    "get_price_history",
    "get_valuation_inputs",
    "get_source_metadata",
    "get_peer_comparables",
    "get_earnings_history",
    "get_catalyst_events",
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "bundle_version",
    "created_at",
    "retrieved_at",
    "as_of_date",
    "currency",
    "market",
    "status",
    "warnings",
    "security",
    "sources",
    "operations",
}


def _strict_json(path: Path) -> dict[str, Any]:
    def reject_constant(_value: str) -> None:
        raise ValueError("non-standard numeric constant")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key in {path.name}")
            result[key] = value
        return result

    value = json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=reject_constant,
        object_pairs_hook=unique_object,
    )
    if not isinstance(value, dict):
        raise AssertionError(f"expected a JSON object: {path}")
    return value


class PublishedBundleContractTests(unittest.TestCase):
    maxDiff = None

    def test_schema_publishes_the_closed_draft_2020_12_contract(self) -> None:
        schema = _strict_json(REPOSITORY_ROOT / SCHEMA_RELATIVE_PATH)

        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(
            schema["$id"],
            "urn:investkit:schema:research-bundle:v1",
        )
        self.assertEqual(schema["type"], "object")
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), TOP_LEVEL_FIELDS)
        self.assertEqual(set(schema["properties"]), TOP_LEVEL_FIELDS)
        self.assertEqual(schema["properties"]["schema_version"]["const"], "1.0")
        self.assertEqual(schema["properties"]["status"]["const"], "imported")

        operations = schema["properties"]["operations"]
        self.assertEqual(operations["type"], "object")
        self.assertIs(operations["additionalProperties"], False)
        self.assertEqual(set(operations["required"]), OPERATION_NAMES)
        self.assertEqual(set(operations["properties"]), OPERATION_NAMES)
        operation_data_definitions = {
            "identify_security": "identityData",
            "get_security_profile": "profileData",
            "get_financial_statements": "financialData",
            "get_price_history": "priceData",
            "get_valuation_inputs": "valuationData",
            "get_source_metadata": "sourceMetadataData",
            "get_peer_comparables": "peerData",
            "get_earnings_history": "earningsData",
            "get_catalyst_events": "catalystData",
        }
        for operation_name, operation in operations["properties"].items():
            with self.subTest(operation=operation_name):
                self.assertEqual(
                    operation["allOf"][0], {"$ref": "#/$defs/operation"}
                )
                self.assertEqual(
                    operation["allOf"][1]["properties"]["data"],
                    {
                        "$ref": (
                            "#/$defs/"
                            + operation_data_definitions[operation_name]
                        )
                    },
                )

        operation_definition = schema["$defs"]["operation"]
        self.assertIs(operation_definition["additionalProperties"], False)
        self.assertEqual(
            set(operation_definition["required"]),
            {"data", "source_ids", "warnings"},
        )
        source_ids = operation_definition["properties"]["source_ids"]
        self.assertEqual(source_ids["type"], "array")
        self.assertNotIn("minItems", source_ids)
        self.assertEqual(source_ids["items"], {"$ref": "#/$defs/canonicalId"})
        self.assertEqual(
            schema["$defs"]["source"]["properties"]["source_id"],
            {"$ref": "#/$defs/canonicalId"},
        )
        self.assertEqual(schema["$defs"]["canonicalId"]["pattern"], r"^\S(?:.*\S)?$")
        empty_source_rule = operation_definition["allOf"][0]
        self.assertEqual(
            empty_source_rule["if"]["properties"]["source_ids"],
            {"maxItems": 0},
        )
        self.assertEqual(
            empty_source_rule["then"]["properties"]["data"],
            {"$ref": "#/$defs/sourceFreeData"},
        )
        source_free = schema["$defs"]["sourceFreeData"]
        self.assertEqual(source_free["type"], "object")
        self.assertEqual(
            source_free["additionalProperties"],
            {"$ref": "#/$defs/explicitGapValue"},
        )

    def test_template_is_runtime_usable_and_models_explicit_missing_operations(
        self,
    ) -> None:
        template_path = REPOSITORY_ROOT / TEMPLATE_RELATIVE_PATH
        template = _strict_json(template_path)
        from investkit.providers.file import load_research_bundle

        validated = load_research_bundle(REPOSITORY_ROOT, template_path)
        self.assertEqual(validated.value, template)
        self.assertEqual(template["schema_version"], "1.0")
        self.assertEqual(template["status"], "imported")
        self.assertEqual(set(template["operations"]), OPERATION_NAMES)

        missing_operations = [
            operation
            for operation in template["operations"].values()
            if operation["source_ids"] == []
        ]
        self.assertTrue(missing_operations)
        for operation in missing_operations:
            with self.subTest(operation=operation):
                self.assertTrue(operation["warnings"])
                serialized_data = json.dumps(operation["data"], allow_nan=False)
                self.assertRegex(serialized_data, r"null|\[\]")

    def test_runtime_rejects_non_standard_nan_and_infinity_like_the_schema(self) -> None:
        template = _strict_json(REPOSITORY_ROOT / TEMPLATE_RELATIVE_PATH)
        from investkit.providers.file import BundleValidationError, FileProvider

        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant), tempfile.TemporaryDirectory(
                prefix="investkit-schema-numbers-"
            ) as temporary:
                project_root = Path(temporary)
                value = deepcopy(template)
                value["operations"]["get_price_history"]["data"][
                    "latest_price"
                ] = "NON_STANDARD_NUMBER"
                encoded = json.dumps(value, indent=2).replace(
                    '"NON_STANDARD_NUMBER"', constant, 1
                )
                path = project_root / "bundle.json"
                path.write_text(encoded, encoding="utf-8")
                with self.assertRaisesRegex(BundleValidationError, "valid JSON"):
                    FileProvider(project_root, path)


class BundleAssetDeliveryTests(unittest.TestCase):
    def test_checkout_asset_inventory_requires_schema_and_template(self) -> None:
        from investkit.assets import (
            BUNDLE_SCHEMA_PATH,
            BUNDLE_TEMPLATE_PATH,
            complete_source_root,
            source_directories,
            source_file,
        )
        from investkit.errors import AssetValidationError

        self.assertEqual(BUNDLE_SCHEMA_PATH, SCHEMA_RELATIVE_PATH)
        self.assertEqual(BUNDLE_TEMPLATE_PATH, TEMPLATE_RELATIVE_PATH)
        root = complete_source_root(REPOSITORY_ROOT)
        self.assertEqual(
            source_file(root, BUNDLE_SCHEMA_PATH).read_bytes(),
            (REPOSITORY_ROOT / SCHEMA_RELATIVE_PATH).read_bytes(),
        )
        self.assertEqual(
            source_file(root, BUNDLE_TEMPLATE_PATH).read_bytes(),
            (REPOSITORY_ROOT / TEMPLATE_RELATIVE_PATH).read_bytes(),
        )
        self.assertEqual(source_directories(root)["schemas"], "schemas")

        original_source_file = source_file

        def omit_schema(source_root: Path, relative_path: str | Path) -> Path:
            if Path(relative_path) == BUNDLE_SCHEMA_PATH:
                raise AssetValidationError("schema deliberately omitted")
            return original_source_file(source_root, relative_path)

        with mock.patch("investkit.assets.source_file", side_effect=omit_schema):
            with self.assertRaisesRegex(AssetValidationError, "incomplete"):
                complete_source_root(REPOSITORY_ROOT)

    def test_wheel_data_mapping_carries_bundle_and_runtime_catalog_assets(self) -> None:
        configuration = tomllib.loads(
            (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        data_files = configuration["tool"]["setuptools"]["data-files"]
        self.assertEqual(
            data_files["share/investkit/schemas"],
            [
                SCHEMA_RELATIVE_PATH.as_posix(),
                TEMPLATE_RELATIVE_PATH.as_posix(),
                "schemas/runtime-asset-catalog-v1.json",
            ],
        )


if __name__ == "__main__":
    unittest.main()
