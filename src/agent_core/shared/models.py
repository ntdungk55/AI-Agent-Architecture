"""
Shared domain models (DTOs) used across the 7 AI Agent modules.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCallRequest(BaseModel):
    """Yêu cầu gọi tool từ LLM sinh ra."""

    id: str = Field(default_factory=lambda: f"call_{uuid4().hex[:8]}")
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    """Một tin nhắn chuẩn hóa trong luồng hội thoại của Agent."""

    id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:8]}")
    role: Role
    content: str = ""
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: List[ToolCallRequest] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    def estimate_tokens(self) -> int:
        """Ước lượng số lượng token của message (xấp xỉ 4 ký tự = 1 token)."""
        base = max(1, len(self.content) // 4)
        if self.tool_calls:
            base += sum(len(tc.name) + len(str(tc.arguments)) // 4 for tc in self.tool_calls)
        return base + 4  # Overhead cho mỗi message


class TokenUsage(BaseModel):
    """Thống kê số lượng token tiêu thụ cho một lần gọi LLM hoặc cả phiên."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def add(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            estimated_cost_usd=round(self.estimated_cost_usd + other.estimated_cost_usd, 6),
        )
