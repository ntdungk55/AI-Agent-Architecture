"""
Module 5: Memory Manager - Data Source Connectors & Unified MemoryManager.
Quản lý tất cả các nguồn dữ liệu (Working Memory, Vector/RAG Knowledge Base,
Episodic Memory, Entity Facts) thông qua một cổng truy xuất thống nhất.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from agent_core.shared.models import Message

from .models import DataSourceType, MemoryItem


class BaseDataSource(ABC):
    """Interface chuẩn cho mọi nguồn dữ liệu (SQL, Redis, VectorDB, Document Store...)."""

    source_type: DataSourceType

    @abstractmethod
    async def add(self, item: MemoryItem) -> None:
        """Lưu một bản ghi vào nguồn dữ liệu."""

    @abstractmethod
    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[MemoryItem]:
        """Truy vấn dữ liệu liên quan đến câu hỏi hiện tại."""


class InMemoryDataSource(BaseDataSource):
    """
    Triển khai Data Source trên bộ nhớ (dễ dàng thay thế bằng ChromaDB, Qdrant, PostgreSQL, Redis)
    có hỗ trợ chấm điểm từ khóa (keyword similarity) để mô phỏng RAG & Episodic Retrieval.
    """

    def __init__(self, source_type: DataSourceType) -> None:
        self.source_type = source_type
        self._items: List[MemoryItem] = []

    async def add(self, item: MemoryItem) -> None:
        self._items.append(item)

    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[MemoryItem]:
        query_words = {w.lower() for w in query.split() if len(w) > 1}
        results: List[MemoryItem] = []

        for item in self._items:
            if user_id and item.user_id and item.user_id != user_id:
                continue
            if session_id and item.session_id and item.session_id != session_id:
                continue

            if not query_words:
                score = 1.0
            else:
                content_lower = item.content.lower()
                matched = sum(1 for w in query_words if w in content_lower)
                # Với ENTITY_FACT của user thì luôn ưu tiên lấy ra
                if self.source_type == DataSourceType.ENTITY_FACT and matched == 0:
                    score = 0.5
                else:
                    score = matched / max(1, len(query_words))

            if score > 0:
                results.append(item.model_copy(update={"relevance_score": round(score, 3)}))

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]


class MemoryManager:
    """
    Facade trung tâm của Module 5 (Memory Manager):
    - Quản lý lịch sử hội thoại theo từng phiên (Working Conversation Store).
    - Điều phối truy vấn đa nguồn dữ liệu (Semantic RAG, Episodic Memory, Entity Facts).
    """

    def __init__(self) -> None:
        self._conversation_history: Dict[str, List[Message]] = {}
        self._data_sources: Dict[DataSourceType, BaseDataSource] = {
            DataSourceType.SEMANTIC_RAG: InMemoryDataSource(DataSourceType.SEMANTIC_RAG),
            DataSourceType.EPISODIC: InMemoryDataSource(DataSourceType.EPISODIC),
            DataSourceType.ENTITY_FACT: InMemoryDataSource(DataSourceType.ENTITY_FACT),
        }

    def register_data_source(self, source: BaseDataSource) -> None:
        """Cho phép gắn thêm hoặc ghi đè nguồn dữ liệu (VD: gắn QdrantVectorSource)."""
        self._data_sources[source.source_type] = source

    # --- Quản lý Working Conversation History ---

    def append_message(self, session_id: str, message: Message) -> None:
        if session_id not in self._conversation_history:
            self._conversation_history[session_id] = []
        self._conversation_history[session_id].append(message)

    def get_session_messages(self, session_id: str) -> List[Message]:
        return list(self._conversation_history.get(session_id, []))

    def clear_session_messages(self, session_id: str) -> None:
        self._conversation_history.pop(session_id, None)

    # --- Quản lý Long-Term & External Data Sources ---

    async def store_knowledge(
        self,
        content: str,
        source_type: DataSourceType = DataSourceType.SEMANTIC_RAG,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> MemoryItem:
        item = MemoryItem(
            source_type=source_type,
            content=content,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {},
        )
        source = self._data_sources.get(source_type)
        if not source:
            raise ValueError(f"Data source '{source_type.value}' chưa được đăng ký.")
        await source.add(item)
        return item

    async def retrieve_relevant_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        top_k_per_source: int = 3,
    ) -> List[MemoryItem]:
        """Truy vấn đồng thời trên các nguồn dữ liệu (Entity Facts, Episodic, RAG)."""
        aggregated: List[MemoryItem] = []
        for source_type in (
            DataSourceType.ENTITY_FACT,
            DataSourceType.EPISODIC,
            DataSourceType.SEMANTIC_RAG,
        ):
            source = self._data_sources.get(source_type)
            if source:
                found = await source.search(
                    query=query, user_id=user_id, top_k=top_k_per_source
                )
                aggregated.extend(found)
        return aggregated
