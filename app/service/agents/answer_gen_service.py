# app/service/agents/answer_gen_service.py
from typing import Dict, Any, List, Optional

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from app.agents.subgraphs.answer_gen import answer_gen_graph
from app.agents.utils import clean_and_parse_json


class AnswerGenService:
    def run(
        self,
        user_query: str,
        extract_logs: List[BaseMessage],
        config: Optional[RunnableConfig] = None,
        history: Optional[List[BaseMessage]] = None,
    ) -> Dict[str, Any]:

        # 정보 추출 로그가 없으면 실패 처리
        if not extract_logs:
            return {
                "answer_logs": [AIMessage(content="내부 정보 추출에 실패했습니다. 잠시 후 다시 시도해 주세요.")],
                "process_status": "fail",
            }

        # Extractor(Verifier)의 마지막 응답(JSON) 파싱
        last_extract_msg = extract_logs[-1]
        parsed_result = clean_and_parse_json(getattr(last_extract_msg, "content", "") or "")

        status = (parsed_result.get("status") if parsed_result else "unknown") or "unknown"
        medical_context = (parsed_result.get("medical_context") if parsed_result else "") or ""
        key_points = (parsed_result.get("key_points") if parsed_result else []) or []

        # 상황에 따른 프롬프트 구성
        if status == "out_of_domain":
            prompt = f"""User Query: "{user_query}"

Task:
- You are a medical AI assistant.
- The user's query is unrelated to medical or health topics.
- Explain politely (Korean) that you can only help with medical/health topics.
- Offer to help if they ask a health-related question.
- Keep it concise and professional.
"""
        else:
            # insufficient / success / unknown 모두 여기로 들어옴
            # 데모용: insufficient이면 "가능한 범위의 일반 정보 + 추가 질문"을 반드시 포함하도록 유도
            extra_guidance = ""
            if status == "insufficient":
                extra_guidance = """
Additional Guidance:
- The context may be insufficient. Provide safe, general guidance.
- Add 3~5 follow-up questions to clarify symptoms (duration, fever, breathing, risk group).
- Avoid definitive diagnosis. Encourage medical consultation for red flags.
"""

            prompt = f"""User Query: "{user_query}"

Retrieved Medical Context:
===
{medical_context}
===

Key Points (if any):
{key_points}

Task:
- Provide a medical consultation based on the context and key points.
- Use Korean.
- Be empathetic and practical.
- Include red flags and when to seek medical care.
- Include the disclaimer that this is informational only and consult a real doctor.
{extra_guidance}
"""

        messages: List[BaseMessage] = []
        if history:
            messages.extend(history)
        messages.append(HumanMessage(content=prompt))

        # 그래프 실행
        sub_result = answer_gen_graph.invoke({"messages": messages}, config=config)

        # 결과 필터링 (새로 생성된 AI 메시지만 추출)
        history_len = len(messages)
        new_messages = [
            msg for msg in sub_result["messages"][history_len:]
            if isinstance(msg, AIMessage)
        ]

        return {
            "answer_logs": new_messages,
            "process_status": "success",
        }
