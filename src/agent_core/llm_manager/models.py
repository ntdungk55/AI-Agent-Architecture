"""
Module 1: LLM Manager - Domain Models.
Quản lý cấu hình model, thông tin API Key (hạn sử dụng, hạn mức token, cooldown),
cài đặt sinh văn bản (temperature, top_p...) và kết quả trả về.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from agent_core.shared.models import Message, TokenUsage, ToolCallRequest, utc_now


class LLMProviderType(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class ModelCapability(str, Enum):
    CHAT = "chat"
    TOOL_CALLING = "tool_calling"
    VISION = "vision"
    REASONING = "reasoning"


class GenerationSettings(BaseModel):
    """Cài đặt thông số khi gọi LLM (LLM Runtime Settings)."""

    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    max_output_tokens: int = Field(default=2048, gt=0)
    timeout_seconds: float = Field(default=30.0, gt=0)
    stop_sequences: List[str] = Field(default_factory=list)


class ModelSpec(BaseModel):
    """Thông tin đặc tả của một loại Model."""

    model_id: str
    provider: LLMProviderType
    display_name: str
    context_window_limit: int = 128_000
    max_output_limit: int = 8_192
    cost_per_1k_input_usd: float = 0.0005
    cost_per_1k_output_usd: float = 0.0015
    capabilities: Set[ModelCapability] = Field(
        default_factory=lambda: {ModelCapability.CHAT, ModelCapability.TOOL_CALLING}
    )
    default_settings: GenerationSettings = Field(default_factory=GenerationSettings)
    is_deprecated: bool = False
    deprecation_date: Optional[datetime] = None

    def is_model_expired(self, now: Optional[datetime] = None) -> bool:
        """Kiểm tra xem model đã bị ngừng hỗ trợ (deprecated/expired) hay chưa."""
        if self.is_deprecated:
            return True
        check_time = now or utc_now()
        if self.deprecation_date and check_time >= self.deprecation_date:
            return True
        return False


class APIKeyCredential(BaseModel):
    """Quản lý trạng thái, thời hạn (expiry) và hạn ngạch (quota) của một API Key."""

    key_id: str
    provider: LLMProviderType
    api_key: str
    expires_at: Optional[datetime] = None
    max_token_quota: Optional[int] = None
    used_tokens: int = 0
    cooldown_until: Optional[datetime] = None
    is_enabled: bool = True

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        check_time = now or utc_now()
        return self.expires_at is not None and check_time >= self.expires_at

    def is_in_cooldown(self, now: Optional[datetime] = None) -> bool:
        check_time = now or utc_now()
        return self.cooldown_until is not None and check_time < self.cooldown_until

    def is_quota_exhausted(self, estimated_tokens: int = 0) -> bool:
        if self.max_token_quota is None:
            return False
        return (self.used_tokens + estimated_tokens) > self.max_token_quota

    def is_available(self, estimated_tokens: int = 0, now: Optional[datetime] = None) -> bool:
        return (
            self.is_enabled
            and not self.is_expired(now)
            and not self.is_in_cooldown(now)
            and not self.is_quota_exhausted(estimated_tokens)
        )


class LLMRequest(BaseModel):
    """Payload chuẩn hóa gửi tới LLM Provider."""

    model_id: str
    messages: List[Message]
    tools_schema: List[Dict[str, Any]] = Field(default_factory=list)
    settings: GenerationSettings = Field(default_factory=GenerationSettings)
    session_id: Optional[str] = None


class LLMResponse(BaseModel):
    """Kết quả chuẩn hóa nhận về từ LLM Provider."""

    model_id: str
    provider: LLMProviderType
    key_id_used: str
    content: str = ""
    tool_calls: List[ToolCallRequest] = Field(default_factory=list)
    usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    finish_reason: str = "stop"
