"""Command-line interface for the AeroForge workflow orchestrator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from src.orchestrator.aircraft_types import AircraftType, list_types
from src.orchestrator.init_wizard import run_project_init_wizard
from src.orchestrator.project_settings import (
    PROJECT_SETTINGS_FILE,
    ProjectScope,
    save_project_settings,
)
from src.orchestrator.server import WorkflowMonitorServer
from src.orchestrator.state_manager import StepStatus, WorkflowStep, WORKFLOW_STEPS, StateManager
from src.orchestrator.workflow_engine import WorkflowEngine


class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    CYAN = "\033[96m"


def _color_status(status: str) -> str:
    colors = {
        StepStatus.DONE.value: _C.GREEN,
        StepStatus.RUNNING.value: _C.YELLOW,
        StepStatus.FAILED.value: _C.RED,
        StepStatus.PENDING.value: _C.GRAY,
        StepStatus.SKIPPED.value: _C.DIM,
    }
    color = colors.get(status, "")
    return f"{color}{status}{_C.RESET}"


def _icon_status(status: str) -> str:
    icons = {
        StepStatus.DONE.value: "+",
        StepStatus.RUNNING.value: ">",
        StepStatus.FAILED.value: "X",
        StepStatus.PENDING.value: "o",
        StepStatus.SKIPPED.value: "-",
    }
    return icons.get(status, "?")


def cmd_status(args: argparse.Namespace) -> None:
    sm = StateManager()
    state = sm.load()
    project = state.get("project", "No project")
    iteration = state.get("current_iteration", "-")
    round_label = state.get("current_round_label", "-")
    ac_type = state.get("aircraft_type", "-")
    active = state.get("active_run")

    print(f"\n{_C.BOLD}{_C.CYAN}{project}{_C.RESET}")
    print(f"  Type: {ac_type}  |  Iteration: {iteration}  |  Round: {round_label}")
    if active:
        print(
            f"  Active: {_C.YELLOW}{active.get('sub_assembly')}:{active.get('step')}{_C.RESET}"
            f"  |  Agent: {active.get('agent') or 'system'}"
        )
    else:
        print(f"  Active: {_C.DIM}none{_C.RESET}")
    print()

    sub_assemblies = state.get("sub_assemblies", {})
    if not sub_assemblies:
        print(f"  {_C.DIM}No sub-assemblies. Start from a profile first.{_C.RESET}")
        return

    header = f"  {'Sub-Assembly':<20s} {'It':>3s} {'Rnd':>7s}  "
    header += " ".join(f"{abbr:>3s}" for abbr in ["REQ", "RES", "AER", "STR", "AR+", "CON", "2D", "3D", "MSH", "VAL", "REL"])
    print(f"{_C.DIM}{header}{_C.RESET}")
    print(f"  {'-' * len(header)}")

    step_names = [step.value for step in WORKFLOW_STEPS]
    for name, sa in sub_assemblies.items():
        row = (
            f"  {name:<20s} {sa.get('current_iteration', 1):>3d} "
            f"{sa.get('current_round_label', '-'):>7s}  "
        )
        step_cells = []
        for step_name in step_names:
            status = sa.get("steps", {}).get(step_name, {}).get("status", StepStatus.PENDING.value)
            step_cells.append(f"{_icon_status(status):>3s}")
        print(row + " ".join(step_cells))

    print()


def cmd_start_legacy(args: argparse.Namespace) -> None:
    engine = WorkflowEngine(n8n_enabled=args.n8n)
    ac_type = AircraftType(args.type)
    state = engine.create_project(
        ac_type,
        args.name,
        metadata={
            "project_code": args.project_code,
            "project_scope": args.project_scope,
            "round_label": args.round,
        },
    )
    print(f"{_C.GREEN}Created project from legacy template: {args.name}{_C.RESET}")
    print(f"  Type: {ac_type.value}")
    print(f"  State file: {engine._sm._path}")
    print(f"  Sub-assemblies: {', '.join(state.get('sub_assemblies', {}).keys())}")


def cmd_start_profile(args: argparse.Namespace) -> None:
    engine = WorkflowEngine(n8n_enabled=args.n8n)
    state = engine.create_project_from_profile_file(
        Path(args.profile),
        args.name,
        metadata={
            "project_code": args.project_code,
        },
    )
    print(f"{_C.GREEN}Created project from profile: {args.name}{_C.RESET}")
    print(f"  Profile: {args.profile}")
    print(f"  Type: {state.get('aircraft_type')}")


def cmd_init(args: argparse.Namespace) -> None:
    settings = run_project_init_wizard(
        project_name=args.name,
        mission_prompt=args.prompt,
        aircraft_type=args.aircraft_type,
        tooling=args.tooling,
        manufacturing=args.manufacturing,
        materials=args.materials,
        production=args.production,
        outputs=args.outputs,
        scope=args.scope,
        top_object=args.top_object,
        project_code=args.project_code,
        current_round=args.current_round,
        next_round=args.next_round,
    )
    target = save_project_settings(settings)
    print(f"{_C.GREEN}Project settings saved{_C.RESET}: {target}")


def cmd_step(args: argparse.Namespace) -> None:
    engine = WorkflowEngine()
    if args.action == "start":
        engine.start_step(args.sub, args.step, agent=args.agent)
        print(f"{_C.YELLOW}Started {args.step} for {args.sub}{_C.RESET}")
        return
    if args.action == "complete":
        output = args.output.split(",") if args.output else None
        engine.complete_step(args.sub, args.step, output_files=output, notes=args.notes or "")
        print(f"{_C.GREEN}Completed {args.step} for {args.sub}{_C.RESET}")
        return
    if args.action == "fail":
        engine.fail_step(args.sub, args.step, reason=args.notes or "")
        print(f"{_C.RED}Failed {args.step} for {args.sub}{_C.RESET}")
        return
    if args.action == "reset":
        engine.reset_step(args.sub, args.step)
        print(f"Reset {args.step} for {args.sub}")
        return
    raise SystemExit(f"Unknown action: {args.action}")


def cmd_dashboard(args: argparse.Namespace) -> None:
    engine = WorkflowEngine()
    path = engine.generate_dashboard()
    print(f"{_C.GREEN}Dashboard generated{_C.RESET}: {path}")


def cmd_history(args: argparse.Namespace) -> None:
    sm = StateManager()
    state = sm.load()
    events = state.get("history", [])[-(args.limit or 20):]
    if not events:
        print(f"{_C.DIM}No history events.{_C.RESET}")
        return
    print(f"\n{_C.BOLD}Recent History{_C.RESET}")
    print("-" * 80)
    for event in reversed(events):
        print(f"  {event.get('timestamp', '-')}  {event.get('event', '-')}")
    print()


def cmd_list_types(args: argparse.Namespace) -> None:
    print(f"\n{_C.BOLD}Legacy Template Types{_C.RESET}")
    print("  Preferred path: use `start-profile` with `aeroforge.yaml`.")
    print("-" * 60)
    for item in list_types():
        print(f"  {_C.CYAN}{item['id']:<15s}{_C.RESET} {item['name']}")
        print(f"  {'':15s} Sub-assemblies: {', '.join(item['sub_assemblies'])}")
        print(f"  {'':15s} {item['description']}")
        print()


def cmd_next(args: argparse.Namespace) -> None:
    engine = WorkflowEngine()
    next_action = engine.get_next_action()
    if not next_action:
        print("No pending action.")
        return
    print(f"{next_action['sub_assembly']} -> {next_action['step']} ({next_action['action']})")


def cmd_rename_round(args: argparse.Namespace) -> None:
    engine = WorkflowEngine()
    engine.rename_round(args.sub, args.label)
    print(f"{_C.GREEN}Renamed {args.sub} round to {args.label}{_C.RESET}")


def cmd_start_iteration(args: argparse.Namespace) -> None:
    engine = WorkflowEngine()
    iteration = engine.start_iteration(args.sub, round_label=args.label)
    print(f"{_C.GREEN}Started iteration {iteration} for {args.sub}{_C.RESET}")


def cmd_serve(args: argparse.Namespace) -> None:
    server = WorkflowMonitorServer(
        host=args.host,
        port=args.port,
        launch_n8n=args.launch_n8n,
    )
    print(f"Serving workflow monitor on http://{args.host}:{args.port}")
    if args.launch_n8n:
        print("Launching n8n on http://127.0.0.1:5678")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="orchestrator",
        description="AeroForge Design Workflow Orchestrator",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_status = sub.add_parser("status", help="Show current workflow status")
    p_status.set_defaults(func=cmd_status)

    p_init = sub.add_parser("init", help="Persist project settings/profile decisions")
    p_init.add_argument("--name", required=True, help="Project name")
    p_init.add_argument("--prompt", required=True, help="Mission prompt or design brief")
    p_init.add_argument("--aircraft-type", help="Aircraft type decided by user/LLM")
    p_init.add_argument("--tooling", help="Selected tooling decided by user/LLM")
    p_init.add_argument("--available-tooling", action="append", help="Additional available tooling ids")
    p_init.add_argument("--manufacturing", action="append", help="Manufacturing strategy entry")
    p_init.add_argument("--materials", action="append", help="Material strategy entry")
    p_init.add_argument("--production", action="append", help="Production strategy entry")
    p_init.add_argument("--outputs", action="append", help="Output artifact entry")
    p_init.add_argument("--scope", default=ProjectScope.AIRCRAFT.value, choices=[scope.value for scope in ProjectScope])
    p_init.add_argument("--top-object", default="Iva_Aeroforge", help="Top assembly or object name")
    p_init.add_argument("--project-code", default="AIR4", help="Project family code")
    p_init.add_argument("--current-round", default="R4", help="Current round label")
    p_init.add_argument("--next-round", default="R5", help="Next round label")
    p_init.set_defaults(func=cmd_init)

    p_start_legacy = sub.add_parser("start", help="Start from legacy hardcoded template registry")
    p_start_legacy.add_argument("--type", required=True, help="Legacy aircraft type enum")
    p_start_legacy.add_argument("--name", required=True, help="Project name")
    p_start_legacy.add_argument("--project-code", default="AIR4")
    p_start_legacy.add_argument("--project-scope", default="aircraft")
    p_start_legacy.add_argument("--round", default="R1")
    p_start_legacy.add_argument("--n8n", action="store_true", help="Enable n8n integration")
    p_start_legacy.set_defaults(func=cmd_start_legacy)

    p_start_profile = sub.add_parser("start-profile", help="Start from the external workflow profile")
    p_start_profile.add_argument("--profile", default=str(PROJECT_SETTINGS_FILE), help="Path to aeroforge.yaml")
    p_start_profile.add_argument("--name", required=True, help="Project name")
    p_start_profile.add_argument("--project-code", default="AIR4")
    p_start_profile.add_argument("--n8n", action="store_true", help="Enable n8n integration")
    p_start_profile.set_defaults(func=cmd_start_profile)

    p_step = sub.add_parser("step", help="Manage a workflow step")
    p_step.add_argument("--sub", required=True, help="Sub-assembly name")
    p_step.add_argument("--step", required=True, choices=[step.value for step in WorkflowStep])
    p_step.add_argument("--action", required=True, choices=["start", "complete", "fail", "reset"])
    p_step.add_argument("--agent", help="Agent name")
    p_step.add_argument("--notes", help="Notes or failure reason")
    p_step.add_argument("--output", help="Comma-separated output files")
    p_step.set_defaults(func=cmd_step)

    p_dash = sub.add_parser("dashboard", help="Generate the HTML dashboard")
    p_dash.set_defaults(func=cmd_dashboard)

    p_hist = sub.add_parser("history", help="Show recent history")
    p_hist.add_argument("--limit", type=int, default=20)
    p_hist.set_defaults(func=cmd_history)

    p_types = sub.add_parser("list-types", help="List legacy template types")
    p_types.set_defaults(func=cmd_list_types)

    p_next = sub.add_parser("next", help="Show next recommended action")
    p_next.set_defaults(func=cmd_next)

    p_round = sub.add_parser("rename-round", help="Rename the tracked round label")
    p_round.add_argument("--sub", required=True, help="Sub-assembly name")
    p_round.add_argument("--label", required=True, help="New round label")
    p_round.set_defaults(func=cmd_rename_round)

    p_iter = sub.add_parser("start-iteration", help="Start a new iteration for one sub-assembly")
    p_iter.add_argument("--sub", required=True, help="Sub-assembly name")
    p_iter.add_argument("--label", help="Optional round label, e.g. R5")
    p_iter.set_defaults(func=cmd_start_iteration)

    p_serve = sub.add_parser("serve", help="Launch the workflow monitor server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8787)
    p_serve.add_argument("--launch-n8n", action="store_true")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
