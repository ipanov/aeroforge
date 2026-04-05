"""Core framework for parametric component design with dependency tracking."""

from .component import Component, OffShelfComponent, CustomComponent, ComponentSpec
from .assembly import Assembly, AssemblyConstraint
from .dag import DependencyGraph
from .validation import ValidationHook, validate_component
from .bom import BillOfMaterials, BOMEntry, ProcurementAction, SupplierCandidate
from .bom_sync import DeliverableEvent, attach_bom_sync_hooks, sync_deliverable_event
from .procurement import ProviderProfile, build_supplier_candidates
