"""Core framework for parametric component design with dependency tracking."""

from .component import Component, OffShelfComponent, CustomComponent, ComponentSpec
from .assembly import Assembly, AssemblyConstraint
from .dag import DependencyGraph
from .validation import ValidationHook, validate_component
