"""
Module 1: LLM Manager - Providers & Central LLMManager Facade.
Hỗ trợ nhiều loại model, tự động chuyển đổi sang Fallback Model nếu model chính
hoặc API Key hết hạn / lỗi, và tích hợp theo dõi Token.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional

from agent_core.shared.exceptions import LLMKeyExpiredOrExhaustedError
from agent_core.shared.models import Role, ToolCallRequest

from .key_pool import APIKeyPool, TokenBudgetTracker
from .models import (
    APIKeyCredential,
    GenerationSettings,
    LLMProviderType,
    LLMRequest,
    LLMResponse,
    ModelSpec,
)


class BaseLLMProvider(ABC):
    """Interface chuẩn cho mọi adapter kết nối tới LLM (OpenAI, Gemini, Anthropic, Local...)."""

    provider_type: LLMProviderType

    @abstractmethod
    async def generate(
        self,
        request: LLMRequest,
        credential: APIKeyCredential,
        model_spec: ModelSpec,
    ) -> LLMResponse:
        """Thực thi lời gọi tới LLM API và trả về LLMResponse chuẩn hóa."""


class SmartMockLLMProvider(BaseLLMProvider):
    """
    Provider giả lập thông minh phục vụ kiểm thử kiến trúc (Architecture Demo & Unit Test)
    mà không tốn chi phí gọi API thật, nhưng vẫn mô phỏng đầy đủ Tool Calling và Reasoning.
    """

    provider_type = LLMProviderType.MOCK

    def __init__(
        self,
        custom_responder: Optional[Callable[[LLMRequest], tuple[str, List[ToolCallRequest]]]] = None,
    ) -> None:
        self._custom_responder = custom_responder

    async def generate(
        self,
        request: LLMRequest,
        credential: APIKeyCredential,
        model_spec: ModelSpec,
    ) -> LLMResponse:
        start = time.perf_counter()
        last_message = request.messages[-1] if request.messages else None
        content = ""
        tool_calls: List[ToolCallRequest] = []

        if self._custom_responder is not None:
            content, tool_calls = self._custom_responder(request)
        elif last_message and last_message.role == Role.USER:
            user_text = last_message.content.lower()
            available_tools = {t["name"] for t in request.tools_schema}

            # Nếu người dùng hỏi tính toán và có tool calculator -> gọi tool
            if ("tính" in user_text or "calculate" in user_text) and "calculator" in available_tools:
                expr = "125 * 48"
                for token in last_message.content.split():
                    if any(ch.isdigit() for ch in token):
                        # Tìm biểu thức trong câu
                        pass
                tool_calls.append(
                    ToolCallRequest(
                        name="calculator",
                        arguments={"expression": "125 * 48 + 400"},
                    )
                )
                content = "Tôi sẽ sử dụng công cụ `calculator` để tính toán chính xác."
            elif ("thời tiết" in user_text or "tra cứu" in user_text) and "knowledge_search" in available_tools:
                tool_calls.append(
                    ToolCallRequest(
                        name="knowledge_search",
                        arguments={"query": last_message.content},
                    )
                )
                content = "Đang tra cứu thông tin qua công cụ `knowledge_search`..."
            else:
                content = (
                    f"[{model_spec.display_name}] Đã xử lý yêu cầu: '{last_message.content}'. "
                    f"Ngữ cảnh hiện tại gồm {len(request.messages)} messages."
                )
        elif last_message and last_message.role == Role.TOOL:
            content = (
                f"[{model_spec.display_name}] Dựa trên kết quả từ công cụ `{last_message.name}` "
                f"({last_message.content}), câu trả lời cuối cùng của bạn đã hoàn tất!"
            )

        prompt_tokens = sum(m.estimate_tokens() for m in request.messages)
        completion_tokens = max(5, len(content) // 4 + len(tool_calls) * 12)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        return LLMResponse(
            model_id=model_spec.model_id,
            provider=self.provider_type,
            key_id_used=credential.key_id,
            content=content,
            tool_calls=tool_calls,
            latency_ms=latency_ms,
            finish_reason="tool_calls" if tool_calls else "stop",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "estimated_cost_usd": 0.0,
            },
        )


class LLMManager:
    """
    Facade trung tâm của Module 1 (LLM Manager):
    - Quản lý danh mục Model (Model Registry) và kiểm tra hạn sử dụng của Model.
    - Quản lý Key Pool (xoay vòng API Key, kiểm tra hết hạn, hạn ngạch token, cooldown).
    - Quản lý cài đặt LLM (GenerationSettings) và chuỗi Fallback Model tự động.
    - Theo dõi và giới hạn ngân sách Token (TokenBudgetTracker).
    """

    def __init__(self, global_token_budget: Optional[int] = None) -> None:
        self._models: Dict[str, ModelSpec] = {}
        self._providers: Dict[LLMProviderType, BaseLLMProvider] = {}
        self.key_pool = APIKeyPool()
        self.token_tracker = TokenBudgetTracker(global_max_tokens=global_token_budget)
        self._default_model_id: Optional[str] = None
        self._fallback_chain: List[str] = []

    def register_provider(self, provider: BaseLLMProvider) -> None:
        self._providers[provider.provider_type] = provider

    def register_model(self, spec: ModelSpec, is_default: bool = False) -> None:
        self._models[spec.model_id] = spec
        if is_default or self._default_model_id is None:
            self._default_model_id = spec.model_id

    def set_fallback_chain(self, model_ids: List[str]) -> None:
        """Thiết lập thứ tự model dự phòng khi model chính hết hạn hoặc hết key."""
        self._fallback_chain = model_ids

    def register_api_key(self, credential: APIKeyCredential) -> None:
        self.key_pool.register_key(credential)

    def get_model_spec(self, model_id: Optional[str] = None) -> ModelSpec:
        target_id = model_id or self._default_model_id
        if not target_id or target_id not in self._models:
            raise ValueError(f"Model '{target_id}' chưa được đăng ký trong LLMManager.")
        return self._models[target_id]

    async def chat_completion(
        self,
        request: LLMRequest,
        allow_fallback: bool = True,
    ) -> LLMResponse:
        """
        Thực thi gọi LLM với cơ chế:
        1. Kiểm tra ngân sách token (Token Budget).
        2. Kiểm tra hạn sử dụng của Model và API Key.
        3. Tự động chuyển sang Fallback Model nếu model chính bị lỗi/hết hạn key.
        4. Ghi nhận token và chi phí thực tế sau khi chạy.
        """
        estimated_prompt_tokens = sum(m.estimate_tokens() for m in request.messages)
        self.token_tracker.check_budget(request.session_id, estimated_prompt_tokens)

        candidate_models = [request.model_id]
        if allow_fallback:
            for fb_id in self._fallback_chain:
                if fb_id not in candidate_models:
                    candidate_models.append(fb_id)

        last_error: Optional[Exception] = None
        for candidate_id in candidate_models:
            spec = self._models.get(candidate_id)
            if not spec or spec.is_model_expired():
                last_error = LLMKeyExpiredOrExhaustedError(
                    f"Model '{candidate_id}' không tồn tại hoặc đã hết hạn (deprecated)."
                )
                continue

            provider = self._providers.get(spec.provider)
            if not provider:
                last_error = ValueError(f"Chưa đăng ký Provider cho '{spec.provider.value}'.")
                continue

            try:
                credential = self.key_pool.acquire_key(
                    spec.provider, estimated_tokens=estimated_prompt_tokens
                )
                actual_request = request.model_copy(update={"model_id": candidate_id})
                response = await provider.generate(actual_request, credential, spec)

                # Tính toán token & chi phí chuẩn xác
                usage = self.token_tracker.record_usage(
                    session_id=request.session_id,
                    spec=spec,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                )
                self.key_pool.record_key_usage(credential.key_id, usage.total_tokens)
                response.usage = usage
                return response

            except Exception as exc:
                last_error = exc
                continue

        raise LLMKeyExpiredOrExhaustedError(
            f"Tất cả các model trong chuỗi {candidate_models} đều thất bại. Lỗi cuối: {last_error}"
        )
