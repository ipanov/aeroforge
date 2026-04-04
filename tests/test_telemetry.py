"""Tests for the telemetry and event logging system."""

from __future__ import annotations

import logging

from src.orchestrator.telemetry import (
    EventType,
    TelemetryEmitter,
    TelemetryEvent,
    get_emitter,
)


class TestTelemetryEvent:

    def test_auto_timestamp(self) -> None:
        event = TelemetryEvent(event_type=EventType.STEP_STARTED)
        assert event.timestamp  # Not empty
        assert "T" in event.timestamp  # ISO format

    def test_to_dict_removes_empty(self) -> None:
        event = TelemetryEvent(
            event_type=EventType.STEP_STARTED,
            sub_assembly="wing",
            step="AERO_PROPOSAL",
        )
        d = event.to_dict()
        assert "agent" not in d  # Empty string removed
        assert "sub_assembly" in d

    def test_to_log_line(self) -> None:
        event = TelemetryEvent(
            event_type=EventType.STEP_COMPLETED,
            sub_assembly="wing",
            step="DRAWING_2D",
            message="Drawing approved",
        )
        line = event.to_log_line()
        assert "step_completed" in line
        assert "wing" in line
        assert "DRAWING_2D" in line
        assert "Drawing approved" in line

    def test_to_log_line_with_duration(self) -> None:
        event = TelemetryEvent(
            event_type=EventType.PROVIDER_CALLED,
            provider="su2_cuda",
            duration_ms=45000,
        )
        line = event.to_log_line()
        assert "45000ms" in line


class TestTelemetryEmitter:

    def test_emit_returns_dict(self) -> None:
        emitter = TelemetryEmitter()
        event = TelemetryEvent(
            event_type=EventType.STEP_STARTED,
            sub_assembly="wing",
            step="REQUIREMENTS",
        )
        result = emitter.emit(event)
        assert isinstance(result, dict)
        assert result["event"] == "step_started"
        assert result["sub_assembly"] == "wing"

    def test_step_started_convenience(self) -> None:
        emitter = TelemetryEmitter()
        result = emitter.step_started("wing", "AERO_PROPOSAL", agent="aerodynamicist")
        assert result["event"] == "step_started"
        assert "wing" in result["message"]

    def test_step_completed_convenience(self) -> None:
        emitter = TelemetryEmitter()
        result = emitter.step_completed("fuselage", "MODEL_3D", notes="Model built")
        assert result["event"] == "step_completed"

    def test_step_failed_convenience(self) -> None:
        emitter = TelemetryEmitter()
        result = emitter.step_failed("wing", "MESH", reason="Boolean operation hang")
        assert result["event"] == "step_failed"

    def test_step_rejected_convenience(self) -> None:
        emitter = TelemetryEmitter()
        result = emitter.step_rejected("wing", "DRAWING_2D", reason="Planform too rectangular")
        assert result["event"] == "step_rejected"

    def test_user_feedback_convenience(self) -> None:
        emitter = TelemetryEmitter()
        result = emitter.user_feedback("I want elliptical tips", sub_assembly="wing")
        assert result["event"] == "user_feedback"

    def test_agent_spawned_convenience(self) -> None:
        emitter = TelemetryEmitter()
        result = emitter.agent_spawned("aerodynamicist", sub_assembly="empennage")
        assert result["event"] == "agent_spawned"

    def test_provider_called_convenience(self) -> None:
        emitter = TelemetryEmitter()
        result = emitter.provider_called("su2_cuda", "cfd", sub_assembly="wing")
        assert result["event"] == "provider_called"

    def test_failed_events_log_as_warning(self, caplog: any) -> None:
        emitter = TelemetryEmitter()
        with caplog.at_level(logging.WARNING, logger="aeroforge.telemetry"):
            emitter.step_failed("wing", "MESH", reason="Crash")
        assert any("step_failed" in r.message for r in caplog.records)

    def test_normal_events_log_as_info(self, caplog: any) -> None:
        emitter = TelemetryEmitter()
        with caplog.at_level(logging.INFO, logger="aeroforge.telemetry"):
            emitter.step_started("wing", "REQUIREMENTS")
        assert any("step_started" in r.message for r in caplog.records)


class TestGetEmitter:

    def test_singleton(self) -> None:
        e1 = get_emitter()
        e2 = get_emitter()
        assert e1 is e2

    def test_recreate_with_n8n(self) -> None:
        class MockN8n:
            available = False
        e1 = get_emitter()
        e2 = get_emitter(n8n_client=MockN8n())
        assert e2 is not e1  # New instance with n8n


class TestEventTypes:

    def test_all_event_types_are_strings(self) -> None:
        for et in EventType:
            assert isinstance(et.value, str)

    def test_key_event_types_exist(self) -> None:
        assert EventType.STEP_STARTED
        assert EventType.STEP_COMPLETED
        assert EventType.STEP_REJECTED
        assert EventType.USER_FEEDBACK
        assert EventType.AGENT_SPAWNED
        assert EventType.PROVIDER_CALLED
        assert EventType.CONSENSUS_REACHED
