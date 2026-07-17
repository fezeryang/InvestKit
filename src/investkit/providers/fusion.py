"""Fuse identity-checked provider evidence into one governed research bundle."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import math
import re
from typing import Any, Mapping, Sequence

from ..errors import InvestKitError
from .ciccwm import ENDPOINT as CICCWM_ENDPOINT
from .guangfa import ENDPOINT, normalize_a_share_symbol


class ProviderFusionError(InvestKitError):
    """Raised when provider evidence cannot be fused without ambiguity."""


def fuse_ciccwm_research_bundle(
    base_bundle: Mapping[str, Any],
    *,
    market_info_response: Mapping[str, Any],
    market_history_response: Mapping[str, Any],
    financial_responses: Mapping[str, Mapping[str, Any]],
    hot_news_response: Mapping[str, Any],
    dragon_tiger_response: Mapping[str, Any],
    dragon_tiger_date: str,
) -> dict[str, Any]:
    """Add bounded CICCWM market, statement, and event evidence to a bundle."""

    bundle = deepcopy(dict(base_bundle))
    security = _mapping(bundle.get("security"), "base security")
    target = normalize_a_share_symbol(_text(security.get("ticker"), "base ticker"))
    legal_name = _text(security.get("legal_name"), "base legal name")
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    market = _cicc_json(market_info_response, "data", "market info")
    market_base = _mapping(market.get("BaseInfo"), "CICCWM market identity")
    if str(market_base.get("Code")) != target.code:
        raise ProviderFusionError("CICCWM market identity conflicts with exchange identity")
    quote = _mapping(market.get("HQInfo"), "CICCWM quote")
    quote_date = _compact_date(quote.get("HQDate"), "CICCWM quote date")
    latest_price = _positive_number(quote.get("Now"), "CICCWM current price")

    history = _cicc_json(market_history_response, "data", "market history")
    if str(history.get("Code")) != target.code:
        raise ProviderFusionError("CICCWM history identity conflicts with exchange identity")
    observations = _history_observations(history)
    if not observations:
        raise ProviderFusionError("CICCWM history contains no usable observations")
    history_date = observations[-1]["date"]

    expected_statements = {"income", "cashflow", "balance", "indicators"}
    if set(financial_responses) != expected_statements:
        raise ProviderFusionError("CICCWM financial response set is incomplete")
    statement_rows = {
        name: _cicc_financial_rows(response, name)
        for name, response in financial_responses.items()
    }

    try:
        event_date = datetime.strptime(dragon_tiger_date, "%Y-%m-%d").date().isoformat()
    except (TypeError, ValueError) as error:
        raise ProviderFusionError("CICCWM Dragon-Tiger date is invalid") from error
    news_rsp = _cicc_rsp(hot_news_response, "hot news")
    lhb_rsp = _cicc_rsp(dragon_tiger_response, "Dragon-Tiger list")

    sources = _list(bundle.get("sources"), "base sources")
    market_source = _append_ciccwm_source(
        sources,
        source_id=f"ciccwm-{target.code}-market-{history_date}",
        title=f"{legal_name} 行情与近端历史价格",
        as_of_date=history_date,
        retrieved_at=now,
        source_type="credentialed-broker-market-data",
    )
    finance_sources: dict[str, str] = {}
    for name in sorted(expected_statements):
        dates = [row["rq"] for row in statement_rows[name]]
        as_of = max(dates) if dates else history_date
        finance_sources[name] = _append_ciccwm_source(
            sources,
            source_id=f"ciccwm-{target.code}-{name}-{as_of}",
            title=f"{legal_name} {name} 财务数据",
            as_of_date=as_of,
            retrieved_at=now,
            source_type="credentialed-broker-financial-data",
        )
    news_source = _append_ciccwm_source(
        sources,
        source_id=f"ciccwm-{target.code}-news-{quote_date}",
        title=f"中金财富热榜资讯证券关联筛选（{legal_name}）",
        as_of_date=quote_date,
        retrieved_at=now,
        source_type="credentialed-broker-news-feed",
    )
    lhb_source = _append_ciccwm_source(
        sources,
        source_id=f"ciccwm-{target.code}-lhb-{event_date}",
        title=f"{event_date} 龙虎榜目标证券筛选（{legal_name}）",
        as_of_date=event_date,
        retrieved_at=now,
        source_type="credentialed-broker-abnormal-trading-list",
    )

    operations = _mapping(bundle.get("operations"), "base operations")
    prices_operation = _mapping(operations.get("get_price_history"), "price operation")
    prices_operation["data"] = {
        "observations": observations,
        "latest_price": latest_price,
        "frequency": "daily",
        "units": "CNY per share; volume and amount retain vendor units",
        "limitations": [
            "The bounded history is suitable for recent context, not long-horizon technical inference."
        ],
    }
    prices_operation["source_ids"] = [market_source]
    prices_operation["warnings"] = list(prices_operation["data"]["limitations"])

    valuation_operation = _mapping(operations.get("get_valuation_inputs"), "valuation operation")
    valuation_data = _mapping(valuation_operation.get("data"), "valuation data")
    valuation_data["current_price"] = latest_price
    valuation_operation["source_ids"] = list(
        dict.fromkeys([*valuation_operation.get("source_ids", []), market_source])
    )

    statements_operation = _mapping(operations.get("get_financial_statements"), "statements operation")
    statements_data = _mapping(statements_operation.get("data"), "statements data")
    periods = _list(statements_data.get("periods"), "statement periods")
    statements_data["periods"] = _merge_ciccwm_periods(periods, statement_rows)
    statements_data["accounting_basis"] = "vendor-defined reported financial fields and ratios"
    statements_data["units"] = "monetary fields in CNY; ratios are percentages or vendor-defined multiples"
    statements_data["limitations"] = [
        "CICCWM supplies structured fields without audited footnote context; ambiguous vendor abbreviations are not normalized."
    ]
    statements_operation["source_ids"] = list(
        dict.fromkeys([*statements_operation.get("source_ids", []), *finance_sources.values()])
    )
    statements_operation["warnings"] = list(statements_data["limitations"])

    events = [
        *_relevant_news_events(news_rsp, target.code, news_source),
        *_relevant_lhb_events(lhb_rsp, target.code, event_date, lhb_source),
    ]
    catalysts_operation = _mapping(operations.get("get_catalyst_events"), "catalyst operation")
    catalysts_operation["data"] = {
        "events": events,
        "limitations": [
            "News and Dragon-Tiger records are event context, not directional forecasts or proof of causality."
        ],
    }
    catalysts_operation["source_ids"] = [news_source, lhb_source] if events else []
    catalysts_operation["warnings"] = list(catalysts_operation["data"]["limitations"])

    bundle["sources"] = sources
    metadata = _mapping(operations.get("get_source_metadata"), "source metadata operation")
    metadata["data"] = {
        "sources": deepcopy(sources),
        "limitations": [
            "Exchange identity, Guangfa fundamentals, and CICCWM market/event evidence have different definitions and coverage."
        ],
    }
    metadata["source_ids"] = [source["source_id"] for source in sources]
    metadata["warnings"] = list(metadata["data"]["limitations"])
    bundle["operations"] = operations
    bundle["created_at"] = now
    bundle["retrieved_at"] = now
    bundle["as_of_date"] = max(str(bundle.get("as_of_date")), quote_date, history_date)
    bundle["bundle_version"] = f"{bundle['bundle_version']}-ciccwm-v1"
    bundle["warnings"] = list(
        dict.fromkeys(
            [
                *bundle.get("warnings", []),
                "CICCWM market, statement, and target-linked event evidence was normalized by InvestKit without vendor telemetry.",
            ]
        )
    )
    return bundle


def fuse_guangfa_target_bundle(
    base_bundle: Mapping[str, Any],
    *,
    f10_response: Mapping[str, Any],
    valuation_response: Mapping[str, Any],
) -> dict[str, Any]:
    """Add target-only Guangfa F10 and relative valuation evidence."""

    bundle = deepcopy(dict(base_bundle))
    security = _mapping(bundle.get("security"), "base security")
    ticker = _text(security.get("ticker"), "base ticker")
    legal_name = _text(security.get("legal_name"), "base legal name")
    target = normalize_a_share_symbol(ticker)
    f10 = _f10_payload(f10_response)
    if _text(f10.get("compName"), "F10 company name") != legal_name:
        raise ProviderFusionError(
            "F10 identity conflicts with the official exchange identity"
        )
    target_valuation = _valuation_item(valuation_response, target.vendor_code)
    valuation_data = _valuation_data(target_valuation)
    trade_date = _date_text(
        _mapping(target_valuation.get("valuation"), "target valuation").get(
            "trade_date"
        ),
        "target valuation trade date",
    )
    now = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    sources = _list(bundle.get("sources"), "base sources")
    f10_source = _append_source(
        sources,
        source_id=f"gf-{target.code}-f10",
        title=f"{legal_name} F10 基础信息",
        as_of_date=now[:10],
        retrieved_at=now,
        source_type="credentialed-broker-f10",
    )
    valuation_source = _append_source(
        sources,
        source_id=f"gf-{target.code}-valuation-{trade_date}",
        title=f"{legal_name} 市值、估值与行业均值快照",
        as_of_date=trade_date,
        retrieved_at=now,
        source_type="credentialed-broker-valuation",
    )
    operations = _mapping(bundle.get("operations"), "base operations")
    profile_operation = _mapping(
        operations.get("get_security_profile"), "profile operation"
    )
    profile = _mapping(profile_operation.get("data"), "profile data")
    business_scope = _text(f10.get("businessScope"), "F10 business scope")
    industry = _text(f10.get("industries"), "F10 industry")
    profile["business_model"] = business_scope
    profile["products"] = [
        item.strip() for item in business_scope.split(",") if item.strip()
    ][:20]
    profile["research_drivers"] = list(profile.get("research_drivers") or []) + [
        f"板块：{_text(f10.get('boardName'), 'F10 board')}",
        f"广发行业：{industry}",
    ]
    profile["limitations"] = [
        "F10 describes registered business scope; segment revenue and customer concentration remain unavailable."
    ]
    profile_operation["source_ids"] = list(
        dict.fromkeys([*profile_operation.get("source_ids", []), f10_source])
    )
    profile_operation["warnings"] = list(profile["limitations"])

    relative_metrics: dict[str, dict[str, float]] = {}
    for metric, target_key, industry_key in (
        (
            "price_to_earnings_ttm",
            "price_to_earnings_ttm",
            "industry_price_to_earnings_ttm",
        ),
        ("price_to_book", "price_to_book", "industry_price_to_book"),
    ):
        target_value = valuation_data[target_key]
        industry_value = valuation_data[industry_key]
        if target_value > 0 and industry_value > 0:
            relative_metrics[metric] = {
                "target": target_value,
                "industry_average": industry_value,
                "target_to_average": target_value / industry_value,
            }
    valuation_operation = _mapping(
        operations.get("get_valuation_inputs"), "valuation operation"
    )
    valuation_operation["data"] = {
        "current_price": None,
        **valuation_data,
        "enterprise_value": None,
        "forecast_unlevered_free_cash_flow": None,
        "forecast_metadata": None,
        "consensus": None,
        "wacc": None,
        "terminal_growth": None,
        "diluted_shares": None,
        "cash": None,
        "total_debt": None,
        "scenario_assumptions": None,
        "sensitivity_wacc_values": None,
        "sensitivity_terminal_growth_values": None,
        "industry_valuation_reference": {
            "classification": industry,
            "as_of_date": trade_date,
            "sample_size": None,
            "metrics": relative_metrics,
        },
        "units": "market capitalization in CNY 100 million; multiples dimensionless",
        "limitations": [
            "Industry valuation averages are usable as a relative reference, but the provider response does not disclose constituent count or membership.",
            "DCF forecasts, capital bridge, discount-rate inputs, and broker consensus are unavailable.",
        ],
    }
    valuation_operation["source_ids"] = [valuation_source]
    valuation_operation["warnings"] = list(
        valuation_operation["data"]["limitations"]
    )

    bundle["sources"] = sources
    metadata = _mapping(
        operations.get("get_source_metadata"), "source metadata operation"
    )
    metadata["data"] = {
        "sources": deepcopy(sources),
        "limitations": [
            "Official exchange identity is fused with target-only Guangfa F10 and valuation evidence."
        ],
    }
    metadata["source_ids"] = [source["source_id"] for source in sources]
    metadata["warnings"] = list(metadata["data"]["limitations"])
    bundle["operations"] = operations
    bundle["created_at"] = now
    bundle["retrieved_at"] = now
    bundle["as_of_date"] = max(str(bundle["as_of_date"]), trade_date)
    bundle["bundle_version"] = f"gf-target-{target.code}-{bundle['as_of_date']}-v1"
    bundle["warnings"] = list(
        dict.fromkeys(
            [
                *bundle.get("warnings", []),
                "Guangfa target valuation was identity-checked and normalized without inferring consensus or DCF inputs.",
            ]
        )
    )
    return bundle


def fuse_equity_research_bundle(
    base_bundle: Mapping[str, Any],
    *,
    f10_response: Mapping[str, Any],
    valuation_response: Mapping[str, Any],
    peer_valuation_response: Mapping[str, Any],
    financial_responses: Sequence[Mapping[str, Any]],
    peer_symbol: str,
) -> dict[str, Any]:
    """Enrich an official-exchange bundle with independently sourced GF evidence."""

    bundle = deepcopy(dict(base_bundle))
    security = _mapping(bundle.get("security"), "base security")
    ticker = _text(security.get("ticker"), "base ticker")
    legal_name = _text(security.get("legal_name"), "base legal name")
    target = normalize_a_share_symbol(ticker)
    peer = normalize_a_share_symbol(peer_symbol)
    if target.canonical == peer.canonical:
        raise ProviderFusionError("peer security must differ from the target")

    f10 = _f10_payload(f10_response)
    if _text(f10.get("compName"), "F10 company name") != legal_name:
        raise ProviderFusionError("F10 identity conflicts with the official exchange identity")
    target_valuation = _valuation_item(valuation_response, target.vendor_code)
    peer_valuation = _valuation_item(peer_valuation_response, peer.vendor_code)
    target_financials, peer_financials = _financial_rows(
        financial_responses, target.vendor_code, peer.vendor_code
    )

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    sources = _list(bundle.get("sources"), "base sources")
    source_ids: list[str] = []
    source_ids.append(
        _append_source(
            sources,
            source_id=f"gf-{target.code}-f10",
            title=f"{legal_name} F10 基础信息",
            as_of_date=now[:10],
            retrieved_at=now,
            source_type="credentialed-broker-f10",
        )
    )
    target_trade_date = _date_text(
        _mapping(target_valuation.get("valuation"), "target valuation").get("trade_date"),
        "target valuation trade date",
    )
    source_ids.append(
        _append_source(
            sources,
            source_id=f"gf-{target.code}-valuation-{target_trade_date}",
            title=f"{legal_name} 市值与估值快照",
            as_of_date=target_trade_date,
            retrieved_at=now,
            source_type="credentialed-broker-valuation",
        )
    )
    peer_trade_date = _date_text(
        _mapping(peer_valuation.get("valuation"), "peer valuation").get("trade_date"),
        "peer valuation trade date",
    )
    peer_name = _text(peer_valuation.get("stock_name"), "peer name")
    source_ids.append(
        _append_source(
            sources,
            source_id=f"gf-{peer.code}-valuation-{peer_trade_date}",
            title=f"{peer_name} 市值与估值快照",
            as_of_date=peer_trade_date,
            retrieved_at=now,
            source_type="credentialed-broker-peer-valuation",
        )
    )
    financial_source_ids: list[str] = []
    for period in target_financials:
        year = _text(period.get("year"), "financial year")
        financial_source_ids.append(
            _append_source(
                sources,
                source_id=f"gf-{target.code}-{peer.code}-financial-{year}",
                title=f"{legal_name}与{peer_name} {year} 年财务指标对比",
                as_of_date=f"{year}-12-31",
                retrieved_at=now,
                source_type="credentialed-broker-financial-comparison",
            )
        )
    operations = _mapping(bundle.get("operations"), "base operations")
    profile_operation = _mapping(operations.get("get_security_profile"), "profile operation")
    profile = _mapping(profile_operation.get("data"), "profile data")
    business_scope = _text(f10.get("businessScope"), "F10 business scope")
    profile["business_model"] = business_scope
    profile["products"] = [item.strip() for item in business_scope.split(",") if item.strip()][:20]
    profile["research_drivers"] = list(profile.get("research_drivers") or []) + [
        f"板块：{_text(f10.get('boardName'), 'F10 board')}",
        f"广发行业：{_text(f10.get('industries'), 'F10 industry')}",
    ]
    profile["limitations"] = [
        "F10 describes registered business scope; segment revenue and customer concentration remain unavailable."
    ]
    profile_operation["source_ids"] = list(dict.fromkeys([*profile_operation["source_ids"], source_ids[0]]))
    profile_operation["warnings"] = list(profile["limitations"])

    periods = [_statement_period(item) for item in target_financials]
    statements_operation = _mapping(operations.get("get_financial_statements"), "statements operation")
    statements_operation["data"] = {
        "accounting_basis": "vendor-defined reported financial indicators",
        "period_type": "annual",
        "currency": "CNY",
        "units": "ratios are percentages or vendor-defined multiples",
        "periods": periods,
        "limitations": [
            "The provider supplies comparative indicators, not complete audited three-statement line items."
        ],
    }
    statements_operation["source_ids"] = financial_source_ids
    statements_operation["warnings"] = list(statements_operation["data"]["limitations"])

    valuation_data = _valuation_data(target_valuation)
    valuation_operation = _mapping(operations.get("get_valuation_inputs"), "valuation operation")
    valuation_operation["data"] = {
        "current_price": None,
        "market_capitalization": valuation_data["market_capitalization"],
        "enterprise_value": None,
        "price_to_earnings_ttm": valuation_data["price_to_earnings_ttm"],
        "price_to_book": valuation_data["price_to_book"],
        "industry_price_to_earnings_ttm": valuation_data["industry_price_to_earnings_ttm"],
        "industry_price_to_book": valuation_data["industry_price_to_book"],
        "pe_history_percentile": valuation_data["pe_history_percentile"],
        "pb_history_percentile": valuation_data["pb_history_percentile"],
        "forecast_unlevered_free_cash_flow": None,
        "wacc": None,
        "terminal_growth": None,
        "diluted_shares": None,
        "cash": None,
        "total_debt": None,
        "peer_ev_to_operating_income": None,
        "scenario_assumptions": None,
        "sensitivity_wacc_values": None,
        "sensitivity_terminal_growth_values": None,
        "units": "market capitalization in CNY 100 million; multiples dimensionless",
        "limitations": [
            "Market-relative valuation is available, but DCF cash-flow, capital bridge, and discount-rate inputs are unavailable."
        ],
    }
    valuation_operation["source_ids"] = [source_ids[1]]
    valuation_operation["warnings"] = list(valuation_operation["data"]["limitations"])

    peer_data = _peer_data(peer, peer_valuation, peer_financials[-1])
    peers_operation = _mapping(operations.get("get_peer_comparables"), "peers operation")
    peers_operation["data"] = {
        "peers": [peer_data],
        "selection_method": "User-approved household-appliance operating peer; identity and period alignment validated by the Harness.",
        "period_alignment": target_financials[-1]["year"],
        "units": "CNY 100 million and dimensionless multiples",
        "limitations": ["The current peer set contains one company and is not a broad industry sample."],
    }
    peers_operation["source_ids"] = [source_ids[2], financial_source_ids[-1]]
    peers_operation["warnings"] = list(peers_operation["data"]["limitations"])

    bundle["sources"] = sources
    metadata_operation = _mapping(operations.get("get_source_metadata"), "source metadata operation")
    metadata_operation["data"] = {
        "sources": deepcopy(sources),
        "limitations": [
            "Official exchange identity is fused with permission-gated broker data; complete filing tables and consensus estimates remain unavailable."
        ],
    }
    metadata_operation["source_ids"] = [source["source_id"] for source in sources]
    metadata_operation["warnings"] = list(metadata_operation["data"]["limitations"])
    bundle["operations"] = operations
    bundle["created_at"] = now
    bundle["retrieved_at"] = now
    bundle["as_of_date"] = max(str(bundle["as_of_date"]), target_trade_date, peer_trade_date)
    bundle["bundle_version"] = f"fusion-{target.code}-{bundle['as_of_date']}-v1"
    bundle["warnings"] = [
        "Multi-provider evidence was identity-checked and fused by InvestKit.",
        "Missing DCF, complete statement, news, and consensus inputs remain explicit unknowns.",
    ]
    return bundle


def _f10_payload(response: Mapping[str, Any]) -> Mapping[str, Any]:
    envelope = _mapping(response.get("data"), "F10 envelope")
    if envelope.get("errcode") != 0:
        raise ProviderFusionError("Guangfa F10 response is unsuccessful")
    return _mapping(envelope.get("data"), "F10 payload")


def _valuation_item(response: Mapping[str, Any], expected_code: str) -> Mapping[str, Any]:
    if response.get("retcode") not in {None, 0}:
        raise ProviderFusionError("Guangfa valuation response is unsuccessful")
    envelope = _mapping(response.get("data"), "valuation envelope")
    if envelope.get("retcode") != 0:
        raise ProviderFusionError("Guangfa valuation response is unsuccessful")
    values = _list(envelope.get("data"), "valuation data")
    matches = [item for item in values if isinstance(item, Mapping) and item.get("stock_code") == expected_code]
    if len(matches) != 1:
        raise ProviderFusionError("Guangfa valuation identity is missing or ambiguous")
    return matches[0]


def _financial_rows(
    responses: Sequence[Mapping[str, Any]], target_code: str, peer_code: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if len(responses) < 2:
        raise ProviderFusionError("at least two comparable financial periods are required")
    target_rows: list[dict[str, Any]] = []
    peer_rows: list[dict[str, Any]] = []
    for response in responses:
        envelope = _mapping(response.get("data"), "financial envelope")
        if envelope.get("retcode") != 0:
            raise ProviderFusionError("Guangfa financial response is unsuccessful")
        payload = _mapping(envelope.get("data"), "financial payload")
        year = _text(payload.get("year"), "financial year")
        rows = _list(payload.get("data"), "financial rows")
        target = [row for row in rows if isinstance(row, Mapping) and row.get("stock_code") == target_code]
        peer = [row for row in rows if isinstance(row, Mapping) and row.get("stock_code") == peer_code]
        if len(target) != 1 or len(peer) != 1:
            raise ProviderFusionError("Guangfa financial identities are missing or ambiguous")
        target_rows.append({"year": year, **dict(target[0])})
        peer_rows.append({"year": year, **dict(peer[0])})
    target_rows.sort(key=lambda item: item["year"])
    peer_rows.sort(key=lambda item: item["year"])
    if [row["year"] for row in target_rows] != [row["year"] for row in peer_rows]:
        raise ProviderFusionError("target and peer financial periods are not aligned")
    return target_rows, peer_rows


def _statement_period(row: Mapping[str, Any]) -> dict[str, Any]:
    aliases = {
        "roe": "roe_percent",
        "sale_gross_rate": "gross_margin_percent",
        "net_profit2totalincome": "net_margin_percent",
        "cashflow_oper2income": "operating_cash_to_income",
        "net_cashflow_oper2net_profit": "operating_cash_to_net_profit",
        "liablity2asset": "liabilities_to_assets_percent",
        "operate_income_yoy": "revenue_growth_percent",
        "net_profit_yoy": "net_profit_growth_percent",
        "inventory_turnover": "inventory_turnover",
        "acctreceivable_turnover": "accounts_receivable_turnover",
        "quick_ratio": "quick_ratio",
        "equity2asset": "equity_to_assets_percent",
    }
    result: dict[str, Any] = {
        "fiscal_year": _text(row.get("year"), "financial year"),
        "end_date": _date_text(row.get("end_date"), "financial end date"),
    }
    for source, target in aliases.items():
        value = row.get(source)
        if value is None:
            result[target] = None
        else:
            result[target] = _number(value, source)
    return result


def _valuation_data(item: Mapping[str, Any]) -> dict[str, float]:
    basic = _mapping(item.get("basic"), "valuation basic data")
    valuation = _mapping(item.get("valuation"), "valuation metrics")
    return {
        "market_capitalization": _number(basic.get("total_marketcap"), "market capitalization"),
        "price_to_earnings_ttm": _number(valuation.get("pettm"), "PE TTM"),
        "price_to_book": _number(valuation.get("pb"), "PB"),
        "industry_price_to_earnings_ttm": _number(valuation.get("pettm_avg"), "industry PE"),
        "industry_price_to_book": _number(valuation.get("pb_avg"), "industry PB"),
        "pe_history_percentile": _number(valuation.get("pettm_percent"), "PE percentile"),
        "pb_history_percentile": _number(valuation.get("pb_percent"), "PB percentile"),
    }


def _peer_data(
    symbol: Any, valuation_item: Mapping[str, Any], financial_row: Mapping[str, Any]
) -> dict[str, Any]:
    values = _valuation_data(valuation_item)
    market_cap = values["market_capitalization"]
    pe = values["price_to_earnings_ttm"]
    pb = values["price_to_book"]
    if pe <= 0 or pb <= 0:
        raise ProviderFusionError("peer valuation denominators must be positive")
    return {
        "ticker": symbol.canonical,
        "name": _text(valuation_item.get("stock_name"), "peer name"),
        "status": "included",
        "market_capitalization": market_cap,
        "net_income": market_cap / pe,
        "total_equity": market_cap / pb,
        "price_to_earnings": pe,
        "price_to_book": pb,
        "roe_percent": _number(financial_row.get("roe"), "peer ROE"),
        "revenue_growth_percent": _number(
            financial_row.get("operate_income_yoy"), "peer revenue growth"
        ),
        "net_profit_growth_percent": _number(
            financial_row.get("net_profit_yoy"), "peer net profit growth"
        ),
        "period": _text(financial_row.get("year"), "peer financial year"),
    }


def _append_source(
    sources: list[Any],
    *,
    source_id: str,
    title: str,
    as_of_date: str,
    retrieved_at: str,
    source_type: str,
) -> str:
    if any(isinstance(source, Mapping) and source.get("source_id") == source_id for source in sources):
        raise ProviderFusionError("duplicate fused source ID")
    sources.append(
        {
            "source_id": source_id,
            "publisher": "广发证券",
            "title": title,
            "source_type": source_type,
            "locator": ENDPOINT,
            "publication_date": None,
            "as_of_date": as_of_date,
            "retrieved_at": retrieved_at,
            "quality": "credentialed-structured-provider",
            "freshness": "point-in-time-as-retrieved",
            "access_notes": "Read-only response acquired through the permission-gated InvestKit Guangfa adapter; telemetry is not used.",
            "license_notes": "User authorized API access; downstream data use remains subject to Guangfa terms.",
        }
    )
    return source_id


def _append_ciccwm_source(
    sources: list[Any],
    *,
    source_id: str,
    title: str,
    as_of_date: str,
    retrieved_at: str,
    source_type: str,
) -> str:
    if any(isinstance(source, Mapping) and source.get("source_id") == source_id for source in sources):
        raise ProviderFusionError("duplicate fused source ID")
    sources.append(
        {
            "source_id": source_id,
            "publisher": "中金财富",
            "title": title,
            "source_type": source_type,
            "locator": CICCWM_ENDPOINT,
            "publication_date": None,
            "as_of_date": as_of_date,
            "retrieved_at": retrieved_at,
            "quality": "credentialed-structured-provider",
            "freshness": "point-in-time-as-retrieved",
            "access_notes": "Read-only response acquired through InvestKit's allowlisted no-telemetry CICCWM adapter.",
            "license_notes": "User authorized API access; downstream data use remains subject to CICCWM terms.",
        }
    )
    return source_id


def _cicc_rsp(response: Mapping[str, Any], label: str) -> dict[str, Any]:
    if response.get("ret") not in {0, "0"}:
        raise ProviderFusionError(f"CICCWM {label} response is unsuccessful")
    rsp = _mapping(response.get("rsp"), f"CICCWM {label} envelope")
    if rsp.get("ret_code") not in {None, 0, "0"}:
        raise ProviderFusionError(f"CICCWM {label} response is unsuccessful")
    return rsp


def _cicc_json(response: Mapping[str, Any], field: str, label: str) -> Any:
    rsp = _cicc_rsp(response, label)
    raw = rsp.get(field)
    if not isinstance(raw, str) or not raw or len(raw.encode("utf-8")) > 2 * 1024 * 1024:
        raise ProviderFusionError(f"CICCWM {label} embedded JSON is invalid")
    try:
        return json.loads(
            raw,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, ValueError) as error:
        raise ProviderFusionError(f"CICCWM {label} embedded JSON is invalid") from error


def _cicc_financial_rows(response: Mapping[str, Any], label: str) -> list[dict[str, Any]]:
    value = _cicc_json(response, "rsp_json", f"{label} financial")
    if not isinstance(value, list) or len(value) > 100:
        raise ProviderFusionError(f"CICCWM {label} financial rows are invalid")
    rows: list[dict[str, Any]] = []
    for item in value:
        row = _mapping(item, f"CICCWM {label} financial row")
        row["rq"] = _date_text(row.get("rq"), f"CICCWM {label} report date")
        rows.append(row)
    return rows


def _compact_date(value: Any, label: str) -> str:
    text = _text(value, label)
    try:
        return datetime.strptime(text, "%Y%m%d").date().isoformat()
    except ValueError as error:
        raise ProviderFusionError(f"{label} is invalid") from error


def _positive_number(value: Any, label: str) -> float:
    number = _coerce_number(value, label)
    if number <= 0:
        raise ProviderFusionError(f"{label} must be positive")
    return number


def _coerce_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ProviderFusionError(f"{label} must be numeric")
    if isinstance(value, str):
        if re.fullmatch(r"-?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", value) is None:
            raise ProviderFusionError(f"{label} must be numeric")
        value = float(value)
    if not isinstance(value, (int, float)):
        raise ProviderFusionError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ProviderFusionError(f"{label} must be finite")
    return result


def _history_observations(value: Any) -> list[dict[str, Any]]:
    history = _mapping(value, "CICCWM history")
    columns = _list(
        _mapping(history.get("ListHead"), "CICCWM history header").get("ItemHead"),
        "CICCWM history columns",
    )
    rows = _list(history.get("ListItem"), "CICCWM history rows")
    if len(rows) > 250 or len(columns) > 40:
        raise ProviderFusionError("CICCWM history exceeds the bounded contract")
    aliases = {"Data": "date", "High": "high", "Amount": "amount", "Volume": "volume"}
    observations: list[dict[str, Any]] = []
    for item in rows:
        values = _list(_mapping(item, "CICCWM history row").get("Item"), "CICCWM history values")
        if len(values) != len(columns):
            raise ProviderFusionError("CICCWM history row width is inconsistent")
        raw = dict(zip(columns, values))
        observation = {
            "date": _compact_date(raw.get("Data"), "CICCWM history date"),
            "open": _coerce_number(raw.get("Open"), "CICCWM history open"),
            "high": _coerce_number(raw.get("High"), "CICCWM history high"),
            "low": _coerce_number(raw.get("Low"), "CICCWM history low"),
            "close": _positive_number(raw.get("Close"), "CICCWM history close"),
            "amount": _coerce_number(raw.get("Amount"), "CICCWM history amount"),
            "volume": _coerce_number(raw.get("Volume"), "CICCWM history volume"),
        }
        if observation["low"] > observation["high"]:
            raise ProviderFusionError("CICCWM history high/low values are inconsistent")
        observations.append(observation)
    observations.sort(key=lambda item: item["date"])
    if len({item["date"] for item in observations}) != len(observations):
        raise ProviderFusionError("CICCWM history contains duplicate dates")
    del aliases
    return observations


def _merge_ciccwm_periods(
    existing: list[Any], statement_rows: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[dict[str, Any]]:
    by_date: dict[str, dict[str, Any]] = {}
    for item in existing:
        period = _mapping(item, "existing statement period")
        end_date = _date_text(period.get("end_date"), "existing statement date")
        by_date[end_date] = dict(period)
    aliases = {
        "income": {
            "yysr": "revenue", "yycb": "cost_of_revenue", "yylr": "operating_income",
            "lrze": "pretax_income", "jlr": "net_income",
        },
        "cashflow": {
            "jyxjje": "cash_from_operations", "tzxjje": "cash_from_investing",
            "czxjje": "cash_from_financing",
        },
        "balance": {
            "zczj": "total_assets", "fzhj": "total_liabilities", "gdqyhj": "total_equity",
            "hbzj": "cash_and_equivalents", "chjr": "inventory", "yszk": "accounts_receivable",
        },
        "indicators": {
            "xsmll": "gross_margin_percent", "jzcsyl": "roe_percent",
            "zcfzl": "liabilities_to_assets_percent", "yysrzzl": "revenue_growth_percent",
            "jlrtbzzl": "net_profit_growth_percent",
        },
    }
    for statement, rows in statement_rows.items():
        for row in rows:
            end_date = _date_text(row.get("rq"), "CICCWM financial date")
            if not end_date.endswith("-12-31"):
                continue
            period = by_date.setdefault(
                end_date,
                {"fiscal_year": end_date[:4], "end_date": end_date},
            )
            for source, target in aliases[statement].items():
                value = row.get(source)
                if value in {None, ""}:
                    continue
                period[target] = _coerce_number(value, f"CICCWM financial field {source}")
    return [by_date[key] for key in sorted(by_date)]


def _relevant_news_events(
    rsp: Mapping[str, Any], target_code: str, source_id: str
) -> list[dict[str, Any]]:
    items = rsp.get("content_list", [])
    if not isinstance(items, list) or len(items) > 100:
        raise ProviderFusionError("CICCWM news list is invalid")
    events: list[dict[str, Any]] = []
    for item_value in items:
        item = _mapping(item_value, "CICCWM news item")
        stock_info = item.get("stock_info") or []
        if not isinstance(stock_info, list):
            raise ProviderFusionError("CICCWM news stock links are invalid")
        if not any(isinstance(stock, Mapping) and str(stock.get("stock_code")) == target_code for stock in stock_info):
            continue
        identifier = _safe_identifier(item.get("id"), "news item ID")
        published = _text(item.get("pub_time"), "news publication time")[:10]
        published = _date_text(published, "news publication date")
        events.append(
            {
                "event_id": f"news-{target_code}-{identifier}",
                "date": published,
                "event_type": "target-linked-news-context",
                "title": _text(item.get("title"), "news title"),
                "summary": str(item.get("short_content") or "No bounded summary supplied."),
                "dependencies": ["The report must be corroborated and its operating or financial impact observed."],
                "uncertainty": "high - news relevance does not establish direction or materiality",
                "materiality": "not quantified",
                "downside_path": "The reported development may be immaterial, delayed, reversed, or already reflected in price.",
                "source_ids": [source_id],
            }
        )
    return events


def _relevant_lhb_events(
    rsp: Mapping[str, Any], target_code: str, event_date: str, source_id: str
) -> list[dict[str, Any]]:
    charts = _mapping(rsp.get("charts_info"), "CICCWM Dragon-Tiger charts")
    matches: list[Mapping[str, Any]] = []
    for key in ("overall_list", "jgqc_list", "yzby_list"):
        values = charts.get(key) or []
        if not isinstance(values, list) or len(values) > 500:
            raise ProviderFusionError("CICCWM Dragon-Tiger list is invalid")
        matches.extend(
            item for item in values if isinstance(item, Mapping) and str(item.get("secu_code")) == target_code
        )
    if not matches:
        return []
    item = matches[0]
    return [
        {
            "event_id": f"lhb-{target_code}-{event_date}",
            "date": event_date,
            "event_type": "dragon-tiger-abnormal-trading",
            "title": f"龙虎榜记录：{str(item.get('s_reason_type') or '上榜原因未披露')}",
            "dependencies": ["Abnormal trading must be interpreted with liquidity, disclosures, and subsequent price action."],
            "uncertainty": "high - list inclusion does not identify durable fundamental information",
            "materiality": "not quantified",
            "downside_path": "Short-term flow concentration may reverse and amplify volatility.",
            "source_ids": [source_id],
        }
    ]


def _safe_identifier(value: Any, label: str) -> str:
    text = _text(value, label)
    if re.fullmatch(r"[A-Za-z0-9._-]{1,120}", text) is None:
        raise ProviderFusionError(f"{label} is invalid")
    return text


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate embedded response key")
        value[key] = child
    return value


def _reject_json_constant(value: str) -> Any:
    del value
    raise ValueError("non-finite embedded response number")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ProviderFusionError(f"{label} must be an object")
    return value if isinstance(value, dict) else dict(value)


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ProviderFusionError(f"{label} must be a list")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ProviderFusionError(f"{label} is invalid")
    return value.strip()


def _date_text(value: Any, label: str) -> str:
    text = _text(value, label)
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError as error:
        raise ProviderFusionError(f"{label} is invalid") from error
    return text


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProviderFusionError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ProviderFusionError(f"{label} must be finite")
    return result
