"""Command-line interface for the first offline InvestKit vertical slice."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from .assets import default_source_root
from .doctor import run_doctor
from .errors import InvestKitError, safe_error_message
from .initializer import initialize_project
from .research.workflow import resume_demo_research, run_demo_research


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="investkit",
        description="Initialize and run an offline investment-research Harness.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser(
        "init",
        help="Initialize the current project for Codex.",
        description="Create InvestKit-owned project state without overwriting files.",
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
        source_root = _default_source_root()
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
    except (InvestKitError, RuntimeError, ValueError, OSError) as error:
        print(f"ERROR: {safe_error_message(error)}", file=sys.stderr)
        return 1
    parser.error("unsupported command")
    return 2


def _default_source_root() -> Path:
    return default_source_root()
