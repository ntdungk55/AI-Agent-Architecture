"""
Application Bootstrapper (Dependency Injection Container).
Khởi tạo và kết nối cả 7 module thành một hệ thống AI Agent hoàn chỉnh.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from agent_core.context_manager import ContextManager, ContextWindowPolicy
from agent_core.llm_manager import (
    APIKeyCredential,
    LLMManager,
    LLMProviderType,
    ModelSpec,
    SmartMockLLMProvider,
)
from agent_core.memory_manager import DataSourceType, MemoryManager
from agent_core.monitoring import MonitoringManager
from agent_core.orchestrator import AgentOrchestrator
from agent_core.prompt_manager import SkillDefinition, SystemPromptManager
from agent_core.shared.models import utc_now
from agent_core.tool_manager import (
    CalculatorTool,
    ExternalSystemControlTool,
    ToolManager,
)


@dataclass
class AgentAppContainer:
    """Container giữ tham chiếu tới cả 7 module để dễ dàng theo dõi và kiểm thử."""

    llm_manager: LLMManager
    prompt_manager: SystemPromptManager
    orchestrator: AgentOrchestrator
    context_manager: ContextManager
    memory_manager: MemoryManager
    tool_manager: ToolManager
    monitoring_manager: MonitoringManager


async def build_default_agent_app() -> AgentAppContainer:
    """
    Khởi tạo toàn bộ 7 module với cấu hình mẫu chuẩn chỉnh:
    - Đăng ký Model chính (đã hết hạn key để demo cơ chế tự động Fallback) & Model dự phòng.
    - Đăng ký các tầng Prompt (App, User, Session, Skills).
    - Nạp sẵn dữ liệu mẫu vào Memory Manager (RAG & Entity Facts).
    - Đăng ký các công cụ vào Tool Manager.
    """
    now = utc_now()

    # 1. Khởi tạo Module 1: LLM Manager
    llm_manager = LLMManager(global_token_budget=100_000)
    llm_manager.register_provider(SmartMockLLMProvider())

    # Đăng ký 2 model: model chính và model fallback
    llm_manager.register_model(
        ModelSpec(
            model_id="gemini-2.5-pro-expired-demo",
            provider=LLMProviderType.MOCK,
            display_name="Gemini 2.5 Pro (Primary)",
            context_window_limit=32_000,
            is_deprecated=True,  # Giả lập model hết hạn để kiểm tra tính năng tự động chuyển đổi
        ),
        is_default=True,
    )
    llm_manager.register_model(
        ModelSpec(
            model_id="gemini-2.5-flash-active",
            provider=LLMProviderType.MOCK,
            display_name="Gemini 2.5 Flash (Active Fallback)",
            context_window_limit=32_000,
        )
    )
    llm_manager.set_fallback_chain(["gemini-2.5-flash-active"])

    # Đăng ký 1 API key đã hết hạn và 1 API key còn hạn
    llm_manager.register_api_key(
        APIKeyCredential(
            key_id="key_expired_01",
            provider=LLMProviderType.MOCK,
            api_key="mock-secret-expired",
            expires_at=now - timedelta(days=1),
        )
    )
    llm_manager.register_api_key(
        APIKeyCredential(
            key_id="key_active_02",
            provider=LLMProviderType.MOCK,
            api_key="mock-secret-active",
            expires_at=now + timedelta(days=30),
            max_token_quota=50_000,
        )
    )

    # 2. Khởi tạo Module 2: System Prompt Manager
    prompt_manager = SystemPromptManager(
        default_app_prompt=(
            "Bạn là Antigravity Enterprise Agent hoạt động theo kiến trúc 7 module chuẩn hóa."
        )
    )
    prompt_manager.register_skill(
        SkillDefinition(
            skill_id="skill_math_analyst",
            name="Chuyên gia Phân tích & Tính toán",
            description="Kích hoạt khi người dùng yêu cầu tính toán số liệu hoặc tài chính.",
            instructions="Luôn gọi công cụ `calculator` để tính toán chính xác trước khi trả lời.",
            trigger_keywords=["tính", "chi phí", "doanh thu", "calculate"],
            allowed_tools=["calculator"],
        )
    )

    # 3. Khởi tạo Module 5: Memory Manager (Quản lý các Data Source)
    memory_manager = MemoryManager()
    await memory_manager.store_knowledge(
        content="Người dùng ưu tiên trình bày ngắn gọn bằng tiếng Việt và thích kiến trúc Clean Architecture.",
        source_type=DataSourceType.ENTITY_FACT,
        user_id="dev_user_01",
    )
    await memory_manager.store_knowledge(
        content="Quy định công ty: Ngân sách máy chủ AI hàng tháng tối đa là 6,400 USD.",
        source_type=DataSourceType.SEMANTIC_RAG,
        user_id="dev_user_01",
    )

    # 4. Khởi tạo Module 4: Context Manager
    context_manager = ContextManager(
        prompt_manager=prompt_manager,
        memory_manager=memory_manager,
        default_policy=ContextWindowPolicy(
            max_context_tokens=2048,
            reserved_output_tokens=512,
            max_retrieved_memories=3,
            keep_minimum_recent_messages=4,
        ),
    )

    # 5. Khởi tạo Module 6: Tool Manager
    tool_manager = ToolManager()
    tool_manager.register_tool(CalculatorTool())
    tool_manager.register_tool(ExternalSystemControlTool())

    # 6. Khởi tạo Module 7: Monitoring & Validators
    monitoring_manager = MonitoringManager()

    # 7. Khởi tạo Module 3: Agent Orchestrator
    orchestrator = AgentOrchestrator(
        llm_manager=llm_manager,
        prompt_manager=prompt_manager,
        context_manager=context_manager,
        memory_manager=memory_manager,
        tool_manager=tool_manager,
        monitoring_manager=monitoring_manager,
    )

    return AgentAppContainer(
        llm_manager=llm_manager,
        prompt_manager=prompt_manager,
        orchestrator=orchestrator,
        context_manager=context_manager,
        memory_manager=memory_manager,
        tool_manager=tool_manager,
        monitoring_manager=monitoring_manager,
    )
