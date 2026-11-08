"""
Module 1: LLM Manager - Key Pool & Token Budget Tracker.
Quản lý vòng đời API Key (kiểm tra hết hạn, xoay vòng key, đặt cooldown khi lỗi)
và theo dõi ngân sách token theo phiên / toàn cục.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Dict, List, Optional

from agent_core.shared.exceptions import (
    LLMKeyExpiredOrExhaustedError,
    TokenBudgetExceededError,
)
from agent_core.shared.models import TokenUsage, utc_now

from .models import APIKeyCredential, LLMProviderType, ModelSpec


class APIKeyPool:
    """Bể chứa và điều phối API Key theo từng nhà cung cấp (Provider)."""

    def __init__(self) -> None:
        self._keys: Dict[str, APIKeyCredential] = {}

    def register_key(self, credential: APIKeyCredential) -> None:
        self._keys[credential.key_id] = credential

    def acquire_key(
        self, provider: LLMProviderType, estimated_tokens: int = 0
    ) -> APIKeyCredential:
        """Lấy một API key còn hạn, còn quota và không bị cooldown."""
        now = utc_now()
        candidates = [
            k
            for k in self._keys.values()
            if k.provider == provider and k.is_available(estimated_tokens, now)
        ]
        if not candidates:
            raise LLMKeyExpiredOrExhaustedError(
                f"Không còn API Key khả dụng cho provider '{provider.value}' "
                f"(tất cả đã hết hạn, hết quota hoặc đang trong thời gian cooldown)."
            )
        # Ưu tiên key có số lượng token đã dùng ít nhất (Load Balancing)
        candidates.sort(key=lambda k: k.used_tokens)
        return candidates[0]

    def record_key_usage(self, key_id: str, total_tokens: int) -> None:
        if key_id in self._keys:
            self._keys[key_id].used_tokens += total_tokens

    def mark_key_cooldown(self, key_id: str, cooldown_seconds: int = 60) -> None:
        """Đưa key vào trạng thái tạm nghỉ (ví dụ khi gặp lỗi HTTP 429 Rate Limit)."""
        if key_id in self._keys:
            self._keys[key_id].cooldown_until = utc_now() + timedelta(
                seconds=cooldown_seconds
            )

    def get_key_statuses(self) -> List[Dict[str, object]]:
        now = utc_now()
        return [
            {
                "key_id": k.key_id,
                "provider": k.provider.value,
                "available": k.is_available(now=now),
                "expired": k.is_expired(now=now),
                "in_cooldown": k.is_in_cooldown(now=now),
                "used_tokens": k.used_tokens,
                "max_token_quota": k.max_token_quota,
            }
            for k in self._keys.values()
        ]


class TokenBudgetTracker:
    """Theo dõi lượng token tiêu thụ và chi phí ước tính cho từng Session và toàn App."""

    def __init__(self, global_max_tokens: Optional[int] = None) -> None:
        self.global_max_tokens = global_max_tokens
        self._global_usage = TokenUsage()
        self._session_usage: Dict[str, TokenUsage] = {}
        self._session_limits: Dict[str, int] = {}

    def set_session_budget(self, session_id: str, max_tokens: int) -> None:
        self._session_limits[session_id] = max_tokens

    def check_budget(self, session_id: Optional[str], estimated_tokens: int) -> None:
        """Kiểm tra trước khi gọi LLM xem có vượt ngân sách token hay không."""
        if (
            self.global_max_tokens is not None
            and (self._global_usage.total_tokens + estimated_tokens) > self.global_max_tokens
        ):
            raise TokenBudgetExceededError(
                f"Vượt quá ngân sách token toàn cục ({self.global_max_tokens} tokens)."
            )

        if session_id and session_id in self._session_limits:
            current = self._session_usage.get(session_id, TokenUsage()).total_tokens
            limit = self._session_limits[session_id]
            if (current + estimated_tokens) > limit:
                raise TokenBudgetExceededError(
                    f"Session '{session_id}' vượt quá ngân sách token cho phép "
                    f"({current + estimated_tokens} > {limit})."
                )

    def record_usage(
        self,
        session_id: Optional[str],
        spec: ModelSpec,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> TokenUsage:
        cost = (
            (prompt_tokens / 1000.0) * spec.cost_per_1k_input_usd
            + (completion_tokens / 1000.0) * spec.cost_per_1k_output_usd
        )
        delta = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=round(cost, 6),
        )
        self._global_usage = self._global_usage.add(delta)
        if session_id:
            prev = self._session_usage.get(session_id, TokenUsage())
            self._session_usage[session_id] = prev.add(delta)
        return delta

    def get_session_usage(self, session_id: str) -> TokenUsage:
        return self._session_usage.get(session_id, TokenUsage())

    @property
    def global_usage(self) -> TokenUsage:
        return self._global_usage
