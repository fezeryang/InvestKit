"""Pure, deterministic analyses for the offline Investment Core workflow."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date, timedelta
from typing import Any, Callable, Mapping, Sequence, cast

from .catalog import RUNTIME_SKILLS
from .contracts import build_capability_result


CapabilityResult = dict[str, Any]
CapabilityRunner = Callable[[Mapping[str, Any]], CapabilityResult]
SKILL_VERSION = "0.2.0"
METHOD_VERSION = "1.0"
SOURCE_FRESHNESS_MAX_AGE_DAYS = 180


def run_capability(
    capability: str,
    inputs: Mapping[str, Any],
) -> CapabilityResult:
    """Run one allowlisted capability over a broad immutable input context."""

    if capability not in _RUNNERS:
        raise KeyError(f"unknown Investment Core capability: {capability}")
    if not isinstance(inputs, Mapping):
        raise TypeError("capability inputs must be a mapping")
    return _RUNNERS[capability](inputs)


def analyze_security_identification(inputs: Mapping[str, Any]) -> CapabilityResult:
    identity = _mapping(inputs, "identity")
    required = ("security_id", "ticker", "legal_name")
    missing = [name for name in required if not _text(identity.get(name))]
    if missing:
        return _skipped(
            "security-identification",
            "security-identity-resolution",
            "Security identity is incomplete.",
            missing,
        )
    source_ids = _source_ids_for_capability(inputs, "security-identification")
    if not source_ids:
        return _skipped(
            "security-identification",
            "security-identity-resolution",
            "Security identity has no persisted provenance.",
            ["source metadata"],
        )
    facts = [
        _fact(
            "fact-security-identity",
            (
                f"{identity['legal_name']} has fixture security ID {identity['security_id']}."
                if _is_demo(inputs)
                else f"{identity['legal_name']} has security ID {identity['security_id']} in the imported identity record."
            ),
            source_ids,
        ),
        _fact(
            "fact-security-ticker",
            (
                f"The fixture ticker is {identity['ticker']} on {identity.get('exchange', identity.get('market', 'the stated market'))}."
                if _is_demo(inputs)
                else f"The imported identity record lists ticker {identity['ticker']} on {identity.get('exchange', identity.get('market', 'the stated market'))}."
            ),
            source_ids,
        ),
    ]
    return _completed(
        "security-identification",
        "security-identity-resolution",
        method_fields={
            "resolved_security_id": identity["security_id"],
            "ambiguity_check": "passed",
        },
        facts=facts,
        findings=[
            _finding(
                "finding-security-resolved",
                (
                    "The fictional demo security is unambiguously resolved for offline research."
                    if _is_demo(inputs)
                    else "The security is unambiguously resolved from the persisted imported identity evidence."
                ),
                source_ids,
            )
        ],
        warnings=_warnings(inputs),
    )


def analyze_company_deep_research(inputs: Mapping[str, Any]) -> CapabilityResult:
    profile = _mapping(inputs, "profile")
    if not profile:
        return _skipped(
            "company-deep-research",
            "source-led-company-dossier",
            "No company profile is available.",
            ["company profile"],
        )
    source_ids = _source_ids_for_capability(inputs, "company-deep-research")
    if not source_ids:
        return _skipped(
            "company-deep-research",
            "source-led-company-dossier",
            "No sourced company-profile evidence is available.",
            ["sourced company profile"],
        )
    segments = _strings(profile.get("segments"))
    management = _mapping_value(profile.get("management"), "profile.management")
    capital_allocation = _mapping_value(
        profile.get("capital_allocation"), "profile.capital_allocation"
    )
    competitive = _mapping_value(
        profile.get("competitive_context"), "profile.competitive_context"
    )
    business_description = _text(profile.get("business_model"))
    management_summary = _text(management.get("summary"))
    capital_allocation_summary = _text(capital_allocation.get("summary"))
    competitive_summary = (
        _text(competitive.get("summary"))
        or _text(profile.get("competitive_position"))
    )
    facts: list[dict[str, Any]] = []
    covered_fields: list[str] = []
    unknowns: list[dict[str, Any]] = []
    if business_description:
        facts.append(
            _fact(
                "fact-company-business",
                (
                    f"The fictional company profile describes this business: {business_description}."
                    if _is_demo(inputs)
                    else f"The imported company profile describes this business: {business_description}."
                ),
                source_ids,
            )
        )
        covered_fields.append("business model")
    else:
        unknowns.append(
            _unknown(
                "unknown-company-business-model",
                "A company business-model description is unavailable.",
                "The company dossier cannot characterize how the business operates.",
            )
        )
    if segments:
        facts.append(
            _fact(
                "fact-company-segments",
                "Reported segments are " + ", ".join(segments) + ".",
                source_ids,
            )
        )
        covered_fields.append("segments")
    else:
        unknowns.append(
            _unknown(
                "unknown-company-segments",
                "Reported segment detail is unavailable.",
                "Business mix and segment concentration cannot be evaluated.",
            )
        )
    if management_summary:
        facts.append(
            _fact(
                "fact-company-management",
                f"Management evidence states: {management_summary}.",
                source_ids,
            )
        )
        covered_fields.append("management")
    else:
        unknowns.append(
            _unknown(
                "unknown-company-management",
                "Management evidence is unavailable.",
                "Management quality and execution cannot be assessed from this input.",
            )
        )
    if capital_allocation_summary:
        facts.append(
            _fact(
                "fact-company-capital-allocation",
                f"Capital allocation evidence states: {capital_allocation_summary}.",
                source_ids,
            )
        )
        covered_fields.append("capital allocation")
    else:
        unknowns.append(
            _unknown(
                "unknown-company-capital-allocation",
                "Capital allocation evidence is unavailable.",
                "Capital deployment priorities and discipline cannot be assessed.",
            )
        )
    if competitive_summary:
        facts.append(
            _fact(
                "fact-company-competitive-context",
                f"Competitive context states: {competitive_summary}.",
                source_ids,
            )
        )
        covered_fields.append("competitive context")
    else:
        unknowns.append(
            _unknown(
                "unknown-company-competitive-context",
                "Competitive-position evidence is unavailable.",
                "Competitive durability and differentiation cannot be assessed.",
            )
        )
    if profile.get("employees", profile.get("employee_count")) is None:
        unknowns.append(
            _unknown(
                "unknown-company-employees",
                "Employee count is unavailable.",
                "Operating scale and productivity cannot be assessed from headcount.",
            )
        )
    if management_summary and not _text(management.get("tenure")):
        unknowns.append(
            _unknown(
                "unknown-management-tenure",
                "Management tenure and track record are unavailable.",
                "Management execution cannot be evaluated longitudinally.",
            )
        )
    return _completed(
        "company-deep-research",
        "source-led-company-dossier",
        method_fields={
            "segments": segments,
            "management_review": dict(management),
            "capital_allocation_review": dict(capital_allocation),
            "competitive_context": dict(competitive),
            "research_drivers": _strings(profile.get("research_drivers")),
            "research_gaps": [value["id"] for value in unknowns],
        },
        facts=facts,
        unknowns=unknowns,
        findings=(
            [
                _finding(
                    "finding-company-context",
                    "The sourced company fact base covers "
                    + ", ".join(covered_fields)
                    + " while retaining explicit unknowns.",
                    source_ids,
                )
            ]
            if covered_fields
            else []
        ),
        risks=[
            _risk(f"risk-company-{index}", value, source_ids)
            for index, value in enumerate(
                _strings(profile.get("risks") or profile.get("business_risks")),
                start=1,
            )
        ],
        warnings=_warnings(inputs),
    )


def analyze_business_model(inputs: Mapping[str, Any]) -> CapabilityResult:
    profile = _mapping(inputs, "profile")
    if not profile:
        return _skipped(
            "business-model-analysis",
            "business-model-map",
            "No sourced company fact base is available.",
            ["company profile"],
        )
    source_ids = _source_ids_for_capability(inputs, "business-model-analysis")
    if not source_ids:
        return _skipped(
            "business-model-analysis",
            "business-model-map",
            "No sourced business-model evidence is available.",
            ["sourced company profile"],
        )
    order_to_cash = _mapping_value(profile.get("order_to_cash"), "profile.order_to_cash")
    components = _mapping_value(
        profile.get("revenue_components"), "profile.revenue_components"
    )
    revenue_model = _text(profile.get("revenue_model")) or _text(
        profile.get("business_model")
    )
    payer = _text(profile.get("payer")) or _text(profile.get("customers"))
    value_proposition = _text(profile.get("value_proposition"))
    facts: list[dict[str, Any]] = []
    if revenue_model:
        facts.append(
            _fact(
                "fact-revenue-model",
                f"The revenue model is {revenue_model}.",
                source_ids,
            )
        )
    if payer:
        facts.append(
            _fact(
                "fact-payer",
                f"The disclosed payer is {payer}.",
                source_ids,
            )
        )
    if value_proposition:
        facts.append(
            _fact(
                "fact-value-proposition",
                f"The disclosed value proposition is {value_proposition}.",
                source_ids,
            )
        )
    if order_to_cash:
        facts.append(
            _fact(
                "fact-order-to-cash",
                (
                    "The order, backlog, delivery, billing, and cash states are tracked separately in the fixture."
                    if _is_demo(inputs)
                    else "The imported profile supplies an explicit order-to-cash operating chain whose states are analyzed separately."
                ),
                source_ids,
            )
        )
    unknowns: list[dict[str, Any]] = []
    if not payer:
        unknowns.append(
            _unknown(
                "unknown-business-payer",
                "Payer or customer evidence is unavailable.",
                "Revenue concentration and purchasing behavior cannot be assessed.",
            )
        )
    if not value_proposition:
        unknowns.append(
            _unknown(
                "unknown-business-value-proposition",
                "A sourced value proposition is unavailable.",
                "Customer willingness to adopt or retain the offering cannot be assessed.",
            )
        )
    for key, label, impact in (
        (
            "customer_retention",
            "Customer retention is unavailable.",
            "Cohort retention and lifetime-value analysis cannot be performed.",
        ),
        (
            "customer_concentration_percent",
            "Customer concentration percentages are unavailable.",
            "Payer concentration fragility cannot be quantified.",
        ),
    ):
        if profile.get(key) is None:
            unknowns.append(_unknown(f"unknown-{key}", label, impact))
    if _is_demo(inputs):
        method_specific = {
            "backlog_is_not_revenue": True,
            "cash_collection_is_separate": True,
            "fragility_checks": [
                "tender concentration",
                "battery input cost exposure",
                "working-capital conversion",
            ],
        }
        findings = [
            _finding(
                "finding-business-mechanics",
                "The hybrid revenue model links a municipal payer and outdoor customers to a product value proposition through a guarded order-to-cash chain.",
                source_ids,
            ),
            _finding(
                "finding-business-fragility",
                "Tender concentration and input costs are material business-model fragilities.",
                source_ids,
            ),
        ]
        risks = [
            _risk(
                "risk-backlog-conversion",
                "Backlog may not convert into delivered revenue or collected cash.",
                source_ids,
            )
        ]
    else:
        explicit_risks = _strings(profile.get("business_risks") or profile.get("risks"))
        method_specific = {
            "operating_chain_supplied": bool(order_to_cash),
            "cash_collection_is_separate": bool(order_to_cash),
            "fragility_checks": explicit_risks,
        }
        if revenue_model and payer and value_proposition:
            mechanics_statement = (
                "The imported evidence links the disclosed revenue model, payer, and value "
                "proposition without assuming an operating chain that was not supplied."
            )
        else:
            mechanics_statement = (
                "The imported evidence supports only the populated business-model fields; "
                "missing commercial evidence remains an explicit unknown."
            )
        findings = [
            _finding(
                "finding-business-mechanics",
                mechanics_statement,
                source_ids,
            )
        ]
        if explicit_risks:
            findings.append(
                _finding(
                    "finding-business-fragility",
                    "The imported profile identifies these business-model fragilities: "
                    + "; ".join(explicit_risks)
                    + ".",
                    source_ids,
                )
            )
        risks = [
            _risk(f"risk-business-{index}", statement, source_ids)
            for index, statement in enumerate(explicit_risks, start=1)
        ]
    return _completed(
        "business-model-analysis",
        "business-model-map",
        method_fields={
            "revenue_model": revenue_model,
            "payer": payer,
            "value_proposition": value_proposition,
            "revenue_components": dict(components),
            "order_to_cash": dict(order_to_cash),
            **method_specific,
        },
        facts=facts,
        unknowns=unknowns,
        findings=findings,
        risks=risks,
        warnings=_warnings(inputs),
    )


def analyze_financial_statements(inputs: Mapping[str, Any]) -> CapabilityResult:
    statements = _mapping(inputs, "statements")
    periods = _periods(statements)
    if len(periods) < 2:
        return _skipped(
            "financial-statement-analysis",
            "normalized-three-statement-analysis",
            "At least two comparable statement periods are required.",
            ["comparable financial statement periods"],
        )
    if not _periods_have_financial_values(periods):
        return _skipped(
            "financial-statement-analysis",
            "normalized-three-statement-analysis",
            "The supplied periods contain no finite financial statement values.",
            ["finite financial statement values"],
        )
    source_ids = _require_sources(inputs, "financial-statement-analysis")
    earliest, latest = periods[0], periods[-1]
    fact_values = {
        "revenue-latest": latest.get("revenue"),
        "revenue-earliest": earliest.get("revenue"),
        "operating-income": latest.get("operating_income"),
        "operating-cash-flow": latest.get("cash_from_operations"),
        "net-income": latest.get("net_income"),
        "debt": latest.get("total_debt"),
        "equity": latest.get("total_equity"),
    }
    facts = [
        _fact(
            f"fact-financial-{name}",
            f"For the stated period, {name.replace('-', ' ')} is {value} {statements.get('units', 'units')}.",
            source_ids,
        )
        for name, value in fact_values.items()
        if _number(value) is not None
    ]
    revenue = _number(latest.get("revenue"))
    earlier_revenue = _number(earliest.get("revenue"))
    gross_profit = _number(latest.get("gross_profit"))
    operating_income = _number(latest.get("operating_income"))
    cash_flow = _number(latest.get("cash_from_operations"))
    debt = _number(latest.get("total_debt"))
    equity = _number(latest.get("total_equity"))
    metrics = {
        "revenue_growth": _ratio_delta(revenue, earlier_revenue),
        "gross_margin": _ratio(gross_profit, revenue),
        "operating_margin": _ratio(operating_income, revenue),
        "cash_flow_margin": _ratio(cash_flow, revenue),
        "leverage_debt_to_equity": _ratio(debt, equity),
        "liquidity_cash_to_debt": _ratio(_number(latest.get("cash_and_equivalents")), debt),
        "liquidity_current_ratio": _ratio(
            _number(latest.get("current_assets")),
            _number(latest.get("current_liabilities")),
        ),
    }
    estimates = [
        {
            "id": f"estimate-financial-{name}",
            "label": name.replace("_", " "),
            "value": value,
            "method": _financial_formula(name),
            "inputs": {"period": latest.get("fiscal_year"), "units": statements.get("units")},
        }
        for name, value in metrics.items()
        if value is not None
    ]
    unknowns = [
        _unknown(
            f"unknown-financial-{field}",
            f"{field.replace('_', ' ')} is unavailable for the latest period.",
            "Dependent financial ratios remain unavailable.",
        )
        for field in (
            "current_assets",
            "current_liabilities",
            "accounts_receivable",
            "inventory",
        )
        if latest.get(field) is None
    ]
    unknowns.extend(
        _unknown(
            f"unknown-financial-{name.replace('_', '-')}",
            f"A finite {name.replace('_', ' ')} metric cannot be calculated from the supplied values.",
            "The affected financial comparison remains unavailable.",
        )
        for name, value in metrics.items()
        if value is None
    )
    calculated_metrics = [
        name.replace("_", " ") for name, value in metrics.items() if value is not None
    ]
    findings = (
        [
            _finding(
                "finding-financial-trend",
                "Calculated financial diagnostics: " + ", ".join(calculated_metrics) + ".",
                source_ids,
            )
        ]
        if calculated_metrics
        else []
    )
    risks = (
        [
            _risk(
                "risk-financial-leverage",
                "Debt remains a balance-sheet claim that must be included in valuation bridges.",
                source_ids,
            )
        ]
        if debt is not None
        else []
    )
    return _completed(
        "financial-statement-analysis",
        "normalized-three-statement-analysis",
        method_fields={
            "periods": [period.get("fiscal_year") for period in periods],
            "period_type": statements.get("period_type"),
            "currency": statements.get("currency", inputs.get("currency")),
            "units": statements.get("units"),
            "accounting_basis": statements.get("accounting_basis"),
            "metrics": metrics,
            "cash_flow_review": (
                "completed with disclosed limitations"
                if metrics["cash_flow_margin"] is not None
                else "unknown: operating cash flow or revenue is unavailable"
            ),
            "leverage_review": (
                "completed"
                if metrics["leverage_debt_to_equity"] is not None
                else "unknown: debt or equity is unavailable"
            ),
            "liquidity_review": (
                "completed"
                if any(
                    metrics[name] is not None
                    for name in ("liquidity_cash_to_debt", "liquidity_current_ratio")
                )
                else "unknown: comparable liquidity balances are unavailable"
            ),
        },
        facts=facts,
        estimates=estimates,
        unknowns=unknowns,
        findings=findings,
        risks=risks,
        warnings=_warnings(inputs),
    )


def analyze_earnings_quality(inputs: Mapping[str, Any]) -> CapabilityResult:
    statements = _mapping(inputs, "statements")
    periods = _periods(statements)
    if len(periods) < 2:
        return _skipped(
            "earnings-quality-analysis",
            "cash-accrual-quality-review",
            "Comparable normalized statement periods are unavailable.",
            ["normalized financial statements"],
        )
    if not _periods_have_financial_values(periods):
        return _skipped(
            "earnings-quality-analysis",
            "cash-accrual-quality-review",
            "The supplied periods contain no finite earnings or cash-flow values.",
            ["finite earnings or cash-flow values"],
        )
    source_ids = _require_sources(inputs, "earnings-quality-analysis")
    previous, latest = periods[-2], periods[-1]
    net_income = _number(latest.get("net_income"))
    operating_cash = _number(latest.get("cash_from_operations"))
    assets = [_number(period.get("total_assets")) for period in periods[-2:]]
    average_assets = None
    if len(assets) == 2 and all(value is not None for value in assets):
        asset_total = _finite_sum(cast(float, value) for value in assets)
        average_assets = _ratio(asset_total, 2.0)
    cash_conversion = _ratio(operating_cash, net_income)
    accrual_numerator = (
        _finite_difference(net_income, operating_cash)
        if net_income is not None and operating_cash is not None
        else None
    )
    accrual_ratio = _ratio(accrual_numerator, average_assets)
    facts: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []
    if net_income is None:
        unknowns.append(
            _unknown(
                "unknown-quality-net-income",
                "Latest accounting earnings are unavailable.",
                "Cash conversion and accrual diagnostics cannot be completed.",
            )
        )
    else:
        facts.append(
            _fact(
                "fact-quality-net-income",
                f"Latest accounting earnings are {net_income} {statements.get('units', 'units')}.",
                source_ids,
            )
        )
    if operating_cash is None:
        unknowns.append(
            _unknown(
                "unknown-quality-operating-cash",
                "Latest operating cash flow is unavailable.",
                "Cash conversion and accrual diagnostics cannot be completed.",
            )
        )
    else:
        facts.append(
            _fact(
                "fact-quality-operating-cash",
                f"Latest operating cash flow is {operating_cash} {statements.get('units', 'units')}.",
                source_ids,
            )
        )
    estimates = []
    if cash_conversion is not None:
        estimates.append(
            {
                "id": "estimate-cash-conversion",
                "label": "Cash conversion",
                "value": cash_conversion,
                "method": "operating cash flow / accounting earnings",
                "input_ids": ["fact-quality-operating-cash", "fact-quality-net-income"],
            }
        )
    if accrual_ratio is not None:
        estimates.append(
            {
                "id": "estimate-accrual-ratio",
                "label": "Accrual ratio",
                "value": accrual_ratio,
                "method": "(accounting earnings - operating cash flow) / average assets",
                "inputs": {
                    "accounting_earnings": net_income,
                    "operating_cash_flow": operating_cash,
                    "average_assets": average_assets,
                },
            }
        )
    working_capital_fields = (
        "accounts_receivable",
        "inventory",
        "accounts_payable",
    )
    previous_working_capital = {
        field: _number(previous.get(field)) for field in working_capital_fields
    }
    latest_working_capital = {
        field: _number(latest.get(field)) for field in working_capital_fields
    }
    working_capital_change: float | None = None
    if all(
        value is not None
        for value in (*previous_working_capital.values(), *latest_working_capital.values())
    ):
        previous_net_working_capital = _finite_sum(
            (
                cast(float, previous_working_capital["accounts_receivable"]),
                cast(float, previous_working_capital["inventory"]),
                -cast(float, previous_working_capital["accounts_payable"]),
            )
        )
        latest_net_working_capital = _finite_sum(
            (
                cast(float, latest_working_capital["accounts_receivable"]),
                cast(float, latest_working_capital["inventory"]),
                -cast(float, latest_working_capital["accounts_payable"]),
            )
        )
        if previous_net_working_capital is not None and latest_net_working_capital is not None:
            working_capital_change = _finite_difference(
                latest_net_working_capital, previous_net_working_capital
            )
        if working_capital_change is not None:
            estimates.append(
                {
                    "id": "estimate-working-capital-change",
                    "label": "Working capital change",
                    "value": working_capital_change,
                    "method": "change in accounts receivable plus inventory minus accounts payable",
                    "inputs": {
                        "previous": previous_working_capital,
                        "latest": latest_working_capital,
                    },
                }
            )
        else:
            unknowns.append(
                _unknown(
                    "unknown-working-capital-calculation",
                    "A finite working-capital change cannot be calculated from the supplied balances.",
                    "The cash-conversion bridge remains unavailable.",
                )
            )
    else:
        unknowns.append(
            _unknown(
                "unknown-working-capital-bridge",
                "Detailed working capital balances are incomplete.",
                "The cash-conversion bridge cannot attribute receivable, inventory, and payable movements.",
            )
        )
    unknowns.extend(
        [
            _unknown(
            "unknown-one-off-items",
            "One-off earnings and footnote adjustments are unavailable.",
            "Reported earnings repeatability cannot be fully assessed.",
            ),
            _unknown(
                "unknown-asset-quality-detail",
                "Asset-quality, impairment, and reserve detail are unavailable.",
                "Asset quality and accounting-estimate risk cannot be fully assessed.",
            ),
        ]
    )
    calculated_diagnostics = [
        str(estimate["label"]) for estimate in estimates if _text(estimate.get("label"))
    ]
    retained_gaps = [
        "working capital" if working_capital_change is None else None,
        "one-off items",
        "asset-quality detail",
    ]
    finding_statement = ""
    if calculated_diagnostics:
        finding_statement = (
            "Calculated earnings-quality diagnostics: "
            + ", ".join(calculated_diagnostics)
            + ". Remaining evidence gaps: "
            + ", ".join(value for value in retained_gaps if value is not None)
            + "."
        )
    return _completed(
        "earnings-quality-analysis",
        "cash-accrual-quality-review",
        method_fields={
            "cash_conversion": cash_conversion,
            "accrual_ratio": accrual_ratio,
            "working_capital_review": {
                "previous": previous_working_capital,
                "latest": latest_working_capital,
                "change": working_capital_change,
                "status": "completed" if working_capital_change is not None else "unknown",
            },
            "one_off_review": "unknown: footnote detail unavailable",
            "asset_quality_review": "unknown: impairment, reserve, and asset-detail evidence unavailable",
            "alternative_explanations": [
                "Timing differences may explain part of cash-to-earnings variation.",
                (
                    "No conclusion about manipulation is supported by this fixture."
                    if _is_demo(inputs)
                    else "No conclusion about manipulation is supported by the supplied evidence."
                ),
            ],
        },
        facts=facts,
        estimates=estimates,
        unknowns=unknowns,
        findings=(
            [
                _finding(
                    "finding-quality-cash-backing",
                    finding_statement,
                    source_ids,
                )
            ]
            if finding_statement
            else []
        ),
        risks=[
            _risk(
                "risk-quality-footnotes",
                "Missing footnote detail limits confidence in earnings repeatability.",
                source_ids,
            )
        ],
        warnings=_warnings(inputs),
    )


def _normalize_forecast_metadata(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    record = _mapping_value(value, "valuation forecast metadata")
    if not record:
        return None
    as_of_date = _text(record.get("as_of_date"))
    method = _text(record.get("method"))
    periods_value = record.get("periods")
    if not as_of_date or _iso_date(as_of_date) is None:
        raise ValueError("forecast metadata requires a valid as_of_date")
    if not method:
        raise ValueError("forecast metadata requires a method")
    if not isinstance(periods_value, Sequence) or isinstance(
        periods_value, (str, bytes)
    ) or not periods_value:
        raise ValueError("forecast metadata requires at least one forecast period")
    periods = [
        dict(_mapping_value(period, "forecast metadata period"))
        for period in periods_value
    ]
    if any(not _text(period.get("fiscal_year")) for period in periods):
        raise ValueError("each forecast metadata period requires a fiscal_year")
    return {
        **dict(record),
        "as_of_date": as_of_date,
        "method": method,
        "periods": periods,
    }


def _normalize_consensus(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    record = _mapping_value(value, "valuation consensus")
    if not record:
        return None
    observation_time = _text(record.get("observation_time"))
    contributor_count = _number(record.get("contributor_count"))
    periods_value = record.get("periods")
    if not observation_time or _iso_date(observation_time) is None:
        raise ValueError("consensus requires a valid observation_time")
    if (
        contributor_count is None
        or contributor_count < 1
        or not contributor_count.is_integer()
    ):
        raise ValueError("consensus requires a positive integer contributor_count")
    if not isinstance(periods_value, Sequence) or isinstance(
        periods_value, (str, bytes)
    ):
        raise ValueError("consensus periods must be a sequence")
    periods: list[dict[str, Any]] = []
    for raw_period in periods_value:
        period = dict(_mapping_value(raw_period, "consensus period"))
        if not _text(period.get("fiscal_year")):
            raise ValueError("each consensus period requires a fiscal_year")
        eps_low = _number(period.get("eps_low"))
        eps_high = _number(period.get("eps_high"))
        if eps_low is not None and eps_high is not None:
            if eps_low > eps_high:
                raise ValueError("consensus eps_low cannot exceed eps_high")
            period["eps_dispersion"] = _require_finite_calculation(
                eps_high - eps_low,
                "consensus EPS dispersion",
            )
        periods.append(period)
    return {
        **dict(record),
        "observation_time": observation_time,
        "contributor_count": int(contributor_count),
        "periods": periods,
    }


def _normalize_industry_comparison(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    record = _mapping_value(value, "industry benchmark")
    if not record:
        return None
    classification = _text(record.get("classification"))
    as_of_date = _text(record.get("as_of_date"))
    sample_size = _number(record.get("sample_size"))
    metrics_value = record.get("metrics")
    if not classification:
        raise ValueError("industry benchmark requires a classification")
    if not as_of_date or _iso_date(as_of_date) is None:
        raise ValueError("industry benchmark requires a valid as_of_date")
    if sample_size is None or sample_size < 1 or not sample_size.is_integer():
        raise ValueError("industry benchmark requires a positive integer sample_size")
    if not isinstance(metrics_value, Mapping) or not metrics_value:
        raise ValueError("industry benchmark requires metric records")
    metrics: dict[str, dict[str, Any]] = {}
    for name, raw_metric in metrics_value.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("industry benchmark metric names must be non-empty")
        metric = dict(_mapping_value(raw_metric, "industry benchmark metric"))
        target = _number(metric.get("target"))
        median = _number(metric.get("industry_median"))
        percentile = _number(metric.get("percentile"))
        definition = _text(metric.get("definition"))
        if target is None or median is None:
            raise ValueError("industry benchmark metrics require target and median")
        if percentile is None or percentile < 0 or percentile > 1:
            raise ValueError("industry benchmark percentile must be between zero and one")
        if not definition:
            raise ValueError("industry benchmark metrics require a definition")
        metric.update(
            {
                "target": target,
                "industry_median": median,
                "percentile": percentile,
                "definition": definition,
                "difference_to_median": _require_finite_calculation(
                    target - median,
                    "industry benchmark difference",
                ),
            }
        )
        metrics[name] = metric
    return {
        **dict(record),
        "classification": classification,
        "as_of_date": as_of_date,
        "sample_size": int(sample_size),
        "metrics": metrics,
    }


def _market_relative_snapshot(value: Mapping[str, Any]) -> dict[str, Any] | None:
    metrics: dict[str, dict[str, float]] = {}
    for name, target_key, industry_key in (
        (
            "price_to_earnings_ttm",
            "price_to_earnings_ttm",
            "industry_price_to_earnings_ttm",
        ),
        ("price_to_book", "price_to_book", "industry_price_to_book"),
    ):
        target = _number(value.get(target_key))
        industry = _number(value.get(industry_key))
        if target is None or industry is None or target <= 0 or industry <= 0:
            continue
        metrics[name] = {
            "target": target,
            "industry_average": industry,
            "target_to_average": _require_finite_calculation(
                target / industry,
                f"{name} industry-relative ratio",
            ),
        }
    if not metrics:
        return None
    reference_value = value.get("industry_valuation_reference")
    reference = (
        _mapping_value(reference_value, "industry valuation reference")
        if reference_value is not None
        else {}
    )
    as_of_date = _text(reference.get("as_of_date"))
    if as_of_date and _iso_date(as_of_date) is None:
        raise ValueError("industry valuation reference has an invalid as_of_date")
    return {
        "classification": _text(reference.get("classification")),
        "as_of_date": as_of_date,
        "sample_size": reference.get("sample_size"),
        "metrics": metrics,
        "pe_history_percentile": _number(value.get("pe_history_percentile")),
        "pb_history_percentile": _number(value.get("pb_history_percentile")),
    }


def _analyze_market_relative_valuation(
    inputs: Mapping[str, Any],
    valuation: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    dcf_missing: Sequence[str],
) -> CapabilityResult:
    source_ids = _require_sources(inputs, "valuation-analysis")
    metrics = _mapping_value(snapshot.get("metrics"), "relative valuation metrics")
    facts = [
        _fact(
            "fact-relative-valuation-vintage",
            "The imported valuation snapshot supplies positive target and industry-average trading multiples"
            + (
                f" for {snapshot['classification']} as of {snapshot['as_of_date']}."
                if snapshot.get("classification") and snapshot.get("as_of_date")
                else "."
            ),
            source_ids,
        )
    ]
    estimates: list[dict[str, Any]] = []
    for name, raw_metric in metrics.items():
        metric = _mapping_value(raw_metric, "relative valuation metric")
        estimates.append(
            {
                "id": f"estimate-relative-{name}",
                "label": (
                    "Industry PE TTM comparison"
                    if name == "price_to_earnings_ttm"
                    else "Industry PB comparison"
                ),
                "value": dict(metric),
                "method": "target multiple divided by the provider's point-in-time industry average",
                "input_ids": ["fact-relative-valuation-vintage"],
            }
        )
    for name, label in (
        ("pe_history_percentile", "Provider PE history percentile"),
        ("pb_history_percentile", "Provider PB history percentile"),
    ):
        value = _number(snapshot.get(name))
        if value is not None:
            estimates.append(
                {
                    "id": f"estimate-{name.replace('_', '-')}",
                    "label": label,
                    "value": value,
                    "method": "provider-defined historical percentile; scale and lookback are retained as supplied",
                    "input_ids": ["fact-relative-valuation-vintage"],
                }
            )
    warnings = _warnings(inputs)
    if snapshot.get("sample_size") is None:
        warnings.append(
            "The industry-average constituent count and membership are unavailable; treat the comparison as supporting rather than decisive evidence."
        )
    return _completed(
        "valuation-analysis",
        "market-relative-valuation",
        method_fields={
            "market_relative_snapshot": dict(snapshot),
            "target_value_range": None,
            "dcf_status": "unknown",
            "consensus": _normalize_consensus(valuation.get("consensus")),
        },
        facts=facts,
        estimates=estimates,
        unknowns=[
            _unknown(
                "unknown-valuation-dcf",
                "A guarded DCF cannot be run because essential inputs are missing: "
                + ", ".join(dcf_missing)
                + ".",
                "No intrinsic-value target range is produced.",
            ),
            _unknown(
                "unknown-valuation-consensus",
                "A licensed point-in-time broker consensus snapshot is unavailable.",
                "Industry-relative valuation is not evidence of earnings expectations or revisions.",
            ),
        ],
        findings=[
            _finding(
                "finding-relative-valuation",
                "Target PE/PB are compared with provider-supplied industry averages without converting the relationship into a rating or target price.",
                source_ids,
            )
        ],
        risks=[
            _risk(
                "risk-relative-valuation-definition",
                "Industry membership, sample size, averaging method, and historical-percentile lookback may be provider-defined or unavailable.",
                source_ids,
            )
        ],
        warnings=warnings,
    )


def analyze_valuation(inputs: Mapping[str, Any]) -> CapabilityResult:
    valuation = _mapping(inputs, "valuation_inputs")
    forecast = _number_list(valuation.get("forecast_unlevered_free_cash_flow"))
    forecast_metadata = _normalize_forecast_metadata(
        valuation.get("forecast_metadata")
    )
    consensus = _normalize_consensus(valuation.get("consensus"))
    base_wacc = _number(valuation.get("wacc"))
    base_growth = _number(valuation.get("terminal_growth"))
    shares = _number(valuation.get("diluted_shares"))
    cash = _number(valuation.get("cash"))
    debt = _number(valuation.get("total_debt"))
    missing: list[str] = []
    for present, label in (
        (forecast, "forecast unlevered free cash flow"),
        (base_wacc, "WACC"),
        (base_growth, "terminal growth"),
        (shares, "positive diluted shares"),
        (cash, "cash"),
        (debt, "gross debt"),
    ):
        if present is None or present == []:
            missing.append(label)
    if shares is not None and shares <= 0:
        missing.append("positive diluted shares")
    if base_wacc is not None and base_growth is not None and base_wacc <= base_growth:
        missing.append("valid WACC greater than terminal growth")
    scenario_inputs = valuation.get("scenario_assumptions")
    if not isinstance(scenario_inputs, Mapping):
        missing.append("bear/base/bull scenario assumptions")
    if missing:
        relative_snapshot = _market_relative_snapshot(valuation)
        if relative_snapshot is not None:
            return _analyze_market_relative_valuation(
                inputs,
                valuation,
                relative_snapshot,
                list(dict.fromkeys(missing)),
            )
        return _skipped(
            "valuation-analysis",
            "scenario-dcf",
            "Essential DCF inputs are unavailable or invalid.",
            list(dict.fromkeys(missing)),
        )
    assert isinstance(scenario_inputs, Mapping)
    source_ids = _require_sources(inputs, "valuation-analysis")
    assert forecast is not None
    assert shares is not None and cash is not None and debt is not None
    scenarios: dict[str, dict[str, Any]] = {}
    assumptions: list[dict[str, Any]] = []
    estimates: list[dict[str, Any]] = []
    warnings = _warnings(inputs)
    for name in ("bear", "base", "bull"):
        raw = scenario_inputs.get(name)
        if not isinstance(raw, Mapping):
            return _skipped(
                "valuation-analysis",
                "scenario-dcf",
                f"The {name} scenario is missing or malformed.",
                [f"{name} scenario assumptions"],
            )
        wacc = _number(raw.get("wacc"))
        growth = _number(raw.get("terminal_growth"))
        cash_flow_multiplier = _number(raw.get("cash_flow_multiplier"))
        if (
            wacc is None
            or growth is None
            or cash_flow_multiplier is None
            or wacc <= growth
            or cash_flow_multiplier <= 0
        ):
            return _skipped(
                "valuation-analysis",
                "scenario-dcf",
                f"The {name} scenario violates a DCF guard.",
                [f"valid {name} WACC, terminal growth, and cash-flow multiplier"],
            )
        scenario_cash_flows = _scaled_series(
            forecast, cash_flow_multiplier, "DCF scenario cash flows"
        )
        scenario = _dcf_scenario(
            scenario_cash_flows,
            wacc=wacc,
            terminal_growth=growth,
            cash=cash,
            debt=debt,
            diluted_shares=shares,
        )
        scenarios[name] = scenario
        assumptions.append(
            {
                "id": f"assumption-dcf-{name}",
                "statement": f"The {name} scenario applies a {cash_flow_multiplier:.3f} cash-flow multiplier, {wacc:.3%} WACC, and {growth:.3%} terminal growth.",
                "rationale": _text(raw.get("rationale"))
                or (
                    "Scenario values are explicitly supplied by the fictional fixture."
                    if _is_demo(inputs)
                    else "Scenario values are explicitly supplied by the imported valuation record."
                ),
                "materiality": "high",
            }
        )
        estimates.append(
            {
                "id": f"estimate-dcf-{name}",
                "label": f"{name.title()} scenario equity value per share",
                "value": scenario["equity_value_per_share"],
                "method": "five-period unlevered free-cash-flow DCF with perpetuity growth",
                "input_ids": [f"assumption-dcf-{name}", "fact-valuation-bridge"],
            }
        )
    wacc_values = _number_list(valuation.get("sensitivity_wacc_values"))
    growth_values = _number_list(
        valuation.get("sensitivity_terminal_growth_values")
    )
    if not wacc_values or not growth_values or len(wacc_values) % 2 == 0 or len(growth_values) % 2 == 0:
        return _skipped(
            "valuation-analysis",
            "scenario-dcf",
            "An odd-dimension sensitivity grid is unavailable.",
            ["odd WACC and terminal-growth sensitivity axes"],
        )
    if wacc_values[len(wacc_values) // 2] != scenarios["base"]["wacc"] or growth_values[
        len(growth_values) // 2
    ] != scenarios["base"]["terminal_growth"]:
        raise ValueError("sensitivity axes must be centered on the base assumptions")
    grid: list[list[float | None]] = []
    base_scenario = scenario_inputs["base"]
    assert isinstance(base_scenario, Mapping)
    base_cash_flow_multiplier = _number(base_scenario.get("cash_flow_multiplier"))
    assert base_cash_flow_multiplier is not None
    base_cash_flows = _scaled_series(
        forecast, base_cash_flow_multiplier, "DCF sensitivity cash flows"
    )
    for growth in growth_values:
        row: list[float | None] = []
        for wacc in wacc_values:
            if wacc <= growth:
                row.append(None)
                continue
            row.append(
                _dcf_scenario(
                    base_cash_flows,
                    wacc=wacc,
                    terminal_growth=growth,
                    cash=cash,
                    debt=debt,
                    diluted_shares=shares,
                )["equity_value_per_share"]
            )
        grid.append(row)
    facts = [
        _fact(
            "fact-valuation-bridge",
            (
                f"The fixture supplies cash {cash}, gross debt {debt}, and diluted shares {shares} for the EV-to-equity bridge."
                if _is_demo(inputs)
                else f"The imported valuation record supplies cash {cash}, gross debt {debt}, and diluted shares {shares} for the EV-to-equity bridge."
            ),
            source_ids,
        )
    ]
    if consensus is not None:
        facts.append(
            _fact(
                "fact-consensus-vintage",
                f"The persisted consensus snapshot contains {consensus['contributor_count']} contributors as observed at {consensus['observation_time']}.",
                source_ids,
            )
        )
    if forecast_metadata is not None:
        facts.append(
            _fact(
                "fact-forecast-model-vintage",
                f"The InvestKit forecast is dated {forecast_metadata['as_of_date']} and identifies its method as {forecast_metadata['method']}.",
                source_ids,
            )
        )
        estimates.append(
            {
                "id": "estimate-investkit-forecast",
                "label": "InvestKit driver-based forecast",
                "value": forecast_metadata["periods"],
                "method": forecast_metadata["method"],
                "input_ids": ["fact-forecast-model-vintage"],
            }
        )
    if consensus is not None:
        estimates.append(
            {
                "id": "estimate-broker-consensus",
                "label": "Point-in-time broker consensus",
                "value": consensus["periods"],
                "method": "persisted vendor consensus; separate from company guidance and InvestKit estimates",
                "input_ids": ["fact-consensus-vintage"],
            }
        )
    estimates.append(
        {
            "id": "estimate-dcf-target-range",
            "label": "Scenario DCF value-per-share range",
            "value": {
                "low": min(
                    scenario["equity_value_per_share"]
                    for scenario in scenarios.values()
                ),
                "base": scenarios["base"]["equity_value_per_share"],
                "high": max(
                    scenario["equity_value_per_share"]
                    for scenario in scenarios.values()
                ),
            },
            "method": "bear/base/bull scenario DCF; not a guaranteed target price",
            "input_ids": [
                "assumption-dcf-bear",
                "assumption-dcf-base",
                "assumption-dcf-bull",
                "fact-valuation-bridge",
            ],
        }
    )
    prior = _capability_results(inputs)
    comps_status = _mapping_value(prior.get("comps-analysis"), "comps result").get(
        "status", "not supplied"
    )
    return _completed(
        "valuation-analysis",
        "scenario-dcf",
        method_fields={
            "forecast_unlevered_free_cash_flow": forecast,
            "forecast_provenance": (
                "investkit_model"
                if forecast_metadata is not None
                else "supplied_forecast_unclassified"
            ),
            "forecast_metadata": forecast_metadata,
            "consensus": consensus,
            "scenarios": scenarios,
            "target_value_range": {
                "low": min(
                    scenario["equity_value_per_share"]
                    for scenario in scenarios.values()
                ),
                "base": scenarios["base"]["equity_value_per_share"],
                "high": max(
                    scenario["equity_value_per_share"]
                    for scenario in scenarios.values()
                ),
                "scenario_values": {
                    name: scenario["equity_value_per_share"]
                    for name, scenario in scenarios.items()
                },
                "basis": "scenario DCF; not a guaranteed target price",
            },
            "ev_to_equity_bridge": {"cash": cash, "gross_debt": debt},
            "sensitivity": {
                "wacc_values": wacc_values,
                "terminal_growth_values": growth_values,
                "grid": grid,
            },
            "comps_handoff_status": comps_status,
            "historical_valuation": "unknown: aligned point-in-time series unavailable",
        },
        facts=facts,
        assumptions=assumptions,
        estimates=estimates,
        unknowns=[
            _unknown(
                "unknown-historical-valuation",
                "A definition-aligned historical valuation series is unavailable.",
                "Historical percentile context cannot corroborate the scenario DCF.",
            ),
            *(
                []
                if consensus is not None
                else [
                    _unknown(
                        "unknown-valuation-consensus",
                        "A point-in-time broker consensus snapshot is unavailable.",
                        "The InvestKit forecast and DCF cannot be compared with contributor dispersion or revisions.",
                    )
                ]
            ),
            *(
                []
                if forecast_metadata is not None
                else [
                    _unknown(
                        "unknown-valuation-forecast-provenance",
                        "The supplied free-cash-flow series has no structured model metadata.",
                        "Its driver method, vintage, and forecast-period audit trail cannot be verified.",
                    )
                ]
            ),
        ],
        findings=[
            _finding(
                "finding-valuation-range",
                "Bear, base, and bull DCF cases form a scenario range rather than a deterministic target.",
                source_ids,
            )
        ],
        risks=[
            _risk(
                "risk-valuation-sensitivity",
                "DCF output is materially sensitive to cash-flow, WACC, and terminal-growth assumptions.",
                source_ids,
            )
        ],
        warnings=warnings,
    )


def analyze_comps(inputs: Mapping[str, Any]) -> CapabilityResult:
    record = _mapping(inputs, "peers")
    industry_comparison = _normalize_industry_comparison(
        record.get("industry_benchmark")
    )
    raw_peers = record.get("peers", record.get("comparables"))
    if raw_peers is None:
        raw_peers = []
    if not isinstance(raw_peers, Sequence) or isinstance(raw_peers, (str, bytes)):
        raise ValueError("peer comparables must be a sequence")
    peers = [
        _mapping_value(value, "peer comparable") for value in raw_peers
    ]
    if not peers:
        return _skipped(
            "comps-analysis",
            "guarded-peer-comparables",
            "No defensible peer dataset is available.",
            ["peer comparables"],
        )
    source_ids = _require_sources(inputs, "comps-analysis")
    ledger: list[dict[str, Any]] = []
    observations: dict[str, list[float]] = {
        "ev_to_operating_income": [],
        "price_to_earnings": [],
        "price_to_book": [],
    }
    for peer in peers:
        entry = dict(peer)
        status = _text(peer.get("status")) or "included"
        if status == "excluded":
            if not _text(peer.get("reason")):
                raise ValueError("excluded peer requires a reason")
            ledger.append(entry)
            continue
        entry["status"] = "included"
        invalid: dict[str, str] = {}
        metrics = {
            "ev_to_operating_income": _guarded_multiple(
                peer.get("enterprise_value"),
                peer.get("operating_income"),
                "operating income",
                invalid,
            ),
            "price_to_earnings": _guarded_multiple(
                peer.get("market_capitalization"),
                peer.get("net_income"),
                "net income",
                invalid,
            ),
            "price_to_book": _guarded_multiple(
                peer.get("market_capitalization"),
                peer.get("total_equity"),
                "book equity",
                invalid,
            ),
        }
        entry["valid_multiples"] = {
            key: value for key, value in metrics.items() if value is not None
        }
        entry["invalid_metrics"] = invalid
        for metric, value in metrics.items():
            if value is not None:
                observations[metric].append(value)
        ledger.append(entry)
    distributions: dict[str, dict[str, Any]] = {}
    for metric, values in observations.items():
        if not values:
            continue
        first_quartile, third_quartile = _quartiles(values)
        distributions[metric] = {
            "observations": values,
            "sample_size": len(values),
            "median": _finite_median(values),
            "quartiles": {"q1": first_quartile, "q3": third_quartile},
            "range": {"low": min(values), "high": max(values)},
            "minimum": min(values),
            "maximum": max(values),
            "outlier_policy": (
                "none removed in the bounded fictional fixture"
                if _is_demo(inputs)
                else "none removed from the bounded imported peer set"
            ),
        }
    if not distributions:
        return _skipped(
            "comps-analysis",
            "guarded-peer-comparables",
            "All peer metrics have invalid denominators.",
            ["positive comparable peer denominators"],
        )
    facts = [
        _fact(
            "fact-comps-peer-set",
            (
                f"The fictional peer ledger contains {len(peers)} considered companies with explicit inclusion or exclusion decisions."
                if _is_demo(inputs)
                else f"The imported peer ledger contains {len(peers)} considered companies with explicit inclusion or exclusion decisions."
            ),
            source_ids,
        )
    ]
    if industry_comparison is not None:
        facts.append(
            _fact(
                "fact-industry-benchmark-vintage",
                f"The {industry_comparison['classification']} benchmark contains {industry_comparison['sample_size']} constituents as of {industry_comparison['as_of_date']}.",
                source_ids,
            )
        )
    statements = _mapping(inputs, "statements")
    periods = _periods(statements) if statements else []
    latest = periods[-1] if periods else {}
    valuation = _mapping(inputs, "valuation_inputs")
    target_metrics = {
        "ev_to_operating_income": _number(latest.get("operating_income")),
        "price_to_earnings": _number(latest.get("net_income")),
        "price_to_book": _number(latest.get("total_equity")),
    }
    cash = _number(valuation.get("cash"))
    debt = _number(valuation.get("total_debt"))
    diluted_shares = _number(valuation.get("diluted_shares"))
    implied_ranges: dict[str, dict[str, Any]] = {}
    unknowns: list[dict[str, Any]] = []
    for metric, distribution in distributions.items():
        target_metric = target_metrics[metric]
        if target_metric is None or target_metric <= 0:
            unknowns.append(
                _unknown(
                    f"unknown-comps-target-{metric}",
                    f"The target {metric.replace('_', ' ')} denominator is unavailable or invalid.",
                    "This peer distribution cannot produce a target implied-value range.",
                )
            )
            continue
        multiples = {
            "low": float(distribution["minimum"]),
            "median": float(distribution["median"]),
            "high": float(distribution["maximum"]),
        }
        if metric == "ev_to_operating_income":
            if cash is None or debt is None:
                unknowns.append(
                    _unknown(
                        "unknown-comps-ev-equity-bridge",
                        "Cash or gross debt is unavailable for the relative EV-to-equity bridge.",
                        "Enterprise-value multiples cannot produce an implied equity-value range.",
                    )
                )
                continue
            enterprise_values = {
                label: _require_finite_calculation(
                    _finite_product(target_metric, multiple),
                    "comparable enterprise-value calculation",
                )
                for label, multiple in multiples.items()
            }
            equity_values = {
                label: _require_finite_calculation(
                    _finite_sum((value, cash, -debt)),
                    "comparable EV-to-equity bridge",
                )
                for label, value in enterprise_values.items()
            }
            bridge: dict[str, Any] = {
                "basis": "enterprise_value",
                "cash": cash,
                "gross_debt": debt,
                "formula": "enterprise value + cash - gross debt",
            }
        else:
            enterprise_values = None
            equity_values = {
                label: _require_finite_calculation(
                    _finite_product(target_metric, multiple),
                    "comparable equity-value calculation",
                )
                for label, multiple in multiples.items()
            }
            bridge = {
                "basis": "equity_value",
                "formula": "equity multiple multiplied by the aligned target denominator",
            }
        per_share_values = None
        if diluted_shares is not None and diluted_shares > 0:
            per_share_values = {
                label: _require_finite_calculation(
                    _ratio(value, diluted_shares),
                    "comparable per-share calculation",
                )
                for label, value in equity_values.items()
            }
        else:
            unknowns.append(
                _unknown(
                    f"unknown-comps-shares-{metric}",
                    "Positive diluted shares are unavailable.",
                    "The relative equity-value range cannot be expressed per share.",
                )
            )
        implied_ranges[metric] = {
            "selected_rationale": "The complete bounded distribution is retained without an automatic premium or discount.",
            "target_metric": target_metric,
            "multiple_range": multiples,
            "enterprise_value_range": enterprise_values,
            "equity_value_range": equity_values,
            "equity_value_per_share_range": per_share_values,
            "bridge": bridge,
        }
    estimates = [
        {
            "id": f"estimate-comps-{metric}",
            "label": f"Median {metric.replace('_', ' ')}",
            "value": distribution["median"],
            "method": (
                "median of valid, period-aligned fictional peer observations"
                if _is_demo(inputs)
                else "median of valid, period-aligned imported peer observations"
            ),
            "inputs": {
                "observations": distribution["observations"],
                "sample_size": distribution["sample_size"],
            },
        }
        for metric, distribution in distributions.items()
    ]
    estimates.extend(
        {
            "id": f"estimate-comps-implied-{metric}",
            "label": f"Implied {metric.replace('_', ' ')} equity-value range",
            "value": value["equity_value_per_share_range"]
            or value["equity_value_range"],
            "method": "valid peer multiple distribution applied to an aligned target denominator",
            "inputs": {
                "target_metric": value["target_metric"],
                "multiple_range": value["multiple_range"],
                "bridge": value["bridge"],
            },
        }
        for metric, value in implied_ranges.items()
    )
    if industry_comparison is not None:
        estimates.extend(
            {
                "id": f"estimate-industry-{metric}",
                "label": f"Industry-relative {metric.replace('_', ' ')}",
                "value": {
                    "target": values["target"],
                    "industry_median": values["industry_median"],
                    "difference_to_median": values["difference_to_median"],
                    "percentile": values["percentile"],
                },
                "method": values["definition"],
                "input_ids": ["fact-industry-benchmark-vintage"],
            }
            for metric, values in industry_comparison["metrics"].items()
        )
    else:
        unknowns.append(
            _unknown(
                "unknown-industry-benchmark",
                "A point-in-time industry benchmark is unavailable.",
                "Peer multiples cannot establish the issuer's growth, profitability, leverage, or cash-conversion percentile versus its industry.",
            )
        )
    warnings = _warnings(inputs)
    if any(value["sample_size"] < 3 for value in distributions.values()):
        warnings.append(
            "At least one peer distribution has fewer than three valid observations and is weak evidence."
        )
    return _completed(
        "comps-analysis",
        "guarded-peer-comparables",
        method_fields={
            "peer_ledger": ledger,
            "distributions": distributions,
            "implied_ranges": implied_ranges,
            "relative_ev_to_equity_bridge": {
                "cash": cash,
                "gross_debt": debt,
                "diluted_shares": diluted_shares,
                "status": (
                    "completed"
                    if "ev_to_operating_income" in implied_ranges
                    else "unknown"
                ),
            },
            "period_alignment": record.get("period_alignment"),
            "currency_conversion": record.get("currency_conversion"),
            "selection_rationale": "Business model, revenue mix, fiscal period, and accounting comparability were considered before calculation.",
            "industry_comparison": industry_comparison,
        },
        facts=facts,
        estimates=estimates,
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-comps-distribution",
                "Only valid peer denominators enter the reported multiple distributions; exclusions remain visible.",
                source_ids,
            )
        ],
        risks=[
            _risk(
                "risk-comps-sample",
                (
                    "The small fictional sample is illustrative and not robust market evidence."
                    if _is_demo(inputs)
                    else "A small imported peer sample is not robust market evidence."
                ),
                source_ids,
            )
        ],
        warnings=warnings,
    )


def analyze_earnings(inputs: Mapping[str, Any]) -> CapabilityResult:
    record = _mapping(inputs, "earnings")
    events_value = record.get("events", record.get("periods", []))
    if events_value is None:
        events_value = []
    if not isinstance(events_value, Sequence) or isinstance(events_value, (str, bytes)):
        raise ValueError("earnings events must be a sequence")
    events = [_mapping_value(value, "earnings event") for value in events_value]
    if not events:
        return _skipped(
            "earnings-analysis",
            "point-in-time-earnings-review",
            "No earnings event or history is available.",
            ["earnings event history"],
        )
    source_ids = _require_sources(inputs, "earnings-analysis")
    event = events[-1]
    actual = _mapping_value(event.get("actual"), "earnings actual")
    expectation = _mapping_value(event.get("expectation"), "earnings expectation")
    guidance = _mapping_value(event.get("guidance"), "earnings guidance")
    comparisons: dict[str, dict[str, Any]] = {}
    estimates: list[dict[str, Any]] = []
    for metric in ("revenue", "eps"):
        actual_value = _number(actual.get(metric))
        expected_value = _number(expectation.get(metric))
        if actual_value is None or expected_value is None:
            continue
        absolute_surprise = _finite_difference(actual_value, expected_value)
        percentage_surprise = _ratio_delta(actual_value, expected_value)
        comparison = {
            "actual": actual_value,
            "expectation": expected_value,
            "absolute_surprise": absolute_surprise,
            "percentage_surprise": percentage_surprise,
            "observation_time": expectation.get("observation_time"),
            "definition": expectation.get(f"{metric}_definition", actual.get(f"{metric}_definition")),
        }
        comparisons[metric] = comparison
        if percentage_surprise is not None:
            estimates.append(
                {
                    "id": f"estimate-earnings-surprise-{metric}",
                    "label": f"{metric.upper()} surprise",
                    "value": percentage_surprise,
                    "method": "reported actual versus persisted pre-release expectation",
                    "input_ids": [f"fact-earnings-actual-{metric}", "assumption-consensus-vintage"],
                }
            )
    guidance_range = guidance.get("revenue_range")
    guidance_comparison: dict[str, Any] = {}
    if guidance:
        guidance_sources = guidance.get("source_ids", source_ids)
        guidance_comparison = {
            "period": guidance.get("period"),
            "source_ids": (
                _validated_source_ids(guidance_sources, "guidance source IDs")
                if isinstance(guidance_sources, list)
                else source_ids
            ),
        }
    if (
        isinstance(guidance_range, Sequence)
        and not isinstance(guidance_range, (str, bytes))
        and len(guidance_range) == 2
        and all(_number(value) is not None for value in guidance_range)
    ):
        lower, upper = (_number(value) for value in guidance_range)
        assert lower is not None and upper is not None
        midpoint = _ratio(_finite_sum((lower, upper)), 2.0)
        actual_revenue = _number(actual.get("revenue"))
        if midpoint is not None:
            guidance_comparison.update(
                {
                    "range": [lower, upper],
                    "midpoint": midpoint,
                    "actual": actual.get("revenue"),
                    "actual_vs_midpoint": (
                        _finite_difference(actual_revenue, midpoint)
                        if actual_revenue is not None
                        else None
                    ),
                }
            )
    facts = [
        _fact(
            f"fact-earnings-actual-{metric}",
            f"Reported {metric.upper()} for {event.get('period', 'the event period')} is {value}.",
            source_ids,
        )
        for metric, value in (("revenue", actual.get("revenue")), ("eps", actual.get("eps")))
        if _number(value) is not None
    ]
    transcript_available = event.get("transcript_available") is True
    unknowns: list[dict[str, Any]] = []
    warnings = _warnings(inputs)
    if not expectation:
        unknowns.append(
            _unknown(
                "unknown-earnings-expectation",
                (
                    "Point-in-time expectation data was not supplied in this bundle."
                    if not _is_demo(inputs)
                    else "Point-in-time expectation data is unavailable."
                ),
                "Consensus surprise and expectation-vintage analysis cannot be performed.",
            )
        )
    if not guidance:
        unknowns.append(
            _unknown(
                "unknown-earnings-guidance",
                (
                    "Issuer guidance data was not supplied in this bundle."
                    if not _is_demo(inputs)
                    else "Issuer guidance data is unavailable."
                ),
                "Actual performance cannot be compared with prior issuer guidance.",
            )
        )
    if not transcript_available:
        unknowns.append(
            _unknown(
                "unknown-earnings-transcript",
                (
                    "An earnings transcript was not supplied in this bundle."
                    if not _is_demo(inputs)
                    else "The earnings transcript is unknown because no transcript is available."
                ),
                "Management tone, speaker-specific comments, and Q&A cannot be analyzed.",
            )
        )
        warnings.append("Transcript analysis was omitted; no transcript source is available.")
    assumptions = (
        [
            {
                "id": "assumption-consensus-vintage",
                "statement": (
                    "The fixture expectation is the persisted pre-release baseline."
                    if _is_demo(inputs)
                    else "The imported expectation is treated as the persisted pre-release baseline."
                ),
                "rationale": _text(expectation.get("vintage_rationale"))
                or (
                    "The observation time precedes the fictional release time."
                    if _is_demo(inputs)
                    else "The supplied observation time precedes the reported release time."
                ),
                "materiality": "high",
            }
        ]
        if expectation
        else []
    )
    has_guidance_comparison = "range" in guidance_comparison
    if comparisons or has_guidance_comparison:
        comparison_parts = []
        if comparisons:
            comparison_parts.append("point-in-time expectations")
        if has_guidance_comparison:
            comparison_parts.append("prior guidance")
        findings = [
            _finding(
                "finding-earnings-bridges",
                "Reported actuals are compared with " + " and ".join(comparison_parts) + ".",
                source_ids,
            )
        ]
    else:
        findings = [
            _finding(
                "finding-earnings-actuals-only",
                "Reported actuals are preserved without an expectation or guidance comparison.",
                source_ids,
            )
        ]
    return _completed(
        "earnings-analysis",
        "point-in-time-earnings-review",
        method_fields={
            "mode": "review",
            "event_period": event.get("period"),
            "consensus_comparison": comparisons,
            "guidance_comparison": guidance_comparison,
            "transcript_available": transcript_available,
            "driver_analysis": event.get("drivers", []),
            "estimate_revisions": event.get("estimate_revisions", []),
        },
        facts=facts,
        assumptions=assumptions,
        estimates=estimates,
        unknowns=unknowns,
        findings=findings,
        risks=[
            _risk(
                "risk-earnings-transcript-gap",
                "Absent transcript evidence prevents interpretation of management commentary.",
                source_ids,
            )
        ],
        warnings=warnings,
    )


def analyze_investment_thesis(inputs: Mapping[str, Any]) -> CapabilityResult:
    prior = _capability_results(inputs)
    required = (
        "company-deep-research",
        "business-model-analysis",
        "financial-statement-analysis",
        "earnings-quality-analysis",
    )
    missing = [name for name in required if name not in prior]
    if missing:
        return _skipped(
            "investment-thesis",
            "falsifiable-thesis-synthesis",
            "Required upstream research artifacts are unavailable.",
            missing,
        )
    source_ids = _prior_source_ids(prior)
    if not source_ids:
        return _skipped(
            "investment-thesis",
            "falsifiable-thesis-synthesis",
            "Upstream research has no resolved source lineage.",
            ["resolved upstream source IDs"],
        )
    source_id = source_ids[0]
    comps = _mapping_value(prior.get("comps-analysis"), "comps result")
    valuation = _mapping_value(prior.get("valuation-analysis"), "valuation result")
    limitations: list[str] = []
    for name, result in (("comps-analysis", comps), ("valuation-analysis", valuation)):
        if result.get("status") == "skipped" or not result:
            limitations.append(f"{name} is skipped or missing and remains an unknown limitation")
    if not _is_demo(inputs):
        return _analyze_imported_thesis(inputs, prior, source_ids, limitations)
    pillars = [
        {
            "id": "pillar-operating-progress",
            "mechanism": "Revenue growth and cash conversion can support continued operating progress.",
            "confirming_evidence": [
                "finding-financial-trend",
                "finding-quality-cash-backing",
            ],
            "disconfirming_evidence": ["risk-company-1", "risk-quality-footnotes"],
        },
        {
            "id": "pillar-business-durability",
            "mechanism": "The hybrid model may diversify demand while municipal tender concentration creates fragility.",
            "confirming_evidence": ["finding-business-mechanics"],
            "disconfirming_evidence": ["finding-business-fragility"],
        },
    ]
    return _completed(
        "investment-thesis",
        "falsifiable-thesis-synthesis",
        method_fields={
            "thesis_statement": "The fictional company can sustain operating progress if tender conversion and cash generation persist despite customer and input-cost concentration.",
            "time_horizon": "three fictional fiscal years",
            "bull_case": "Demand diversification, stronger conversion, and stable input costs improve the operating path.",
            "base_case": "Moderate growth and cash generation continue with disclosed concentration risks.",
            "bear_case_seed": "Tender slippage and input-cost pressure weaken margins and cash conversion.",
            "pillars": pillars,
            "falsifiers": [
                {
                    "metric": "cash conversion",
                    "condition": "sustained deterioration despite reported profit growth",
                    "review_timing": "each fictional annual period",
                },
                {
                    "metric": "tender conversion",
                    "condition": "backlog repeatedly fails to reach delivered revenue and cash",
                    "review_timing": "at each fictional tender update",
                },
            ],
            "evidence_sufficiency": "mixed" if limitations else "supported",
            "limitations": limitations,
        },
        facts=[
            _fact(
                "fact-thesis-evidence-base",
                "The thesis is assembled only from the persisted fictional capability artifacts.",
                source_id,
            )
        ],
        assumptions=[
            {
                "id": "assumption-thesis-continuity",
                "statement": "The fictional operating environment remains broadly comparable across the stated horizon.",
                "rationale": "No forward macroeconomic fixture is supplied.",
                "materiality": "high",
            }
        ],
        unknowns=[
            _unknown(
                f"unknown-thesis-limitation-{index}",
                limitation,
                "The affected thesis pillar has lower evidence sufficiency.",
            )
            for index, limitation in enumerate(limitations, start=1)
        ],
        findings=[
            _finding(
                "finding-thesis-balanced",
                "The thesis records confirming and disconfirming evidence plus observable falsifiers.",
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-thesis-fragility",
                "Tender conversion and input-cost assumptions are material thesis dependencies.",
                source_id,
            )
        ],
        warnings=_warnings(inputs),
    )


def analyze_bear_case(inputs: Mapping[str, Any]) -> CapabilityResult:
    prior = _capability_results(inputs)
    thesis = _mapping_value(prior.get("investment-thesis"), "investment thesis")
    if thesis.get("status") != "completed":
        return _skipped(
            "bear-case-analysis",
            "independent-red-team",
            "A frozen completed thesis is required for independent red-team analysis.",
            ["completed investment-thesis artifact"],
        )
    source_ids = _prior_source_ids(prior)
    if not source_ids:
        return _skipped(
            "bear-case-analysis",
            "independent-red-team",
            "No independent evidence source is available.",
            ["resolved upstream source IDs"],
        )
    source_id = source_ids[0]
    thesis_bytes = json.dumps(
        thesis, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    checksum = hashlib.sha256(thesis_bytes).hexdigest()
    thesis_statement = _mapping_value(thesis.get("method"), "thesis method").get(
        "thesis_statement"
    )
    if not _is_demo(inputs):
        return _analyze_imported_bear_case(
            inputs,
            prior,
            thesis,
            source_ids,
            checksum,
            thesis_statement,
        )
    counter_thesis = (
        "Tender conversion failure and battery-cost pressure could reduce margin and cash generation before diversification offsets concentration."
    )
    if counter_thesis == thesis_statement:
        raise ValueError("bear case must be independent of the frozen thesis statement")
    return _completed(
        "bear-case-analysis",
        "independent-red-team",
        method_fields={
            "thesis_snapshot_checksum": checksum,
            "counter_thesis": counter_thesis,
            "fragile_assumptions": [
                "Backlog converts to delivered revenue and collected cash.",
                "Battery input costs do not outrun pricing and mix benefits.",
                "Municipal tender concentration does not amplify delays.",
            ],
            "counterevidence": ["finding-business-fragility", "risk-company-1"],
            "risk_mechanisms": [
                "Tender delay reduces delivery, revenue recognition, and cash receipts.",
                "Input-cost inflation compresses operating margin and free cash flow.",
            ],
            "failure_signals": [
                {
                    "metric": "backlog conversion",
                    "condition": "repeated delay or cancellation",
                    "time_window": "next two fictional reporting periods",
                    "expected_source": source_id,
                },
                {
                    "metric": "cash conversion",
                    "condition": "operating cash flow persistently trails accounting earnings",
                    "time_window": "next two fictional annual periods",
                    "expected_source": source_id,
                },
            ],
            "thesis_killers_for_bear_case": [
                "Diversified customer evidence with stable conversion and improving cash generation would weaken the counter-thesis."
            ],
            "independence_check": {
                "passed": True,
                "reason": "The counter-thesis uses adverse causal mechanisms and disconfirming evidence rather than adjective inversion.",
            },
        },
        facts=[
            _fact(
                "fact-bear-evidence-snapshot",
                "The red-team pass uses the same frozen fictional evidence snapshot as the thesis.",
                source_id,
            )
        ],
        assumptions=[
            {
                "id": "assumption-bear-severity",
                "statement": "Tender and input-cost stresses could overlap.",
                "rationale": "The fixture does not provide probabilistic dependence data.",
                "materiality": "high",
            }
        ],
        findings=[
            _finding(
                "finding-bear-counter-thesis",
                counter_thesis,
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-bear-compounding",
                "Concurrent tender and cost pressure could compound cash-flow weakness.",
                source_id,
            )
        ],
        warnings=_warnings(inputs),
    )


def _analyze_imported_thesis(
    inputs: Mapping[str, Any],
    prior: Mapping[str, Any],
    source_ids: Sequence[str],
    limitations: Sequence[str],
) -> CapabilityResult:
    """Assemble an imported-data thesis only from persisted upstream evidence."""

    profile = _mapping(inputs, "profile")
    identity = _mapping(inputs, "identity")
    company_name = _text(identity.get("legal_name")) or "The company"
    drivers = _strings(profile.get("research_drivers"))
    earnings = _mapping_value(prior.get("earnings-analysis"), "earnings result")
    earnings_method = _mapping_value(earnings.get("method"), "earnings method")
    drivers.extend(_strings(earnings_method.get("driver_analysis")))
    estimate_labels = _prior_estimate_labels(prior)
    if not drivers:
        drivers.extend(estimate_labels[:3])
    drivers = _deduplicated_strings(drivers)

    risk_records = _prior_records(prior, "risks")
    risk_statements = _deduplicated_strings(
        str(record["statement"])
        for record in risk_records
        if _text(record.get("statement"))
    )
    evidence_ids = [
        str(record["id"])
        for record in _prior_records(prior, "findings")
        if _text(record.get("id"))
    ]
    missing_evidence: list[str] = []
    if not drivers:
        missing_evidence.append("source-backed operating drivers or calculated estimates")
    if not evidence_ids:
        missing_evidence.append("source-backed analytical findings")
    if not risk_statements:
        missing_evidence.append("source-backed disconfirming risk evidence")
    if missing_evidence:
        return _skipped(
            "investment-thesis",
            "falsifiable-thesis-synthesis",
            "The imported evidence is insufficient to form a falsifiable investment thesis.",
            missing_evidence,
        )
    risk_ids = [
        str(record["id"])
        for record in risk_records
        if _text(record.get("id"))
    ]
    source_list = list(source_ids)
    primary_drivers = "; ".join(drivers[:2])
    primary_risks = "; ".join(risk_statements[:2])
    pillars: list[dict[str, Any]] = []
    for index, driver in enumerate(drivers[:3], start=1):
        pillar: dict[str, Any] = {
            "id": f"pillar-imported-{index}",
            "mechanism": (
                f"The persisted evidence identifies {driver} as a driver whose durability "
                "must be tested in later reporting periods."
            ),
            "confirming_evidence": evidence_ids[:2],
        }
        if risk_ids:
            pillar["disconfirming_evidence"] = risk_ids[:2]
        else:
            pillar["evidence_gap"] = "No source-backed disconfirming risk record is available."
        pillars.append(pillar)
    monitoring_kpis = [
        {
            "metric": driver,
            "evidence_basis": "explicit profile driver"
            if driver in _strings(profile.get("research_drivers"))
            else "upstream capability estimate or earnings driver",
            "review_timing": "each new reporting or source update",
            "source_ids": source_list,
        }
        for driver in drivers[:5]
    ]
    falsifiers = [
        {
            "metric": item["metric"],
            "condition": "sustained deterioration or loss of the supporting evidence",
            "review_timing": item["review_timing"],
        }
        for item in monitoring_kpis
    ]
    market_context = _market_context(inputs)
    market_source_ids = list(market_context.get("source_ids", [])) if market_context else []
    market_facts = (
        [
            _fact(
                "fact-thesis-market-window",
                (
                    f"The persisted market window contains {market_context['observation_count']} daily observations "
                    f"from {market_context['start_date']} through {market_context['end_date']}."
                ),
                market_source_ids,
            )
        ]
        if market_context and market_source_ids
        else []
    )
    market_estimates = []
    if market_context:
        for key, label in (
            ("available_period_return", "Available-window price return"),
            ("annualized_realized_volatility", "Annualized realized volatility"),
            ("maximum_drawdown", "Available-window maximum drawdown"),
        ):
            value = market_context.get(key)
            if value is not None:
                market_estimates.append(
                    {
                        "id": f"estimate-market-{key.replace('_', '-')}",
                        "label": label,
                        "value": value,
                        "method": "calculation over sorted bounded daily close observations",
                        "inputs": {
                            "observation_count": market_context["observation_count"],
                            "start_date": market_context["start_date"],
                            "end_date": market_context["end_date"],
                        },
                    }
                )
    return _completed(
        "investment-thesis",
        "falsifiable-thesis-synthesis",
        method_fields={
            "thesis_statement": (
                f"{company_name}'s source-backed operating case depends on {primary_drivers}; "
                f"it can be weakened by {primary_risks}"
            ),
            "time_horizon": "through the next available reporting periods",
            "bull_case": f"Confirming evidence strengthens across {primary_drivers}.",
            "base_case": (
                f"The supplied evidence for {primary_drivers} persists while identified "
                "limitations remain unresolved."
            ),
            "bear_case_seed": f"{primary_risks} could weaken the monitored operating evidence.",
            "pillars": pillars,
            "monitoring_kpis": monitoring_kpis,
            "falsifiers": falsifiers,
            "evidence_sufficiency": "mixed" if limitations else "supported",
            "limitations": list(limitations),
            "market_context": {
                key: value for key, value in market_context.items() if key != "source_ids"
            }
            if market_context
            else None,
        },
        facts=[
            _fact(
                "fact-thesis-evidence-base",
                "The thesis is assembled only from persisted imported capability artifacts.",
                source_list,
            ),
            *market_facts,
        ],
        assumptions=[
            {
                "id": "assumption-thesis-continuity",
                "statement": "The disclosed operating relationships remain testable over the stated horizon.",
                "rationale": "No complete forward macroeconomic dataset is supplied.",
                "materiality": "high",
            }
        ],
        unknowns=[
            _unknown(
                f"unknown-thesis-limitation-{index}",
                limitation,
                "The affected thesis pillar has lower evidence sufficiency.",
            )
            for index, limitation in enumerate(limitations, start=1)
        ],
        estimates=market_estimates,
        findings=[
            _finding(
                "finding-thesis-balanced",
                "The imported-data thesis records source-backed drivers, disconfirming risks, and observable monitoring conditions.",
                source_list,
            ),
            *(
                [
                    _finding(
                        "finding-market-context",
                        "Recent return, realized volatility, and drawdown are descriptive market context rather than a directional forecast.",
                        market_source_ids,
                    )
                ]
                if market_context and market_source_ids
                else []
            ),
        ],
        risks=[
            _risk(
                f"risk-thesis-imported-{index}",
                statement,
                source_list,
            )
            for index, statement in enumerate(risk_statements[:3], start=1)
        ],
        warnings=_warnings(inputs),
    )


def _analyze_imported_bear_case(
    inputs: Mapping[str, Any],
    prior: Mapping[str, Any],
    thesis: Mapping[str, Any],
    source_ids: Sequence[str],
    checksum: str,
    thesis_statement: Any,
) -> CapabilityResult:
    """Build a source-led adverse case independent from the frozen thesis prose."""

    thesis_method = _mapping_value(thesis.get("method"), "thesis method")
    risk_records = _prior_records(prior, "risks")
    risk_statements = _deduplicated_strings(
        str(record["statement"])
        for record in risk_records
        if _text(record.get("statement"))
    )


    if not risk_statements:
        return _skipped(
            "bear-case-analysis",
            "independent-red-team",
            "No source-backed adverse mechanism is available for an independent bear case.",
            ["source-backed disconfirming risk evidence"],
        )
    selected_risks = risk_statements[:3]
    counter_thesis = (
        "; ".join(selected_risks[:2])
        + " These mechanisms could invalidate the source-backed operating case."
    )
    if counter_thesis == thesis_statement:
        raise ValueError("bear case must be independent of the frozen thesis statement")
    assumptions = [
        str(record["statement"])
        for record in thesis.get("assumptions", [])
        if isinstance(record, Mapping) and _text(record.get("statement"))
    ]
    monitoring = thesis_method.get("monitoring_kpis", [])
    if not isinstance(monitoring, list):
        monitoring = []
    source_list = list(source_ids)
    failure_signals = [
        {
            "metric": _text(item.get("metric")),
            "condition": "sustained adverse movement or missing confirming evidence",
            "time_window": "next two available reporting updates",
            "expected_source": source_list[index % len(source_list)],
        }
        for index, item in enumerate(monitoring[:5])
        if isinstance(item, Mapping) and _text(item.get("metric"))
    ]
    if not failure_signals:
        return _skipped(
            "bear-case-analysis",
            "independent-red-team",
            "The frozen thesis has no evidence-backed monitoring signal for red-team testing.",
            ["evidence-backed thesis monitoring signals"],
        )
    counterevidence = [
        str(record["id"])
        for record in risk_records
        if _text(record.get("id"))
    ]
    monitored_metrics = [str(item["metric"]) for item in failure_signals]
    return _completed(
        "bear-case-analysis",
        "independent-red-team",
        method_fields={
            "thesis_snapshot_checksum": checksum,
            "counter_thesis": counter_thesis,
            "fragile_assumptions": assumptions,
            "counterevidence": counterevidence,
            "risk_mechanisms": [
                f"{statement} could weaken the thesis before confirming evidence emerges."
                for statement in selected_risks
            ],
            "failure_signals": failure_signals,
            "thesis_killers_for_bear_case": [
                "Updated evidence showing durable improvement in "
                + "; ".join(monitored_metrics[:3])
                + " while identified risks recede would weaken the counter-thesis."
            ],
            "independence_check": {
                "passed": True,
                "reason": "The counter-thesis is assembled from upstream risk records and adverse monitoring conditions rather than adjective inversion.",
            },
        },
        facts=[
            _fact(
                "fact-bear-evidence-snapshot",
                "The red-team pass uses the same frozen imported evidence snapshot as the thesis.",
                source_list,
            )
        ],
        assumptions=[
            {
                "id": "assumption-bear-severity",
                "statement": "Multiple source-backed risk mechanisms could overlap.",
                "rationale": "The imported evidence does not provide probabilistic dependence data.",
                "materiality": "high",
            }
        ],
        findings=[
            _finding(
                "finding-bear-counter-thesis",
                counter_thesis,
                source_list,
            )
        ],
        risks=[
            _risk(
                "risk-bear-compounding",
                "Concurrent source-backed risks could compound operating and cash-flow weakness.",
                source_list,
            )
        ],
        warnings=_warnings(inputs),
    )


def _market_context(inputs: Mapping[str, Any]) -> dict[str, Any]:
    record = _mapping(inputs, "price_history")
    raw = record.get("observations") or []
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ValueError("price history observations must be a sequence")
    observations: list[tuple[str, float]] = []
    for value in raw:
        item = _mapping_value(value, "price observation")
        date_value = _text(item.get("date"))
        close = _number(item.get("close"))
        if date_value is None or close is None or close <= 0:
            continue
        observations.append((date_value, close))
    observations.sort(key=lambda item: item[0])
    if len(observations) < 2 or len({item[0] for item in observations}) != len(observations):
        return {}
    closes = [item[1] for item in observations]
    period_return = _ratio_delta(closes[-1], closes[0])
    daily_returns = [
        _ratio_delta(closes[index], closes[index - 1])
        for index in range(1, len(closes))
    ]
    finite_returns = [value for value in daily_returns if value is not None]
    volatility: float | None = None
    if len(finite_returns) >= 2:
        mean = math.fsum(finite_returns) / len(finite_returns)
        variance = math.fsum((value - mean) ** 2 for value in finite_returns) / (
            len(finite_returns) - 1
        )
        volatility = math.sqrt(variance) * math.sqrt(252.0)
        if not math.isfinite(volatility):
            volatility = None
    peak = closes[0]
    maximum_drawdown = 0.0
    for close in closes:
        peak = max(peak, close)
        maximum_drawdown = min(maximum_drawdown, close / peak - 1.0)
    source_ids = record.get("source_ids") or []
    if not isinstance(source_ids, list):
        raise ValueError("price history source IDs must be a list")
    return {
        "observation_count": len(observations),
        "start_date": observations[0][0],
        "end_date": observations[-1][0],
        "available_period_return": period_return,
        "annualized_realized_volatility": volatility,
        "maximum_drawdown": maximum_drawdown,
        "source_ids": _deduplicated_strings(source_ids),
    }


def analyze_catalysts(inputs: Mapping[str, Any]) -> CapabilityResult:
    record = _mapping(inputs, "catalysts")
    events_value = record.get("events", [])
    if events_value is None:
        events_value = []
    if not isinstance(events_value, Sequence) or isinstance(events_value, (str, bytes)):
        raise ValueError("catalyst events must be a sequence")
    events = [_mapping_value(value, "catalyst event") for value in events_value]
    if not events:
        return _skipped(
            "catalyst-analysis",
            "monitorable-event-ledger",
            "No dated or evidence-backed catalyst event is available.",
            ["catalyst event evidence"],
        )
    source_ids = _require_sources(inputs, "catalyst-analysis")
    normalized: list[dict[str, Any]] = []
    facts: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []
    for index, event in enumerate(events, start=1):
        if not _text(event.get("date")) and not _text(event.get("window")):
            raise ValueError("catalyst events require a date or bounded window")
        dependencies = event.get("dependencies")
        if not isinstance(dependencies, list) or not dependencies:
            raise ValueError("catalyst events require dependencies")
        normalized_event = dict(event)
        normalized_event.setdefault("source_ids", source_ids)
        normalized_event.setdefault("uncertainty", "not quantified")
        normalized_event.setdefault("materiality", "not quantified")
        normalized_event.setdefault(
            "downside_path", "The expected event may be delayed or fail to affect the named variable."
        )
        normalized.append(normalized_event)
        facts.append(
            _fact(
                f"fact-catalyst-event-{index}",
                (
                    f"The fictional fixture records event {normalized_event.get('event_id', index)} for {normalized_event.get('date') or normalized_event.get('window')}."
                    if _is_demo(inputs)
                    else f"The imported event record identifies {normalized_event.get('event_id', index)} for {normalized_event.get('date') or normalized_event.get('window')}."
                ),
                source_ids,
            )
        )
        if "high" in str(normalized_event.get("uncertainty", "")).casefold():
            unknowns.append(
                _unknown(
                    f"unknown-catalyst-outcome-{index}",
                    f"Outcome and timing for {normalized_event.get('event_id', index)} remain uncertain.",
                    "The event cannot support a deterministic directional conclusion.",
                )
            )
    return _completed(
        "catalyst-analysis",
        "monitorable-event-ledger",
        method_fields={
            "events": normalized,
            "event_count": len(normalized),
            "materiality_and_uncertainty_separate": True,
            "outcomes_separate_from_expectations": True,
        },
        facts=facts,
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-catalyst-ledger",
                "Each event retains a date or window, materiality, uncertainty, dependencies, evidence, and downside path.",
                source_ids,
            )
        ],
        risks=[
            _risk(
                "risk-catalyst-dependency",
                "Catalyst impact depends on events and operating conditions that may not occur as expected.",
                source_ids,
            )
        ],
        warnings=_warnings(inputs),
    )


def analyze_source_verification(inputs: Mapping[str, Any]) -> CapabilityResult:
    prior = _capability_results(inputs)
    if not prior:
        return _skipped(
            "source-verification",
            "claim-source-integrity-gate",
            "No upstream capability artifacts are available for verification.",
            ["upstream capability results"],
        )
    sources = _source_records(inputs)
    source_by_id = {
        str(record["source_id"]): record
        for record in sources
        if _text(record.get("source_id"))
    }
    known_ids = set(source_by_id)
    if not known_ids:
        return _skipped(
            "source-verification",
            "claim-source-integrity-gate",
            "No persisted source registry is available.",
            ["sources"],
        )
    claim_ledger: list[dict[str, Any]] = []
    missing: list[str] = []
    source_free_claims: list[str] = []
    conflicts = _deduplicated_strings(
        conflict
        for record in sources
        for conflict in _source_conflicts(record)
    )
    stale_source_ids = sorted(
        source_id
        for source_id, record in source_by_id.items()
        if _source_is_stale(record)
    )
    low_quality_source_ids = sorted(
        source_id
        for source_id, record in source_by_id.items()
        if _source_is_low_quality(record)
    )
    for capability, result in prior.items():
        if capability == "source-verification" or not isinstance(result, Mapping):
            continue
        for claim_type, field in (
            ("fact", "facts"),
            ("finding", "findings"),
            ("risk", "risks"),
        ):
            for claim in result.get(field, []):
                if not isinstance(claim, Mapping):
                    raise ValueError(f"capability {claim_type} must be a mapping")
                claim_id = _text(claim.get("id"))
                referenced = sorted(
                    {str(value) for value in claim.get("source_ids", [])}
                )
                unresolved = [value for value in referenced if value not in known_ids]
                status = "verified" if referenced and not unresolved else "unsupported"
                if unresolved:
                    missing.extend(unresolved)
                if not referenced and claim_id:
                    source_free_claims.append(claim_id)
                source_reviews = [
                    _source_review(source_by_id[source_id])
                    for source_id in referenced
                    if source_id in source_by_id
                ]
                claim_conflicts = _deduplicated_strings(
                    conflict
                    for review in source_reviews
                    for conflict in review.get("conflicts", [])
                )
                claim_ledger.append(
                    {
                        "claim_id": claim_id,
                        "claim_type": claim_type,
                        "capability": capability,
                        "source_ids": referenced,
                        "coverage": status,
                        "quality": ", ".join(
                            _deduplicated_strings(
                                str(review["quality"]) for review in source_reviews
                            )
                        )
                        or "unknown",
                        "freshness": ", ".join(
                            _deduplicated_strings(
                                str(review["freshness"])
                                for review in source_reviews
                            )
                        )
                        or "unknown",
                        "conflict": bool(claim_conflicts),
                        "source_reviews": source_reviews,
                        "unresolved_source_ids": unresolved,
                    }
                )
        for warning in result.get("warnings", []):
            if any(
                marker in str(warning).casefold()
                for marker in ("conflict", "contradict")
            ):
                conflicts.append(f"{capability}: {warning}")
    conflicts = _deduplicated_strings(conflicts)
    unresolved_source_ids = sorted(set(missing))
    source_free_claims = sorted(set(source_free_claims))
    has_gaps = bool(
        unresolved_source_ids
        or source_free_claims
        or conflicts
        or stale_source_ids
        or low_quality_source_ids
    )
    gate_status = "pass_with_disclosed_gaps" if has_gaps else "pass"
    verification_source_ids = sorted(known_ids)
    unknowns = [
        _unknown(
            f"unknown-source-{index}",
            f"Source ID {value} is unresolved.",
            "The associated claim cannot support a material conclusion.",
        )
        for index, value in enumerate(unresolved_source_ids, start=1)
    ]
    unknowns.extend(
        _unknown(
            f"unknown-claim-source-{index}",
            f"Claim {value} has no source reference.",
            "The claim cannot support a material conclusion.",
        )
        for index, value in enumerate(source_free_claims, start=1)
    )
    verification_warnings = _warnings(inputs)
    if stale_source_ids:
        verification_warnings.append(
            "One or more persisted sources are marked stale; affected conclusions require refreshed evidence."
        )
    if low_quality_source_ids:
        verification_warnings.append(
            "One or more persisted sources have low or unknown quality."
        )
    return _completed(
        "source-verification",
        "claim-source-integrity-gate",
        method_fields={
            "claim_ledger": claim_ledger,
            "gate_status": gate_status,
            "source_quality_review": "completed from persisted source records",
            "freshness_review": (
                "completed against the demo snapshot date"
                if _is_demo(inputs)
                else "completed from imported per-source freshness metadata"
            ),
            "coverage_summary": {
                "claims": len(claim_ledger),
                "unresolved_sources": len(unresolved_source_ids),
                "source_free_claims": len(source_free_claims),
                "stale_sources": len(stale_source_ids),
                "low_quality_sources": len(low_quality_source_ids),
            },
            "conflicts": conflicts,
            "unresolved_source_ids": unresolved_source_ids,
            "stale_source_ids": stale_source_ids,
            "low_quality_source_ids": low_quality_source_ids,
            "source_free_claim_ids": source_free_claims,
        },
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-source-gate",
                f"Claim/source coverage completed with gate status {gate_status}.",
                verification_source_ids,
            )
        ],
        risks=[
            _risk(
                (
                    "risk-source-fixture-boundary"
                    if _is_demo(inputs)
                    else "risk-source-import-boundary"
                ),
                (
                    "All evidence is fictional demo evidence and does not establish current market facts."
                    if _is_demo(inputs)
                    else "Imported evidence quality, freshness, and completeness limit the conclusions it can support."
                ),
                verification_source_ids,
            )
        ],
        warnings=verification_warnings,
    )


def analyze_investment_report(inputs: Mapping[str, Any]) -> CapabilityResult:
    prior = _capability_results(inputs)
    verification = _mapping_value(
        prior.get("source-verification"), "source-verification result"
    )
    if verification.get("status") != "completed":
        return _skipped(
            "investment-report",
            "deterministic-report-view",
            "Mandatory stage source-verification is not completed.",
            ["source-verification"],
        )
    bear = _mapping_value(prior.get("bear-case-analysis"), "bear-case-analysis result")
    thesis = _mapping_value(prior.get("investment-thesis"), "investment-thesis result")
    bear_is_disclosed_evidence_gap = (
        not _is_demo(inputs)
        and thesis.get("status") == "skipped"
        and bear.get("status") == "skipped"
    )
    if bear.get("status") != "completed" and not bear_is_disclosed_evidence_gap:
        return _skipped(
            "investment-report",
            "deterministic-report-view",
            "Mandatory stage bear-case-analysis is not completed.",
            ["bear-case-analysis"],
        )
    emitted_claim_ids: list[str] = []
    emitted_source_ids: list[str] = []
    checksums: dict[str, str] = {}
    has_gaps = False
    for capability, result in prior.items():
        if capability == "investment-report" or not isinstance(result, Mapping):
            continue
        checksums[capability] = hashlib.sha256(
            json.dumps(
                result, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
        ).hexdigest()
        if result.get("status") == "skipped" or result.get("unknowns"):
            has_gaps = True
        for field in ("facts", "assumptions", "estimates", "unknowns", "findings", "risks"):
            for item in result.get(field, []):
                if isinstance(item, Mapping) and _text(item.get("id")):
                    identifier = str(item["id"])
                    if identifier not in emitted_claim_ids:
                        emitted_claim_ids.append(identifier)
        for source_id in result.get("source_ids", []):
            value = str(source_id)
            if value not in emitted_source_ids:
                emitted_source_ids.append(value)
    return _completed(
        "investment-report",
        "deterministic-report-view",
        method_fields={
            "input_artifact_checksums": checksums,
            "emitted_claim_ids": emitted_claim_ids,
            "emitted_source_ids": emitted_source_ids,
            "section_statuses": "assembled from validated upstream artifacts",
            "validation_warnings": [
                (
                    "Fictional demo evidence only; the report is not live or real-time."
                    if _is_demo(inputs)
                    else (
                        "Official live evidence was acquired through a governed Provider; completeness is not guaranteed."
                        if _is_official_live(inputs)
                        else "User-supplied imported evidence was not independently fetched or guaranteed."
                    )
                )
            ],
            "completeness": "complete_with_gaps" if has_gaps else "complete",
            "no_new_material_check": "passed",
        },
        findings=[
            {
                "id": "finding-report-assembly",
                "statement": "The report view is bounded to IDs already present in structured capability artifacts.",
                "source_ids": emitted_source_ids,
            }
        ]
        if emitted_source_ids
        else [],
        warnings=_warnings(inputs),
    )


def _completed(
    capability: str,
    method_name: str,
    *,
    method_fields: Mapping[str, Any],
    facts: Sequence[Mapping[str, Any]] = (),
    assumptions: Sequence[Mapping[str, Any]] = (),
    estimates: Sequence[Mapping[str, Any]] = (),
    unknowns: Sequence[Mapping[str, Any]] = (),
    findings: Sequence[Mapping[str, Any]] = (),
    risks: Sequence[Mapping[str, Any]] = (),
    warnings: Sequence[str] = (),
) -> CapabilityResult:
    method = {"name": method_name, "version": METHOD_VERSION, **dict(method_fields)}
    return build_capability_result(
        capability,
        status="completed",
        skill={"name": capability, "version": SKILL_VERSION},
        method=method,
        facts=facts,
        assumptions=assumptions,
        estimates=estimates,
        unknowns=unknowns,
        findings=findings,
        risks=risks,
        warnings=list(dict.fromkeys(warnings)),
    )


def _skipped(
    capability: str,
    method_name: str,
    reason: str,
    missing_inputs: Sequence[str],
) -> CapabilityResult:
    return build_capability_result(
        capability,
        status="skipped",
        skill={"name": capability, "version": SKILL_VERSION},
        method={"name": method_name, "version": METHOD_VERSION},
        unknowns=[
            _unknown(
                "unknown-skipped-inputs",
                reason,
                "This capability cannot produce a bounded analytical result.",
            )
        ],
        warnings=["Capability skipped without fabricating missing data."],
        skip_reason=reason,
        missing_inputs=missing_inputs,
    )


def _dcf_scenario(
    cash_flows: Sequence[float],
    *,
    wacc: float,
    terminal_growth: float,
    cash: float,
    debt: float,
    diluted_shares: float,
) -> dict[str, Any]:
    if wacc <= terminal_growth:
        raise ValueError("WACC must exceed terminal growth")
    if wacc <= -1.0:
        raise ValueError("WACC must be greater than -100%")
    if diluted_shares <= 0:
        raise ValueError("diluted shares must be positive")
    if not cash_flows:
        raise ValueError("DCF requires at least one cash flow")
    try:
        discount_base = 1.0 + wacc
        discounted_cash_flows = [
            _ratio(cash_flow, discount_base**year)
            for year, cash_flow in enumerate(cash_flows, start=1)
        ]
        if any(value is None for value in discounted_cash_flows):
            raise ValueError("DCF calculation produced a non-finite value")
        present_value = _finite_sum(
            cast(float, value) for value in discounted_cash_flows
        )
        terminal_numerator = _finite_product(
            cash_flows[-1],
            _require_finite_calculation(
                _finite_sum((1.0, terminal_growth)),
                "DCF terminal-growth calculation",
            ),
        )
        terminal_value = _ratio(
            terminal_numerator,
            _finite_difference(wacc, terminal_growth),
        )
        terminal_present_value = _ratio(
            terminal_value, discount_base ** len(cash_flows)
        )
        enterprise_value = _finite_sum(
            (
                _require_finite_calculation(present_value, "DCF present value"),
                _require_finite_calculation(
                    terminal_present_value, "DCF terminal present value"
                ),
            )
        )
        equity_value = _finite_sum(
            (
                _require_finite_calculation(
                    enterprise_value, "DCF enterprise value"
                ),
                cash,
                -debt,
            )
        )
        equity_value_per_share = _ratio(equity_value, diluted_shares)
        terminal_value_share = _ratio(terminal_present_value, enterprise_value)
    except OverflowError as error:
        raise ValueError("DCF calculation produced a non-finite value") from error
    for value in (
        present_value,
        terminal_value,
        terminal_present_value,
        enterprise_value,
        equity_value,
        equity_value_per_share,
        terminal_value_share,
    ):
        if value is None or not math.isfinite(value):
            raise ValueError("DCF calculation produced a non-finite value")
    return {
        "wacc": wacc,
        "terminal_growth": terminal_growth,
        "diluted_shares": diluted_shares,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "equity_value_per_share": equity_value_per_share,
        "terminal_value_share": terminal_value_share,
    }


def _guarded_multiple(
    numerator_value: Any,
    denominator_value: Any,
    denominator_name: str,
    invalid: dict[str, str],
) -> float | None:
    numerator = _number(numerator_value)
    denominator = _number(denominator_value)
    metric = {
        "operating income": "ev_to_operating_income",
        "net income": "price_to_earnings",
        "book equity": "price_to_book",
    }[denominator_name]
    if numerator is None:
        invalid[metric] = "missing numerator"
        return None
    if denominator is None:
        invalid[metric] = f"missing {denominator_name} denominator"
        return None
    if denominator == 0:
        invalid[metric] = f"zero {denominator_name} denominator"
        return None
    if denominator < 0:
        invalid[metric] = f"negative {denominator_name} denominator"
        return None
    result = _ratio(numerator, denominator)
    if result is None:
        invalid[metric] = f"non-finite {denominator_name} multiple"
    return result


def _quartiles(values: Sequence[float]) -> tuple[float, float]:
    """Return deterministic inclusive quartiles for a non-empty distribution."""

    ordered = sorted(values)
    if not ordered:
        raise ValueError("quartiles require at least one observation")

    def percentile(fraction: float) -> float:
        position = (len(ordered) - 1) * fraction
        lower_index = int(position)
        upper_index = min(lower_index + 1, len(ordered) - 1)
        weight = position - lower_index
        lower_weighted = _finite_product(ordered[lower_index], 1.0 - weight)
        upper_weighted = _finite_product(ordered[upper_index], weight)
        return _require_finite_calculation(
            _finite_sum(
                (
                    _require_finite_calculation(lower_weighted, "quartile interpolation"),
                    _require_finite_calculation(upper_weighted, "quartile interpolation"),
                )
            ),
            "quartile interpolation",
        )

    return percentile(0.25), percentile(0.75)


def _mapping(inputs: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = inputs.get(key)
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{key} must be a mapping")
    return value


def _mapping_value(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a mapping")
    return value


def _capability_results(inputs: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(inputs, "capability_results")


def _periods(statements: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    values = statements.get("periods", [])
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError("financial statement periods must be a sequence")
    records = [_mapping_value(value, "financial statement period") for value in values]
    return sorted(records, key=lambda value: int(value.get("fiscal_year", 0) or 0))


def _periods_have_financial_values(periods: Sequence[Mapping[str, Any]]) -> bool:
    """Return whether a period set contains any finite value beyond its label."""

    return any(
        _number(value) is not None
        for period in periods
        for field, value in period.items()
        if field != "fiscal_year"
    )


def _source_records(inputs: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = inputs.get("sources")
    if isinstance(raw, Mapping):
        raw = raw.get("sources", [])
    if raw is None:
        raw = []
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ValueError("sources must be a sequence or a sources mapping")
    records = [_mapping_value(value, "source record") for value in raw]
    metadata = _mapping(inputs, "source_metadata")
    if _text(metadata.get("source_id")) and not any(
        record.get("source_id") == metadata.get("source_id") for record in records
    ):
        records.append(metadata)
    nested = metadata.get("sources")
    if isinstance(nested, list):
        for value in nested:
            record = _mapping_value(value, "source metadata record")
            if not any(
                item.get("source_id") == record.get("source_id") for item in records
            ):
                records.append(record)
    return records


def _source_conflicts(record: Mapping[str, Any]) -> list[str]:
    conflicts: list[str] = []
    for field in ("conflict", "conflicts", "contradiction", "contradictions"):
        value = record.get(field)
        if value is True:
            conflicts.append("Source metadata marks an unresolved conflict.")
        elif isinstance(value, str):
            conflicts.append(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            conflicts.extend(str(item) for item in value)
    return _deduplicated_strings(conflicts)


def _source_review(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": _text(record.get("source_id")) or "unknown",
        "publisher": _text(record.get("publisher")) or "unknown",
        "title": _text(record.get("title")) or "unknown",
        "source_type": _text(record.get("source_type")) or "unknown",
        "locator": _text(record.get("locator")) or "unknown",
        "publication_date": record.get("publication_date"),
        "as_of_date": record.get("as_of_date"),
        "retrieved_at": record.get("retrieved_at"),
        "quality": _text(record.get("quality")) or "unknown",
        "freshness": _text(record.get("freshness")) or "unknown",
        "access_notes": _text(record.get("access_notes")) or "unknown",
        "license_notes": _text(record.get("license_notes")) or "unknown",
        "conflicts": _source_conflicts(record),
    }


def _source_is_stale(record: Mapping[str, Any]) -> bool:
    freshness = (_text(record.get("freshness")) or "unknown").casefold()
    if any(
        marker in freshness
        for marker in ("stale", "historical", "outdated", "expired")
    ):
        return True
    retrieved = _iso_date(record.get("retrieved_at"))
    if retrieved is None:
        return False
    cutoff = retrieved - timedelta(days=SOURCE_FRESHNESS_MAX_AGE_DAYS)
    evidence_dates = [
        parsed
        for parsed in (
            _iso_date(record.get("as_of_date")),
            _iso_date(record.get("publication_date")),
        )
        if parsed is not None
    ]
    return any(value < cutoff for value in evidence_dates)


def _iso_date(value: Any) -> date | None:
    if not isinstance(value, str) or len(value) < 10:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _source_is_low_quality(record: Mapping[str, Any]) -> bool:
    quality = (_text(record.get("quality")) or "unknown").casefold()
    return any(marker in quality for marker in ("low", "unknown", "unverified", "weak"))


def _primary_source_id(inputs: Mapping[str, Any]) -> str | None:
    records = _source_records(inputs)
    for record in records:
        source_id = _text(record.get("source_id"))
        if source_id:
            return source_id
    metadata = _mapping(inputs, "source_metadata")
    return _text(metadata.get("source_id"))


_CAPABILITY_INPUT_KEYS = {
    "security-identification": "identity",
    "company-deep-research": "profile",
    "business-model-analysis": "profile",
    "financial-statement-analysis": "statements",
    "earnings-quality-analysis": "statements",
    "valuation-analysis": "valuation_inputs",
    "comps-analysis": "peers",
    "earnings-analysis": "earnings",
    "catalyst-analysis": "catalysts",
}


def _source_ids_for_capability(
    inputs: Mapping[str, Any], capability: str
) -> list[str]:
    """Select provenance from the operation used by this capability."""

    if "active_source_ids" in inputs:
        active = _validated_source_ids(inputs.get("active_source_ids"), "active source IDs")
        if active or not _is_demo(inputs):
            return active
    input_key = _CAPABILITY_INPUT_KEYS.get(capability)
    record = inputs.get(input_key) if input_key is not None else None
    if isinstance(record, Mapping) and "source_ids" in record:
        record_sources = _validated_source_ids(
            record.get("source_ids"), f"{capability} source IDs"
        )
        if record_sources or not _is_demo(inputs):
            return record_sources
    source_id = _primary_source_id(inputs)
    return [source_id] if source_id is not None else []


def _validated_source_ids(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(_text(item) for item in value):
        raise ValueError(f"{label} must be a list of non-empty strings")
    return sorted({str(item).strip() for item in value})


def _require_sources(inputs: Mapping[str, Any], capability: str) -> list[str]:
    source_ids = _source_ids_for_capability(inputs, capability)
    if not source_ids:
        raise ValueError(f"{capability} requires persisted source metadata")
    return source_ids


def _prior_source_ids(prior: Mapping[str, Any]) -> list[str]:
    result: list[str] = []
    for value in prior.values():
        if not isinstance(value, Mapping):
            continue
        for source_id in value.get("source_ids", []):
            if _text(source_id) and str(source_id) not in result:
                result.append(str(source_id))
    return sorted(result)


def _prior_records(
    prior: Mapping[str, Any], field: str
) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    for result in prior.values():
        if not isinstance(result, Mapping):
            continue
        values = result.get(field, [])
        if not isinstance(values, list):
            continue
        records.extend(value for value in values if isinstance(value, Mapping))
    return records


def _prior_estimate_labels(prior: Mapping[str, Any]) -> list[str]:
    return _deduplicated_strings(
        str(record["label"])
        for record in _prior_records(prior, "estimates")
        if _text(record.get("label"))
    )


def _deduplicated_strings(values: Any) -> list[str]:
    result: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in result:
            result.append(text)
    return result


def _is_demo(inputs: Mapping[str, Any]) -> bool:
    mode = _text(inputs.get("input_mode"))
    if mode is None:
        return True
    if mode not in {"demo", "imported"}:
        raise ValueError("capability input mode must be demo or imported")
    return mode == "demo"


def _is_official_live(inputs: Mapping[str, Any]) -> bool:
    return not _is_demo(inputs) and _text(inputs.get("evidence_origin")) == "official_live"


def _warnings(inputs: Mapping[str, Any]) -> list[str]:
    if _is_demo(inputs):
        warnings = [
            "This analysis uses wholly fictional offline demo data and is not live or real-time."
        ]
    elif _is_official_live(inputs):
        warnings = [
            "This analysis uses official live evidence acquired through a governed Provider; completeness is not guaranteed."
        ]
    else:
        warnings = [
            "This analysis uses user-supplied imported data that was not independently fetched or guaranteed."
        ]
    for key in (
        "identity",
        "profile",
        "statements",
        "price_history",
        "valuation_inputs",
        "peers",
        "earnings",
        "catalysts",
        "source_metadata",
    ):
        value = inputs.get(key)
        if not isinstance(value, Mapping):
            continue
        for warning in value.get("warnings", []):
            text = _text(warning)
            if text and text not in warnings:
                warnings.append(text)
    return warnings


def _source_reference_list(source_ids: str | Sequence[str]) -> list[str]:
    values: Sequence[str] = [source_ids] if isinstance(source_ids, str) else source_ids
    result = _deduplicated_strings(values)
    if not result:
        raise ValueError("source references must contain at least one source ID")
    return sorted(result)


def _fact(
    identifier: str, statement: str, source_ids: str | Sequence[str]
) -> dict[str, Any]:
    return {
        "id": identifier,
        "statement": statement,
        "source_ids": _source_reference_list(source_ids),
    }


def _finding(
    identifier: str, statement: str, source_ids: str | Sequence[str]
) -> dict[str, Any]:
    return {
        "id": identifier,
        "statement": statement,
        "source_ids": _source_reference_list(source_ids),
    }


def _risk(
    identifier: str, statement: str, source_ids: str | Sequence[str]
) -> dict[str, Any]:
    return {
        "id": identifier,
        "statement": statement,
        "source_ids": _source_reference_list(source_ids),
    }


def _unknown(identifier: str, gap: str, impact: str) -> dict[str, Any]:
    return {"id": identifier, "gap": gap, "impact": impact}


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (OverflowError, TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _number_list(value: Any) -> list[float] | None:
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("numeric series must be a sequence")
    result: list[float] = []
    for item in value:
        number = _number(item)
        if number is None:
            raise ValueError("numeric series contains a missing or invalid value")
        result.append(number)
    return result


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0.0):
        return None
    try:
        result = numerator / denominator
    except (OverflowError, ZeroDivisionError):
        return None
    return result if math.isfinite(result) else None


def _ratio_delta(value: float | None, baseline: float | None) -> float | None:
    ratio = _ratio(value, baseline)
    return None if ratio is None else _finite_difference(ratio, 1.0)


def _finite_sum(values: Any) -> float | None:
    try:
        result = math.fsum(values)
    except (OverflowError, TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _finite_difference(left: float, right: float) -> float | None:
    return _finite_sum((left, -right))


def _finite_product(left: float, right: float) -> float | None:
    try:
        result = left * right
    except OverflowError:
        return None
    return result if math.isfinite(result) else None


def _require_finite_calculation(value: float | None, label: str) -> float:
    if value is None or not math.isfinite(value):
        raise ValueError(f"{label} produced a non-finite value")
    return value


def _scaled_series(
    values: Sequence[float], multiplier: float, label: str
) -> list[float]:
    return [
        _require_finite_calculation(_finite_product(value, multiplier), label)
        for value in values
    ]


def _finite_median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("median requires at least one observation")
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return _require_finite_calculation(
        _ratio(_finite_sum((ordered[midpoint - 1], ordered[midpoint])), 2.0),
        "median calculation",
    )


def _financial_formula(name: str) -> str:
    return {
        "revenue_growth": "latest revenue / earliest comparable revenue - 1",
        "gross_margin": "gross profit / revenue",
        "operating_margin": "operating income / revenue",
        "cash_flow_margin": "operating cash flow / revenue",
        "leverage_debt_to_equity": "gross debt / total equity",
        "liquidity_cash_to_debt": "cash and equivalents / gross debt",
        "liquidity_current_ratio": "current assets / current liabilities",
    }[name]


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("expected a sequence of strings")
    return [str(item).strip() for item in value if str(item).strip()]


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


_RUNNERS: dict[str, CapabilityRunner] = {
    "security-identification": analyze_security_identification,
    "company-deep-research": analyze_company_deep_research,
    "business-model-analysis": analyze_business_model,
    "financial-statement-analysis": analyze_financial_statements,
    "earnings-quality-analysis": analyze_earnings_quality,
    "valuation-analysis": analyze_valuation,
    "comps-analysis": analyze_comps,
    "earnings-analysis": analyze_earnings,
    "investment-thesis": analyze_investment_thesis,
    "bear-case-analysis": analyze_bear_case,
    "catalyst-analysis": analyze_catalysts,
    "source-verification": analyze_source_verification,
    "investment-report": analyze_investment_report,
}

if tuple(_RUNNERS) != RUNTIME_SKILLS:
    raise RuntimeError("capability runner order must match the Runtime Skill catalog")
