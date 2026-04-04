"""Structured telemetry and event logging for AeroForge workflows.

All workflow events (step lifecycle, agent invocations, user feedback,
provider calls) flow through this module. Events are:
1. Logged via Python ``logging`` with structured formatters
2. Pushed to n8n for dashboard visibility (if available)
3. Appended to the workflow state history

This is the single source of truth for "what happened and when."
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("aeroforge.telemetry")


class EventType(str, Enum):
    """Categories of telemetry events."""

    # Step lifecycle
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    STEP_REJECTED = "step_rejected"
    STEP_REWORK = "step_rework"
    STEP_SKIPPED = "step_skipped"

    # Agent lifecycle
    AGENT_SPAWNED = "agent_spawned"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"

    # Iteration
    ITERATION_STARTED = "iteration_started"
    ROUND_STARTED = "round_started"
    ROUND_COMPLETED = "round_completed"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_FAILED = "consensus_failed"

    # User interaction
    USER_FEEDBACK = "user_feedback"
    USER_APPROVAL = "user_approval"
    USER_REJECTION = "user_rejection"
    DESIGN_DIRECTION = "design_direction"

    # Provider calls
    PROVIDER_CALLED = "provider_called"
    PROVIDER_COMPLETED = "provider_completed"
    PROVIDER_FAILED = "provider_failed"

    # Deliverables
    DELIVERABLE_CREATED = "deliverable_created"
    DELIVERABLE_VALIDATED = "deliverable_validated"

    # Project lifecycle
    PROJECT_CREATED = "project_created"
    PROJECT_SWITCHED = "project_switched"

    # System
    WORKFLOW_INITIALIZED = "workflow_initialized"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"


@dataclass
class TelemetryEvent:
    """A single telemetry event."""

    event_type: str
    timestamp: str = ""
    sub_assembly: str = ""
    step: str = ""
    agent: str = ""
    provider: str = ""
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Remove empty fields for cleaner logs
        return {k: v for k, v in d.items() if v}

    def to_log_line(self) -> str:
        """One-line log representation."""
        parts = [f"[{self.event_type}]"]
        if self.sub_assembly:
            parts.append(f"sa={self.sub_assembly}")
        if self.step:
            parts.append(f"step={self.step}")
        if self.agent:
            parts.append(f"agent={self.agent}")
        if self.provider:
            parts.append(f"provider={self.provider}")
        if self.message:
            parts.append(self.message)
        if self.duration_ms is not None:
            parts.append(f"({self.duration_ms:.0f}ms)")
        return " ".join(parts)


class TelemetryEmitter:
    """Central telemetry emitter. All workflow events flow through here.

    Events are:
    1. Logged via Python logging
    2. Pushed to n8n (if available)
    3. Returned as dicts for state history storage
    """

    def __init__(self, n8n_client: Any = None) -> None:
        self._n8n = n8n_client

    def emit(self, event: TelemetryEvent) -> dict[str, Any]:
        """Emit a telemetry event through all channels."""
        # 1. Structured log
        log_line = event.to_log_line()
        level = self._event_log_level(event.event_type)
        logger.log(level, log_line)

        # 2. Push to n8n
        if self._n8n and hasattr(self._n8n, "available") and self._n8n.available:
            try:
                self._n8n.update_status(
                    sub_assembly=event.sub_assembly or "__system__",
                    step=event.step or event.event_type,
                    status=event.event_type,
                    notes=event.message,
                )
            except Exception:
                logger.debug("Failed to push event to n8n", exc_info=True)

        # 3. Return for state history
        return {
            "timestamp": event.timestamp,
            "event": event.event_type,
            "sub_assembly": event.sub_assembly,
            "step": event.step,
            "message": event.message,
        }

    # -- Convenience methods ------------------------------------------------

    def step_started(
        self, sub_assembly: str, step: str, agent: str = "",
    ) -> dict[str, Any]:
        return self.emit(TelemetryEvent(
            event_type=EventType.STEP_STARTED,
            sub_assembly=sub_assembly, step=step, agent=agent,
            message=f"Step {step} started for {sub_assembly}",
        ))

    def step_completed(
        self, sub_assembly: str, step: str, notes: str = "",
    ) -> dict[str, Any]:
        return self.emit(TelemetryEvent(
            event_type=EventType.STEP_COMPLETED,
            sub_assembly=sub_assembly, step=step,
            message=notes or f"Step {step} completed for {sub_assembly}",
        ))

    def step_failed(
        self, sub_assembly: str, step: str, reason: str = "",
    ) -> dict[str, Any]:
        return self.emit(TelemetryEvent(
            event_type=EventType.STEP_FAILED,
            sub_assembly=sub_assembly, step=step,
            message=reason or f"Step {step} failed for {sub_assembly}",
        ))

    def step_rejected(
        self, sub_assembly: str, step: str, reason: str = "",
    ) -> dict[str, Any]:
        return self.emit(TelemetryEvent(
            event_type=EventType.STEP_REJECTED,
            sub_assembly=sub_assembly, step=step,
            message=reason,
        ))

    def user_feedback(
        self, message: str, sub_assembly: str = "", step: str = "",
    ) -> dict[str, Any]:
        return self.emit(TelemetryEvent(
            event_type=EventType.USER_FEEDBACK,
            sub_assembly=sub_assembly, step=step,
            message=message,
        ))

    def agent_spawned(
        self, agent: str, sub_assembly: str = "", step: str = "",
    ) -> dict[str, Any]:
        return self.emit(TelemetryEvent(
            event_type=EventType.AGENT_SPAWNED,
            agent=agent, sub_assembly=sub_assembly, step=step,
            message=f"Agent {agent} spawned",
        ))

    def provider_called(
        self, provider: str, category: str, sub_assembly: str = "",
    ) -> dict[str, Any]:
        return self.emit(TelemetryEvent(
            event_type=EventType.PROVIDER_CALLED,
            provider=provider, sub_assembly=sub_assembly,
            message=f"Provider {provider} ({category}) called",
        ))

    @staticmethod
    def _event_log_level(event_type: str) -> int:
        if "failed" in event_type or "rejected" in event_type:
            return logging.WARNING
        if "error" in event_type:
            return logging.ERROR
        return logging.INFO


# Module-level singleton (lazy init with n8n client)
_emitter: Optional[TelemetryEmitter] = None


def get_emitter(n8n_client: Any = None) -> TelemetryEmitter:
    """Get or create the module-level telemetry emitter."""
    global _emitter
    if _emitter is None or n8n_client is not None:
        _emitter = TelemetryEmitter(n8n_client)
    return _emitter
