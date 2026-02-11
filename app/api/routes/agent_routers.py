# app/api/route/agent_routers.py

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.logger import logger
from app.core.seed import get_seed_status
from app.deps import get_agent_service
from app.service.agent_service import AgentService

from app.models import (
    AddKnowledgeRequest,
    KnowledgeResponse,
    StatsResponse,
    ChatRequest,
    ChatResponse,
    TokenStreamEvent,
    LogStreamEvent,
    ErrorStreamEvent,
)

from app.exceptions import AgentException, KnowledgeBaseException


router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "Agent service is running"}


@router.get("/seed-status")
async def seed_status():
    """시딩 진행 상태 확인"""
    return get_seed_status()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    일반(Non-streaming) 채팅
    - super_graph가 끝날 때까지 기다린 뒤 최종 답변만 반환
    """
    try:
        inputs = {"user_query": request.query, "process_status": "start"}
        result = agent_service.run_agent(inputs, session_id=request.session_id)

        answer = ""
        answer_logs = result.get("answer_logs", [])
        if answer_logs:
            # 마지막 AIMessage의 content를 최종 답변으로 간주
            last_msg = answer_logs[-1]
            answer = getattr(last_msg, "content", "") or ""

        return ChatResponse(
            answer=answer,
            user_query=result.get("user_query", request.query),
            process_status=result.get("process_status", "success"),
            loop_count=result.get("loop_count", 0),
        )

    except (AgentException, KnowledgeBaseException) as e:
        raise e
    except Exception as e:
        raise AgentException(f"Chat processing failed: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    SSE 스트리밍 채팅
    - Workflow 단계 로그(LogStreamEvent)
    - 최종 답변 토큰(TokenStreamEvent)
    """

    async def event_generator():
        current_node = ""  # 현재 워크플로우 단계 추적

        try:
            inputs = {"user_query": request.query, "process_status": "start"}

            async for event in agent_service.stream_agent(
                inputs, session_id=request.session_id
            ):
                kind = event.get("event")
                name = event.get("name", "")

                # 1) 체인(노드) 시작 시: 상태 로그
                if kind == "on_chain_start":
                    # super_graph / workflow 관련 노드 이름만 추적
                    if name:
                        current_node = name

                        if name == "info_extract_agent_workflow":
                            yield (
                                "data: "
                                + LogStreamEvent(
                                    log="내부 지식 검색 중..."
                                ).model_dump_json(ensure_ascii=False)
                                + "\n\n"
                            )
                        elif name == "knowledge_augment_workflow":
                            yield (
                                "data: "
                                + LogStreamEvent(
                                    log="외부 지식 검색 중(Google Search)..."
                                ).model_dump_json(ensure_ascii=False)
                                + "\n\n"
                            )
                        elif name == "answer_gen_agent_workflow":
                            yield (
                                "data: "
                                + LogStreamEvent(
                                    log="답변 생성 중..."
                                ).model_dump_json(ensure_ascii=False)
                                + "\n\n"
                            )

                # 2) Tool 시작 시: 도구 로그
                elif kind == "on_tool_start":
                    tool_name = event.get("name", "")
                    if tool_name == "search_medical_qa":
                        yield (
                            "data: "
                            + LogStreamEvent(
                                log="내부 DB 검색 실행..."
                            ).model_dump_json(ensure_ascii=False)
                            + "\n\n"
                        )
                    elif tool_name == "google_search":
                        yield (
                            "data: "
                            + LogStreamEvent(
                                log="Google 검색 실행..."
                            ).model_dump_json(ensure_ascii=False)
                            + "\n\n"
                        )

                # 3) LLM 토큰 스트림
                elif kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    content = getattr(chunk, "content", None)

                    if content:
                        # IMPORTANT: Extract/Augment 단계 출력은 사용자에게 숨기고,
                        # AnswerGen 단계에서만 토큰 전송
                        if current_node == "answer_gen_agent_workflow":
                            yield (
                                "data: "
                                + TokenStreamEvent(answer=content).model_dump_json(
                                    ensure_ascii=False
                                )
                                + "\n\n"
                            )

            # 종료 신호
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield (
                "data: "
                + ErrorStreamEvent(error=str(e)).model_dump_json(ensure_ascii=False)
                + "\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/knowledge", response_model=KnowledgeResponse)
async def add_knowledge(
    request: AddKnowledgeRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    """문서를 수동으로 추가"""
    try:
        result = agent_service.add_knowledge(
            documents=request.documents,
            metadatas=request.metadatas,
        )
        return KnowledgeResponse(**result)

    except (AgentException, KnowledgeBaseException) as e:
        raise e
    except Exception as e:
        raise KnowledgeBaseException(f"Adding knowledge failed: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_knowledge_stats(
    agent_service: AgentService = Depends(get_agent_service),
):
    """현재 지식베이스 통계 조회"""
    try:
        stats = agent_service.get_knowledge_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise KnowledgeBaseException(f"Failed to get stats: {str(e)}")


@router.delete("/knowledge/{doc_id}")
async def delete_knowledge(
    doc_id: str,
    agent_service: AgentService = Depends(get_agent_service),
):
    """특정 문서를 ID로 삭제"""
    try:
        agent_service.vector_service.delete_document(doc_id)
        return {"status": "success", "message": f"Document {doc_id} deleted"}
    except Exception as e:
        raise KnowledgeBaseException(f"Deletion failed: {str(e)}")
