"""
Module 7: Monitoring & Validators - Domain Models.
Lưu trữ kết quả kiểm duyệt an toàn (ValidationOutcome) và nhật ký theo dõi
từng bước hoạt động của AI Agent (TraceEvent).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from agent_core.shared.models import utc_now


class ValidationStage(str, Enum):
    USER_INPUT = "user_input"
    TOOL_CALL = "tool_call"
    LLM_OUTPUT = "llm_output"


class ValidationOutcome(BaseModel):
    """Kết quả trả về từ một bộ kiểm duyệt (Validator / Guardrail)."""

    validator_name: str
    stage: ValidationStage
    is_valid: bool = True
    sanitized_content: Optional[str] = None
    violation_reason: Optional[str] = None


class TraceEvent(BaseModel):
    """Một sự kiện giám sát (Telemetry Span/Event) trong vòng đời thực thi của Agent."""

    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex[:8]}")
    session_id: str
    step_name: str
    module_name: str
    status: str = "OK"
    duration_ms: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)
