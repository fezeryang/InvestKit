#!/usr/bin/env python3
"""Build the reproducible A-share innovation-board panorama report.

The pipeline has two deliberately separate modes:

* ``--mode fetch`` downloads declared Sina Market Center pages and preserves
  every response before normalizing it.
* ``--mode offline`` performs no network access and rebuilds all derived
  artifacts from those preserved responses (or the explicitly-labelled legacy
  one-page snapshots used during development).

Sina's public market-centre response supplies a current cross-section but does
not include an explicit trading date or industry classification.  The caller's
``--as-of`` value is therefore retained as a declared research cut-off, not
silently treated as provider-verified metadata.  Interpretive research copy is
read from an optional JSON content file; missing copy remains visibly marked as
pending and is never invented by this script.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import re
import shutil
import statistics
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

try:
    from jinja2 import Environment
except ImportError as exc:  # pragma: no cover - environment contract check
    raise SystemExit("jinja2 is required by the report builder") from exc


REPORT_SLUG = "a-share-innovation-2026-07-17"
DEFAULT_OUTPUT = Path("reports/market") / REPORT_SLUG
SINA_ENDPOINT = (
    "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
    "Market_Center.getHQNodeData"
)
SINA_KLINE_ENDPOINT = (
    "https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20data=/"
    "CN_MarketDataService.getKLineData"
)
INDEX_SPECS = {
    "sh000688": {"name": "科创50", "role": "科创板代表指数"},
    "sz399006": {"name": "创业板指", "role": "创业板代表指数"},
    "bj899050": {"name": "北证50", "role": "北交所代表指数；代码有效性以响应校验"},
    "sh000300": {"name": "沪深300", "role": "大盘风格参照"},
    "sh000852": {"name": "中证1000", "role": "小盘风格参照"},
}
# The host environment may define a localhost proxy that cannot reach public
# data services.  Fetch mode deliberately bypasses inherited proxy variables
# without mutating process-wide environment state.
NETWORK_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
PAGE_SIZE = 100
BOARD_SPECS = {
    "kcb": {
        "name": "科创板",
        "short": "STAR",
        "legacy": "sina-star-2026-07-17.json",
        "code_pattern": r"^(688|689)\d{3}$",
        "color": "#3478F6",
    },
    "cyb": {
        "name": "创业板",
        "short": "ChiNext",
        "legacy": "sina-chinext-2026-07-17.json",
        "code_pattern": r"^(300|301|302)\d{3}$",
        "color": "#13A37A",
    },
    "hs_bjs": {
        "name": "北交所",
        "short": "BSE",
        "legacy": "sina-bse-2026-07-17.json",
        "code_pattern": r"^\d{6}$",
        "color": "#F59E0B",
    },
}
NUMERIC_FIELDS = (
    "trade",
    "pricechange",
    "changepercent",
    "settlement",
    "open",
    "high",
    "low",
    "volume",
    "amount",
    "per",
    "pb",
    "mktcap",
    "nmc",
    "turnoverratio",
)


@dataclass(frozen=True)
class SnapshotPage:
    board: str
    page: int
    path: Path
    records: tuple[dict[str, Any], ...]
    sha256: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_sina_payload(payload: bytes) -> list[dict[str, Any]]:
    """Parse JSON while tolerating a UTF-8 BOM and a JSONP wrapper."""
    text = payload.decode("utf-8-sig").strip()
    if not text:
        return []
    if not text.startswith("["):
        match = re.search(r"(\[.*\])", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Sina response was neither a JSON array nor JSONP")
        text = match.group(1)
    value = json.loads(text)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError("Sina response must be an array of objects")
    return value


def fetch_page(board: str, page: int, timeout: float) -> tuple[bytes, str]:
    query = urllib.parse.urlencode(
        {
            "page": page,
            "num": PAGE_SIZE,
            "sort": "symbol",
            "asc": 1,
            "node": board,
            "symbol": "",
            "_s_r_a": "page",
        }
    )
    url = f"{SINA_ENDPOINT}?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "InvestKit/0.3 research snapshot (no trading)",
        },
    )
    with NETWORK_OPENER.open(request, timeout=timeout) as response:
        return response.read(), url


def parse_kline_payload(payload: bytes) -> list[dict[str, Any]]:
    text = payload.decode("utf-8-sig").strip()
    match = re.search(r"(\[.*\])", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Sina K-line response did not contain a JSON array")
    value = json.loads(match.group(1))
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError("Sina K-line response must contain an array of objects")
    return value


def fetch_kline_snapshots(
    output_dir: Path, *, timeout: float, length: int = 250
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    raw_root = output_dir / "raw" / "sina-index-kline"
    raw_root.mkdir(parents=True, exist_ok=True)
    result: dict[str, list[dict[str, Any]]] = {}
    symbols: dict[str, Any] = {}
    for symbol, spec in INDEX_SPECS.items():
        query = urllib.parse.urlencode(
            {"symbol": symbol, "scale": 240, "ma": "no", "datalen": length}
        )
        url = f"{SINA_KLINE_ENDPOINT}?{query}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json,text/plain,*/*",
                "User-Agent": "InvestKit/0.3 research snapshot (no trading)",
            },
        )
        with NETWORK_OPENER.open(request, timeout=timeout) as response:
            payload = response.read()
        rows = parse_kline_payload(payload)
        if not rows:
            raise RuntimeError(f"No K-line observations returned for {symbol} ({spec['name']})")
        dates = [str(row.get("day") or "")[:10] for row in rows]
        if any(not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) for day in dates):
            raise ValueError(f"Invalid K-line date returned for {symbol}")
        if dates != sorted(dates) or len(set(dates)) != len(dates):
            raise ValueError(f"K-line dates for {symbol} are not unique ascending observations")
        path = raw_root / f"{symbol}-daily-250.jsonp"
        path.write_bytes(payload)
        meta = {
            "symbol": symbol,
            "name": spec["name"],
            "role": spec["role"],
            "request_url": url,
            "retrieved_at_utc": utc_now(),
            "record_count": len(rows),
            "first_date": dates[0],
            "last_date": dates[-1],
            "sha256": sha256_bytes(payload),
        }
        write_json(path.with_suffix(".meta.json"), meta)
        result[symbol] = rows
        symbols[symbol] = meta
    manifest = {
        "schema_version": "1.0.0",
        "source_id": "sina-cn-market-data-service-kline",
        "source_title": "新浪行情指数日线公开接口",
        "endpoint": SINA_KLINE_ENDPOINT,
        "symbols": symbols,
        "limitations": [
            "日线仅用于研究上下文，非交易执行行情。",
            "250 条记录不足以支持完整市场周期或无偏策略回测。",
        ],
    }
    write_json(raw_root / "manifest.json", manifest)
    return result, manifest


def load_kline_snapshots(
    output_dir: Path,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    raw_root = output_dir / "raw" / "sina-index-kline"
    manifest_path = raw_root / "manifest.json"
    if not manifest_path.exists():
        return {}, {
            "schema_version": "1.0.0",
            "source_id": "sina-cn-market-data-service-kline",
            "symbols": {},
            "limitations": ["离线目录没有指数日线快照；历史指标为未知。"],
        }
    manifest = load_json(manifest_path)
    result: dict[str, list[dict[str, Any]]] = {}
    for symbol in INDEX_SPECS:
        path = raw_root / f"{symbol}-daily-250.jsonp"
        if not path.exists():
            continue
        result[symbol] = parse_kline_payload(path.read_bytes())
    return result, manifest


def fetch_snapshots(
    output_dir: Path,
    *,
    timeout: float,
    max_pages: int,
    pause: float,
) -> tuple[list[SnapshotPage], dict[str, Any]]:
    raw_root = output_dir / "raw" / "sina-market-center"
    fetched_at = utc_now()
    pages: list[SnapshotPage] = []
    board_status: dict[str, Any] = {}
    for board in BOARD_SPECS:
        board_dir = raw_root / board
        board_dir.mkdir(parents=True, exist_ok=True)
        nonempty_pages = 0
        record_count = 0
        terminated_by_empty_page = False
        for page_number in range(1, max_pages + 1):
            payload, url = fetch_page(board, page_number, timeout)
            records = parse_sina_payload(payload)
            raw_path = board_dir / f"page-{page_number:04d}.json"
            raw_path.write_bytes(payload)
            page_meta = {
                "board": board,
                "page": page_number,
                "page_size": PAGE_SIZE,
                "record_count": len(records),
                "retrieved_at_utc": utc_now(),
                "request_url": url,
                "sha256": sha256_bytes(payload),
                "source": "Sina Market Center public endpoint",
            }
            write_json(raw_path.with_suffix(".meta.json"), page_meta)
            if not records:
                terminated_by_empty_page = True
                break
            snapshot = SnapshotPage(
                board=board,
                page=page_number,
                path=raw_path,
                records=tuple(records),
                sha256=page_meta["sha256"],
            )
            pages.append(snapshot)
            nonempty_pages += 1
            record_count += len(records)
            if len(records) < PAGE_SIZE:
                # A short terminal page is sufficient evidence that pagination
                # reached the end; still record the precise termination type.
                terminated_by_empty_page = True
                break
            if pause:
                time.sleep(pause)
        board_status[board] = {
            "name": BOARD_SPECS[board]["name"],
            "nonempty_pages": nonempty_pages,
            "record_count": record_count,
            "pagination_complete": terminated_by_empty_page,
        }
        if not terminated_by_empty_page:
            raise RuntimeError(
                f"{board} pagination did not terminate before --max-pages={max_pages}"
            )
    manifest = {
        "schema_version": "1.0.0",
        "mode": "fetch",
        "source_id": "sina-market-center-hq-node-data",
        "source_title": "新浪财经行情中心板块行情公开接口",
        "endpoint": SINA_ENDPOINT,
        "retrieved_at_utc": fetched_at,
        "page_size": PAGE_SIZE,
        "boards": board_status,
        "limitations": [
            "响应未提供可机器验证的交易日期；as-of 为调用方声明的研究截止日。",
            "响应未提供行业、研发、财务质量、历史收益或停牌状态字段。",
            "公开接口可能调整字段、覆盖范围或访问策略。",
        ],
    }
    write_json(raw_root / "manifest.json", manifest)
    return pages, manifest


def load_saved_snapshots(output_dir: Path) -> tuple[list[SnapshotPage], dict[str, Any]]:
    raw_root = output_dir / "raw" / "sina-market-center"
    manifest_path = raw_root / "manifest.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        pages: list[SnapshotPage] = []
        for board in BOARD_SPECS:
            paths = sorted((raw_root / board).glob("page-[0-9][0-9][0-9][0-9].json"))
            for path in paths:
                page_number = int(path.stem.split("-")[-1])
                payload = path.read_bytes()
                records = parse_sina_payload(payload)
                if not records:
                    continue
                pages.append(
                    SnapshotPage(
                        board=board,
                        page=page_number,
                        path=path,
                        records=tuple(records),
                        sha256=sha256_bytes(payload),
                    )
                )
        if not pages:
            raise RuntimeError(f"No non-empty raw pages found below {raw_root}")
        return pages, manifest

    # Development compatibility: the three existing files are deliberately
    # labelled incomplete.  They let offline rendering be tested without ever
    # being accepted as a full-universe research snapshot.
    legacy_pages: list[SnapshotPage] = []
    for board, spec in BOARD_SPECS.items():
        path = output_dir / "data" / spec["legacy"]
        if not path.exists():
            raise FileNotFoundError(
                f"No saved raw manifest and legacy snapshot is missing: {path}"
            )
        payload = path.read_bytes()
        records = parse_sina_payload(payload)
        legacy_pages.append(
            SnapshotPage(board, 1, path, tuple(records), sha256_bytes(payload))
        )
    manifest = {
        "schema_version": "1.0.0",
        "mode": "offline-legacy-smoke-test",
        "source_id": "sina-market-center-hq-node-data",
        "source_title": "新浪财经行情中心板块行情公开接口",
        "retrieved_at_utc": None,
        "page_size": PAGE_SIZE,
        "boards": {
            board: {
                "name": spec["name"],
                "nonempty_pages": 1,
                "record_count": len(legacy_pages[index].records),
                "pagination_complete": False,
            }
            for index, (board, spec) in enumerate(BOARD_SPECS.items())
        },
        "limitations": [
            "仅含每板首 100 条记录，用于离线流水线冒烟测试，不是全样本。",
            "原始响应未附抓取元数据；交易日期不可由响应独立验证。",
            "不得从该快照形成全市场研究结论。",
        ],
    }
    return legacy_pages, manifest


def to_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
    else:
        text = str(value).strip().replace(",", "")
        if text in {"", "--", "None", "null", "nan"}:
            return None
        try:
            result = float(text)
        except ValueError:
            return None
    return result if math.isfinite(result) else None


def normalize_rows(pages: Sequence[SnapshotPage]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for snapshot in sorted(pages, key=lambda item: (item.board, item.page)):
        spec = BOARD_SPECS[snapshot.board]
        for raw in snapshot.records:
            code = str(raw.get("code") or "").strip()
            symbol = str(raw.get("symbol") or "").strip().lower()
            if not re.fullmatch(spec["code_pattern"], code):
                raise ValueError(f"Invalid {spec['name']} code {code!r} in {snapshot.path}")
            if code in seen:
                raise ValueError(
                    f"Duplicate security code {code} in {snapshot.board}; first seen in {seen[code]}"
                )
            seen[code] = str(snapshot.path)
            numeric = {field: to_number(raw.get(field)) for field in NUMERIC_FIELDS}
            row = {
                "board_id": snapshot.board,
                "board": spec["name"],
                "code": code,
                "symbol": symbol,
                "name": str(raw.get("name") or "").strip(),
                "last_price_cny": numeric["trade"],
                "change_pct": numeric["changepercent"],
                "previous_close_cny": numeric["settlement"],
                "open_cny": numeric["open"],
                "high_cny": numeric["high"],
                "low_cny": numeric["low"],
                "volume_shares": numeric["volume"],
                "amount_cny": numeric["amount"],
                "pe_reported": numeric["per"],
                "pb_reported": numeric["pb"],
                # Sina's market-cap fields are observed to be in CNY 10k.
                # The original fields remain in the CSV for auditability.
                "market_cap_cny_10k": numeric["mktcap"],
                "market_cap_cny": (
                    numeric["mktcap"] * 10_000 if numeric["mktcap"] is not None else None
                ),
                "float_market_cap_cny_10k": numeric["nmc"],
                "float_market_cap_cny": (
                    numeric["nmc"] * 10_000 if numeric["nmc"] is not None else None
                ),
                "turnover_pct": numeric["turnoverratio"],
                "tick_time": str(raw.get("ticktime") or "").strip() or None,
                "source_page": str(snapshot.path),
                "source_page_sha256": snapshot.sha256,
            }
            rows.append(row)
    return sorted(rows, key=lambda row: (row["board_id"], row["code"]))


def write_normalized_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Cannot write an empty normalized universe")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def present(values: Iterable[float | None]) -> list[float]:
    return [value for value in values if value is not None and math.isfinite(value)]


def percentile(values: Sequence[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def safe_median(values: Iterable[float | None]) -> float | None:
    clean = present(values)
    return statistics.median(clean) if clean else None


def safe_sum(values: Iterable[float | None]) -> float | None:
    clean = present(values)
    return sum(clean) if clean else None


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def compute_statistics(
    rows: Sequence[dict[str, Any]],
    manifest: dict[str, Any],
    as_of: str,
    klines: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    board_stats: dict[str, Any] = {}
    for board_id, spec in BOARD_SPECS.items():
        subset = [row for row in rows if row["board_id"] == board_id]
        changes = present(row["change_pct"] for row in subset)
        caps = present(row["market_cap_cny"] for row in subset)
        amounts = present(row["amount_cny"] for row in subset)
        turnovers = present(row["turnover_pct"] for row in subset)
        positive_pe = [
            row["pe_reported"]
            for row in subset
            if row["pe_reported"] is not None and row["pe_reported"] > 0
        ]
        positive_pb = [
            row["pb_reported"]
            for row in subset
            if row["pb_reported"] is not None and row["pb_reported"] > 0
        ]
        total_cap = sum(caps)
        top_caps = sorted(caps, reverse=True)[:10]
        board_stats[board_id] = {
            "name": spec["name"],
            "count": len(subset),
            "market_cap_total_cny": total_cap,
            "market_cap_median_cny": safe_median(caps),
            "amount_total_cny": sum(amounts),
            "amount_median_cny": safe_median(amounts),
            "turnover_median_pct": safe_median(turnovers),
            "change_median_pct": safe_median(changes),
            "change_q25_pct": percentile(changes, 0.25),
            "change_q75_pct": percentile(changes, 0.75),
            "advance_count": sum(1 for value in changes if value > 0),
            "flat_count": sum(1 for value in changes if value == 0),
            "decline_count": sum(1 for value in changes if value < 0),
            "advance_ratio": ratio(sum(1 for value in changes if value > 0), len(changes)),
            "pe_positive_median": safe_median(positive_pe),
            "pe_positive_coverage": ratio(len(positive_pe), len(subset)),
            "pb_positive_median": safe_median(positive_pb),
            "pb_positive_coverage": ratio(len(positive_pb), len(subset)),
            "top10_market_cap_share": ratio(sum(top_caps), total_cap),
            "pagination_complete": bool(
                manifest.get("boards", {}).get(board_id, {}).get("pagination_complete")
            ),
        }
    missing: dict[str, Any] = {}
    measured_fields = (
        "last_price_cny",
        "change_pct",
        "amount_cny",
        "market_cap_cny",
        "turnover_pct",
        "pe_reported",
        "pb_reported",
    )
    for field in measured_fields:
        count = sum(1 for row in rows if row[field] is None)
        missing[field] = {"count": count, "ratio": ratio(count, len(rows))}
    provider_pagination_complete = all(
        item["pagination_complete"] for item in board_stats.values()
    )
    warnings = list(manifest.get("limitations") or [])
    if not provider_pagination_complete:
        warnings.insert(0, "分页未被完整证明；当前输出仅用于流水线验证，不得称为全样本。")
    else:
        warnings.insert(
            0,
            "三个行情节点均已抓取至终止页，但未以交易所正式证券名录独立核验上市证券全量覆盖；2337 仅表示提供方返回的有效行情观测。",
        )
    index_metrics = compute_index_metrics(klines or {}, as_of)
    if not index_metrics:
        warnings.append("指数日线快照不可用；20/60日、年初至今、波动和回撤指标为未知。")
    return {
        "schema_version": "1.0.0",
        "as_of_declared": as_of,
        "generated_at_utc": utc_now(),
        "universe_count": len(rows),
        "provider_pagination_complete": provider_pagination_complete,
        "universe_complete": False,
        "board_statistics": board_stats,
        "missingness": missing,
        "index_metrics": index_metrics,
        "warnings": warnings,
        "definitions": {
            "market_cap_cny": "Sina mktcap × 10,000; original field retained",
            "amount_cny": "provider-reported daily transaction amount in CNY",
            "advance_ratio": "positive change_pct observations / non-missing change_pct observations",
            "positive_pe": "provider-reported PE > 0; loss-making and missing observations excluded",
        },
    }


def sample_return(closes: Sequence[float], sessions: int) -> float | None:
    if len(closes) <= sessions or closes[-sessions - 1] == 0:
        return None
    return closes[-1] / closes[-sessions - 1] - 1


def compute_index_metrics(
    klines: dict[str, list[dict[str, Any]]], as_of: str
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    cutoff = as_of[:4] + "-01-01"
    for symbol, raw_rows in klines.items():
        observations = []
        for row in raw_rows:
            day = str(row.get("day") or "")[:10]
            close = to_number(row.get("close"))
            if close is not None and close > 0 and day <= as_of:
                observations.append((day, close))
        observations.sort()
        if len(observations) < 2:
            continue
        days = [item[0] for item in observations]
        closes = [item[1] for item in observations]
        log_returns = [
            math.log(closes[index] / closes[index - 1])
            for index in range(1, len(closes))
        ]
        annualized_vol = (
            statistics.stdev(log_returns) * math.sqrt(242)
            if len(log_returns) > 1
            else None
        )
        peak = closes[0]
        max_drawdown = 0.0
        for close in closes:
            peak = max(peak, close)
            max_drawdown = min(max_drawdown, close / peak - 1)
        prior_year = [close for day, close in observations if day < cutoff]
        ytd_return = (
            closes[-1] / prior_year[-1] - 1 if prior_year and prior_year[-1] else None
        )
        result[symbol] = {
            "symbol": symbol,
            "name": INDEX_SPECS[symbol]["name"],
            "role": INDEX_SPECS[symbol]["role"],
            "first_date": days[0],
            "last_date": days[-1],
            "observation_count": len(observations),
            "return_20d": sample_return(closes, 20),
            "return_60d": sample_return(closes, 60),
            "return_ytd": ytd_return,
            "return_1y_240d": sample_return(closes, 240),
            "annualized_vol_242d": annualized_vol,
            "max_drawdown_window": max_drawdown,
        }
    return result


def fmt_number(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "未知"
    return f"{value:,.{digits}f}"


def fmt_pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "未知"
    return f"{value * 100:.{digits}f}%"


def fmt_cny_yi(value: float | None) -> str:
    if value is None:
        return "未知"
    return f"{value / 100_000_000:,.1f} 亿元"


def svg_document(width: int, height: int, content: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">'
        "<style>text{font-family:'Noto Sans CJK SC','Microsoft YaHei','PingFang SC',sans-serif;}"
        ".axis{fill:#64748b;font-size:12px}.label{fill:#132238;font-size:13px}"
        ".title{fill:#0f172a;font-size:18px;font-weight:700}.grid{stroke:#e2e8f0;stroke-width:1}</style>"
        f'<rect width="100%" height="100%" fill="#ffffff" rx="14"/>'
        f'<text x="28" y="34" class="title">{html.escape(title)}</text>{content}</svg>'
    )


def save_svg(path: Path, body: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path.name


def bar_chart(
    path: Path,
    title: str,
    labels: Sequence[str],
    values: Sequence[float | None],
    colors: Sequence[str],
    *,
    value_format=lambda value: fmt_number(value),
) -> str:
    width, height = 760, 360
    clean = [0 if value is None else max(0, float(value)) for value in values]
    maximum = max(clean) if clean else 1
    maximum = maximum or 1
    left, top, plot_width, plot_height = 90, 65, 630, 220
    parts: list[str] = []
    for tick in range(5):
        y = top + plot_height - tick * plot_height / 4
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_width}" y2="{y:.1f}" class="grid"/>')
    slot = plot_width / max(1, len(labels))
    for index, (label, value, color) in enumerate(zip(labels, clean, colors)):
        bar_width = slot * 0.48
        bar_height = value / maximum * plot_height
        x = left + index * slot + (slot - bar_width) / 2
        y = top + plot_height - bar_height
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="5" fill="{color}"/>')
        parts.append(f'<text x="{x+bar_width/2:.1f}" y="{max(55,y-9):.1f}" text-anchor="middle" class="label">{html.escape(value_format(values[index]))}</text>')
        parts.append(f'<text x="{x+bar_width/2:.1f}" y="{top+plot_height+28:.1f}" text-anchor="middle" class="label">{html.escape(label)}</text>')
    return save_svg(path, svg_document(width, height, "".join(parts), title))


def diverging_bar_chart(
    path: Path,
    title: str,
    labels: Sequence[str],
    values: Sequence[float | None],
    colors: Sequence[str],
) -> str:
    width, height = 760, 360
    clean = [0 if value is None else float(value) for value in values]
    bound = max([abs(value) for value in clean] + [1.0])
    left, top, plot_width, plot_height = 90, 65, 630, 220
    zero_y = top + plot_height / 2
    parts = [f'<line x1="{left}" y1="{zero_y}" x2="{left+plot_width}" y2="{zero_y}" stroke="#94a3b8" stroke-width="1.5"/>']
    slot = plot_width / max(1, len(labels))
    for index, (label, value, color) in enumerate(zip(labels, clean, colors)):
        bar_width = slot * 0.48
        bar_height = abs(value) / bound * plot_height / 2
        x = left + index * slot + (slot - bar_width) / 2
        y = zero_y - bar_height if value >= 0 else zero_y
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="5" fill="{color}"/>')
        label_y = (
            y - 8
            if value >= 0
            else min(top + plot_height - 12, y + bar_height + 18)
        )
        parts.append(f'<text x="{x+bar_width/2:.1f}" y="{label_y:.1f}" text-anchor="middle" class="label">{fmt_number(value,2)}%</text>')
        parts.append(f'<text x="{x+bar_width/2:.1f}" y="{top+plot_height+28}" text-anchor="middle" class="label">{html.escape(label)}</text>')
    return save_svg(path, svg_document(width, height, "".join(parts), title))


def histogram_chart(
    path: Path,
    title: str,
    values_by_board: dict[str, Sequence[float]],
    *,
    bins: int = 18,
    clip: tuple[float, float] | None = None,
    suffix: str = "",
) -> str:
    width, height = 760, 380
    all_values = [value for values in values_by_board.values() for value in values]
    if clip:
        lower, upper = clip
    elif all_values:
        lower = percentile(all_values, 0.02) or min(all_values)
        upper = percentile(all_values, 0.98) or max(all_values)
    else:
        lower, upper = 0.0, 1.0
    if lower == upper:
        upper = lower + 1
    bin_width = (upper - lower) / bins
    series: dict[str, list[int]] = {}
    maximum = 1
    for board, values in values_by_board.items():
        counts = [0] * bins
        for value in values:
            if lower <= value <= upper:
                index = min(bins - 1, int((value - lower) / bin_width))
                counts[index] += 1
        series[board] = counts
        maximum = max(maximum, max(counts, default=0))
    left, top, plot_width, plot_height = 70, 65, 660, 240
    parts: list[str] = []
    for tick in range(5):
        y = top + plot_height - tick * plot_height / 4
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_width}" y2="{y:.1f}" class="grid"/>')
    for series_index, (board, counts) in enumerate(series.items()):
        color = BOARD_SPECS[board]["color"]
        for index, count in enumerate(counts):
            x = left + index * plot_width / bins
            bar_width = plot_width / bins
            bar_height = count / maximum * plot_height
            opacity = 0.42 + series_index * 0.16
            parts.append(f'<rect x="{x:.1f}" y="{top+plot_height-bar_height:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{color}" opacity="{opacity:.2f}"/>')
        legend_x = 80 + series_index * 150
        parts.append(f'<rect x="{legend_x}" y="330" width="14" height="14" fill="{color}" opacity="0.7"/>')
        parts.append(f'<text x="{legend_x+21}" y="342" class="label">{BOARD_SPECS[board]["name"]}</text>')
    for tick in range(5):
        value = lower + tick * (upper - lower) / 4
        x = left + tick * plot_width / 4
        parts.append(f'<text x="{x:.1f}" y="{top+plot_height+23}" text-anchor="middle" class="axis">{value:.1f}{html.escape(suffix)}</text>')
    return save_svg(path, svg_document(width, height, "".join(parts), title))


def breadth_chart(path: Path, stats: dict[str, Any]) -> str:
    width, height = 760, 350
    left, top, plot_width = 140, 70, 560
    parts: list[str] = []
    colors = {"advance_count": "#12A174", "flat_count": "#94A3B8", "decline_count": "#E55353"}
    for index, (board, item) in enumerate(stats.items()):
        y = top + index * 74
        total = max(1, item["advance_count"] + item["flat_count"] + item["decline_count"])
        cursor = left
        for key in ("advance_count", "flat_count", "decline_count"):
            width_part = plot_width * item[key] / total
            parts.append(f'<rect x="{cursor:.1f}" y="{y}" width="{width_part:.1f}" height="34" fill="{colors[key]}"/>')
            if width_part > 28:
                parts.append(f'<text x="{cursor+width_part/2:.1f}" y="{y+23}" text-anchor="middle" fill="#fff" font-size="12">{item[key]}</text>')
            cursor += width_part
        parts.append(f'<text x="{left-15}" y="{y+23}" text-anchor="end" class="label">{item["name"]}</text>')
    legend = [("上涨", "#12A174"), ("平盘", "#94A3B8"), ("下跌", "#E55353")]
    for index, (label, color) in enumerate(legend):
        x = 230 + index * 120
        parts.append(f'<rect x="{x}" y="305" width="14" height="14" fill="{color}"/>')
        parts.append(f'<text x="{x+20}" y="317" class="label">{label}</text>')
    return save_svg(path, svg_document(width, height, "".join(parts), "涨跌家数结构"))


def scatter_chart(
    path: Path,
    title: str,
    rows: Sequence[dict[str, Any]],
    x_field: str,
    y_field: str,
    x_label: str,
    y_label: str,
    *,
    log_x: bool = False,
    log_y: bool = False,
) -> str:
    points = [
        row
        for row in rows
        if row[x_field] is not None
        and row[y_field] is not None
        and (not log_x or row[x_field] > 0)
        and (not log_y or row[y_field] > 0)
    ]
    width, height = 760, 410
    left, top, plot_width, plot_height = 90, 65, 620, 275
    if not points:
        body = '<text x="380" y="205" text-anchor="middle" class="label">无可用观测</text>'
        return save_svg(path, svg_document(width, height, body, title))
    xs = [math.log10(row[x_field]) if log_x else row[x_field] for row in points]
    ys = [math.log10(row[y_field]) if log_y else row[y_field] for row in points]
    x_min, x_max = percentile(xs, 0.01) or min(xs), percentile(xs, 0.99) or max(xs)
    y_min, y_max = percentile(ys, 0.01) or min(ys), percentile(ys, 0.99) or max(ys)
    if x_min == x_max:
        x_max += 1
    if y_min == y_max:
        y_max += 1
    parts: list[str] = []
    for tick in range(5):
        x = left + tick * plot_width / 4
        y = top + tick * plot_height / 4
        parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top+plot_height}" class="grid"/>')
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_width}" y2="{y}" class="grid"/>')
    for row, x_value, y_value in zip(points, xs, ys):
        if not (x_min <= x_value <= x_max and y_min <= y_value <= y_max):
            continue
        x = left + (x_value - x_min) / (x_max - x_min) * plot_width
        y = top + plot_height - (y_value - y_min) / (y_max - y_min) * plot_height
        color = BOARD_SPECS[row["board_id"]]["color"]
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{color}" opacity="0.48"><title>{html.escape(row["code"]+" "+row["name"])}</title></circle>')
    parts.append(f'<text x="{left+plot_width/2}" y="{height-24}" text-anchor="middle" class="axis">{html.escape(x_label)}</text>')
    parts.append(f'<text x="20" y="{top+plot_height/2}" transform="rotate(-90 20 {top+plot_height/2})" text-anchor="middle" class="axis">{html.escape(y_label)}</text>')
    return save_svg(path, svg_document(width, height, "".join(parts), title))


def generate_charts(
    output_dir: Path, rows: Sequence[dict[str, Any]], stats: dict[str, Any]
) -> dict[str, str]:
    chart_dir = output_dir / "charts"
    board_stats = stats["board_statistics"]
    labels = [item["name"] for item in board_stats.values()]
    colors = [BOARD_SPECS[key]["color"] for key in board_stats]
    charts: dict[str, str] = {}

    def register(key: str, filename: str) -> None:
        charts[key] = f"charts/{filename}"

    register("count", bar_chart(chart_dir / "01-board-count.svg", "样本证券数量", labels, [item["count"] for item in board_stats.values()], colors, value_format=lambda x: fmt_number(x, 0)))
    register("cap_total", bar_chart(chart_dir / "02-market-cap-total.svg", "总市值（亿元）", labels, [item["market_cap_total_cny"] / 1e8 for item in board_stats.values()], colors))
    register("cap_median", bar_chart(chart_dir / "03-market-cap-median.svg", "市值中位数（亿元）", labels, [(item["market_cap_median_cny"] or 0) / 1e8 for item in board_stats.values()], colors))
    register("amount_total", bar_chart(chart_dir / "04-amount-total.svg", "当日成交额（亿元）", labels, [item["amount_total_cny"] / 1e8 for item in board_stats.values()], colors))
    register("turnover", bar_chart(chart_dir / "05-turnover-median.svg", "换手率中位数", labels, [item["turnover_median_pct"] for item in board_stats.values()], colors, value_format=lambda x: f"{fmt_number(x,2)}%"))
    register("return_median", diverging_bar_chart(chart_dir / "06-return-median.svg", "当日涨跌幅中位数", labels, [item["change_median_pct"] for item in board_stats.values()], colors))
    register("breadth", breadth_chart(chart_dir / "07-market-breadth.svg", board_stats))
    register("pe_median", bar_chart(chart_dir / "08-pe-positive-median.svg", "正值 PE 中位数", labels, [item["pe_positive_median"] for item in board_stats.values()], colors))
    register("pb_median", bar_chart(chart_dir / "09-pb-positive-median.svg", "正值 PB 中位数", labels, [item["pb_positive_median"] for item in board_stats.values()], colors))
    register("concentration", bar_chart(chart_dir / "10-top10-cap-share.svg", "前十大市值集中度", labels, [(item["top10_market_cap_share"] or 0) * 100 for item in board_stats.values()], colors, value_format=lambda x: f"{fmt_number(x,1)}%"))
    changes = {board: present(row["change_pct"] for row in rows if row["board_id"] == board) for board in BOARD_SPECS}
    register("return_hist", histogram_chart(chart_dir / "11-return-distribution.svg", "涨跌幅分布（2%—98%分位截尾展示）", changes, bins=20, suffix="%"))
    pes = {board: [row["pe_reported"] for row in rows if row["board_id"] == board and row["pe_reported"] is not None and 0 < row["pe_reported"] <= 200] for board in BOARD_SPECS}
    register("pe_hist", histogram_chart(chart_dir / "12-pe-distribution.svg", "正值 PE 分布（展示区间 0—200）", pes, bins=20, clip=(0, 200)))
    caps = {board: [math.log10(row["market_cap_cny"] / 1e8) for row in rows if row["board_id"] == board and row["market_cap_cny"] and row["market_cap_cny"] > 0] for board in BOARD_SPECS}
    register("cap_hist", histogram_chart(chart_dir / "13-market-cap-log-distribution.svg", "市值分布（log10 亿元）", caps, bins=20))
    register("liquidity_return", scatter_chart(chart_dir / "14-liquidity-return.svg", "成交额与涨跌幅截面", rows, "amount_cny", "change_pct", "成交额（对数刻度）", "涨跌幅（%）", log_x=True))
    register("cap_turnover", scatter_chart(chart_dir / "15-cap-turnover.svg", "市值与换手率截面", rows, "market_cap_cny", "turnover_pct", "总市值（对数刻度）", "换手率（%）", log_x=True))
    register("valuation_map", scatter_chart(chart_dir / "16-valuation-map.svg", "正值 PE / PB 估值截面", [row for row in rows if row["pe_reported"] and row["pe_reported"] > 0 and row["pb_reported"] and row["pb_reported"] > 0], "pe_reported", "pb_reported", "PE（对数刻度）", "PB（对数刻度）", log_x=True, log_y=True))
    index_metrics = stats.get("index_metrics") or {}
    if index_metrics:
        index_labels = [item["name"] for item in index_metrics.values()]
        index_colors = ["#3478F6", "#13A37A", "#F59E0B", "#64748B", "#8B5CF6"][: len(index_labels)]
        register("index_20d", diverging_bar_chart(chart_dir / "17-index-20d-return.svg", "代表指数近 20 个交易日收益", index_labels, [(item["return_20d"] or 0) * 100 for item in index_metrics.values()], index_colors))
        register("index_ytd", diverging_bar_chart(chart_dir / "18-index-ytd-return.svg", "代表指数年初至今收益", index_labels, [(item["return_ytd"] or 0) * 100 for item in index_metrics.values()], index_colors))
        register("index_vol", bar_chart(chart_dir / "19-index-volatility.svg", "代表指数年化波动率（242 日）", index_labels, [(item["annualized_vol_242d"] or 0) * 100 for item in index_metrics.values()], index_colors, value_format=lambda x: f"{fmt_number(x,1)}%"))
        register("index_drawdown", diverging_bar_chart(chart_dir / "20-index-drawdown.svg", "250 条日线窗口最大回撤", index_labels, [(item["max_drawdown_window"] or 0) * 100 for item in index_metrics.values()], index_colors))
    return charts


def default_content() -> dict[str, Any]:
    pending = "【待主研究流程补充】本段必须引用已登记来源，并标注事实、计算、推断、情景或未知。"
    return {
        "title": "A股创新板块全景研究",
        "subtitle": "科创板 · 创业板 · 北京证券交易所",
        "executive_summary": [pending],
        "regime_observations": [pending],
        "innovation_framework": [pending],
        "industry_clusters": [],
        "counter_evidence": [pending],
        "scenario_analysis": [],
        "watchlist_method": [pending],
        "risks": [pending],
        "conclusion": [pending],
        "sources": [],
        "used_skills": [],
    }


def load_content(path: Path | None, output_dir: Path) -> dict[str, Any]:
    template_path = output_dir / "research-content.template.json"
    if not template_path.exists():
        write_json(template_path, default_content())
    if path is None:
        return default_content()
    value = load_json(path)
    if not isinstance(value, dict):
        raise ValueError("Research content must be a JSON object")
    merged = default_content()
    merged.update(value)
    return merged


def load_brief_content(path: Path) -> dict[str, Any]:
    """Convert the task's evidence brief into labelled report content.

    This intentionally supports only the brief's simple headings and bullets;
    it does not attempt general Markdown interpretation or introduce new prose.
    """
    sections: dict[str, list[str]] = {}
    current = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
        elif current and line:
            sections[current].append(line)

    def bullets(name: str, label: str) -> list[str]:
        results = []
        bullet_pattern = re.compile(r"^[-*]\s+|^\d+[.]\s+")
        for line in sections.get(name, []):
            if bullet_pattern.match(line):
                results.append(f"【{label}】{bullet_pattern.sub('', line)}")
        return results

    sources = []
    source_pattern = re.compile(r"^\d+[.]\s+([^：]+)：(.+?)(https?://\S+)$")
    for line in sections.get("一手与高质量来源", []):
        match = source_pattern.match(line)
        if match:
            sources.append(
                {
                    "organization": match.group(1).strip(),
                    "title": match.group(2).strip(" ，,"),
                    "date": "见原文",
                    "url": match.group(3),
                    "use": "事实核验或研究背景",
                }
            )
        elif "新浪财经公开行情 API" in line:
            sources.append(
                {
                    "organization": "新浪财经",
                    "title": "公开行情 API：三板截面与指数日线",
                    "date": "以本地快照元数据为准",
                    "url": SINA_ENDPOINT,
                    "use": "行情节点有效截面与代表指数日线",
                }
            )
    content = default_content()
    content.update(
        {
            "executive_summary": bullets("已确认的事实", "事实"),
            "regime_observations": bullets("非传统分析主线", "研究推断"),
            "innovation_framework": bullets("研究判断框架", "分析框架"),
            "counter_evidence": bullets("必须披露的限制", "限制"),
            "risks": bullets("必须披露的限制", "限制"),
            "watchlist_method": bullets("建议的研究分层（不是买卖评级）", "研究分层"),
            "sources": sources,
        }
    )
    return content


def top_rows(
    rows: Sequence[dict[str, Any]], field: str, *, reverse: bool = True, limit: int = 12
) -> list[dict[str, Any]]:
    available = [row for row in rows if row[field] is not None]
    return sorted(available, key=lambda row: row[field], reverse=reverse)[:limit]


def source_rows(content: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for index, source in enumerate(content.get("sources") or [], start=1):
        if not isinstance(source, dict):
            continue
        result.append(
            {
                "index": index,
                "title": str(source.get("title") or "未命名来源"),
                "organization": str(source.get("organization") or "未知"),
                "date": str(source.get("date") or "未知"),
                "url": str(source.get("url") or ""),
                "use": str(source.get("use") or "待说明"),
            }
        )
    return result


def build_report_html(
    output_dir: Path,
    rows: Sequence[dict[str, Any]],
    stats: dict[str, Any],
    charts: dict[str, str],
    content: dict[str, Any],
) -> Path:
    template_path = Path(__file__).with_name("templates") / "a_share_innovation_report.html.j2"
    if not template_path.exists():
        raise FileNotFoundError(f"Missing report template: {template_path}")
    environment = Environment(autoescape=True, trim_blocks=True, lstrip_blocks=True)
    template = environment.from_string(template_path.read_text(encoding="utf-8"))
    pagination_complete = stats["provider_pagination_complete"]
    context = {
        "content": content,
        "stats": stats,
        "boards": stats["board_statistics"],
        "charts": charts,
        "rows": rows,
        "as_of": stats["as_of_declared"],
        "generated_at": stats["generated_at_utc"],
        "status_label": (
            "行情节点分页完成 · 官方全量未核验"
            if pagination_complete
            else "行情节点分页不完整 / 仅供流水线验证"
        ),
        "status_class": "warning",
        "top_cap": top_rows(rows, "market_cap_cny"),
        "top_amount": top_rows(rows, "amount_cny"),
        "top_gainers": top_rows(rows, "change_pct"),
        "top_decliners": top_rows(rows, "change_pct", reverse=False),
        "top_turnover": top_rows(rows, "turnover_pct"),
        "source_rows": source_rows(content),
        "fmt_number": fmt_number,
        "fmt_pct": fmt_pct,
        "fmt_cny_yi": fmt_cny_yi,
    }
    html_path = output_dir / "report.html"
    html_path.write_text(template.render(**context), encoding="utf-8")
    return html_path


def render_pdf(html_path: Path, pdf_path: Path, chrome: str | None) -> None:
    executable = chrome or shutil.which("google-chrome") or shutil.which("chromium")
    if not executable:
        raise RuntimeError("Google Chrome/Chromium was not found; use --chrome PATH")
    command = [
        executable,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--allow-file-access-from-files",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if completed.returncode != 0 or not pdf_path.exists():
        raise RuntimeError(
            "Chrome PDF rendering failed: "
            + (completed.stderr.strip() or completed.stdout.strip() or "unknown error")
        )


def pdf_page_count(pdf_path: Path) -> int | None:
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        completed = subprocess.run(
            [pdfinfo, str(pdf_path)], capture_output=True, text=True, timeout=30
        )
        match = re.search(r"^Pages:\s+(\d+)", completed.stdout, flags=re.MULTILINE)
        if match:
            return int(match.group(1))
    payload = pdf_path.read_bytes()
    count = len(re.findall(rb"/Type\s*/Page\b", payload))
    return count or None


def build_metadata(
    output_dir: Path,
    mode: str,
    manifest: dict[str, Any],
    stats: dict[str, Any],
    charts: dict[str, str],
    html_path: Path,
    pdf_path: Path | None,
) -> dict[str, Any]:
    artifacts: dict[str, Any] = {
        "normalized_csv": "data/universe-normalized.csv",
        "statistics_json": "data/cross-sectional-statistics.json",
        "html": html_path.name,
        "charts": list(charts.values()),
    }
    if pdf_path and pdf_path.exists():
        artifacts["pdf"] = {
            "path": pdf_path.name,
            "bytes": pdf_path.stat().st_size,
            "sha256": sha256_bytes(pdf_path.read_bytes()),
            "pages": pdf_page_count(pdf_path),
        }
    return {
        "schema_version": "1.0.0",
        "pipeline": "scripts/build_a_share_innovation_report.py",
        "mode": mode,
        "generated_at_utc": utc_now(),
        "as_of_declared": stats["as_of_declared"],
        "universe_count": stats["universe_count"],
        "provider_pagination_complete": stats["provider_pagination_complete"],
        "universe_complete": stats["universe_complete"],
        "source_manifest": manifest,
        "artifacts": artifacts,
        "acceptance": {
            "minimum_charts": 10,
            "chart_count": len(charts),
            "minimum_pdf_pages": 15,
            "pdf_page_count": artifacts.get("pdf", {}).get("pages"),
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("fetch", "offline"), required=True)
    parser.add_argument("--as-of", default="2026-07-17", help="Declared research cut-off (YYYY-MM-DD)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--content", type=Path, help="Optional analyst-authored JSON content")
    parser.add_argument("--brief", type=Path, help="Optional labelled Markdown evidence brief")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--pause", type=float, default=0.15)
    parser.add_argument("--chrome", help="Path to Google Chrome/Chromium")
    parser.add_argument("--no-pdf", action="store_true", help="Build data, charts, and HTML only")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.as_of):
        parser.error("--as-of must use YYYY-MM-DD")
    if args.max_pages < 1:
        parser.error("--max-pages must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "fetch":
        pages, manifest = fetch_snapshots(
            output_dir,
            timeout=args.timeout,
            max_pages=args.max_pages,
            pause=args.pause,
        )
        klines, kline_manifest = fetch_kline_snapshots(
            output_dir, timeout=args.timeout
        )
    else:
        pages, manifest = load_saved_snapshots(output_dir)
        klines, kline_manifest = load_kline_snapshots(output_dir)

    rows = normalize_rows(pages)
    manifest = {**manifest, "index_kline": kline_manifest}
    stats = compute_statistics(rows, manifest, args.as_of, klines)
    data_dir = output_dir / "data"
    write_normalized_csv(data_dir / "universe-normalized.csv", rows)
    write_json(data_dir / "cross-sectional-statistics.json", stats)
    charts = generate_charts(output_dir, rows, stats)
    if args.content and args.brief:
        raise ValueError("Use either --content or --brief, not both")
    content = (
        load_brief_content(args.brief)
        if args.brief
        else load_content(args.content, output_dir)
    )
    html_path = build_report_html(output_dir, rows, stats, charts, content)
    pdf_path: Path | None = None
    if not args.no_pdf:
        pdf_path = output_dir / "report.pdf"
        render_pdf(html_path, pdf_path, args.chrome)
    metadata = build_metadata(
        output_dir, args.mode, manifest, stats, charts, html_path, pdf_path
    )
    write_json(output_dir / "build-metadata.json", metadata)
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "universe_count": len(rows),
                "provider_pagination_complete": stats[
                    "provider_pagination_complete"
                ],
                "universe_complete": stats["universe_complete"],
                "chart_count": len(charts),
                "pdf_pages": metadata["acceptance"]["pdf_page_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
