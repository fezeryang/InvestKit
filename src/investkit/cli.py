"""Command-line interface for the first offline InvestKit vertical slice."""

from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import sys
from typing import Sequence

from .assets import default_source_root
from .catalog import ASSET_TYPES, DECISIONS, RUNTIME_STATES, load_asset_catalog
from .doctor import run_doctor
from .environment import load_provider_environment
from .errors import InvestKitError, safe_error_message
from .initializer import initialize_project
from .planning import build_research_plan, evaluate_asset_state
from .providers.ciccwm import CiccwmClient
from .providers.file import FileProvider
from .providers.fusion import (
    fuse_ciccwm_research_bundle,
    fuse_equity_research_bundle,
    fuse_guangfa_target_bundle,
)
from .providers.guangfa import GuangfaClient
from .providers.sse import SseAnnouncementClient
from .research.workflow import (
    resume_demo_research,
    resume_research,
    run_demo_research,
    run_research,
    run_research_bundle,
)


class InvestKitArgumentParser(argparse.ArgumentParser):
    """Argument parser with validated research invocation shapes."""

    def parse_args(  # type: ignore[override]
        self,
        args: Sequence[str] | None = None,
        namespace: argparse.Namespace | None = None,
    ) -> argparse.Namespace:
        parsed = super().parse_args(args, namespace)
        assert parsed is not None
        if getattr(parsed, "command", None) == "research":
            input_path = getattr(parsed, "input", None)
            symbol = getattr(parsed, "symbol", None)
            resume = getattr(parsed, "resume", None)
            question = getattr(parsed, "question", None)
            allow_network = bool(getattr(parsed, "allow_network", False))
            peer = getattr(parsed, "peer", None)
            if (input_path is not None or symbol is not None) and (
                not isinstance(question, str) or not question.strip()
            ):
                self.error("research --input/--symbol requires a non-empty --question")
            if resume is not None and question is not None:
                self.error("research --resume cannot be combined with --question")
            if allow_network and symbol is None:
                self.error("research --allow-network is valid only with --symbol")
            if peer is not None and symbol is None:
                self.error("research --peer is valid only with --symbol")
        return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = InvestKitArgumentParser(
        prog="investkit",
        description="Initialize and run an offline investment-research Harness.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser(
        "init",
        help="Initialize the current project for Codex.",
        description="Create InvestKit-owned project state without overwriting files.",
    )
    assets = commands.add_parser(
        "assets",
        help="Inspect the Investment Research Harness asset catalog.",
        description="List and inspect governed, blocked, unavailable, and reference assets without executing them.",
    )
    asset_commands = assets.add_subparsers(dest="assets_command", required=True)
    asset_list = asset_commands.add_parser("list", help="List catalogued assets.")
    asset_list.add_argument("--type", choices=sorted(ASSET_TYPES))
    asset_list.add_argument("--capability")
    asset_list.add_argument("--decision", choices=sorted(DECISIONS))
    asset_list.add_argument("--state", choices=sorted(RUNTIME_STATES))
    asset_list.add_argument("--json", action="store_true", dest="json_output")
    asset_show = asset_commands.add_parser("show", help="Show one catalogued asset.")
    asset_show.add_argument("asset_id")
    asset_show.add_argument("--json", action="store_true", dest="json_output")
    asset_plan = asset_commands.add_parser(
        "plan", help="Plan capabilities without executing assets."
    )
    asset_plan.add_argument(
        "--capability", action="append", required=True, dest="capabilities"
    )
    asset_plan.add_argument("--type", action="append", choices=sorted(ASSET_TYPES), dest="asset_types")
    asset_plan.add_argument("--allow-network", action="store_true")
    asset_plan.add_argument("--json", action="store_true", dest="json_output")
    imported = commands.add_parser(
        "research",
        help="Research one company from a validated project-local bundle.",
        description=(
            "Run research from --input PATH or an official exchange --symbol, "
            "or resume an existing task with --resume TASK_ID."
        ),
    )
    imported_mode = imported.add_mutually_exclusive_group(required=True)
    imported_mode.add_argument(
        "--input",
        metavar="PATH",
        help="Project-local validated research bundle.",
    )
    imported_mode.add_argument(
        "--symbol",
        metavar="TICKER",
        help="A-share ticker resolved through an approved official exchange provider.",
    )
    imported_mode.add_argument(
        "--resume",
        metavar="TASK_ID",
        help="Resume or inspect an imported research task.",
    )
    imported.add_argument(
        "--question",
        metavar="TEXT",
        help="Non-empty analyst research question (required with --input/--symbol).",
    )
    imported.add_argument(
        "--allow-network",
        action="store_true",
        help="Explicitly permit the allowlisted official lookup used by --symbol.",
    )
    imported.add_argument(
        "--peer",
        metavar="TICKER",
        help="Optional comparison ticker; enables approved multi-provider evidence fusion.",
    )
    commands.add_parser(
        "doctor",
        help="Diagnose the current InvestKit project.",
        description="Run read-only project, asset, and research-state diagnostics.",
    )
    demo = commands.add_parser("demo", help="Run a deterministic offline demo.")
    demo_commands = demo.add_subparsers(dest="demo_command", required=True)
    research = demo_commands.add_parser(
        "research", help="Research the bundled fictional company."
    )
    research.add_argument(
        "--resume",
        metavar="TASK_ID",
        help="Resume or inspect an existing research task.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    project_root = Path.cwd()
    try:
        load_provider_environment(project_root)
        source_root = _default_source_root()
        if args.command == "assets":
            catalog = load_asset_catalog(source_root)
            if args.assets_command == "list":
                matches = catalog.filter(
                    type=args.type,
                    capability=args.capability,
                    decision=args.decision,
                    state=args.state,
                )
                if args.json_output:
                    print(
                        json.dumps(
                            {
                                "schema_version": catalog.schema_version,
                                "catalog_version": catalog.catalog_version,
                                "count": len(matches),
                                "assets": [asset.to_dict() for asset in matches],
                            },
                            ensure_ascii=False,
                            sort_keys=True,
                        )
                    )
                else:
                    for asset in matches:
                        print(f"{asset.id}\t{asset.type}\t{asset.state}\t{asset.name}")
                    print(f"TOTAL {len(matches)}")
                return 0
            if args.assets_command == "show":
                try:
                    asset = catalog.get(args.asset_id)
                except KeyError:
                    print(f"ERROR: asset not found: {args.asset_id}", file=sys.stderr)
                    return 1
                if args.json_output:
                    print(json.dumps(asset.to_dict(), ensure_ascii=False, sort_keys=True))
                else:
                    print(f"ID {asset.id}")
                    print(f"NAME {asset.name}")
                    print(f"TYPE {asset.type}")
                    print(f"STATE {asset.state}")
                    print(f"DECISION {asset.decision}")
                    print(f"CAPABILITIES {', '.join(asset.capabilities)}")
                    if asset.credentials:
                        print(f"CREDENTIALS {', '.join(asset.credentials)}")
                    print(f"REASON {asset.reason}")
                return 0
            if args.assets_command == "plan":
                credential_names = {
                    name
                    for asset in catalog.assets
                    for name in asset.credentials
                    if os.environ.get(name)
                }
                plan = build_research_plan(
                    catalog,
                    capabilities=args.capabilities,
                    required_types=args.asset_types or (),
                    credential_names=credential_names,
                    allow_network=args.allow_network,
                )
                if args.json_output:
                    print(json.dumps(plan.to_dict(), ensure_ascii=False, sort_keys=True))
                else:
                    for item in plan.selected:
                        print(f"SELECT {item.asset_id}: {item.reason}")
                    for item in plan.considered:
                        print(
                            f"SKIP {item.asset_id} [{item.effective_state}]: "
                            f"{item.reason}"
                        )
                    for capability in plan.blocked_capabilities:
                        print(f"BLOCKED {capability}")
                return 0 if plan.runnable else 1
        if args.command == "init":
            result = initialize_project(project_root, source_root=source_root)
            for action in result.actions:
                suffix = f": {action.message}" if action.message else ""
                print(f"{action.action} {action.path}{suffix}")
            return result.exit_code
        if args.command == "doctor":
            report = run_doctor(project_root, source_root=source_root)
            for check in report.checks:
                print(f"[{check.status.value}] {check.name}: {check.message}")
            return report.exit_code
        if args.command == "demo" and args.demo_command == "research":
            if args.resume:
                result = resume_demo_research(
                    project_root,
                    args.resume,
                    source_root,
                )
            else:
                result = run_demo_research(project_root, source_root)
            if result.status == "completed":
                print(f"[PASS] demo research task: {result.task_id}")
                if result.report_path is not None:
                    print(f"REPORT {result.report_path}")
            else:
                print(
                    f"[FAIL] demo research task {result.task_id}: "
                    f"{result.error or 'workflow failed'}",
                    file=sys.stderr,
                )
            return result.exit_code
        if args.command == "research":
            if args.resume:
                result = resume_research(project_root, args.resume, source_root)
                mode = "imported"
            elif args.symbol:
                requested_capabilities = ["security_identification"]
                if args.peer:
                    requested_capabilities.extend(
                        ["company_fundamentals", "financial_statements", "valuation"]
                    )
                catalog = load_asset_catalog(source_root)
                credential_names = {
                    name
                    for name in ("GF_SKILLS_APIKEY", "MX_APIKEY", "CICCWM_API_KEY")
                    if os.environ.get(name)
                }
                plan = build_research_plan(
                    catalog,
                    capabilities=requested_capabilities,
                    required_types=("data_provider",),
                    credential_names=credential_names,
                    allow_network=args.allow_network,
                )
                selected_ids = {item.asset_id for item in plan.selected}
                if not plan.runnable or "sse-announcement-provider" not in selected_ids:
                    raise InvestKitError(
                        "symbol research requires explicit network permission for an approved official provider"
                    )
                bundle = SseAnnouncementClient(
                    allow_network=args.allow_network
                ).acquire_bundle(args.symbol)
                guangfa_target_ready = all(
                    evaluate_asset_state(
                        catalog.get(identifier),
                        credential_names=credential_names,
                        allow_network=args.allow_network,
                    )
                    == "ready"
                    for identifier in ("GF-002", "GF-003")
                )
                if args.peer:
                    if not guangfa_target_ready:
                        raise InvestKitError(
                            "peer research requires an approved Guangfa credential and explicit network permission"
                        )
                    guangfa = GuangfaClient.from_environment(
                        allow_network=args.allow_network
                    )
                    previous_year = date.today().year - 1
                    bundle = fuse_equity_research_bundle(
                        bundle,
                        f10_response=guangfa.stock_f10(args.symbol),
                        valuation_response=guangfa.stock_valuation(args.symbol),
                        peer_valuation_response=guangfa.stock_valuation(args.peer),
                        financial_responses=[
                            guangfa.compare_financials(
                                args.symbol,
                                peer_symbol=args.peer,
                                year=str(year),
                                report_type=12,
                            )
                            for year in (previous_year - 1, previous_year)
                        ],
                        peer_symbol=args.peer,
                    )
                elif guangfa_target_ready:
                    guangfa = GuangfaClient.from_environment(
                        allow_network=args.allow_network
                    )
                    bundle = fuse_guangfa_target_bundle(
                        bundle,
                        f10_response=guangfa.stock_f10(args.symbol),
                        valuation_response=guangfa.stock_valuation(args.symbol),
                    )
                ciccwm_ids = ("CICCWM-001", "CICCWM-002", "CICCWM-003", "CICCWM-005")
                ciccwm_ready = all(
                    evaluate_asset_state(
                        catalog.get(identifier),
                        credential_names=credential_names,
                        allow_network=args.allow_network,
                    )
                    == "ready"
                    for identifier in ciccwm_ids
                )
                if ciccwm_ready:
                    ciccwm = CiccwmClient.from_environment(
                        allow_network=args.allow_network
                    )
                    analysis_year = str(date.today().year - 1)
                    bundle = fuse_ciccwm_research_bundle(
                        bundle,
                        market_info_response=ciccwm.market_info(args.symbol),
                        market_history_response=ciccwm.market_history(args.symbol, days=60),
                        financial_responses={
                            statement: ciccwm.stock_finance(
                                args.symbol,
                                statement=statement,
                                year=analysis_year,
                            )
                            for statement in ("income", "cashflow", "balance", "indicators")
                        },
                        hot_news_response=ciccwm.hot_news(page=1, size=20),
                        dragon_tiger_response=ciccwm.dragon_tiger_list(
                            date=date.today().isoformat()
                        ),
                        dragon_tiger_date=date.today().isoformat(),
                    )
                provider_names = ["sse"]
                if args.peer or guangfa_target_ready:
                    provider_names.append("guangfa")
                if ciccwm_ready:
                    provider_names.append("ciccwm")
                provider = FileProvider.from_mapping(
                    bundle,
                    origin=f"provider:{'+'.join(provider_names)}:{bundle['security']['ticker']}",
                )
                result = run_research_bundle(
                    project_root,
                    source_root,
                    provider=provider,
                    question=args.question,
                    acquisition_mode="official_live",
                )
                mode = "symbol"
            else:
                result = run_research(
                    project_root,
                    source_root,
                    input_path=args.input,
                    question=args.question,
                )
                mode = "imported"
            if result.status == "completed":
                print(f"[PASS] {mode} research task: {result.task_id}")
                if result.report_path is not None:
                    print(f"REPORT {result.report_path}")
            else:
                print(
                    f"[FAIL] imported research task {result.task_id}: "
                    f"{result.error or 'workflow failed'}",
                    file=sys.stderr,
                )
            return result.exit_code
    except (InvestKitError, RuntimeError, ValueError, OSError) as error:
        print(f"ERROR: {safe_error_message(error)}", file=sys.stderr)
        return 1
    parser.error("unsupported command")
    return 2


def _default_source_root() -> Path:
    return default_source_root()
