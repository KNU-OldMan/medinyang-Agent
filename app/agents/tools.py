from typing import Optional, Dict, Any, List

from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from app.core.llm import get_solar_chat
from app.service.vector_service import VectorService
from app.repository.client.search_client import SerperSearchClient

solar_chat = get_solar_chat()
search_client = SerperSearchClient()


@tool
def add_to_medical_qa(
    content: str,
    config: RunnableConfig,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    외부에서 찾은 유용한 의학 정보를 내부 지식 저장소(ChromaDB)에 추가합니다.
    """
    try:
        vector_service: Optional[VectorService] = config["configurable"].get("vector_service")
        if not vector_service:
            return "Error: VectorService not found in config"

        vector_service.add_documents(
            documents=[content],
            metadatas=[metadata or {"source": "google_search"}],
        )
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
