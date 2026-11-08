"""
Module 3: Agent Orchestrator - Domain Models.
Quản lý trạng thái phiên làm việc (AgentSession) và kết quả trả về sau mỗi lượt
tương tác hoàn chỉnh (AgentTurnResult).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from agent_core.llm_manager.models import GenerationSettings
from agent_core.monitoring.models import TraceEvent
from agent_core.shared.models import TokenUsage, utc_now


class SessionStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED_BY_GUARDRAIL = "blocked_by_guardrail"
    FAILED = "failed"


class AgentSession(BaseModel):
    """Thông tin định danh và cấu hình của một phiên làm việc (Session) của AI."""

    session_id: str = Field(default_factory=lambda: f"sess_{uuid4().hex[:8]}")
    user_id: str = "default_user"
    preferred_model_id: str = "gpt-4o-primary"
    max_react_steps: int = Field(default=5, ge=1, le=20)
    explicit_skills: List[str] = Field(default_factory=list)
    allowed_tools: Optional[List[str]] = None
    llm_settings: GenerationSettings = Field(default_factory=GenerationSettings)
    status: SessionStatus = SessionStatus.IDLE
    created_at: datetime = Field(default_factory=utc_now)


class AgentTurnResult(BaseModel):
    """Báo cáo kết quả toàn diện của một lượt xử lý trong AgentOrchestrator."""

    session_id: str
    user_id: str
    final_answer: str
    model_used: str
    key_used: str
    iterations_used: int
    invoked_tools: List[str] = Field(default_factory=list)
    active_skills: List[str] = Field(default_factory=list)
    turn_usage: TokenUsage = Field(default_factory=TokenUsage)
    traces: List[TraceEvent] = Field(default_factory=list)
