"""
Module 5: Memory Manager - Domain Models.
Định nghĩa các loại nguồn dữ liệu (Data Sources) mà AI Agent có thể lưu trữ và truy vấn:
- WORKING: Bộ nhớ ngắn hạn trong phiên (lịch sử chat hiện tại)
- EPISODIC: Ký ức sự kiện từ các phiên làm việc trước của người dùng
- SEMANTIC_RAG: Kho tri thức tài liệu / Vector DB (RAG)
- ENTITY_FACT: Các thông tin sự thật có cấu trúc về người dùng / hệ thống (Key-Value / Graph)
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from agent_core.shared.models import utc_now


class DataSourceType(str, Enum):
    WORKING = "working_memory"
    EPISODIC = "episodic_memory"
    SEMANTIC_RAG = "semantic_rag"
    ENTITY_FACT = "entity_fact"


class MemoryItem(BaseModel):
    """Một bản ghi dữ liệu chuẩn hóa từ bất kỳ Data Source nào."""

    item_id: str = Field(default_factory=lambda: f"mem_{uuid4().hex[:8]}")
    source_type: DataSourceType
    content: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    relevance_score: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
