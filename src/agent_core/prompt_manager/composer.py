"""
Module 2: System Prompt Manager - Skill Registry & Prompt Composer.
Kết hợp tất cả các tầng Prompt (App -> User -> Session -> Skills) thành một
System Message hoàn chỉnh trước khi đưa vào Context Manager.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from agent_core.shared.models import Message, Role

from .models import PromptLayerConfig, SkillDefinition


class SystemPromptManager:
    """
    Quản lý toàn bộ các tầng Prompt (App, User, Chat Session, Skills)
    và biên dịch (compile) chúng thành System Prompt cuối cùng.
    """

    def __init__(self, default_app_prompt: Optional[str] = None) -> None:
        self._app_prompt: str = default_app_prompt or (
            "Bạn là một trợ lý AI Agent chuyên nghiệp. "
            "Hãy suy luận từng bước, sử dụng công cụ (Tools) khi cần thiết và bảo mật thông tin."
        )
        self._user_prompts: Dict[str, str] = {}
        self._session_prompts: Dict[str, str] = {}
        self._skills: Dict[str, SkillDefinition] = {}

    # --- Quản lý các tầng Prompt ---

    def set_app_system_prompt(self, prompt: str) -> None:
        self._app_prompt = prompt.strip()

    def set_user_system_prompt(self, user_id: str, prompt: str) -> None:
        self._user_prompts[user_id] = prompt.strip()

    def set_session_prompt(self, session_id: str, prompt: str) -> None:
        self._session_prompts[session_id] = prompt.strip()

    # --- Quản lý Skills ---

    def register_skill(self, skill: SkillDefinition) -> None:
        self._skills[skill.skill_id] = skill

    def resolve_active_skills(
        self,
        user_query: str = "",
        explicit_skill_ids: Optional[List[str]] = None,
    ) -> List[SkillDefinition]:
        """Xác định danh sách các Skill cần kích hoạt dựa trên chỉ định hoặc từ khóa."""
        explicit_set = set(explicit_skill_ids or [])
        matched: List[SkillDefinition] = []
        for skill_id, skill in self._skills.items():
            if skill_id in explicit_set or skill.matches_query(user_query):
                matched.append(skill)
        return matched

    # --- Biên dịch System Prompt hoàn chỉnh ---

    def build_system_message(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_query: str = "",
        explicit_skill_ids: Optional[List[str]] = None,
        extra_variables: Optional[Dict[str, str]] = None,
    ) -> Message:
        """
        Hợp nhất 4 tầng Prompt:
        [1. APP SYSTEM PROMPT] -> [2. USER SYSTEM PROMPT] -> [3. CHAT SESSION PROMPT] -> [4. SKILLS]
        """
        sections: List[str] = []

        # 1. App System Prompt
        if self._app_prompt:
            sections.append(f"### [APP SYSTEM INSTRUCTIONS]\n{self._app_prompt}")

        # 2. User System Prompt
        if user_id and user_id in self._user_prompts and self._user_prompts[user_id]:
            sections.append(
                f"### [USER PREFERENCES ({user_id})]\n{self._user_prompts[user_id]}"
            )

        # 3. Chat Session Prompt
        if session_id and session_id in self._session_prompts and self._session_prompts[session_id]:
            sections.append(
                f"### [CHAT SESSION CONTEXT ({session_id})]\n{self._session_prompts[session_id]}"
            )

        # 4. Skills Prompt
        active_skills = self.resolve_active_skills(
            user_query=user_query, explicit_skill_ids=explicit_skill_ids
        )
        if active_skills:
            skill_blocks = []
            for sk in active_skills:
                tools_note = (
                    f" (Tools ưu tiên: {', '.join(sk.allowed_tools)})"
                    if sk.allowed_tools
                    else ""
                )
                skill_blocks.append(f"- **{sk.name}**{tools_note}: {sk.instructions}")
            sections.append("### [ACTIVE SKILLS]\n" + "\n".join(skill_blocks))

        compiled_text = "\n\n".join(sections)

        # Render biến động (nếu có)
        if extra_variables:
            for k, v in extra_variables.items():
                compiled_text = compiled_text.replace(f"{{{{{k}}}}}", str(v))

        return Message(
            role=Role.SYSTEM,
            content=compiled_text,
            metadata={
                "active_skills": [s.skill_id for s in active_skills],
                "user_id": user_id,
                "session_id": session_id,
            },
        )
