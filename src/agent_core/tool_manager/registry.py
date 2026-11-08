"""
Module 6: Tool Manager - Tool Registry, Executor & Built-in Sample Tools.
Cho phép đăng ký công cụ mới dễ dàng, xuất schema cho LLM và thực thi an toàn
với cơ chế cô lập lỗi (sandboxed error handling) và giới hạn thời gian (timeout).
"""

from __future__ import annotations

import ast
import asyncio
import operator
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from agent_core.shared.models import ToolCallRequest

from .models import ToolExecutionResult, ToolPermissionLevel, ToolSpec


class BaseTool(ABC):
    """Lớp cơ sở cho mọi công cụ (Tool) mà AI Agent có thể sử dụng."""

    spec: ToolSpec

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Thực thi logic của công cụ."""


class CalculatorTool(BaseTool):
    """Công cụ tính toán biểu thức toán học an toàn (không dùng eval trực tiếp)."""

    spec = ToolSpec(
        name="calculator",
        description="Tính toán chính xác giá trị của biểu thức số học (+, -, *, /, **).",
        parameters_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Biểu thức toán học cần tính, ví dụ: '125 * 48 + 400'",
                }
            },
            "required": ["expression"],
        },
        permission=ToolPermissionLevel.READ_ONLY,
    )

    _ALLOWED_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def _safe_eval(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in self._ALLOWED_OPS:
            return float(
                self._ALLOWED_OPS[type(node.op)](
                    self._safe_eval(node.left), self._safe_eval(node.right)
                )
            )
        if isinstance(node, ast.UnaryOp) and type(node.op) in self._ALLOWED_OPS:
            return float(self._ALLOWED_OPS[type(node.op)](self._safe_eval(node.operand)))
        raise ValueError(f"Biểu thức chứa toán tử không được phép: {ast.dump(node)}")

    async def execute(self, expression: str, **_: Any) -> str:
        tree = ast.parse(expression, mode="eval")
        result = self._safe_eval(tree.body)
        if result.is_integer():
            return f"{expression} = {int(result)}"
        return f"{expression} = {round(result, 4)}"


class ExternalSystemControlTool(BaseTool):
    """Công cụ mẫu điều khiển hoặc lấy trạng thái từ hệ thống bên ngoài."""

    spec = ToolSpec(
        name="system_control",
        description="Kiểm tra trạng thái dịch vụ hoặc điều khiển tác vụ hệ thống bên ngoài.",
        parameters_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["check_status", "restart_worker", "delete_database"],
                },
                "target": {"type": "string"},
            },
            "required": ["action", "target"],
        },
        permission=ToolPermissionLevel.SYSTEM_CONTROL,
    )

    async def execute(self, action: str, target: str, **_: Any) -> str:
        return f"Đã thực thi hành động '{action}' trên mục tiêu '{target}' thành công (Status: HEALTHY)."


class ToolManager:
    """
    Facade trung tâm của Module 6 (Tool Manager):
    - Quản lý danh sách các Tool đã đăng ký.
    - Xuất danh sách JSON Schema để truyền vào LLMRequest.
    - Điều phối thực thi Tool bất đồng bộ kèm Timeout và bắt lỗi an toàn.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        self._tools[tool.spec.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def get_tools_schema(
        self, allowed_tool_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Xuất danh sách Schema của các công cụ được phép sử dụng trong phiên."""
        schemas: List[Dict[str, Any]] = []
        allowed_set = set(allowed_tool_names) if allowed_tool_names is not None else None
        for name, tool in self._tools.items():
            if allowed_set is None or name in allowed_set:
                schemas.append(tool.spec.to_llm_schema())
        return schemas

    async def execute_tool_call(self, call: ToolCallRequest) -> ToolExecutionResult:
        """Thực thi một yêu cầu gọi công cụ từ AI và đóng gói kết quả an toàn."""
        start = time.perf_counter()
        tool = self._tools.get(call.name)
        if not tool:
            return ToolExecutionResult(
                tool_call_id=call.id,
                tool_name=call.name,
                success=False,
                error_message=f"Tool '{call.name}' không tồn tại trong ToolManager.",
            )

        try:
            raw_output = await asyncio.wait_for(
                tool.execute(**call.arguments),
                timeout=tool.spec.timeout_seconds,
            )
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            return ToolExecutionResult(
                tool_call_id=call.id,
                tool_name=call.name,
                success=True,
                output=str(raw_output),
                execution_time_ms=elapsed,
            )
        except Exception as exc:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            return ToolExecutionResult(
                tool_call_id=call.id,
                tool_name=call.name,
                success=False,
                error_message=str(exc),
                execution_time_ms=elapsed,
            )
