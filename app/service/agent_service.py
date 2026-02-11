# app/service/agent_service.py
from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

from openai import OpenAI
from langchain_core.messages import HumanMessage

from app.exceptions import AgentException, ValidationException
from app.service.vector_service import VectorService
from app.service.agents.info_extractor_service import InfoExtractorService
from app.service.agents.knowledge_augmentor_service import KnowledgeAugmentorService
from app.service.agents.answer_gen_service import AnswerGenService
from app.agents import super_graph


class AgentService:
    def __init__(
        self,
        vector_service: VectorService,
        info_extractor_service: InfoExtractorService,
        knowledge_augmentor_service: KnowledgeAugmentorService,
        answer_gen_service: AnswerGenService,
    ):
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise ValidationException("UPSTAGE_API_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")

        self.vector_service = vector_service
        self.info_extractor_service = info_extractor_service
        self.knowledge_augmentor_service = knowledge_augmentor_service
        self.answer_gen_service = answer_gen_service

    def add_knowledge(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, str]:
        try:
            self.vector_service.add_documents(documents, metadatas)
            return {"status": "success", "message": f"Added {len(documents)} documents to knowledge base"}
        except Exception as e:
            # VectorService가 KnowledgeBaseException을 던지더라도
            # 여기서는 API 응답용으로만 포맷팅하고 싶으면 이렇게 처리
            return {"status": "error", "message": f"Failed to add documents: {str(e)}"}

    def get_knowledge_stats(self) -> Dict[str, Any]:
        return self.vector_service.get_collection_info()

    def run_agent(self, inputs: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        if not inputs or not inputs.get("user_query"):
            raise ValidationException("user_query is required")

        full_inputs = {
            "user_query": inputs["user_query"],
            "answer_logs": [HumanMessage(content=inputs["user_query"])],
            "build_logs": [],
            "augment_logs": [],
            "extract_logs": [],
            "loop_count": 0,
        }

        config: Dict[str, Any] = {
            "configurable": {
                "vector_service": self.vector_service,
                "info_extractor_service": self.info_extractor_service,
                "knowledge_augmentor_service": self.knowledge_augmentor_service,
                "answer_gen_service": self.answer_gen_service,
            }
        }
        if session_id:
            config["configurable"]["thread_id"] = session_id

        try:
            return super_graph.invoke(full_inputs, config=config)
        except BaseException as e:
            raise AgentException(
                f"Agent execution failed: {str(e)}",
                details={"user_query": inputs.get("user_query", ""), "session_id": session_id or ""},
            )

    async def stream_agent(self, inputs: Dict[str, Any], session_id: str = None):
        if not inputs or not inputs.get("user_query"):
            raise ValidationException("user_query is required")

        full_inputs = {
            "user_query": inputs["user_query"],
            "answer_logs": [HumanMessage(content=inputs["user_query"])],
            "build_logs": [],
            "augment_logs": [],
            "extract_logs": [],
            "loop_count": 0,
        }

        config: Dict[str, Any] = {
            "configurable": {
                "vector_service": self.vector_service,
                "info_extractor_service": self.info_extractor_service,
                "knowledge_augmentor_service": self.knowledge_augmentor_service,
                "answer_gen_service": self.answer_gen_service,
            }
        }
        if session_id:
            config["configurable"]["thread_id"] = session_id

        try:
            async for event in super_graph.astream_events(full_inputs, config=config, version="v2"):
                yield event
        except BaseException as e:
            raise AgentException(
                f"Agent streaming failed: {str(e)}",
                details={"user_query": inputs.get("user_query", ""), "session_id": session_id or ""},
            )
