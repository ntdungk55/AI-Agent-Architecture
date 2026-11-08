"""
Module 4: Context Manager - Context Collector & Window Optimizer.
Chịu trách nhiệm:
1. Thu thập System Prompt từ Module 2 (SystemPromptManager).
2. Thu thập dữ liệu liên quan (RAG, Episodic, Facts) và lịch sử chat từ Module 5 (MemoryManager).
3. Lắp ghép (Assemble) và nén/cắt tỉa (Compact/Prune) sao cho vừa khít giới hạn Token.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from agent_core.memory_manager.manager import MemoryManager
from agent_core.memory_manager.models import MemoryItem
from agent_core.prompt_manager.composer import SystemPromptManager
from agent_core.shared.models import Message, Role

from .models import AssembledContext, ContextWindowPolicy


class ContextManager:
    """
    Facade trung tâm của Module 4 (Context Manager):
    Biến dữ liệu thô từ nhiều nguồn thành một danh sách `Message` tối ưu về mặt ngữ nghĩa và token.
    """

    def __init__(
        self,
        prompt_manager: SystemPromptManager,
        memory_manager: MemoryManager,
        default_policy: Optional[ContextWindowPolicy] = None,
    ) -> None:
        self.prompt_manager = prompt_manager
        self.memory_manager = memory_manager
        self.policy = default_policy or ContextWindowPolicy()

    def _format_memories_block(self, memories: List[MemoryItem]) -> str:
        if not memories:
            return ""
        lines = ["### [RETRIEVED MEMORY & KNOWLEDGE SOURCES]"]
        for idx, mem in enumerate(memories, start=1):
            lines.append(
                f"{idx}. [{mem.source_type.value} | score={mem.relevance_score}] {mem.content}"
            )
        return "\n".join(lines)

    async def build_context(
        self,
        session_id: str,
        user_query: str,
        user_id: Optional[str] = None,
        explicit_skill_ids: Optional[List[str]] = None,
        runtime_vars: Optional[Dict[str, str]] = None,
        policy_override: Optional[ContextWindowPolicy] = None,
    ) -> AssembledContext:
        """
        Thu thập và đóng gói toàn bộ Context cho lượt suy luận hiện tại của Agent.
        """
        policy = policy_override or self.policy
        budget = policy.effective_input_budget

        # 1. Lấy System Message từ Module 2 (SystemPromptManager)
        system_msg = self.prompt_manager.build_system_message(
            user_id=user_id,
            session_id=session_id,
            user_query=user_query,
            explicit_skill_ids=explicit_skill_ids,
            extra_variables=runtime_vars,
        )

        # 2. Truy xuất các mảnh ký ức & tài liệu RAG từ Module 5 (MemoryManager)
        retrieved_memories = await self.memory_manager.retrieve_relevant_memories(
            query=user_query,
            user_id=user_id,
            top_k_per_source=policy.max_retrieved_memories,
        )
        memory_block = self._format_memories_block(retrieved_memories)
        if memory_block:
            system_msg = system_msg.model_copy(
                update={"content": f"{system_msg.content}\n\n{memory_block}"}
            )

        # 3. Lấy lịch sử hội thoại của phiên hiện tại
        history_messages = self.memory_manager.get_session_messages(session_id)

        # 4. Cắt tỉa (Sliding Window Compaction) nếu vượt quá ngân sách Token
        system_tokens = system_msg.estimate_tokens()
        remaining_budget = max(64, budget - system_tokens)

        kept_history: List[Message] = []
        running_tokens = 0

        # Duyệt ngược từ tin nhắn mới nhất về cũ nhất để giữ mạch hội thoại gần nhất
        for msg in reversed(history_messages):
            msg_tokens = msg.estimate_tokens()
            if (
                running_tokens + msg_tokens <= remaining_budget
                or len(kept_history) < policy.keep_minimum_recent_messages
            ):
                kept_history.append(msg)
                running_tokens += msg_tokens
            else:
                break

        kept_history.reverse()
        dropped_count = len(history_messages) - len(kept_history)

        # Nếu có tin nhắn bị cắt bỏ, chèn một ghi chú tóm tắt nhỏ để AI biết ngữ cảnh trước đó đã được rút gọn
        final_messages: List[Message] = [system_msg]
        if dropped_count > 0:
            summary_notice = Message(
                role=Role.SYSTEM,
                content=f"[Context Notice: Đã lược bỏ {dropped_count} tin nhắn cũ để tối ưu bộ nhớ token.]",
            )
            final_messages.append(summary_notice)

        final_messages.extend(kept_history)
        total_estimated = sum(m.estimate_tokens() for m in final_messages)

        return AssembledContext(
            messages=final_messages,
            retrieved_memories=retrieved_memories,
            estimated_input_tokens=total_estimated,
            dropped_messages_count=dropped_count,
            active_skills=system_msg.metadata.get("active_skills", []),
        )
