"""
Module 6: Tool Manager - Domain Models.
Định nghĩa chuẩn JSON Schema cho công cụ (Tool), phân quyền thực thi (Permission Level),
và kết quả trả về sau khi AI gọi công cụ.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ToolPermissionLevel(str, Enum):
    READ_ONLY = "read_only"          # Chỉ đọc thông tin (tra cứu, tính toán)
    EXTERNAL_API = "external_api"    # Gọi API bên ngoài
    SYSTEM_CONTROL = "system_control"  # Điều khiển hệ thống / ghi dữ liệu (cần giám sát chặt)


class ToolSpec(BaseModel):
    """Đặc tả kỹ thuật của một Tool để xuất ra JSON Schema cho LLM."""

    name: str
    description: str
    parameters_schema: Dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}, "required": []}
    )
    permission: ToolPermissionLevel = ToolPermissionLevel.READ_ONLY
    timeout_seconds: float = 10.0

    def to_llm_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
        }


class ToolExecutionResult(BaseModel):
    """Kết quả chuẩn hóa sau khi ToolManager thực thi một ToolCallRequest."""

    tool_call_id: str
    tool_name: str
    success: bool
    output: str = ""
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
