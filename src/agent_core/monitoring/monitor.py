"""
Module 7: Monitoring & Validators - Central MonitoringManager.
Kết hợp hệ thống Telemetry Tracing (theo dõi từng bước chạy của 7 module)
và hệ thống Validators (kiểm duyệt Input, ToolCall, Output).
"""

from __future__ import annotations

from typing import Any, Dict, List

from agent_core.shared.exceptions import GuardrailViolationError
from agent_core.shared.models import ToolCallRequest

from .models import TraceEvent, ValidationOutcome
from .validators import (
    PromptInjectionInputValidator,
    SensitiveDataOutputValidator,
    ToolPolicyValidator,
)


class MonitoringManager:
    """
    Facade trung tâm của Module 7 (Monitoring & Validators):
    - Thực thi chuỗi kiểm duyệt an toàn (Input -> ToolCall -> Output).
    - Ghi nhận toàn bộ nhật ký hoạt động (Trace Events) theo từng Session để dễ dàng debug.
    """

    def __init__(self) -> None:
        self._input_validators: List[PromptInjectionInputValidator] = [
            PromptInjectionInputValidator()
        ]
        self._tool_validators: List[ToolPolicyValidator] = [ToolPolicyValidator()]
        self._output_validators: List[SensitiveDataOutputValidator] = [
            SensitiveDataOutputValidator()
        ]
        self._traces: List[TraceEvent] = []

    # --- Telemetry & Tracing ---

    def record_event(
        self,
        session_id: str,
        module_name: str,
        step_name: str,
        status: str = "OK",
        duration_ms: float = 0.0,
        details: Dict[str, Any] | None = None,
    ) -> TraceEvent:
        event = TraceEvent(
            session_id=session_id,
            module_name=module_name,
            step_name=step_name,
            status=status,
            duration_ms=duration_ms,
            details=details or {},
        )
        self._traces.append(event)
        return event

    def get_session_traces(self, session_id: str) -> List[TraceEvent]:
        return [t for t in self._traces if t.session_id == session_id]

    # --- Guardrail Validators ---

    def validate_input(self, session_id: str, user_input: str) -> str:
        current_text = user_input
        for validator in self._input_validators:
            outcome: ValidationOutcome = validator.validate(current_text)
            if not outcome.is_valid:
                self.record_event(
                    session_id=session_id,
                    module_name="7.Monitoring",
                    step_name=f"InputRejected:{validator.name}",
                    status="BLOCKED",
                    details={"reason": outcome.violation_reason},
                )
                raise GuardrailViolationError(
                    validator.name, outcome.violation_reason or "Input rejected"
                )
            if outcome.sanitized_content is not None:
                current_text = outcome.sanitized_content

        self.record_event(
            session_id=session_id,
            module_name="7.Monitoring",
            step_name="ValidateUserInput",
            status="PASSED",
        )
        return current_text

    def validate_tool_call(self, session_id: str, tool_call: ToolCallRequest) -> None:
        for validator in self._tool_validators:
            outcome = validator.validate(tool_call)
            if not outcome.is_valid:
                self.record_event(
                    session_id=session_id,
                    module_name="7.Monitoring",
                    step_name=f"ToolBlocked:{tool_call.name}",
                    status="BLOCKED",
                    details={"reason": outcome.violation_reason, "args": tool_call.arguments},
                )
                raise GuardrailViolationError(
                    validator.name, outcome.violation_reason or "Tool call blocked"
                )

        self.record_event(
            session_id=session_id,
            module_name="7.Monitoring",
            step_name=f"ValidateToolCall:{tool_call.name}",
            status="PASSED",
        )

    def validate_output(self, session_id: str, llm_output: str) -> str:
        current_text = llm_output
        for validator in self._output_validators:
            outcome = validator.validate(current_text)
            if not outcome.is_valid:
                raise GuardrailViolationError(
                    validator.name, outcome.violation_reason or "Output rejected"
                )
            if outcome.sanitized_content is not None:
                current_text = outcome.sanitized_content

        self.record_event(
            session_id=session_id,
            module_name="7.Monitoring",
            step_name="ValidateLLMOutput",
            status="PASSED",
        )
        return current_text
