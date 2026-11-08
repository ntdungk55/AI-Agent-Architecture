"""
Module 4: Context Manager - Domain Models.
Định nghĩa cấu trúc gói ngữ cảnh (AssembledContext) sau khi đã thu thập
từ System Prompt, Memory Manager (RAG/Facts), Lịch sử hội thoại và được tối ưu Token.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from agent_core.memory_manager.models import MemoryItem
from agent_core.shared.models import Message


class ContextWindowPolicy(BaseModel):
    """Chính sách giới hạn và cắt tỉa Context Window."""

    max_context_tokens: int = Field(default=4096, gt=100)
    reserved_output_tokens: int = Field(default=512, gt=0)
    max_retrieved_memories: int = Field(default=5, ge=0)
    keep_minimum_recent_messages: int = Field(default=4, ge=1)

    @property
    def effective_input_budget(self) -> int:
        return max(128, self.max_context_tokens - self.reserved_output_tokens)


class AssembledContext(BaseModel):
    """Gói ngữ cảnh hoàn chỉnh sẵn sàng gửi sang LLM Manager."""

    messages: List[Message] = Field(default_factory=list)
    retrieved_memories: List[MemoryItem] = Field(default_factory=list)
    estimated_input_tokens: int = 0
    dropped_messages_count: int = 0
    active_skills: List[str] = Field(default_factory=list)
