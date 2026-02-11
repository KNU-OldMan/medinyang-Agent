# app/service/agent_service.py
from __future__ import annotations

import os
from typing import List, Dict, Any, Optional, AsyncGenerator

from openai import OpenAI  # openai==1.52.2
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from app.service.vector_service import VectorService
from app.service.agents.info_extractor_service import InfoExtractorService
from app.service.agents.knowledge_augmentor_service import KnowledgeAugmentorService
from app.service.agents.answer_gen_service import AnswerGenService

from app.agents import super_graph


# 배포 환경(Kubernetes)에서는 ConfigMap/Secret으로 환경변수가 자동 주입되므로 .env 로드를 건너뜁니다.
# 로컬 개발 환경에서만 .env 파일을 읽어오도록 처리합니다.
if os.getenv("KUBERNETES_SERVICE_HOST") is None:
    load_dotenv()


class AgentService:
    """
    API 서버(FastAPI)가 에이전트(Super Graph)와 소통하는 창구.
    - run_agent: 동기 실행(디버깅/테스트용)
    - stream_agent: LangGraph v2 astream_events 기반 스트리밍
    - add_knowledge/get_knowledge_stats: Vector DB 관리 헬퍼
    """

    def __init__(
        self,
        vector_service: VectorService,
        info_extractor_service: InfoExtractorService,
        knowledge_augmentor_service: KnowledgeAugmentorService,
        answer_gen_service: AnswerGenService,
    ):
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise ValueError("UPSTAGE_API_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")

        self.vector_service = vector_service
        self.info_extractor_service = info_extractor_service
        self.knowledge_augmentor_service = knowledge_augmentor_service
        self.answer_gen_service = answer_gen_service

    # -------------------------
    # Knowledge 관리 헬퍼
    # -------------------------
    def add_knowledge(
        self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        지식 베이스(Vector DB)에 새로운 정보를 추가합니다.
        """
        try:
            self.vector_service.add_documents(documents, metadatas)
            return {
                "status": "success",
                "message": f"Added {len(documents)} documents to knowledge base",
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to add documents: {str(e)}"}

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        현재 구축된 지식 베이스의 상태(문서 수 등)를 조회합니다.
        """
        return self.vector_service.get_collection_info()

    # -------------------------
    # Super Graph 실행
    # -------------------------
    def _build_config(self, session_id: Optional[str]) -> RunnableConfig:
        """
        그래프 노드들이 사용할 서비스(도구)들을 Config에 주입.
        MemorySaver 체크포인터를 위해 thread_id를 configurable에 넣습니다.
        """
        cfg: RunnableConfig = {
            "configurable": {
                "vector_service": self.vector_service,
                "info_extractor_service": self.info_extractor_service,
                "knowledge_augmentor_service": self.knowledge_augmentor_service,
                "answer_gen_service": self.answer_gen_service,
            }
        }
        if session_id:
            # ✅ MemorySaver(Checkpointer) 식별자
            cfg["configurable"]["thread_id"] = session_id
        return cfg

    def run_agent(self, inputs: Dict[str, Any], session_id: str | None = None) -> Dict[str, Any]:
        """
        에이전트를 실행하고 최종 결과를 반환합니다. (디버깅/테스트용)
        - session_id가 있으면 checkpointer가 이전 대화(answer_logs 등)를 불러옵니다.
        - 여기서는 초기 state를 최소로만 넣고, 이후 누적은 checkpointer가 담당하게 둡니다.
        """
        if "user_query" not in inputs:
            raise ValueError("inputs must include 'user_query'")

        full_inputs = {
            "user_query": inputs["user_query"],
            # ✅ 체크포인터가 불러오고 누적하므로 여기선 비워둠
            "answer_logs": [],
            "build_logs": [],
            "augment_logs": [],
            "extract_logs": [],
            "loop_count": 0,
        }

        config = self._build_config(session_id=session_id)

        result = super_graph.invoke(full_inputs, config=config)
        return result

    async def stream_agent(
        self, inputs: Dict[str, Any], session_id: str | None = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        에이전트를 스트리밍 모드로 실행합니다.
        LangGraph v2의 astream_events를 사용하여 이벤트 단위 스트리밍을 제공합니다.
        """
        if "user_query" not in inputs:
            raise ValueError("inputs must include 'user_query'")

        full_inputs = {
            "user_query": inputs["user_query"],
            "answer_logs": [],
            "build_logs": [],
            "augment_logs": [],
            "extract_logs": [],
            "loop_count": 0,
        }

        config = self._build_config(session_id=session_id)

        async for event in super_graph.astream_events(full_inputs, config=config, version="v2"):
            yield event
