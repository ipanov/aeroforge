"""AeroForge Orchestrator - Iterative aircraft design workflow engine.

Manages the top-down drill-down design process from aircraft requirements
through sub-assemblies to individual components, tracking agent rounds
(aerodynamicist + structural engineer), CFD/FEA validation loops, and
n8n workflow integration.

Usage:
    from src.orchestrator import WorkflowEngine, StateManager

    engine = WorkflowEngine()
    engine.start_iteration("wing")
    engine.complete_step("wing", "AERO_PROPOSAL")
    status = engine.get_status()
"""

__version__ = "0.1.0"

from src.orchestrator.workflow_engine import WorkflowEngine
from src.orchestrator.state_manager import StateManager
from src.orchestrator.dashboard import DashboardGenerator

from src.orchestrator.n8n_client import N8nClient

__all__ = [
    "WorkflowEngine",
    "StateManager",
    "DashboardGenerator",
    "N8nClient",
]
