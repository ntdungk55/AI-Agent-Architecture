"""
Custom exceptions for the 7-Module AI Agent Architecture.
"""


class AgentArchitectureError(Exception):
    """Base exception cho toàn bộ hệ thống AI Agent."""


class LLMKeyExpiredOrExhaustedError(AgentArchitectureError):
    """Ném ra khi tất cả API key hoặc model đều hết hạn / hết quota."""


class TokenBudgetExceededError(AgentArchitectureError):
    """Ném ra khi phiên làm việc hoặc request vượt quá ngân sách token cho phép."""


class GuardrailViolationError(AgentArchitectureError):
    """Ném ra khi Monitoring/Validator phát hiện vi phạm an toàn (Input/Output/Tool)."""

    def __init__(self, validator_name: str, reason: str) -> None:
        self.validator_name = validator_name
        self.reason = reason
        super().__init__(f"[{validator_name}] Guardrail blocked execution: {reason}")


class ToolExecutionError(AgentArchitectureError):
    """Ném ra khi Tool không tồn tại, không đủ quyền hoặc gặp lỗi khi chạy."""
