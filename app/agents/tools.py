from typing import Optional, Dict, Any, List

from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from app.core.llm import get_solar_chat
from app.service.vector_service import VectorService
from app.repository.client.search_client import SerperSearchClient
from app.agents.utils import normalize_metadata


solar_chat = get_solar_chat()
search_client = SerperSearchClient()


@tool
def add_to_medical_qa(content: str, config: RunnableConfig, metadata: Optional[Dict] = None) -> str:
    """
    외부에서 찾은 유용한 의학 정보를 내부 지식 저장소(ChromaDB)에 추가합니다.
    metadata는 dict 형태이며, 표준 스키마로 정규화됩니다.
    """
    try:
        vector_service: VectorService = config["configurable"].get("vector_service")
        if not vector_service:
            return "Error: VectorService not found in config"

        meta_in = metadata or {}
        # 표준 스키마 강제
        meta = normalize_metadata(
            source=meta_in.get("source", "google_search"),
            domain=meta_in.get("domain", "unknown"),
            title=meta_in.get("title", ""),
            query=meta_in.get("query", ""),
            fetched_at=meta_in.get("fetched_at"),
            extra=meta_in.get("extra"),
        )

        vector_service.add_documents([content], metadatas=[meta])
        return "Successfully added information to knowledge base."
    except Exception as e:
        return f"Error adding to knowledge base: {e}"


@tool
def google_search(query: str) -> str:
    """
    내부 지식이 부족할 때, Google 검색을 통해 최신 의학 정보를 찾습니다.
    """
    try:
        result = search_client.search(query)
        return result
    except Exception as e:
        return f"Google Search Error: {e}"


@tool
def search_medical_qa(query: str, config: RunnableConfig) -> str:
    """
    사용자 질문과 관련된 의학 정보를 내부 DB에서 검색합니다.
    """
    try:
        vector_service: Optional[VectorService] = config["configurable"].get("vector_service")
        if not vector_service:
            return "Error: VectorService not found in config"

        results = vector_service.search(query, n_results=5)
        docs: List[str] = results.get("documents", []) or []
        metas: List[Dict[str, Any]] = results.get("metadatas", []) or []
        dists: List[float] = results.get("distances", []) or []

        if not docs:
            return ""  # 검색 결과 없음

        context_parts = []
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else None
            context_parts.append(
                f"Source {i+1} (distance={dist}, metadata={meta}):\n{doc}"
            )

        return "\n\n".join(context_parts)
    except Exception as e:
        return f"Search Error: {e}"
