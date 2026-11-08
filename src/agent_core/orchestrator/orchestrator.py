"""
Module 3: Agent Orchestrator - Session & ReAct Loop Coordinator.
Nhạc trưởng điều phối sự phối hợp nhịp nhàng giữa 6 module còn lại:
[7. Monitoring] -> [5. Memory] -> [4. Context + 2. Prompt] -> [1. LLM] -> [6. Tool] -> [7. Monitoring]
"""

from __future__ import annotations

from typing import Dict, Optional

from agent_core.context_manager.manager import ContextManager
from agent_core.llm_manager.manager import LLMManager
from agent_core.llm_manager.models import LLMRequest
from agent_core.memory_manager.manager import MemoryManager
from agent_core.monitoring.monitor import MonitoringManager
from agent_core.prompt_manager.composer import SystemPromptManager
from agent_core.shared.exceptions import GuardrailViolationError
from agent_core.shared.models import Message, Role, TokenUsage
from agent_core.tool_manager.registry import ToolManager

from .models import AgentSession, AgentTurnResult, SessionStatus


class AgentOrchestrator:
    """
    Facade trung tâm của Module 3 (Agent Orchestrator):
    - Quản lý danh sách các phiên làm việc (Session Lifecycle).
    - Điều khiển vòng lặp suy luận - hành động (Think -> Validate -> Act -> Observe).
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: SystemPromptManager,
        context_manager: ContextManager,
        memory_manager: MemoryManager,
        tool_manager: ToolManager,
        monitoring_manager: MonitoringManager,
    ) -> None:
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.context_manager = context_manager
        self.memory_manager = memory_manager
        self.tool_manager = tool_manager
        self.monitoring = monitoring_manager
        self._sessions: Dict[str, AgentSession] = {}

    def create_session(
        self,
        user_id: str,
        preferred_model_id: str = "gpt-4o-primary",
        session_prompt: Optional[str] = None,
        session_token_budget: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> AgentSession:
        """Khởi tạo một phiên làm việc mới và cấu hình Prompt/Budget cho phiên đó."""
        session = AgentSession(
            user_id=user_id,
            preferred_model_id=preferred_model_id,
            **({"session_id": session_id} if session_id else {}),
        )
        self._sessions[session.session_id] = session

        if session_prompt:
            self.prompt_manager.set_session_prompt(session.session_id, session_prompt)
        if session_token_budget is not None:
            self.llm_manager.token_tracker.set_session_budget(
                session.session_id, session_token_budget
            )

        self.monitoring.record_event(
            session_id=session.session_id,
            module_name="3.Orchestrator",
            step_name="SessionCreated",
            details={"user_id": user_id, "preferred_model": preferred_model_id},
        )
        return session

    def get_session(self, session_id: str) -> AgentSession:
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' không tồn tại.")
        return self._sessions[session_id]

    async def handle_user_message(
        self,
        session_id: str,
        user_input: str,
    ) -> AgentTurnResult:
        """
        Thực thi trọn vẹn 1 lượt tương tác của người dùng qua tất cả 7 module.
        """
        session = self.get_session(session_id)
        session.status = SessionStatus.RUNNING

        try:
            # BƯỚC 1: [Module 7 - Monitoring] Kiểm duyệt an toàn đầu vào của User
            clean_input = self.monitoring.validate_input(session_id, user_input)

            # BƯỚC 2: [Module 5 - Memory] Lưu tin nhắn của User vào bộ nhớ phiên
            user_msg = Message(role=Role.USER, content=clean_input)
            self.memory_manager.append_message(session_id, user_msg)

            turn_usage = TokenUsage()
            invoked_tools = []
            active_skills = []
            last_model_used = session.preferred_model_id
            last_key_used = "unknown"
            final_answer = ""

            # BƯỚC 3: Vòng lặp ReAct (Think -> Act -> Observe)
            for iteration in range(1, session.max_react_steps + 1):
                # 3.1: [Module 4 - Context & Module 2 - Prompt & Module 5 - Memory RAG]
                assembled_ctx = await self.context_manager.build_context(
                    session_id=session_id,
                    user_query=clean_input,
                    user_id=session.user_id,
                    explicit_skill_ids=session.explicit_skills,
                )
                active_skills = assembled_ctx.active_skills
                self.monitoring.record_event(
                    session_id=session_id,
                    module_name="4.ContextManager",
                    step_name=f"AssembleContext(iter={iteration})",
                    details={
                        "messages_count": len(assembled_ctx.messages),
                        "retrieved_memories": len(assembled_ctx.retrieved_memories),
                        "estimated_tokens": assembled_ctx.estimated_input_tokens,
                        "dropped_messages": assembled_ctx.dropped_messages_count,
                        "active_skills": active_skills,
                    },
                )

                # 3.2: [Module 6 - Tool Manager] Xuất JSON Schema các công cụ khả dụng
                tools_schema = self.tool_manager.get_tools_schema(session.allowed_tools)

                # 3.3: [Module 1 - LLM Manager] Gọi LLM (tự động chọn Key & Fallback nếu cần)
                llm_req = LLMRequest(
                    model_id=session.preferred_model_id,
                    messages=assembled_ctx.messages,
                    tools_schema=tools_schema,
                    settings=session.llm_settings,
                    session_id=session_id,
                )
                llm_resp = await self.llm_manager.chat_completion(llm_req)
                turn_usage = turn_usage.add(llm_resp.usage)
                last_model_used = llm_resp.model_id
                last_key_used = llm_resp.key_id_used

                self.monitoring.record_event(
                    session_id=session_id,
                    module_name="1.LLMManager",
                    step_name=f"ChatCompletion(iter={iteration})",
                    duration_ms=llm_resp.latency_ms,
                    details={
                        "model_used": llm_resp.model_id,
                        "key_used": llm_resp.key_id_used,
                        "tokens": llm_resp.usage.total_tokens,
                        "tool_calls_count": len(llm_resp.tool_calls),
                    },
                )

                # 3.4: Nếu LLM yêu cầu gọi Tool (Tool Calling)
                if llm_resp.tool_calls:
                    assistant_tool_msg = Message(
                        role=Role.ASSISTANT,
                        content=llm_resp.content,
                        tool_calls=llm_resp.tool_calls,
                    )
                    self.memory_manager.append_message(session_id, assistant_tool_msg)

                    for tool_call in llm_resp.tool_calls:
                        # [Module 7 - Monitoring] Kiểm duyệt lệnh gọi Tool trước khi chạy
                        self.monitoring.validate_tool_call(session_id, tool_call)

                        # [Module 6 - Tool Manager] Thực thi Tool
                        tool_result = await self.tool_manager.execute_tool_call(tool_call)
                        invoked_tools.append(tool_call.name)

                        self.monitoring.record_event(
                            session_id=session_id,
                            module_name="6.ToolManager",
                            step_name=f"ExecuteTool:{tool_call.name}",
                            status="OK" if tool_result.success else "ERROR",
                            duration_ms=tool_result.execution_time_ms,
                            details={
                                "arguments": tool_call.arguments,
                                "output": tool_result.output or tool_result.error_message,
                            },
                        )

                        # [Module 5 - Memory] Lưu kết quả Tool vào phiên để LLM quan sát ở vòng lặp kế tiếp
                        observation_text = (
                            tool_result.output
                            if tool_result.success
                            else f"Error: {tool_result.error_message}"
                        )
                        tool_msg = Message(
                            role=Role.TOOL,
                            name=tool_call.name,
                            tool_call_id=tool_call.id,
                            content=observation_text,
                        )
                        self.memory_manager.append_message(session_id, tool_msg)

                    # Tiếp tục vòng lặp để LLM tổng hợp câu trả lời từ kết quả Tool
                    continue

                # 3.5: Nếu LLM đã đưa ra câu trả lời cuối cùng (không gọi thêm Tool)
                validated_output = self.monitoring.validate_output(
                    session_id, llm_resp.content
                )
                final_msg = Message(role=Role.ASSISTANT, content=validated_output)
                self.memory_manager.append_message(session_id, final_msg)
                final_answer = validated_output
                session.status = SessionStatus.COMPLETED

                return AgentTurnResult(
                    session_id=session_id,
                    user_id=session.user_id,
                    final_answer=final_answer,
                    model_used=last_model_used,
                    key_used=last_key_used,
                    iterations_used=iteration,
                    invoked_tools=invoked_tools,
                    active_skills=active_skills,
                    turn_usage=turn_usage,
                    traces=self.monitoring.get_session_traces(session_id),
                )

            # Nếu chạm giới hạn số bước lặp tối đa
            session.status = SessionStatus.COMPLETED
            return AgentTurnResult(
                session_id=session_id,
                user_id=session.user_id,
                final_answer=final_answer or "Đã đạt giới hạn bước suy luận tối đa của phiên.",
                model_used=last_model_used,
                key_used=last_key_used,
                iterations_used=session.max_react_steps,
                invoked_tools=invoked_tools,
                active_skills=active_skills,
                turn_usage=turn_usage,
                traces=self.monitoring.get_session_traces(session_id),
            )

        except GuardrailViolationError:
            session.status = SessionStatus.BLOCKED_BY_GUARDRAIL
            raise
        except Exception:
            session.status = SessionStatus.FAILED
            raise
