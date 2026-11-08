"""
Module 2: System Prompt Manager - Domain Models.
Quản lý phân tầng Prompt:
1. App System Prompt (Cấp ứng dụng - bất biến, định hình nhân cách gốc & quy tắc cốt lõi)
2. User System Prompt (Cấp người dùng - sở thích cá nhân, ngôn ngữ, phong cách trả lời)
3. Chat Session Prompt (Cấp phiên hội thoại - mục tiêu cụ thể của cuộc trò chuyện hiện tại)
4. Skills (Các kỹ năng chuyên biệt có thể bật/tắt hoặc tự động kích hoạt theo từ khóa)
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict, List

from pydantic import BaseModel, Field


class PromptLayerPriority(IntEnum):
    """Thứ tự ưu tiên khi ghép nối System Prompt (từ nền tảng đến cụ thể)."""

    APP_SYSTEM = 10
    USER_PERSONA = 20
    CHAT_SESSION = 30
    ACTIVE_SKILLS = 40
    RUNTIME_RULES = 50


class SkillDefinition(BaseModel):
    """Định nghĩa một Kỹ năng (Skill) có thể tiêm vào System Prompt."""

    skill_id: str
    name: str
    description: str
    instructions: str
    trigger_keywords: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    always_active: bool = False

    def matches_query(self, query: str) -> bool:
        """Kiểm tra xem câu hỏi của user có kích hoạt Skill này không."""
        if self.always_active:
            return True
        q_lower = query.lower()
        return any(kw.lower() in q_lower for kw in self.trigger_keywords)


class PromptLayerConfig(BaseModel):
    """Cấu hình các tầng prompt cho một phiên làm việc."""

    app_system_prompt: str = (
        "Bạn là một AI Agent thông minh, tuân thủ nghiêm ngặt kiến trúc 7 module, "
        "luôn trả lời chính xác, rõ ràng và an toàn."
    )
    user_system_prompt: str = ""
    session_system_prompt: str = ""
    active_skill_ids: List[str] = Field(default_factory=list)
    template_variables: Dict[str, str] = Field(default_factory=dict)
