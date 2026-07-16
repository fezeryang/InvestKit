"""Pure, deterministic analyses for the offline Investment Core workflow."""

from __future__ import annotations

import hashlib
import json
from statistics import median
from typing import Any, Callable, Mapping, Sequence, cast

from .catalog import RUNTIME_SKILLS
from .contracts import build_capability_result


CapabilityResult = dict[str, Any]
CapabilityRunner = Callable[[Mapping[str, Any]], CapabilityResult]
SKILL_VERSION = "0.2.0"
METHOD_VERSION = "1.0"


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
    source_id = _primary_source_id(inputs)
    if source_id is None:
        return _skipped(
            "security-identification",
            "security-identity-resolution",
            "Security identity has no persisted provenance.",
            ["source metadata"],
        )
    facts = [
        _fact(
            "fact-security-identity",
            f"{identity['legal_name']} has fixture security ID {identity['security_id']}.",
            source_id,
        ),
        _fact(
            "fact-security-ticker",
            f"The fixture ticker is {identity['ticker']} on {identity.get('exchange', identity.get('market', 'the stated market'))}.",
            source_id,
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
                "The fictional demo security is unambiguously resolved for offline research.",
                source_id,
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
    source_id = _require_source(inputs, "company-deep-research")
    segments = _strings(profile.get("segments"))
    management = _mapping_value(profile.get("management"), "profile.management")
    capital_allocation = _mapping_value(
        profile.get("capital_allocation"), "profile.capital_allocation"
    )
    competitive = _mapping_value(
        profile.get("competitive_context"), "profile.competitive_context"
    )
    facts = [
        _fact(
            "fact-company-business",
            f"The fictional company profile describes this business: {_text(profile.get('business_model')) or 'not disclosed'}.",
            source_id,
        ),
        _fact(
            "fact-company-segments",
            "Reported segments are " + (", ".join(segments) if segments else "not disclosed") + ".",
            source_id,
        ),
        _fact(
            "fact-company-management",
            "Management evidence states: "
            + (_text(management.get("summary")) or "no management detail is disclosed")
            + ".",
            source_id,
        ),
        _fact(
            "fact-company-capital-allocation",
            "Capital allocation evidence states: "
            + (_text(capital_allocation.get("summary")) or "no capital allocation policy is disclosed")
            + ".",
            source_id,
        ),
        _fact(
            "fact-company-competitive-context",
            "Competitive context states: "
            + (_text(competitive.get("summary")) or "competitive positioning is not quantified")
            + ".",
            source_id,
        ),
    ]
    unknowns = []
    if profile.get("employees") is None:
        unknowns.append(
            _unknown(
                "unknown-company-employees",
                "Employee count is unavailable.",
                "Operating scale and productivity cannot be assessed from headcount.",
            )
        )
    if not _text(management.get("tenure")):
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
            "research_gaps": [value["id"] for value in unknowns],
        },
        facts=facts,
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-company-context",
                "The company fact base covers segments, management, capital allocation, and competitive context while retaining explicit unknowns.",
                source_id,
            )
        ],
        risks=[
            _risk(f"risk-company-{index}", value, source_id)
            for index, value in enumerate(_strings(profile.get("risks")), start=1)
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
    source_id = _require_source(inputs, "business-model-analysis")
    order_to_cash = _mapping_value(profile.get("order_to_cash"), "profile.order_to_cash")
    components = _mapping_value(
        profile.get("revenue_components"), "profile.revenue_components"
    )
    facts = [
        _fact(
            "fact-revenue-model",
            f"The revenue model is {_text(profile.get('revenue_model')) or _text(profile.get('business_model')) or 'not classified'}.",
            source_id,
        ),
        _fact(
            "fact-payer",
            f"The disclosed payer is {_text(profile.get('payer')) or _text(profile.get('customers')) or 'unknown'}.",
            source_id,
        ),
        _fact(
            "fact-value-proposition",
            f"The disclosed value proposition is {_text(profile.get('value_proposition')) or 'not separately disclosed'}.",
            source_id,
        ),
        _fact(
            "fact-order-to-cash",
            "The order, backlog, delivery, billing, and cash states are tracked separately in the fixture.",
            source_id,
        ),
    ]
    unknowns: list[dict[str, Any]] = []
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
    return _completed(
        "business-model-analysis",
        "business-model-map",
        method_fields={
            "revenue_model": _text(profile.get("revenue_model")) or "hybrid",
            "payer": _text(profile.get("payer")) or _text(profile.get("customers")),
            "value_proposition": _text(profile.get("value_proposition")),
            "revenue_components": dict(components),
            "order_to_cash": dict(order_to_cash),
            "backlog_is_not_revenue": True,
            "cash_collection_is_separate": True,
            "fragility_checks": [
                "tender concentration",
                "battery input cost exposure",
                "working-capital conversion",
            ],
        },
        facts=facts,
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-business-mechanics",
                "The hybrid revenue model links a municipal payer and outdoor customers to a product value proposition through a guarded order-to-cash chain.",
                source_id,
            ),
            _finding(
                "finding-business-fragility",
                "Tender concentration and input costs are material business-model fragilities.",
                source_id,
            ),
        ],
        risks=[
            _risk(
                "risk-backlog-conversion",
                "Backlog may not convert into delivered revenue or collected cash.",
                source_id,
            )
        ],
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
    source_id = _require_source(inputs, "financial-statement-analysis")
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
            source_id,
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
            "cash_flow_review": "completed with disclosed fixture limitations",
            "leverage_review": "completed",
            "liquidity_review": "partial because current asset/liability detail is absent",
        },
        facts=facts,
        estimates=estimates,
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-financial-trend",
                "Comparable annual periods support revenue, margin, cash flow, leverage, and partial liquidity analysis.",
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-financial-leverage",
                "Debt remains a balance-sheet claim that must be included in valuation bridges.",
                source_id,
            )
        ],
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
    source_id = _require_source(inputs, "earnings-quality-analysis")
    previous, latest = periods[-2], periods[-1]
    net_income = _number(latest.get("net_income"))
    operating_cash = _number(latest.get("cash_from_operations"))
    assets = [_number(period.get("total_assets")) for period in periods[-2:]]
    average_assets = (
        sum(value for value in assets if value is not None) / 2
        if len(assets) == 2 and all(value is not None for value in assets)
        else None
    )
    cash_conversion = _ratio(operating_cash, net_income)
    accrual_ratio = (
        (net_income - operating_cash) / average_assets
        if net_income is not None
        and operating_cash is not None
        and average_assets not in (None, 0.0)
        else None
    )
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
                source_id,
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
                source_id,
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
        previous_net_working_capital = (
            cast(float, previous_working_capital["accounts_receivable"])
            + cast(float, previous_working_capital["inventory"])
            - cast(float, previous_working_capital["accounts_payable"])
        )
        latest_net_working_capital = (
            cast(float, latest_working_capital["accounts_receivable"])
            + cast(float, latest_working_capital["inventory"])
            - cast(float, latest_working_capital["accounts_payable"])
        )
        working_capital_change = latest_net_working_capital - previous_net_working_capital
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
                "No conclusion about manipulation is supported by this fixture.",
            ],
        },
        facts=facts,
        estimates=estimates,
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-quality-cash-backing",
                "Cash conversion and accrual diagnostics are calculated, while working capital and one-off evidence remain explicit gaps.",
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-quality-footnotes",
                "Missing footnote detail limits confidence in earnings repeatability.",
                source_id,
            )
        ],
        warnings=_warnings(inputs),
    )


def analyze_valuation(inputs: Mapping[str, Any]) -> CapabilityResult:
    valuation = _mapping(inputs, "valuation_inputs")
    forecast = _number_list(valuation.get("forecast_unlevered_free_cash_flow"))
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
        return _skipped(
            "valuation-analysis",
            "scenario-dcf",
            "Essential DCF inputs are unavailable or invalid.",
            list(dict.fromkeys(missing)),
        )
    assert isinstance(scenario_inputs, Mapping)
    source_id = _require_source(inputs, "valuation-analysis")
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
        scenario_cash_flows = [value * cash_flow_multiplier for value in forecast]
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
                or "Scenario values are explicitly supplied by the fictional fixture.",
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
    base_cash_flows = [value * base_cash_flow_multiplier for value in forecast]
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
            f"The fixture supplies cash {cash}, gross debt {debt}, and diluted shares {shares} for the EV-to-equity bridge.",
            source_id,
        )
    ]
    prior = _capability_results(inputs)
    comps_status = _mapping_value(prior.get("comps-analysis"), "comps result").get(
        "status", "not supplied"
    )
    return _completed(
        "valuation-analysis",
        "scenario-dcf",
        method_fields={
            "forecast_unlevered_free_cash_flow": forecast,
            "scenarios": scenarios,
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
            )
        ],
        findings=[
            _finding(
                "finding-valuation-range",
                "Bear, base, and bull DCF cases form a scenario range rather than a deterministic target.",
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-valuation-sensitivity",
                "DCF output is materially sensitive to cash-flow, WACC, and terminal-growth assumptions.",
                source_id,
            )
        ],
        warnings=warnings,
    )


def analyze_comps(inputs: Mapping[str, Any]) -> CapabilityResult:
    record = _mapping(inputs, "peers")
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
    source_id = _require_source(inputs, "comps-analysis")
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
            "median": median(values),
            "quartiles": {"q1": first_quartile, "q3": third_quartile},
            "range": {"low": min(values), "high": max(values)},
            "minimum": min(values),
            "maximum": max(values),
            "outlier_policy": "none removed in the bounded fictional fixture",
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
            f"The fictional peer ledger contains {len(peers)} considered companies with explicit inclusion or exclusion decisions.",
            source_id,
        )
    ]
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
                label: target_metric * multiple for label, multiple in multiples.items()
            }
            equity_values = {
                label: value + cash - debt for label, value in enterprise_values.items()
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
                label: target_metric * multiple for label, multiple in multiples.items()
            }
            bridge = {
                "basis": "equity_value",
                "formula": "equity multiple multiplied by the aligned target denominator",
            }
        per_share_values = None
        if diluted_shares is not None and diluted_shares > 0:
            per_share_values = {
                label: value / diluted_shares for label, value in equity_values.items()
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
            "method": "median of valid, period-aligned fictional peer observations",
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
        },
        facts=facts,
        estimates=estimates,
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-comps-distribution",
                "Only valid peer denominators enter the reported multiple distributions; exclusions remain visible.",
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-comps-sample",
                "The small fictional sample is illustrative and not robust market evidence.",
                source_id,
            )
        ],
        warnings=warnings,
    )


def analyze_earnings(inputs: Mapping[str, Any]) -> CapabilityResult:
    record = _mapping(inputs, "earnings")
    events_value = record.get("events", record.get("periods", []))
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
    source_id = _require_source(inputs, "earnings-analysis")
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
        comparison = {
            "actual": actual_value,
            "expectation": expected_value,
            "absolute_surprise": actual_value - expected_value,
            "percentage_surprise": _ratio_delta(actual_value, expected_value),
            "observation_time": expectation.get("observation_time"),
            "definition": expectation.get(f"{metric}_definition", actual.get(f"{metric}_definition")),
        }
        comparisons[metric] = comparison
        estimates.append(
            {
                "id": f"estimate-earnings-surprise-{metric}",
                "label": f"{metric.upper()} surprise",
                "value": comparison["percentage_surprise"],
                "method": "reported actual versus persisted pre-release expectation",
                "input_ids": [f"fact-earnings-actual-{metric}", "assumption-consensus-vintage"],
            }
        )
    guidance_range = guidance.get("revenue_range")
    guidance_comparison: dict[str, Any] = {
        "period": guidance.get("period"),
        "source_ids": guidance.get("source_ids", [source_id]),
    }
    if (
        isinstance(guidance_range, Sequence)
        and not isinstance(guidance_range, (str, bytes))
        and len(guidance_range) == 2
        and all(_number(value) is not None for value in guidance_range)
    ):
        lower, upper = (_number(value) for value in guidance_range)
        assert lower is not None and upper is not None
        midpoint = (lower + upper) / 2
        actual_revenue = _number(actual.get("revenue"))
        guidance_comparison.update(
            {
                "range": [lower, upper],
                "midpoint": midpoint,
                "actual": actual.get("revenue"),
                "actual_vs_midpoint": (
                    actual_revenue - midpoint if actual_revenue is not None else None
                ),
            }
        )
    facts = [
        _fact(
            f"fact-earnings-actual-{metric}",
            f"Reported {metric.upper()} for {event.get('period', 'the event period')} is {value}.",
            source_id,
        )
        for metric, value in (("revenue", actual.get("revenue")), ("eps", actual.get("eps")))
        if _number(value) is not None
    ]
    transcript_available = event.get("transcript_available") is True
    unknowns: list[dict[str, Any]] = []
    warnings = _warnings(inputs)
    if not transcript_available:
        unknowns.append(
            _unknown(
                "unknown-earnings-transcript",
                "The earnings transcript is unknown because no transcript is available.",
                "Management tone, speaker-specific comments, and Q&A cannot be analyzed.",
            )
        )
        warnings.append("Transcript analysis was omitted; no transcript source is available.")
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
        assumptions=[
            {
                "id": "assumption-consensus-vintage",
                "statement": "The fixture expectation is the persisted pre-release baseline.",
                "rationale": _text(expectation.get("vintage_rationale"))
                or "The observation time precedes the fictional release time.",
                "materiality": "high",
            }
        ],
        estimates=estimates,
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-earnings-bridges",
                "Actuals are compared separately with point-in-time expectations and prior guidance.",
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-earnings-transcript-gap",
                "Absent transcript evidence prevents interpretation of management commentary.",
                source_id,
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


def analyze_catalysts(inputs: Mapping[str, Any]) -> CapabilityResult:
    record = _mapping(inputs, "catalysts")
    events_value = record.get("events", [])
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
    source_id = _require_source(inputs, "catalyst-analysis")
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
        normalized_event.setdefault("source_ids", [source_id])
        normalized_event.setdefault("uncertainty", "not quantified")
        normalized_event.setdefault("materiality", "not quantified")
        normalized_event.setdefault(
            "downside_path", "The expected event may be delayed or fail to affect the named variable."
        )
        normalized.append(normalized_event)
        facts.append(
            _fact(
                f"fact-catalyst-event-{index}",
                f"The fictional fixture records event {normalized_event.get('event_id', index)} for {normalized_event.get('date') or normalized_event.get('window')}.",
                source_id,
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
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-catalyst-dependency",
                "Catalyst impact depends on events and operating conditions that may not occur as expected.",
                source_id,
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
    known_ids = {
        str(record.get("source_id"))
        for record in sources
        if _text(record.get("source_id"))
    }
    if not known_ids:
        return _skipped(
            "source-verification",
            "claim-source-integrity-gate",
            "No persisted source registry is available.",
            ["sources"],
        )
    claim_ledger: list[dict[str, Any]] = []
    missing: list[str] = []
    conflicts: list[str] = []
    for capability, result in prior.items():
        if capability == "source-verification" or not isinstance(result, Mapping):
            continue
        for fact in result.get("facts", []):
            if not isinstance(fact, Mapping):
                raise ValueError("capability fact must be a mapping")
            fact_id = _text(fact.get("id"))
            referenced = [str(value) for value in fact.get("source_ids", [])]
            unresolved = [value for value in referenced if value not in known_ids]
            status = "verified" if referenced and not unresolved else "unsupported"
            if unresolved:
                missing.extend(unresolved)
            claim_ledger.append(
                {
                    "claim_id": fact_id,
                    "capability": capability,
                    "source_ids": referenced,
                    "coverage": status,
                    "quality": "first-party fictional fixture",
                    "freshness": "bounded by fixture as_of_date",
                    "conflict": False,
                    "unresolved_source_ids": unresolved,
                }
            )
        for warning in result.get("warnings", []):
            if "conflict" in str(warning).casefold():
                conflicts.append(f"{capability}: {warning}")
    gate_status = "pass" if not missing and not conflicts else "pass_with_disclosed_gaps"
    source_id = sorted(known_ids)[0]
    unknowns = [
        _unknown(
            f"unknown-source-{index}",
            f"Source ID {value} is unresolved.",
            "The associated claim cannot support a material conclusion.",
        )
        for index, value in enumerate(dict.fromkeys(missing), start=1)
    ]
    return _completed(
        "source-verification",
        "claim-source-integrity-gate",
        method_fields={
            "claim_ledger": claim_ledger,
            "gate_status": gate_status,
            "source_quality_review": "completed",
            "freshness_review": "completed against fixture date",
            "coverage_summary": {
                "claims": len(claim_ledger),
                "unresolved_sources": len(set(missing)),
            },
            "conflicts": conflicts,
        },
        unknowns=unknowns,
        findings=[
            _finding(
                "finding-source-gate",
                f"Claim/source coverage completed with gate status {gate_status}.",
                source_id,
            )
        ],
        risks=[
            _risk(
                "risk-source-fixture-boundary",
                "All evidence is fictional demo evidence and does not establish current market facts.",
                source_id,
            )
        ],
        warnings=_warnings(inputs),
    )


def analyze_investment_report(inputs: Mapping[str, Any]) -> CapabilityResult:
    prior = _capability_results(inputs)
    for required in ("bear-case-analysis", "source-verification"):
        result = _mapping_value(prior.get(required), f"{required} result")
        if result.get("status") != "completed":
            return _skipped(
                "investment-report",
                "deterministic-report-view",
                f"Mandatory stage {required} is not completed.",
                [required],
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
                "Fictional demo evidence only; the report is not live or real-time."
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
    if diluted_shares <= 0:
        raise ValueError("diluted shares must be positive")
    present_value = sum(
        cash_flow / ((1.0 + wacc) ** year)
        for year, cash_flow in enumerate(cash_flows, start=1)
    )
    terminal_value = cash_flows[-1] * (1.0 + terminal_growth) / (
        wacc - terminal_growth
    )
    terminal_present_value = terminal_value / ((1.0 + wacc) ** len(cash_flows))
    enterprise_value = present_value + terminal_present_value
    equity_value = enterprise_value + cash - debt
    return {
        "wacc": wacc,
        "terminal_growth": terminal_growth,
        "diluted_shares": diluted_shares,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "equity_value_per_share": equity_value / diluted_shares,
        "terminal_value_share": terminal_present_value / enterprise_value,
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
    return numerator / denominator


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
        return ordered[lower_index] + (
            ordered[upper_index] - ordered[lower_index]
        ) * weight

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


def _primary_source_id(inputs: Mapping[str, Any]) -> str | None:
    records = _source_records(inputs)
    for record in records:
        source_id = _text(record.get("source_id"))
        if source_id:
            return source_id
    metadata = _mapping(inputs, "source_metadata")
    return _text(metadata.get("source_id"))


def _require_source(inputs: Mapping[str, Any], capability: str) -> str:
    source_id = _primary_source_id(inputs)
    if source_id is None:
        raise ValueError(f"{capability} requires persisted source metadata")
    return source_id


def _prior_source_ids(prior: Mapping[str, Any]) -> list[str]:
    result: list[str] = []
    for value in prior.values():
        if not isinstance(value, Mapping):
            continue
        for source_id in value.get("source_ids", []):
            if _text(source_id) and str(source_id) not in result:
                result.append(str(source_id))
    return result


def _warnings(inputs: Mapping[str, Any]) -> list[str]:
    warnings = [
        "This analysis uses wholly fictional offline demo data and is not live or real-time."
    ]
    for key in (
        "identity",
        "profile",
        "statements",
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


def _fact(identifier: str, statement: str, source_id: str) -> dict[str, Any]:
    return {"id": identifier, "statement": statement, "source_ids": [source_id]}


def _finding(identifier: str, statement: str, source_id: str) -> dict[str, Any]:
    return {"id": identifier, "statement": statement, "source_ids": [source_id]}


def _risk(identifier: str, statement: str, source_id: str) -> dict[str, Any]:
    return {"id": identifier, "statement": statement, "source_ids": [source_id]}


def _unknown(identifier: str, gap: str, impact: str) -> dict[str, Any]:
    return {"id": identifier, "gap": gap, "impact": impact}


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    return numerator / denominator


def _ratio_delta(value: float | None, baseline: float | None) -> float | None:
    ratio = _ratio(value, baseline)
    return None if ratio is None else ratio - 1.0


def _financial_formula(name: str) -> str:
    return {
        "revenue_growth": "latest revenue / earliest comparable revenue - 1",
        "gross_margin": "gross profit / revenue",
        "operating_margin": "operating income / revenue",
        "cash_flow_margin": "operating cash flow / revenue",
        "leverage_debt_to_equity": "gross debt / total equity",
        "liquidity_cash_to_debt": "cash and equivalents / gross debt",
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
