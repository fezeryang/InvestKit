"""Deterministic Markdown view over persisted Investment Core artifacts."""

from __future__ import annotations

import html
import json
import re
from typing import Any, Mapping, Sequence


CAPABILITY_ORDER = (
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
RESTRICTED_LANGUAGE_RE = re.compile(
    r"(?im)(?:^|[.!?;:]\s+)(?:please\s+)?(?:buy|sell|hold)\b|"
    r"\b(?:recommend(?:ation|ed|s)?|should|must|rating(?:\s+is)?|"
    r"we\s+(?:would\s+)?recommend)\s*(?::|that|to)?\s*"
    r"(?:buy(?:ing)?|sell(?:ing)?|hold(?:ing)?)\b|"
    r"\b(?:buy|sell|hold)\s+(?:now|the\s+(?:stock|security)|shares?|"
    r"rating|recommendation)\b|guaranteed (?:return|profit)|"
    r"risk-free return|price will|position size|stop loss|"
    r"(?:建议|推荐|应当|应该|必须|务必|立即|马上|现在|可考虑|"
    r"评级(?:为|是)?)"
    r"[^。！？\n]{0,12}(?:买入|卖出|持有|建仓|加仓|减仓|增持|减持)|"
    r"(?:买入|卖出|持有|建仓|加仓|减仓|增持|减持)"
    r"[^。！？\n]{0,8}(?:该?(?:股票|证券|股份)|仓位|建议|推荐|评级)|"
    r"(?:仓位|止损(?:位|价|线)?|"
    r"(?:保证|确保|承诺)[^。！？\n]{0,8}(?:收益|回报|盈利))"
)
UNSAFE_URI_RE = re.compile(
    r"(?i)\b(?:javascript|vbscript)\s*:|"
    r"\bdata\s*:\s*(?:text|image|audio|video|application)/"
)
MARKDOWN_CONTROL_RE = re.compile(r"([\\`*_{}\[\]()#!|])")


def render_report(
    *,
    task_id: str,
    question: str,
    identity: Mapping[str, Any],
    capability_results: Mapping[str, Mapping[str, Any]],
    sources: Mapping[str, Any],
    installed_skills: Sequence[Mapping[str, Any]],
    loaded_specs: Sequence[Mapping[str, Any]],
    generation_time: str,
    input_mode: str = "demo",
    input_provenance: Mapping[str, Any] | None = None,
) -> str:
    """Render a report without inventing analysis outside persisted envelopes."""

    results = {
        name: _mapping(capability_results.get(name)) for name in CAPABILITY_ORDER
    }
    if input_mode not in {"demo", "imported"}:
        raise ValueError("report input mode is invalid")
    provenance = input_provenance or {}
    official_live = (
        input_mode == "imported"
        and provenance.get("acquisition_mode") == "official_live"
    )
    lines = [
        (
            "# Official-Source Company Research Report"
            if official_live
            else "# Imported Company Research Report"
        )
        if input_mode == "imported"
        else "# Offline Company Research Report",
        "",
    ]

    _section(
        lines,
        "Research Subject",
        [
            f"- Task: {_code(task_id)}",
            f"- Question: {_safe_text(question)}",
            f"- Company: {_safe_text(identity.get('legal_name', 'unknown'))}",
            f"- Security ID: {_code(identity.get('security_id', 'unknown'))}",
            f"- Ticker: {_code(identity.get('ticker', 'unknown'))}",
            f"- Market: {_safe_text(identity.get('market', 'unknown'))}",
        ],
    )
    if input_mode == "demo":
        _section(
            lines,
            "Demo Data Declaration",
            [
                "All issuer, security, financial, event, price, and valuation material "
                "in this report is wholly fictional demo data. It is not live or "
                "real-time evidence and does not describe an actual issuer."
            ],
        )
    elif official_live:
        _section(
            lines,
            "Official Live Data Declaration",
            [
                "The research inputs were fetched by an approved InvestKit Provider from allowlisted official public sources. Source authority does not guarantee completeness or analytical sufficiency.",
                f"- Persisted bundle version: {_safe_text(provenance.get('bundle_version', 'unknown'))}",
                f"- Provider origin: {_code(provenance.get('origin', 'unknown'))}",
                f"- Persisted snapshot SHA-256: {_code(provenance.get('sha256', 'unknown'))}",
            ],
        )
    else:
        _section(
            lines,
            "Imported Data Declaration",
            [
                "The research inputs are user-supplied imported data. InvestKit did "
                "not independently fetch, verify, or guarantee their accuracy or "
                "completeness.",
                f"- Persisted bundle version: {_safe_text(provenance.get('bundle_version', 'unknown'))}",
                f"- Original project-local origin: {_code(provenance.get('origin', 'unknown'))}",
                f"- Persisted snapshot SHA-256: {_code(provenance.get('sha256', 'unknown'))}",
            ],
        )
    _section(
        lines,
        "Data Date",
        [f"- Provider as-of date: {_safe_text(identity.get('as_of_date', 'unknown'))}"],
    )
    _section(lines, "Executive Summary", _executive_summary(results))
    _section(
        lines,
        "Company Overview",
        _capability_bullets(
            results["company-deep-research"],
            fields=("facts", "findings", "unknowns"),
        ),
    )
    _section(
        lines,
        "Business Model Analysis",
        _capability_bullets(
            results["business-model-analysis"],
            fields=("facts", "findings", "risks", "unknowns"),
        ),
    )
    _section(
        lines,
        "Financial Analysis",
        _capability_bullets(
            results["financial-statement-analysis"],
            fields=("facts", "findings", "estimates", "risks", "unknowns"),
        ),
    )
    _section(
        lines,
        "Earnings Quality",
        _capability_bullets(
            results["earnings-quality-analysis"],
            fields=("facts", "findings", "estimates", "risks", "unknowns"),
        ),
    )
    _section(
        lines,
        "Cash Flow and Balance Sheet Analysis",
        _capability_bullets(
            results["financial-statement-analysis"],
            fields=("facts", "estimates", "unknowns"),
        ),
    )
    _section(
        lines,
        "Valuation Analysis",
        _capability_bullets(
            results["valuation-analysis"],
            fields=("facts", "assumptions", "estimates", "findings", "risks", "unknowns"),
        ),
    )
    _section(
        lines,
        "Comparable Companies Analysis",
        _capability_bullets(
            results["comps-analysis"],
            fields=("facts", "estimates", "findings", "risks", "unknowns"),
        ),
    )
    _section(
        lines,
        "Earnings Analysis",
        _capability_bullets(
            results["earnings-analysis"],
            fields=("facts", "assumptions", "estimates", "findings", "risks", "unknowns"),
        ),
    )
    _section(lines, "Investment Thesis", _thesis_bullets(results))
    _section(lines, "Bull / Base Case", _scenario_bullets(results))
    _section(
        lines,
        "Independent Bear Case",
        _bear_case_bullets(results["bear-case-analysis"]),
    )
    _section(
        lines,
        "Catalyst Analysis",
        _capability_bullets(
            results["catalyst-analysis"],
            fields=("facts", "findings", "risks", "unknowns"),
        ),
    )
    _section(lines, "Positive Evidence", _confirming_evidence_bullets(results))
    _section(lines, "Negative Evidence", _negative_evidence_bullets(results))
    _section(lines, "Primary Risks", _aggregate_bullets(results, "risks"))
    _section(lines, "Assumptions", _aggregate_bullets(results, "assumptions"))
    _section(lines, "Estimates", _aggregate_bullets(results, "estimates"))
    _section(lines, "Unknowns / To Verify", _aggregate_bullets(results, "unknowns"))
    _section(lines, "Data Limitations", _warning_bullets(results))
    _section(lines, "Skipped Capabilities", _skipped_bullets(results))
    _section(lines, "Source Conflicts", _source_conflict_bullets(results))
    _section(lines, "Data Sources", _source_bullets(sources))
    _section(lines, "Used Skills", _skill_bullets(installed_skills))
    _section(lines, "Loaded Specs", _spec_bullets(loaded_specs))
    _section(
        lines,
        "Generation Time",
        [
            f"- Generated at {_safe_text(generation_time)} from validated local "
            "capability artifacts."
        ],
    )
    if official_live:
        boundary = (
            "This research uses an immutable snapshot acquired from allowlisted official public sources. "
            "It may still be incomplete, stale, or insufficient for a decision."
        )
    elif input_mode == "imported":
        boundary = (
            "This is offline research over user-supplied imported evidence. The inputs "
            "were not independently guaranteed by InvestKit and may be stale, incomplete, "
            "or incorrect."
        )
    else:
        boundary = "This is an offline research-harness demonstration for a fictional issuer."
    _section(
        lines,
        "Research Boundary",
        [
            boundary
            + " It is not individualized financial advice and does not authorize "
            "brokerage access, order placement, transactions, funds transfer, or "
            "any real-money action. Outcomes and returns are not promised."
        ],
    )

    report = "\n".join(lines).rstrip() + "\n"
    if RESTRICTED_LANGUAGE_RE.search(report):
        raise ValueError("report contains language outside the research-only boundary")
    return report


def _section(lines: list[str], title: str, content: Sequence[str]) -> None:
    lines.extend((f"## {title}", "", *(content or ["- No structured record was produced."]), ""))


def _executive_summary(results: Mapping[str, Mapping[str, Any]]) -> list[str]:
    bullets: list[str] = []
    thesis_method = _mapping(results["investment-thesis"].get("method"))
    statement = thesis_method.get("thesis_statement")
    if statement:
        bullets.append(f"- Persisted thesis: {_safe_text(statement)}")
    source_method = _mapping(results["source-verification"].get("method"))
    gate_status = source_method.get("gate_status")
    if gate_status:
        bullets.append(f"- Persisted source-gate status: {_safe_text(gate_status)}")
    report_method = _mapping(results["investment-report"].get("method"))
    completeness = report_method.get("completeness")
    if completeness:
        bullets.append(f"- Persisted report completeness: {_safe_text(completeness)}")
    bullets.extend(
        _record_bullets(
            results["investment-thesis"].get("findings"),
            capability="investment-thesis",
            field="findings",
        )
    )
    return bullets or ["- No completed thesis summary is present in the artifacts."]


def _capability_bullets(
    result: Mapping[str, Any],
    *,
    fields: Sequence[str],
) -> list[str]:
    capability = _safe_text(result.get("capability", "unknown-capability"))
    status = _safe_text(result.get("status", "unknown"))
    bullets = [f"- Capability {_code(capability)} status: {status}."]
    if result.get("status") == "skipped":
        bullets.append(
            f"- Capability {_code(capability)} skipped: "
            f"{_safe_text(result.get('skip_reason', 'reason unavailable'))}"
        )
        missing = _string_list(result.get("missing_inputs"))
        if missing:
            bullets.append("- Missing inputs: " + ", ".join(_code(value) for value in missing))
    for field in fields:
        bullets.extend(
            _record_bullets(result.get(field), capability=capability, field=field)
        )
    return bullets


def _warning_bullets(results: Mapping[str, Mapping[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for capability in CAPABILITY_ORDER:
        for warning in _string_list(results[capability].get("warnings")):
            if warning not in warnings:
                warnings.append(warning)
    return [f"- {_safe_text(warning)}" for warning in warnings] or [
        "- No provider or capability limitation was recorded."
    ]


def _thesis_bullets(results: Mapping[str, Mapping[str, Any]]) -> list[str]:
    result = results["investment-thesis"]
    bullets = _capability_bullets(
        result,
        fields=("facts", "findings", "risks", "assumptions", "unknowns"),
    )
    method = _mapping(result.get("method"))
    for label, key in (
        ("Thesis statement", "thesis_statement"),
        ("Time horizon", "time_horizon"),
        ("Evidence sufficiency", "evidence_sufficiency"),
    ):
        if method.get(key) is not None:
            bullets.append(f"- {label}: {_safe_text(method[key])}")
    return bullets


def _scenario_bullets(results: Mapping[str, Mapping[str, Any]]) -> list[str]:
    method = _mapping(results["investment-thesis"].get("method"))
    bullets = []
    for label, key in (("Bull case", "bull_case"), ("Base case", "base_case")):
        if method.get(key) is not None:
            bullets.append(f"- {label}: {_safe_text(method[key])}")
    return bullets or ["- No structured bull/base scenario text was produced."]


def _bear_case_bullets(result: Mapping[str, Any]) -> list[str]:
    bullets = _capability_bullets(
        result,
        fields=("facts", "findings", "risks", "assumptions", "unknowns"),
    )
    method = _mapping(result.get("method"))
    if method.get("counter_thesis") is not None:
        bullets.append(f"- Counter-thesis: {_safe_text(method['counter_thesis'])}")
    checksum = method.get("thesis_snapshot_checksum")
    if checksum is not None:
        bullets.append(f"- Frozen thesis checksum: {_code(checksum)}")
    return bullets


def _confirming_evidence_bullets(
    results: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    method = _mapping(results["investment-thesis"].get("method"))
    evidence_ids: list[str] = []
    for pillar in _mapping_list(method.get("pillars")):
        for identifier in _string_list(pillar.get("confirming_evidence")):
            if identifier not in evidence_ids:
                evidence_ids.append(identifier)
    return [f"- Confirming evidence ID: {_code(identifier)}" for identifier in evidence_ids] or [
        "- No separate confirming-evidence ID was recorded."
    ]


def _negative_evidence_bullets(
    results: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    identifiers: list[str] = []
    thesis_method = _mapping(results["investment-thesis"].get("method"))
    for pillar in _mapping_list(thesis_method.get("pillars")):
        for identifier in _string_list(pillar.get("disconfirming_evidence")):
            if identifier not in identifiers:
                identifiers.append(identifier)
    bear_method = _mapping(results["bear-case-analysis"].get("method"))
    for identifier in _string_list(bear_method.get("counterevidence")):
        if identifier not in identifiers:
            identifiers.append(identifier)
    bullets = [f"- Disconfirming evidence ID: {_code(value)}" for value in identifiers]
    bullets.extend(
        _record_bullets(
            results["bear-case-analysis"].get("findings"),
            capability="bear-case-analysis",
            field="findings",
        )
    )
    return bullets or ["- No separate disconfirming-evidence ID was recorded."]


def _aggregate_bullets(
    results: Mapping[str, Mapping[str, Any]],
    field: str,
) -> list[str]:
    bullets: list[str] = []
    for capability in CAPABILITY_ORDER:
        if capability == "investment-report":
            continue
        bullets.extend(
            _record_bullets(
                results[capability].get(field),
                capability=capability,
                field=field,
            )
        )
    return bullets or [f"- No structured {field} record was produced."]


def _skipped_bullets(results: Mapping[str, Mapping[str, Any]]) -> list[str]:
    bullets: list[str] = []
    for capability in CAPABILITY_ORDER:
        result = results[capability]
        if result.get("status") != "skipped":
            continue
        reason = _safe_text(result.get("skip_reason", "reason unavailable"))
        missing = _string_list(result.get("missing_inputs"))
        suffix = (
            "; missing inputs: " + ", ".join(_code(value) for value in missing)
            if missing
            else ""
        )
        bullets.append(f"- Capability {_code(capability)} skipped: {reason}{suffix}")
    return bullets or ["- No capability was skipped in this run."]


def _source_conflict_bullets(
    results: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    method = _mapping(results["source-verification"].get("method"))
    conflicts = _string_list(method.get("conflicts"))
    return [f"- {_safe_text(value)}" for value in conflicts] or [
        "- No source conflict was recorded by the verification artifact."
    ]


def _record_bullets(
    value: Any,
    *,
    capability: str,
    field: str,
) -> list[str]:
    bullets: list[str] = []
    for record in _mapping_list(value):
        identifier = _safe_text(record.get("id", "unidentified-record"))
        prefix = f"- [{_code(identifier)}; {_code(capability)}; {field}]"
        if field == "assumptions":
            text = _safe_text(record.get("statement", "statement unavailable"))
            rationale = _safe_text(record.get("rationale", "rationale unavailable"))
            materiality = _safe_text(record.get("materiality", "unknown"))
            bullets.append(
                f"{prefix} {text} Rationale: {rationale} Materiality: {materiality}."
            )
            continue
        if field == "estimates":
            label = _safe_text(record.get("label", "estimate"))
            method = _safe_text(record.get("method", "method unavailable"))
            inputs = record.get("input_ids", record.get("inputs", []))
            bullets.append(
                f"{prefix} {label}: {_json_value(record.get('value'))}. "
                f"Method: {method}. Material inputs: {_json_value(inputs)}."
            )
            continue
        if field == "unknowns":
            gap = _safe_text(record.get("gap", record.get("question", "gap unavailable")))
            impact = _safe_text(record.get("impact", "impact unavailable"))
            bullets.append(f"{prefix} {gap} Decision impact: {impact}")
            continue
        text = _safe_text(
            record.get("statement", record.get("description", "statement unavailable"))
        )
        source_ids = _string_list(record.get("source_ids"))
        source_suffix = (
            " Sources: " + ", ".join(_code(source_id) for source_id in source_ids) + "."
            if source_ids
            else ""
        )
        bullets.append(f"{prefix} {text}{source_suffix}")
    return bullets


def _source_bullets(sources: Mapping[str, Any]) -> list[str]:
    bullets: list[str] = []
    for record in _mapping_list(sources.get("sources")):
        source_id = _code(record.get("source_id", "unknown"))
        title = _safe_text(record.get("title", record.get("source", "Unnamed source")))
        as_of_date = _safe_text(record.get("as_of_date", "unknown"))
        version = _safe_text(
            record.get("fixture_version", record.get("retrieved_at", "unknown"))
        )
        digest = _code(record.get("sha256", "unknown"))
        quality = _safe_text(record.get("quality", "unknown"))
        freshness = _safe_text(record.get("freshness", "unknown"))
        locator = _safe_text(record.get("locator", "not supplied"))
        bullets.append(
            f"- {title} ({source_id}); as of {as_of_date}; version/retrieval "
            f"{version}; quality {quality}; freshness {freshness}; locator {locator}; "
            f"SHA-256 {digest}."
        )
        for warning in _string_list(record.get("warnings")):
            bullets.append(f"  - Source warning: {_safe_text(warning)}")
    return bullets or ["- No source record was produced."]


def _skill_bullets(records: Sequence[Mapping[str, Any]]) -> list[str]:
    return [
        f"- {_code(record.get('name', 'unknown'))} version "
        f"{_safe_text(record.get('version', 'unknown'))} "
        f"(SHA-256 {_code(record.get('sha256', 'unknown'))})"
        for record in records
    ] or ["- No Skill snapshot was produced."]


def _spec_bullets(records: Sequence[Mapping[str, Any]]) -> list[str]:
    return [
        f"- {_code(record.get('name', 'unknown'))} version "
        f"{_safe_text(record.get('version', 'unknown'))} "
        f"(SHA-256 {_code(record.get('sha256', 'unknown'))})"
        for record in records
    ] or ["- No spec snapshot was produced."]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [record for record in value if isinstance(record, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [_safe_text(item) for item in value if str(item).strip()]


def _safe_text(value: Any) -> str:
    text = " ".join(str(value).split()).strip() or "unknown"
    if RESTRICTED_LANGUAGE_RE.search(text) or UNSAFE_URI_RE.search(text):
        return "[content omitted by the research-only output boundary]"
    escaped = html.escape(text, quote=False)
    return MARKDOWN_CONTROL_RE.sub(r"\\\1", escaped)


def _code(value: Any) -> str:
    safe_value = _safe_text(value).replace("`", "'")
    return f"`{safe_value}`"


def _json_value(value: Any) -> str:
    try:
        rendered = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        rendered = str(value)
    return _safe_text(rendered)
